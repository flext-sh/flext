package pagination

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/wms/infrastructure/auth"
)

// WMSPaginator implements pagination for Oracle WMS API
type WMSPaginator struct {
	authenticator *auth.WMSAuthenticator
	config        PaginationConfig
	state         PaginationState
}

// PaginationConfig configures pagination behavior
type PaginationConfig struct {
	Mode     string          `json:"mode"` // "cursor", "offset"
	PageSize int             `json:"page_size"`
	MaxPages *int            `json:"max_pages,omitempty"`
	OrderBy  []OrderByClause `json:"order_by"`

	// Cursor-based pagination
	CursorField     string `json:"cursor_field,omitempty"`
	CursorDirection string `json:"cursor_direction"` // "asc", "desc"

	// Offset-based pagination
	OffsetField string `json:"offset_field,omitempty"`

	// Performance optimizations
	PreloadNextPage bool          `json:"preload_next_page"`
	ConcurrentPages int           `json:"concurrent_pages"`
	RequestTimeout  time.Duration `json:"request_timeout"`

	// Custom parameters
	CustomParams map[string]string `json:"custom_params"`
}

// OrderByClause defines ordering for pagination
type OrderByClause struct {
	Field     string `json:"field"`
	Direction string `json:"direction"` // "asc", "desc"
}

// PaginationState tracks the current pagination state
type PaginationState struct {
	CurrentPage     int    `json:"current_page"`
	TotalPages      *int   `json:"total_pages,omitempty"`
	TotalRecords    *int64 `json:"total_records,omitempty"`
	PageSize        int    `json:"page_size"`
	HasNextPage     bool   `json:"has_next_page"`
	HasPreviousPage bool   `json:"has_previous_page"`

	// Cursor-based state
	NextCursor     string `json:"next_cursor,omitempty"`
	PreviousCursor string `json:"previous_cursor,omitempty"`
	CurrentCursor  string `json:"current_cursor,omitempty"`

	// Offset-based state
	CurrentOffset int64 `json:"current_offset"`

	// Navigation URLs
	NextPageURL     string `json:"next_page_url,omitempty"`
	PreviousPageURL string `json:"previous_page_url,omitempty"`
	FirstPageURL    string `json:"first_page_url,omitempty"`
	LastPageURL     string `json:"last_page_url,omitempty"`

	// Metadata
	StartTime        time.Time `json:"start_time"`
	LastRequestTime  time.Time `json:"last_request_time"`
	TotalRequests    int       `json:"total_requests"`
	TotalRecordsRead int64     `json:"total_records_read"`

	// Performance metrics
	AverageResponseTime time.Duration   `json:"average_response_time"`
	ResponseTimes       []time.Duration `json:"response_times"`
}

// PageResponse represents a response from a paginated API call
type PageResponse struct {
	// Data
	Records     []map[string]interface{} `json:"records"`
	RecordCount int                      `json:"record_count"`

	// Pagination info
	PaginationInfo PaginationInfo `json:"pagination_info"`

	// Metadata
	RequestTime  time.Duration `json:"request_time"`
	ResponseSize int64         `json:"response_size"`
	HTTPStatus   int           `json:"http_status"`

	// Raw response for debugging
	RawResponse map[string]interface{} `json:"raw_response,omitempty"`
}

// PaginationInfo contains pagination metadata from the API response
type PaginationInfo struct {
	CurrentPage     int    `json:"current_page"`
	TotalPages      *int   `json:"total_pages,omitempty"`
	TotalRecords    *int64 `json:"total_records,omitempty"`
	PageSize        int    `json:"page_size"`
	HasNextPage     bool   `json:"has_next_page"`
	HasPreviousPage bool   `json:"has_previous_page"`

	NextPageURL     string `json:"next_page_url,omitempty"`
	PreviousPageURL string `json:"previous_page_url,omitempty"`
	FirstPageURL    string `json:"first_page_url,omitempty"`
	LastPageURL     string `json:"last_page_url,omitempty"`

	NextCursor     string `json:"next_cursor,omitempty"`
	PreviousCursor string `json:"previous_cursor,omitempty"`
	CurrentCursor  string `json:"current_cursor,omitempty"`
}

// NewWMSPaginator creates a new WMS paginator
func NewWMSPaginator(authenticator *auth.WMSAuthenticator, config PaginationConfig) *WMSPaginator {
	// Set defaults
	if config.Mode == "" {
		config.Mode = "cursor"
	}
	if config.PageSize == 0 {
		config.PageSize = 1000
	}
	if config.CursorDirection == "" {
		config.CursorDirection = "asc"
	}
	if config.RequestTimeout == 0 {
		config.RequestTimeout = 30 * time.Second
	}
	if config.CustomParams == nil {
		config.CustomParams = make(map[string]string)
	}

	return &WMSPaginator{
		authenticator: authenticator,
		config:        config,
		state: PaginationState{
			CurrentPage:   1,
			PageSize:      config.PageSize,
			StartTime:     time.Now(),
			ResponseTimes: make([]time.Duration, 0),
		},
	}
}

// GetFirstPage retrieves the first page of data
func (p *WMSPaginator) GetFirstPage(ctx context.Context, baseURL string, filters map[string]interface{}) (*PageResponse, error) {
	// Reset state for new pagination
	p.state = PaginationState{
		CurrentPage:   1,
		PageSize:      p.config.PageSize,
		StartTime:     time.Now(),
		ResponseTimes: make([]time.Duration, 0),
	}

	return p.getCurrentPage(ctx, baseURL, filters)
}

// GetNextPage retrieves the next page of data
func (p *WMSPaginator) GetNextPage(ctx context.Context) (*PageResponse, error) {
	if !p.state.HasNextPage {
		return nil, fmt.Errorf("no next page available")
	}

	// Check max pages limit
	if p.config.MaxPages != nil && p.state.CurrentPage >= *p.config.MaxPages {
		return nil, fmt.Errorf("maximum pages limit reached: %d", *p.config.MaxPages)
	}

	switch p.config.Mode {
	case "cursor":
		return p.getNextPageCursor(ctx)
	case "offset":
		return p.getNextPageOffset(ctx)
	default:
		return nil, fmt.Errorf("unsupported pagination mode: %s", p.config.Mode)
	}
}

// GetPreviousPage retrieves the previous page of data
func (p *WMSPaginator) GetPreviousPage(ctx context.Context) (*PageResponse, error) {
	if !p.state.HasPreviousPage {
		return nil, fmt.Errorf("no previous page available")
	}

	switch p.config.Mode {
	case "cursor":
		return p.getPreviousPageCursor(ctx)
	case "offset":
		return p.getPreviousPageOffset(ctx)
	default:
		return nil, fmt.Errorf("unsupported pagination mode: %s", p.config.Mode)
	}
}

// GetState returns the current pagination state
func (p *WMSPaginator) GetState() PaginationState {
	return p.state
}

// HasNextPage checks if there is a next page available
func (p *WMSPaginator) HasNextPage() bool {
	return p.state.HasNextPage
}

// HasPreviousPage checks if there is a previous page available
func (p *WMSPaginator) HasPreviousPage() bool {
	return p.state.HasPreviousPage
}

// GetEstimatedTotalPages returns an estimate of total pages
func (p *WMSPaginator) GetEstimatedTotalPages() *int {
	return p.state.TotalPages
}

// Private methods

func (p *WMSPaginator) getCurrentPage(ctx context.Context, baseURL string, filters map[string]interface{}) (*PageResponse, error) {
	// Build URL with parameters
	requestURL, err := p.buildRequestURL(baseURL, filters)
	if err != nil {
		return nil, fmt.Errorf("failed to build request URL: %w", err)
	}

	// Make the request
	startTime := time.Now()
	resp, err := p.authenticator.MakeAuthenticatedRequest(ctx, "GET", requestURL, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	requestTime := time.Since(startTime)
	p.updateResponseMetrics(requestTime)

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(body))
	}

	// Read and parse response
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	var rawResponse map[string]interface{}
	if err := json.Unmarshal(body, &rawResponse); err != nil {
		return nil, fmt.Errorf("failed to parse response JSON: %w", err)
	}

	// Parse response into PageResponse
	pageResponse, err := p.parseResponse(rawResponse, requestTime, int64(len(body)), resp.StatusCode)
	if err != nil {
		return nil, fmt.Errorf("failed to parse page response: %w", err)
	}

	// Update pagination state
	p.updatePaginationState(pageResponse.PaginationInfo)

	return pageResponse, nil
}

func (p *WMSPaginator) getNextPageCursor(ctx context.Context) (*PageResponse, error) {
	if p.state.NextPageURL == "" {
		return nil, fmt.Errorf("no next page URL available")
	}

	return p.requestPage(ctx, p.state.NextPageURL)
}

func (p *WMSPaginator) getNextPageOffset(ctx context.Context) (*PageResponse, error) {
	// Calculate next offset
	nextOffset := p.state.CurrentOffset + int64(p.state.PageSize)

	// Build URL with new offset
	baseURL := p.extractBaseURL(p.state.NextPageURL)
	if baseURL == "" {
		return nil, fmt.Errorf("cannot determine base URL for next page")
	}

	// Add offset parameter
	u, err := url.Parse(baseURL)
	if err != nil {
		return nil, fmt.Errorf("invalid base URL: %w", err)
	}

	q := u.Query()
	q.Set("offset", strconv.FormatInt(nextOffset, 10))
	q.Set("limit", strconv.Itoa(p.state.PageSize))
	u.RawQuery = q.Encode()

	return p.requestPage(ctx, u.String())
}

func (p *WMSPaginator) getPreviousPageCursor(ctx context.Context) (*PageResponse, error) {
	if p.state.PreviousPageURL == "" {
		return nil, fmt.Errorf("no previous page URL available")
	}

	return p.requestPage(ctx, p.state.PreviousPageURL)
}

func (p *WMSPaginator) getPreviousPageOffset(ctx context.Context) (*PageResponse, error) {
	// Calculate previous offset
	prevOffset := p.state.CurrentOffset - int64(p.state.PageSize)
	if prevOffset < 0 {
		prevOffset = 0
	}

	// Build URL with new offset
	baseURL := p.extractBaseURL(p.state.PreviousPageURL)
	if baseURL == "" {
		return nil, fmt.Errorf("cannot determine base URL for previous page")
	}

	// Add offset parameter
	u, err := url.Parse(baseURL)
	if err != nil {
		return nil, fmt.Errorf("invalid base URL: %w", err)
	}

	q := u.Query()
	q.Set("offset", strconv.FormatInt(prevOffset, 10))
	q.Set("limit", strconv.Itoa(p.state.PageSize))
	u.RawQuery = q.Encode()

	return p.requestPage(ctx, u.String())
}

func (p *WMSPaginator) requestPage(ctx context.Context, pageURL string) (*PageResponse, error) {
	startTime := time.Now()
	resp, err := p.authenticator.MakeAuthenticatedRequest(ctx, "GET", pageURL, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()

	requestTime := time.Since(startTime)
	p.updateResponseMetrics(requestTime)

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(body))
	}

	// Read and parse response
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	var rawResponse map[string]interface{}
	if err := json.Unmarshal(body, &rawResponse); err != nil {
		return nil, fmt.Errorf("failed to parse response JSON: %w", err)
	}

	// Parse response into PageResponse
	pageResponse, err := p.parseResponse(rawResponse, requestTime, int64(len(body)), resp.StatusCode)
	if err != nil {
		return nil, fmt.Errorf("failed to parse page response: %w", err)
	}

	// Update pagination state
	p.updatePaginationState(pageResponse.PaginationInfo)

	return pageResponse, nil
}

func (p *WMSPaginator) buildRequestURL(baseURL string, filters map[string]interface{}) (string, error) {
	u, err := url.Parse(baseURL)
	if err != nil {
		return "", fmt.Errorf("invalid base URL: %w", err)
	}

	q := u.Query()

	// Add pagination parameters
	switch p.config.Mode {
	case "cursor":
		q.Set("page_mode", "sequenced") // Oracle WMS cursor mode
		q.Set("page_size", strconv.Itoa(p.config.PageSize))

		if p.state.CurrentCursor != "" {
			q.Set("cursor", p.state.CurrentCursor)
		}

	case "offset":
		q.Set("page_mode", "paged") // Oracle WMS offset mode
		q.Set("page_size", strconv.Itoa(p.config.PageSize))
		q.Set("page", strconv.Itoa(p.state.CurrentPage))

		if p.state.CurrentOffset > 0 {
			q.Set("offset", strconv.FormatInt(p.state.CurrentOffset, 10))
		}
	}

	// Add ordering
	if len(p.config.OrderBy) > 0 {
		var orderFields []string
		for _, order := range p.config.OrderBy {
			if order.Direction == "desc" {
				orderFields = append(orderFields, "-"+order.Field)
			} else {
				orderFields = append(orderFields, order.Field)
			}
		}
		q.Set("ordering", strings.Join(orderFields, ","))
	}

	// Add filters
	for key, value := range filters {
		if value != nil {
			q.Set(key, fmt.Sprintf("%v", value))
		}
	}

	// Add custom parameters
	for key, value := range p.config.CustomParams {
		q.Set(key, value)
	}

	u.RawQuery = q.Encode()
	return u.String(), nil
}

func (p *WMSPaginator) parseResponse(rawResponse map[string]interface{}, requestTime time.Duration, responseSize int64, httpStatus int) (*PageResponse, error) {
	pageResponse := &PageResponse{
		Records:      make([]map[string]interface{}, 0),
		RequestTime:  requestTime,
		ResponseSize: responseSize,
		HTTPStatus:   httpStatus,
		RawResponse:  rawResponse,
	}

	// Extract records
	if results, ok := rawResponse["results"].([]interface{}); ok {
		for _, result := range results {
			if record, ok := result.(map[string]interface{}); ok {
				pageResponse.Records = append(pageResponse.Records, record)
			}
		}
	} else if data, ok := rawResponse["data"].([]interface{}); ok {
		for _, result := range data {
			if record, ok := result.(map[string]interface{}); ok {
				pageResponse.Records = append(pageResponse.Records, record)
			}
		}
	}

	pageResponse.RecordCount = len(pageResponse.Records)

	// Parse pagination info
	paginationInfo := PaginationInfo{}

	// Handle different response formats
	if pageInfo, ok := rawResponse["page_info"].(map[string]interface{}); ok {
		p.parsePaginationInfo(pageInfo, &paginationInfo)
	} else {
		// Try direct fields in response
		p.parsePaginationInfo(rawResponse, &paginationInfo)
	}

	// Set defaults
	if paginationInfo.PageSize == 0 {
		paginationInfo.PageSize = pageResponse.RecordCount
	}
	if paginationInfo.CurrentPage == 0 {
		paginationInfo.CurrentPage = p.state.CurrentPage
	}

	pageResponse.PaginationInfo = paginationInfo

	return pageResponse, nil
}

func (p *WMSPaginator) parsePaginationInfo(source map[string]interface{}, info *PaginationInfo) {
	// Current page
	if page, ok := source["page_number"].(float64); ok {
		info.CurrentPage = int(page)
	} else if page, ok := source["page"].(float64); ok {
		info.CurrentPage = int(page)
	}

	// Total pages
	if totalPages, ok := source["page_count"].(float64); ok {
		total := int(totalPages)
		info.TotalPages = &total
	} else if totalPages, ok := source["total_pages"].(float64); ok {
		total := int(totalPages)
		info.TotalPages = &total
	}

	// Total records
	if totalRecords, ok := source["result_count"].(float64); ok {
		total := int64(totalRecords)
		info.TotalRecords = &total
	} else if totalRecords, ok := source["total_records"].(float64); ok {
		total := int64(totalRecords)
		info.TotalRecords = &total
	}

	// Page size
	if pageSize, ok := source["page_size"].(float64); ok {
		info.PageSize = int(pageSize)
	}

	// Navigation URLs
	if nextPage, ok := source["next_page"].(string); ok {
		info.NextPageURL = nextPage
		info.HasNextPage = nextPage != ""
	}

	if prevPage, ok := source["previous_page"].(string); ok {
		info.PreviousPageURL = prevPage
		info.HasPreviousPage = prevPage != ""
	}

	if firstPage, ok := source["first_page"].(string); ok {
		info.FirstPageURL = firstPage
	}

	if lastPage, ok := source["last_page"].(string); ok {
		info.LastPageURL = lastPage
	}

	// Cursor values
	if nextCursor, ok := source["next_cursor"].(string); ok {
		info.NextCursor = nextCursor
	}

	if prevCursor, ok := source["previous_cursor"].(string); ok {
		info.PreviousCursor = prevCursor
	}

	if currentCursor, ok := source["current_cursor"].(string); ok {
		info.CurrentCursor = currentCursor
	}
}

func (p *WMSPaginator) updatePaginationState(info PaginationInfo) {
	p.state.CurrentPage = info.CurrentPage
	p.state.TotalPages = info.TotalPages
	p.state.TotalRecords = info.TotalRecords
	p.state.HasNextPage = info.HasNextPage
	p.state.HasPreviousPage = info.HasPreviousPage

	p.state.NextPageURL = info.NextPageURL
	p.state.PreviousPageURL = info.PreviousPageURL
	p.state.FirstPageURL = info.FirstPageURL
	p.state.LastPageURL = info.LastPageURL

	p.state.NextCursor = info.NextCursor
	p.state.PreviousCursor = info.PreviousCursor
	p.state.CurrentCursor = info.CurrentCursor

	p.state.LastRequestTime = time.Now()
	p.state.TotalRequests++
}

func (p *WMSPaginator) updateResponseMetrics(responseTime time.Duration) {
	p.state.ResponseTimes = append(p.state.ResponseTimes, responseTime)

	// Calculate average response time
	var total time.Duration
	for _, rt := range p.state.ResponseTimes {
		total += rt
	}
	p.state.AverageResponseTime = total / time.Duration(len(p.state.ResponseTimes))

	// Keep only last 100 response times to avoid memory growth
	if len(p.state.ResponseTimes) > 100 {
		p.state.ResponseTimes = p.state.ResponseTimes[len(p.state.ResponseTimes)-100:]
	}
}

func (p *WMSPaginator) extractBaseURL(fullURL string) string {
	u, err := url.Parse(fullURL)
	if err != nil {
		return ""
	}

	// Remove query parameters to get base URL
	u.RawQuery = ""
	u.Fragment = ""

	return u.String()
}
