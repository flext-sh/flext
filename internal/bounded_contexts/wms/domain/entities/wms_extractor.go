package entities

import (
	"context"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/wms/domain/value_objects"
	"github.com/flext-sh/flext/internal/bounded_contexts/wms/infrastructure/pagination"
	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/google/uuid"
)

// WMSExtractor implements advanced data extraction from Oracle WMS with dynamic entity support
type WMSExtractor struct {
	domain.AggregateRoot

	// Extractor configuration
	Client         *WMSClient               `json:"client"`
	EntityName     string                   `json:"entity_name" validate:"required"`
	ExtractionType ExtractionType           `json:"extraction_type"`
	Configuration  *ExtractionConfiguration `json:"configuration"`

	// State management
	State        *ExtractionState       `json:"state"`
	LastBookmark map[string]interface{} `json:"last_bookmark"`

	// Filtering and pagination
	AppliedFilters   map[string]interface{}   `json:"applied_filters"`
	PaginationConfig *PaginationConfiguration `json:"pagination_config"`

	// Performance tracking
	Metrics   ExtractionMetrics `json:"metrics"`
	StartTime *time.Time        `json:"start_time,omitempty"`
	EndTime   *time.Time        `json:"end_time,omitempty"`

	// Error handling
	ErrorPolicy ErrorHandlingPolicy `json:"error_policy"`
	RetryConfig RetryConfiguration  `json:"retry_config"`

	// Concurrency control
	MaxConcurrency int `json:"max_concurrency"`
	BatchSize      int `json:"batch_size"`

	// Internal state (not serialized)
	httpClient          *http.Client        `json:"-"`
	cancelFunc          context.CancelFunc  `json:"-"`
	mutex               sync.RWMutex        `json:"-"`
	extractionCtx       context.Context     `json:"-"`
	errorHandler        ErrorHandler        `json:"-"`
	queryBuilderFactory QueryBuilderFactory `json:"-"`
}

// ExtractionType defines the type of extraction
type ExtractionType string

const (
	ExtractionTypeIncremental ExtractionType = "incremental"
	ExtractionTypeFull        ExtractionType = "full"
	ExtractionTypeSample      ExtractionType = "sample"
	ExtractionTypeResume      ExtractionType = "resume"
)

// ExtractionConfiguration holds configuration for data extraction
type ExtractionConfiguration struct {
	// Replication settings
	ReplicationKey       string `json:"replication_key"`
	SafetyOverlapMinutes int    `json:"safety_overlap_minutes"`

	// Filtering settings
	GlobalFilters   map[string]interface{} `json:"global_filters"`
	EntityFilters   map[string]interface{} `json:"entity_filters"`
	AdvancedFilters map[string]interface{} `json:"advanced_filters"`

	// Incremental settings
	StartDate             *time.Time `json:"start_date,omitempty"`
	EndDate               *time.Time `json:"end_date,omitempty"`
	IncrementalOverlapMin int        `json:"incremental_overlap_minutes"`

	// Full sync settings
	FullSyncStrategy string                 `json:"full_sync_strategy"` // "id_based_resume", "timestamp_based"
	ResumeContext    map[string]interface{} `json:"resume_context"`

	// Field selection
	SelectedFields []string `json:"selected_fields"`
	ExcludedFields []string `json:"excluded_fields"`

	// Data transformation
	FieldMappings       map[string]string    `json:"field_mappings"`
	DataTransformations []DataTransformation `json:"data_transformations"`

	// Quality controls
	ValidationRules   []ValidationRule `json:"validation_rules"`
	DataQualityChecks bool             `json:"data_quality_checks"`

	// Performance settings
	PreferredPageSize int           `json:"preferred_page_size"`
	MaxPageSize       int           `json:"max_page_size"`
	RequestTimeout    time.Duration `json:"request_timeout"`

	// Output settings
	OutputFormat       string `json:"output_format"` // "jsonl", "json", "csv"
	CompressionEnabled bool   `json:"compression_enabled"`
	BufferSize         int    `json:"buffer_size"`
}

// ExtractionState tracks the current state of extraction
type ExtractionState struct {
	Status              ExtractionStatus       `json:"status"`
	Progress            ExtractionProgress     `json:"progress"`
	CurrentBookmark     map[string]interface{} `json:"current_bookmark"`
	LastProcessedRecord map[string]interface{} `json:"last_processed_record"`
	ErrorCount          int                    `json:"error_count"`
	LastError           *ExtractionError       `json:"last_error,omitempty"`
	StateCheckpoints    []StateCheckpoint      `json:"state_checkpoints"`
	ResumeToken         string                 `json:"resume_token,omitempty"`
}

// ExtractionStatus defines the possible extraction states
type ExtractionStatus string

const (
	ExtractionStatusPending   ExtractionStatus = "pending"
	ExtractionStatusRunning   ExtractionStatus = "running"
	ExtractionStatusPaused    ExtractionStatus = "paused"
	ExtractionStatusCompleted ExtractionStatus = "completed"
	ExtractionStatusFailed    ExtractionStatus = "failed"
	ExtractionStatusCancelled ExtractionStatus = "cancelled"
)

// ExtractionProgress tracks extraction progress
type ExtractionProgress struct {
	RecordsExtracted       int64          `json:"records_extracted"`
	BytesExtracted         int64          `json:"bytes_extracted"`
	PagesProcessed         int            `json:"pages_processed"`
	EstimatedTotal         *int64         `json:"estimated_total,omitempty"`
	ProgressPercent        float64        `json:"progress_percent"`
	ElapsedTime            time.Duration  `json:"elapsed_time"`
	EstimatedTimeRemaining *time.Duration `json:"estimated_time_remaining,omitempty"`

	// Rate metrics
	CurrentRecordsPerSecond float64 `json:"current_records_per_second"`
	AverageRecordsPerSecond float64 `json:"average_records_per_second"`
	CurrentBytesPerSecond   float64 `json:"current_bytes_per_second"`

	// Detailed progress by stream
	StreamProgress map[string]int64 `json:"stream_progress"`

	// Checkpoint information
	LastCheckpoint     *time.Time    `json:"last_checkpoint,omitempty"`
	CheckpointInterval time.Duration `json:"checkpoint_interval"`
}

// PaginationConfiguration controls pagination behavior
type PaginationConfiguration struct {
	Mode     string `json:"mode"` // "cursor", "offset"
	PageSize int    `json:"page_size"`
	MaxPages *int   `json:"max_pages,omitempty"`

	// Cursor-based pagination
	CursorField     string `json:"cursor_field,omitempty"`
	CursorDirection string `json:"cursor_direction"` // "asc", "desc"

	// Offset-based pagination
	OffsetField string `json:"offset_field,omitempty"`

	// Performance optimizations
	PreloadNextPage bool `json:"preload_next_page"`
	ConcurrentPages int  `json:"concurrent_pages"`

	// Ordering
	OrderBy []OrderByClause `json:"order_by"`
}

// OrderByClause defines ordering for pagination
type OrderByClause struct {
	Field     string `json:"field"`
	Direction string `json:"direction"` // "asc", "desc"
}

// ExtractionMetrics contains comprehensive extraction metrics
type ExtractionMetrics struct {
	// Performance metrics
	TotalRecordsExtracted int64 `json:"total_records_extracted"`
	TotalBytesExtracted   int64 `json:"total_bytes_extracted"`
	TotalPagesProcessed   int   `json:"total_pages_processed"`
	TotalRequestsMade     int   `json:"total_requests_made"`

	// Timing metrics
	TotalDuration             time.Duration `json:"total_duration"`
	AveragePageProcessingTime time.Duration `json:"average_page_processing_time"`
	AverageRequestTime        time.Duration `json:"average_request_time"`

	// Throughput metrics
	OverallRecordsPerSecond float64 `json:"overall_records_per_second"`
	PeakRecordsPerSecond    float64 `json:"peak_records_per_second"`
	OverallBytesPerSecond   float64 `json:"overall_bytes_per_second"`

	// Error and retry metrics
	TotalErrors  int            `json:"total_errors"`
	TotalRetries int            `json:"total_retries"`
	ErrorsByType map[string]int `json:"errors_by_type"`

	// Quality metrics
	RecordsValidated   int64 `json:"records_validated"`
	ValidationFailures int64 `json:"validation_failures"`
	DuplicateRecords   int64 `json:"duplicate_records"`

	// Resource usage
	PeakMemoryUsageMB       float64 `json:"peak_memory_usage_mb"`
	AverageMemoryUsageMB    float64 `json:"average_memory_usage_mb"`
	NetworkBytesTransferred int64   `json:"network_bytes_transferred"`

	// State management
	CheckpointsSaved int `json:"checkpoints_saved"`
	StateRestores    int `json:"state_restores"`

	// Custom metrics
	CustomMetrics map[string]interface{} `json:"custom_metrics"`
}

// ErrorHandlingPolicy defines how to handle errors during extraction
type ErrorHandlingPolicy struct {
	MaxErrors           int    `json:"max_errors"`
	FailOnFirstError    bool   `json:"fail_on_first_error"`
	SkipErrorRecords    bool   `json:"skip_error_records"`
	LogErrors           bool   `json:"log_errors"`
	ErrorReportingLevel string `json:"error_reporting_level"` // "none", "summary", "detailed", "full"

	// Circuit breaker settings
	UseCircuitBreaker    bool                 `json:"use_circuit_breaker"`
	CircuitBreakerConfig CircuitBreakerConfig `json:"circuit_breaker_config"`
}

// CircuitBreakerConfig configures circuit breaker behavior
type CircuitBreakerConfig struct {
	FailureThreshold int           `json:"failure_threshold"`
	SuccessThreshold int           `json:"success_threshold"`
	Timeout          time.Duration `json:"timeout"`
	MaxRetries       int           `json:"max_retries"`
}

// RetryConfiguration defines retry behavior
type RetryConfiguration struct {
	MaxRetries          int           `json:"max_retries"`
	InitialDelay        time.Duration `json:"initial_delay"`
	MaxDelay            time.Duration `json:"max_delay"`
	BackoffMultiplier   float64       `json:"backoff_multiplier"`
	RandomizationFactor float64       `json:"randomization_factor"`

	// Retry conditions
	RetryableHTTPCodes []int    `json:"retryable_http_codes"`
	RetryableErrors    []string `json:"retryable_errors"`

	// Jitter and rate limiting
	EnableJitter       bool    `json:"enable_jitter"`
	RateLimitPerSecond float64 `json:"rate_limit_per_second"`
}

// DataTransformation defines data transformation rules
type DataTransformation struct {
	Type        string                 `json:"type"` // "map", "filter", "convert", "calculate"
	SourceField string                 `json:"source_field"`
	TargetField string                 `json:"target_field"`
	Rule        string                 `json:"rule"`
	Parameters  map[string]interface{} `json:"parameters"`
}

// ValidationRule defines data validation rules
type ValidationRule struct {
	Field      string                 `json:"field"`
	Type       string                 `json:"type"` // "required", "format", "range", "custom"
	Rule       string                 `json:"rule"`
	Parameters map[string]interface{} `json:"parameters"`
	ErrorLevel string                 `json:"error_level"` // "warning", "error", "critical"
}

// Note: ExtractionError is defined in error_handler_interface.go to avoid duplication

// StateCheckpoint represents a point-in-time state snapshot
type StateCheckpoint struct {
	ID               uuid.UUID              `json:"id"`
	Timestamp        time.Time              `json:"timestamp"`
	Bookmark         map[string]interface{} `json:"bookmark"`
	RecordsExtracted int64                  `json:"records_extracted"`
	BytesExtracted   int64                  `json:"bytes_extracted"`
	Metadata         map[string]interface{} `json:"metadata"`
}

// ExtractedRecord represents a single extracted record
type ExtractedRecord struct {
	// Singer protocol fields
	Type          string                 `json:"type"` // "RECORD", "SCHEMA", "STATE"
	Stream        string                 `json:"stream,omitempty"`
	Record        map[string]interface{} `json:"record,omitempty"`
	TimeExtracted time.Time              `json:"time_extracted"`

	// Additional metadata
	SourceEntity string `json:"source_entity"`
	RecordID     string `json:"record_id,omitempty"`
	Version      string `json:"version,omitempty"`

	// Quality and validation
	ValidationStatus string   `json:"validation_status"` // "valid", "warning", "error"
	ValidationErrors []string `json:"validation_errors,omitempty"`

	// Extraction context
	PageNumber     int           `json:"page_number"`
	RecordIndex    int           `json:"record_index"`
	ExtractedAt    time.Time     `json:"extracted_at"`
	ProcessingTime time.Duration `json:"processing_time"`

	// Transformation metadata
	Transformations []string               `json:"transformations,omitempty"`
	OriginalRecord  map[string]interface{} `json:"original_record,omitempty"`
}

// NewWMSExtractor creates a new WMS extractor for a specific entity
func NewWMSExtractor(client *WMSClient, entityName string, extractionType ExtractionType, queryBuilderFactory QueryBuilderFactory, errorHandlerFactory ErrorHandlerFactory) (*WMSExtractor, error) {
	if client == nil {
		return nil, fmt.Errorf("client cannot be nil")
	}
	if entityName == "" {
		return nil, fmt.Errorf("entity name cannot be empty")
	}

	extractor := &WMSExtractor{
		AggregateRoot:  domain.NewAggregateRoot(),
		Client:         client,
		EntityName:     entityName,
		ExtractionType: extractionType,
		AppliedFilters: make(map[string]interface{}),
		LastBookmark:   make(map[string]interface{}),
		MaxConcurrency: 1,
		BatchSize:      1000,

		// Default configuration
		Configuration: &ExtractionConfiguration{
			ReplicationKey:        "mod_ts",
			SafetyOverlapMinutes:  5,
			GlobalFilters:         make(map[string]interface{}),
			EntityFilters:         make(map[string]interface{}),
			AdvancedFilters:       make(map[string]interface{}),
			IncrementalOverlapMin: 5,
			FullSyncStrategy:      "id_based_resume",
			ResumeContext:         make(map[string]interface{}),
			SelectedFields:        []string{},
			ExcludedFields:        []string{},
			FieldMappings:         make(map[string]string),
			DataTransformations:   []DataTransformation{},
			ValidationRules:       []ValidationRule{},
			DataQualityChecks:     true,
			PreferredPageSize:     1000,
			MaxPageSize:           5000,
			RequestTimeout:        30 * time.Second,
			OutputFormat:          "jsonl",
			CompressionEnabled:    false,
			BufferSize:            10000,
		},

		// Default state
		State: &ExtractionState{
			Status: ExtractionStatusPending,
			Progress: ExtractionProgress{
				StreamProgress:     make(map[string]int64),
				CheckpointInterval: 5 * time.Minute,
			},
			CurrentBookmark:     make(map[string]interface{}),
			LastProcessedRecord: make(map[string]interface{}),
			StateCheckpoints:    []StateCheckpoint{},
		},

		// Default pagination
		PaginationConfig: &PaginationConfiguration{
			Mode:            "cursor",
			PageSize:        1000,
			CursorDirection: "asc",
			PreloadNextPage: false,
			ConcurrentPages: 1,
			OrderBy:         []OrderByClause{},
		},

		// Default error handling
		ErrorPolicy: ErrorHandlingPolicy{
			MaxErrors:           100,
			FailOnFirstError:    false,
			SkipErrorRecords:    true,
			LogErrors:           true,
			ErrorReportingLevel: "summary",
			UseCircuitBreaker:   true,
			CircuitBreakerConfig: CircuitBreakerConfig{
				FailureThreshold: 5,
				SuccessThreshold: 2,
				Timeout:          60 * time.Second,
				MaxRetries:       3,
			},
		},

		// Default retry configuration
		RetryConfig: RetryConfiguration{
			MaxRetries:          3,
			InitialDelay:        1 * time.Second,
			MaxDelay:            30 * time.Second,
			BackoffMultiplier:   2.0,
			RandomizationFactor: 0.1,
			RetryableHTTPCodes:  []int{429, 500, 502, 503, 504},
			RetryableErrors:     []string{"timeout", "connection_error", "temporary_failure"},
			EnableJitter:        true,
			RateLimitPerSecond:  10.0,
		},

		// Initialize metrics
		Metrics: ExtractionMetrics{
			ErrorsByType:  make(map[string]int),
			CustomMetrics: make(map[string]interface{}),
		},

		// HTTP client with appropriate timeouts
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
			Transport: &http.Transport{
				MaxIdleConns:        100,
				MaxIdleConnsPerHost: 10,
				IdleConnTimeout:     90 * time.Second,
			},
		},

		// Initialize error handler and query builder from factories
		errorHandler:        errorHandlerFactory.CreateErrorHandler(),
		queryBuilderFactory: queryBuilderFactory,
	}

	// Emit creation event
	extractor.AddEvent(NewWMSExtractorCreated(
		extractor.GetID(),
		client.GetID(),
		entityName,
		string(extractionType),
	))

	return extractor, nil
}

// StartExtraction begins the data extraction process
func (e *WMSExtractor) StartExtraction(ctx context.Context) error {
	e.mutex.Lock()
	defer e.mutex.Unlock()

	if e.State.Status == ExtractionStatusRunning {
		return fmt.Errorf("extraction is already running")
	}

	// Check if client is connected
	if !e.Client.IsConnected() {
		return fmt.Errorf("client is not connected to WMS API")
	}

	// Validate entity exists
	entity, err := e.Client.GetEntity(e.EntityName)
	if err != nil {
		return fmt.Errorf("entity %s not found: %w", e.EntityName, err)
	}

	// Set up extraction context
	e.extractionCtx, e.cancelFunc = context.WithCancel(ctx)

	// Update state
	startTime := time.Now()
	e.StartTime = &startTime
	e.State.Status = ExtractionStatusRunning
	e.State.Progress.ElapsedTime = 0
	e.MarkAsUpdated()

	// Apply filters based on extraction type
	if err := e.applyFilters(entity); err != nil {
		return fmt.Errorf("failed to apply filters: %w", err)
	}

	// Configure pagination
	if err := e.configurePagination(entity); err != nil {
		return fmt.Errorf("failed to configure pagination: %w", err)
	}

	// Emit extraction started event
	e.AddEvent(&WMSDataExtractionStarted{
		BaseDomainEvent: domain.NewBaseDomainEvent("wms.data.extraction.started", e.GetID()),
		ClientID:        e.Client.GetID(),
		EntityName:      e.EntityName,
		ExtractionType:  string(e.ExtractionType),
		Filters:         e.AppliedFilters,
		PageSize:        e.PaginationConfig.PageSize,
	})

	// Start extraction in background
	go e.runExtraction()

	return nil
}

// StopExtraction stops the current extraction
func (e *WMSExtractor) StopExtraction() error {
	e.mutex.Lock()
	defer e.mutex.Unlock()

	if e.State.Status != ExtractionStatusRunning {
		return fmt.Errorf("extraction is not running")
	}

	// Cancel the extraction context
	if e.cancelFunc != nil {
		e.cancelFunc()
	}

	// Update state
	e.State.Status = ExtractionStatusCancelled
	endTime := time.Now()
	e.EndTime = &endTime
	e.MarkAsUpdated()

	// Emit extraction stopped event
	e.AddEvent(&WMSDataExtractionStopped{
		BaseDomainEvent:  domain.NewBaseDomainEvent("wms.data.extraction.stopped", e.GetID()),
		ExtractorID:      e.GetID(),
		ClientID:         e.Client.GetID(),
		EntityName:       e.EntityName,
		StoppedAt:        endTime,
		RecordsExtracted: e.State.Progress.RecordsExtracted,
	})

	return nil
}

// PauseExtraction pauses the current extraction
func (e *WMSExtractor) PauseExtraction() error {
	e.mutex.Lock()
	defer e.mutex.Unlock()

	if e.State.Status != ExtractionStatusRunning {
		return fmt.Errorf("extraction is not running")
	}

	e.State.Status = ExtractionStatusPaused
	e.MarkAsUpdated()

	// Save checkpoint
	if err := e.saveCheckpoint(); err != nil {
		return fmt.Errorf("failed to save checkpoint: %w", err)
	}

	// Emit extraction paused event
	e.AddEvent(&WMSDataExtractionPaused{
		BaseDomainEvent:  domain.NewBaseDomainEvent("wms.data.extraction.paused", e.GetID()),
		ExtractorID:      e.GetID(),
		ClientID:         e.Client.GetID(),
		EntityName:       e.EntityName,
		PausedAt:         time.Now(),
		RecordsExtracted: e.State.Progress.RecordsExtracted,
	})

	return nil
}

// ResumeExtraction resumes a paused extraction
func (e *WMSExtractor) ResumeExtraction(ctx context.Context) error {
	e.mutex.Lock()
	defer e.mutex.Unlock()

	if e.State.Status != ExtractionStatusPaused {
		return fmt.Errorf("extraction is not paused")
	}

	// Set up extraction context
	e.extractionCtx, e.cancelFunc = context.WithCancel(ctx)

	// Update state
	e.State.Status = ExtractionStatusRunning
	e.MarkAsUpdated()

	// Emit extraction resumed event
	e.AddEvent(&WMSDataExtractionResumed{
		BaseDomainEvent:  domain.NewBaseDomainEvent("wms.data.extraction.resumed", e.GetID()),
		ExtractorID:      e.GetID(),
		ClientID:         e.Client.GetID(),
		EntityName:       e.EntityName,
		ResumedAt:        time.Now(),
		RecordsExtracted: e.State.Progress.RecordsExtracted,
	})

	// Continue extraction in background
	go e.runExtraction()

	return nil
}

// GetExtractionStatus returns the current extraction status
func (e *WMSExtractor) GetExtractionStatus() ExtractionStatus {
	e.mutex.RLock()
	defer e.mutex.RUnlock()

	return e.State.Status
}

// GetExtractionProgress returns the current extraction progress
func (e *WMSExtractor) GetExtractionProgress() ExtractionProgress {
	e.mutex.RLock()
	defer e.mutex.RUnlock()

	// Update elapsed time if running
	if e.State.Status == ExtractionStatusRunning && e.StartTime != nil {
		e.State.Progress.ElapsedTime = time.Since(*e.StartTime)
	}

	return e.State.Progress
}

// GetExtractionMetrics returns comprehensive extraction metrics
func (e *WMSExtractor) GetExtractionMetrics() ExtractionMetrics {
	e.mutex.RLock()
	defer e.mutex.RUnlock()

	return e.Metrics
}

// Private helper methods

func (e *WMSExtractor) applyFilters(entity *WMSEntity) error {
	// Implementation of filter application based on extraction type
	switch e.ExtractionType {
	case ExtractionTypeIncremental:
		return e.applyIncrementalFilters(entity)
	case ExtractionTypeFull:
		return e.applyFullSyncFilters(entity)
	case ExtractionTypeSample:
		return e.applySampleFilters(entity)
	case ExtractionTypeResume:
		return e.applyResumeFilters(entity)
	default:
		return fmt.Errorf("unsupported extraction type: %s", e.ExtractionType)
	}
}

func (e *WMSExtractor) applyIncrementalFilters(entity *WMSEntity) error {
	// Use query builder for incremental filtering
	replicationKey := e.Configuration.ReplicationKey
	if replicationKey == "" {
		replicationKey = entity.ReplicationKey
	}

	// Create query builder for incremental extraction
	var bookmark interface{}
	if bookmarkValue, exists := e.LastBookmark[replicationKey]; exists {
		bookmark = bookmarkValue
	}

	// Use incremental query builder
	queryBuilder := e.queryBuilderFactory.CreateQueryBuilder(entity)

	// Apply incremental filtering
	if bookmark != nil {
		queryBuilder.WhereIncremental(replicationKey, bookmark, 5*time.Minute) // 5 minute safety overlap
	}

	// Order by replication key for consistent ordering
	queryBuilder.OrderByAsc(replicationKey)

	// Apply start date if no bookmark and start date is configured
	if bookmark == nil && e.Configuration.StartDate != nil {
		queryBuilder.WhereDate(replicationKey, value_objects.OpGreaterThanOrEqual, *e.Configuration.StartDate)
	}

	// Apply end date if configured
	if e.Configuration.EndDate != nil {
		queryBuilder.WhereDate(replicationKey, value_objects.OpLessThanOrEqual, *e.Configuration.EndDate)
	}

	// Apply additional global filters
	for key, value := range e.Configuration.GlobalFilters {
		queryBuilder.Where(key, value_objects.OpEquals, value)
	}

	// Apply entity-specific filters
	for key, value := range e.Configuration.EntityFilters {
		queryBuilder.Where(key, value_objects.OpEquals, value)
	}

	// Build filters and update applied filters
	e.AppliedFilters = queryBuilder.GetFilters()

	return nil
}

func (e *WMSExtractor) applyFullSyncFilters(entity *WMSEntity) error {
	// Use query builder for full sync filtering
	queryBuilder := e.queryBuilderFactory.CreateQueryBuilder(entity)

	// Apply resume context if provided
	if minID, exists := e.Configuration.ResumeContext["min_id_in_target"]; exists {
		queryBuilder.Where("id", value_objects.OpLessThan, minID)
		queryBuilder.OrderByDesc("id") // Descending order for resume strategy
	} else {
		queryBuilder.OrderByAsc("id") // Default ascending order
	}

	// Apply date range if timestamp-based strategy
	if e.Configuration.FullSyncStrategy == "timestamp_based" {
		if e.Configuration.StartDate != nil {
			queryBuilder.WhereDate("mod_ts", value_objects.OpGreaterThanOrEqual, *e.Configuration.StartDate)
		}
		if e.Configuration.EndDate != nil {
			queryBuilder.WhereDate("mod_ts", value_objects.OpLessThanOrEqual, *e.Configuration.EndDate)
		}
	}

	// Apply global and entity filters
	for key, value := range e.Configuration.GlobalFilters {
		queryBuilder.Where(key, value_objects.OpEquals, value)
	}

	for key, value := range e.Configuration.EntityFilters {
		queryBuilder.Where(key, value_objects.OpEquals, value)
	}

	// Build filters and update applied filters
	e.AppliedFilters = queryBuilder.GetFilters()

	// Update ordering based on query builder
	ordering := queryBuilder.GetOrdering()
	e.PaginationConfig.OrderBy = make([]OrderByClause, len(ordering))
	for i, orderInterface := range ordering {
		// Type assertion to extract fields - this assumes OrderClause structure
		if orderMap, ok := orderInterface.(map[string]interface{}); ok {
			field, _ := orderMap["field"].(string)
			direction, _ := orderMap["direction"].(string)
			e.PaginationConfig.OrderBy[i] = OrderByClause{
				Field:     field,
				Direction: direction,
			}
		}
	}

	return nil
}

func (e *WMSExtractor) applySampleFilters(entity *WMSEntity) error {
	// Apply sampling filters (e.g., LIMIT)
	if e.PaginationConfig.MaxPages == nil {
		maxPages := 1 // Only one page for sampling
		e.PaginationConfig.MaxPages = &maxPages
	}
	return nil
}

func (e *WMSExtractor) applyResumeFilters(entity *WMSEntity) error {
	// Apply filters for resuming interrupted extraction
	if e.State.ResumeToken != "" {
		e.AppliedFilters["cursor"] = e.State.ResumeToken
	}
	return nil
}

func (e *WMSExtractor) configurePagination(entity *WMSEntity) error {
	// Configure pagination based on entity capabilities
	if entity.PaginationMode != "" {
		e.PaginationConfig.Mode = entity.PaginationMode
	}

	if entity.OptimalPageSize > 0 {
		e.PaginationConfig.PageSize = entity.OptimalPageSize
	}

	// Ensure page size doesn't exceed entity maximum
	if entity.MaxPageSize > 0 && e.PaginationConfig.PageSize > entity.MaxPageSize {
		e.PaginationConfig.PageSize = entity.MaxPageSize
	}

	return nil
}

func (e *WMSExtractor) runExtraction() {
	defer func() {
		if r := recover(); r != nil {
			e.handleExtractionPanic(r)
		}
	}()

	success, lastError := e.executeExtractionLoop()
	e.finalizeExtraction(success, lastError)
}

// executeExtractionLoop handles the main extraction logic
func (e *WMSExtractor) executeExtractionLoop() (bool, error) {
	entity, paginator, err := e.initializeExtraction()
	if err != nil {
		e.handleExtractionError(err)
		return false, err
	}

	pageResponse, err := e.getFirstPage(paginator, entity)
	if err != nil {
		e.handleExtractionError(err)
		return false, err
	}

	return e.processExtractionPages(paginator, pageResponse)
}

// initializeExtraction sets up the extraction components
func (e *WMSExtractor) initializeExtraction() (*WMSEntity, *pagination.WMSPaginator, error) {
	entity, err := e.Client.GetEntity(e.EntityName)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to get entity: %w", err)
	}

	paginator := pagination.NewWMSPaginator(e.Client.authenticator, pagination.PaginationConfig{
		Mode:            e.PaginationConfig.Mode,
		PageSize:        e.PaginationConfig.PageSize,
		MaxPages:        e.PaginationConfig.MaxPages,
		CursorField:     e.PaginationConfig.CursorField,
		CursorDirection: e.PaginationConfig.CursorDirection,
		OrderBy:         convertOrderByClauses(e.PaginationConfig.OrderBy),
		RequestTimeout:  e.Configuration.RequestTimeout,
		CustomParams:    make(map[string]string),
	})

	return entity, paginator, nil
}

// getFirstPage retrieves the first page of data
func (e *WMSExtractor) getFirstPage(paginator *pagination.WMSPaginator, entity *WMSEntity) (*pagination.PageResponse, error) {
	var pageResponse *pagination.PageResponse
	err := func() error {
		var err error
		pageResponse, err = paginator.GetFirstPage(e.extractionCtx, entity.URL, e.AppliedFilters)
		return err
	}()
	if err != nil {
		return nil, fmt.Errorf("failed to get first page after retries: %w", err)
	}
	return pageResponse, nil
}

// processExtractionPages handles the main page processing loop
func (e *WMSExtractor) processExtractionPages(paginator *pagination.WMSPaginator, pageResponse *pagination.PageResponse) (bool, error) {
	currentPage := 1
	checkpointCounter := 0
	checkpointInterval := 100
	var lastError error

	for {
		if shouldStop := e.checkExtractionStatus(); shouldStop {
			return false, lastError
		}

		if shouldPause := e.checkPauseStatus(); shouldPause {
			continue
		}

		success, err := e.processCurrentPage(pageResponse, currentPage)
		if !success {
			lastError = err
			if shouldBreak := e.handlePageError(err); shouldBreak {
				return false, lastError
			}
		}

		e.updateExtractionProgress(pageResponse, currentPage)
		
		if e.shouldSaveCheckpoint(&checkpointCounter, checkpointInterval) {
			e.performCheckpoint()
		}

		e.emitProgressEvent(currentPage)

		if !paginator.HasNextPage() {
			break
		}

		pageResponse, err = e.getNextPage(paginator)
		if err != nil {
			lastError = err
			if e.ErrorPolicy.FailOnFirstError {
				return false, lastError
			}
			continue
		}

		currentPage++
		e.applyRateLimit()
	}

	return true, nil
}

// checkExtractionStatus checks if extraction should be stopped
func (e *WMSExtractor) checkExtractionStatus() bool {
	select {
	case <-e.extractionCtx.Done():
		e.mutex.Lock()
		e.State.Status = ExtractionStatusCancelled
		e.mutex.Unlock()
		return true
	default:
		return false
	}
}

// checkPauseStatus checks if extraction is paused
func (e *WMSExtractor) checkPauseStatus() bool {
	e.mutex.RLock()
	isPaused := e.State.Status == ExtractionStatusPaused
	e.mutex.RUnlock()

	if isPaused {
		time.Sleep(1 * time.Second)
		return true
	}
	return false
}

// processCurrentPage processes a single page of data
func (e *WMSExtractor) processCurrentPage(pageResponse *pagination.PageResponse, currentPage int) (bool, error) {
	if err := e.processPageWithCircuitBreaker(pageResponse, currentPage); err != nil {
		return false, err
	}
	e.recordSuccessfulOperation()
	return true, nil
}

// handlePageError handles errors during page processing
func (e *WMSExtractor) handlePageError(err error) bool {
	e.handleExtractionError(err)

	if e.ErrorPolicy.UseCircuitBreaker && !e.canMakeRequest() {
		return true // Break the loop
	}

	if e.ErrorPolicy.FailOnFirstError {
		return true // Break the loop
	}

	e.Metrics.TotalErrors++
	if e.Metrics.TotalErrors >= e.ErrorPolicy.MaxErrors {
		return true // Break the loop
	}

	return false // Continue the loop
}

// shouldSaveCheckpoint determines if a checkpoint should be saved
func (e *WMSExtractor) shouldSaveCheckpoint(counter *int, interval int) bool {
	*counter++
	return *counter >= interval
}

// performCheckpoint saves a checkpoint and resets the counter
func (e *WMSExtractor) performCheckpoint() {
	if err := e.saveCheckpoint(); err != nil {
		e.handleExtractionError(fmt.Errorf("failed to save checkpoint: %w", err))
	}
}

// emitProgressEvent emits a progress event
func (e *WMSExtractor) emitProgressEvent(currentPage int) {
	e.AddEvent(&WMSDataExtractionProgress{
		BaseDomainEvent:  domain.NewBaseDomainEvent("wms.data.extraction.progress", e.GetID()),
		ClientID:         e.Client.GetID(),
		EntityName:       e.EntityName,
		CurrentPage:      currentPage,
		RecordsExtracted: e.State.Progress.RecordsExtracted,
		BytesExtracted:   e.State.Progress.BytesExtracted,
		ProgressPercent:  e.State.Progress.ProgressPercent,
	})
}

// getNextPage retrieves the next page of data
func (e *WMSExtractor) getNextPage(paginator *pagination.WMSPaginator) (*pagination.PageResponse, error) {
	var pageResponse *pagination.PageResponse
	err := func() error {
		var err error
		pageResponse, err = paginator.GetNextPage(e.extractionCtx)
		return err
	}()
	if err != nil {
		e.handleExtractionError(fmt.Errorf("failed to get next page after retries: %w", err))
		return nil, err
	}
	return pageResponse, nil
}

// applyRateLimit applies rate limiting between requests
func (e *WMSExtractor) applyRateLimit() {
	if e.RetryConfig.RateLimitPerSecond > 0 {
		delay := time.Duration(1000.0/e.RetryConfig.RateLimitPerSecond) * time.Millisecond
		time.Sleep(delay)
	}
}

// finalizeExtraction handles final state updates and event emission
func (e *WMSExtractor) finalizeExtraction(success bool, lastError error) {
	e.mutex.Lock()
	defer e.mutex.Unlock()

	endTime := time.Now()
	e.EndTime = &endTime

	if success {
		e.emitSuccessEvent()
	} else {
		e.emitFailureEvent(lastError)
	}

	e.MarkAsUpdated()
}

// emitSuccessEvent emits a successful completion event
func (e *WMSExtractor) emitSuccessEvent() {
	e.State.Status = ExtractionStatusCompleted
	e.AddEvent(&WMSDataExtractionCompleted{
		BaseDomainEvent:  domain.NewBaseDomainEvent("wms.data.extraction.completed", e.GetID()),
		ClientID:         e.Client.GetID(),
		EntityName:       e.EntityName,
		ExtractionType:   string(e.ExtractionType),
		RecordsExtracted: e.State.Progress.RecordsExtracted,
		BytesExtracted:   e.State.Progress.BytesExtracted,
		PagesProcessed:   e.State.Progress.PagesProcessed,
		DurationMs:       e.GetDurationMs(),
		Success:          true,
	})
}

// emitFailureEvent emits a failure event
func (e *WMSExtractor) emitFailureEvent(lastError error) {
	e.State.Status = ExtractionStatusFailed
	if lastError != nil {
		e.State.LastError = &ExtractionError{
			Code:        "EXTRACTION_FAILED",
			Message:     lastError.Error(),
			Timestamp:   time.Now(),
			Recoverable: true,
		}
	}

	e.AddEvent(&WMSDataExtractionFailed{
		BaseDomainEvent:               domain.NewBaseDomainEvent("wms.data.extraction.failed", e.GetID()),
		ClientID:                      e.Client.GetID(),
		EntityName:                    e.EntityName,
		ExtractionType:                string(e.ExtractionType),
		Error:                         lastError.Error(),
		RecordsExtractedBeforeFailure: e.State.Progress.RecordsExtracted,
		FailedAtPage:                  e.State.Progress.PagesProcessed,
	})
}

func (e *WMSExtractor) saveCheckpoint() error {
	// Implementation of checkpoint saving
	checkpoint := StateCheckpoint{
		ID:               uuid.New(),
		Timestamp:        time.Now(),
		Bookmark:         e.State.CurrentBookmark,
		RecordsExtracted: e.State.Progress.RecordsExtracted,
		BytesExtracted:   e.State.Progress.BytesExtracted,
		Metadata:         make(map[string]interface{}),
	}

	e.State.StateCheckpoints = append(e.State.StateCheckpoints, checkpoint)
	e.Metrics.CheckpointsSaved++

	return nil
}

func (e *WMSExtractor) handleExtractionPanic(r interface{}) {
	e.mutex.Lock()
	defer e.mutex.Unlock()

	e.State.Status = ExtractionStatusFailed
	e.State.LastError = &ExtractionError{
		Code:        "PANIC",
		Message:     fmt.Sprintf("Extraction panicked: %v", r),
		Timestamp:   time.Now(),
		Recoverable: false,
	}

	endTime := time.Now()
	e.EndTime = &endTime
	e.MarkAsUpdated()

	// Emit failure event
	e.AddEvent(&WMSDataExtractionFailed{
		BaseDomainEvent:               domain.NewBaseDomainEvent("wms.data.extraction.failed", e.GetID()),
		ClientID:                      e.Client.GetID(),
		EntityName:                    e.EntityName,
		ExtractionType:                string(e.ExtractionType),
		Error:                         fmt.Sprintf("Panic: %v", r),
		RecordsExtractedBeforeFailure: e.State.Progress.RecordsExtracted,
		FailedAtPage:                  e.State.Progress.PagesProcessed,
	})
}

func (e *WMSExtractor) GetDurationMs() int64 {
	if e.StartTime == nil {
		return 0
	}

	endTime := time.Now()
	if e.EndTime != nil {
		endTime = *e.EndTime
	}

	return endTime.Sub(*e.StartTime).Milliseconds()
}

// Helper methods for data extraction

func (e *WMSExtractor) processPage(pageResponse *pagination.PageResponse, pageNumber int) error {
	startTime := time.Now()

	// Process each record in the page
	for recordIndex, record := range pageResponse.Records {
		// Apply data transformations
		transformedRecord, err := e.applyTransformations(record)
		if err != nil {
			e.Metrics.ErrorsByType["transformation"]++
			if !e.ErrorPolicy.SkipErrorRecords {
				return fmt.Errorf("transformation failed for record %d: %w", recordIndex, err)
			}
			continue
		}

		// Apply validation rules
		if err := e.validateRecord(transformedRecord); err != nil {
			e.Metrics.ValidationFailures++
			if !e.ErrorPolicy.SkipErrorRecords {
				return fmt.Errorf("validation failed for record %d: %w", recordIndex, err)
			}
			continue
		}

		// Create extracted record
		extractedRecord := &ExtractedRecord{
			Type:             "RECORD",
			Stream:           e.EntityName,
			Record:           transformedRecord,
			TimeExtracted:    time.Now(),
			SourceEntity:     e.EntityName,
			ValidationStatus: "valid",
			PageNumber:       pageNumber,
			RecordIndex:      recordIndex,
			ExtractedAt:      time.Now(),
			ProcessingTime:   time.Since(startTime),
			OriginalRecord:   record,
		}

		// Update bookmark for incremental extraction
		e.updateBookmark(extractedRecord.Record)

		// Update metrics
		e.Metrics.RecordsValidated++
		e.State.Progress.RecordsExtracted++
	}

	// Update page-level metrics
	e.Metrics.TotalPagesProcessed++
	e.State.Progress.PagesProcessed++
	e.State.Progress.BytesExtracted += pageResponse.ResponseSize
	e.Metrics.TotalBytesExtracted += pageResponse.ResponseSize
	e.Metrics.NetworkBytesTransferred += pageResponse.ResponseSize

	// Update response time metrics
	e.updateResponseTimeMetrics(pageResponse.RequestTime)

	return nil
}

func (e *WMSExtractor) applyTransformations(record map[string]interface{}) (map[string]interface{}, error) {
	result := make(map[string]interface{})

	// Copy original record
	for key, value := range record {
		result[key] = value
	}

	// Apply field selections
	if len(e.Configuration.SelectedFields) > 0 {
		filtered := make(map[string]interface{})
		for _, field := range e.Configuration.SelectedFields {
			if value, exists := result[field]; exists {
				filtered[field] = value
			}
		}
		result = filtered
	}

	// Apply field exclusions
	for _, field := range e.Configuration.ExcludedFields {
		delete(result, field)
	}

	// Apply field mappings
	for sourceField, targetField := range e.Configuration.FieldMappings {
		if value, exists := result[sourceField]; exists {
			result[targetField] = value
			if sourceField != targetField {
				delete(result, sourceField)
			}
		}
	}

	// Apply data transformations
	for _, transformation := range e.Configuration.DataTransformations {
		if err := e.applyTransformation(result, transformation); err != nil {
			return nil, fmt.Errorf("failed to apply transformation %s: %w", transformation.Type, err)
		}
	}

	return result, nil
}

func (e *WMSExtractor) applyTransformation(record map[string]interface{}, transformation DataTransformation) error {
	switch transformation.Type {
	case "map":
		// Simple field mapping
		if value, exists := record[transformation.SourceField]; exists {
			record[transformation.TargetField] = value
			if transformation.SourceField != transformation.TargetField {
				delete(record, transformation.SourceField)
			}
		}

	case "filter":
		// Filter based on rule
		if shouldFilter, err := e.evaluateFilterRule(record, transformation.Rule, transformation.Parameters); err != nil {
			return err
		} else if shouldFilter {
			delete(record, transformation.SourceField)
		}

	case "convert":
		// Type conversion
		if value, exists := record[transformation.SourceField]; exists {
			converted, err := e.convertValue(value, transformation.Rule, transformation.Parameters)
			if err != nil {
				return err
			}
			record[transformation.TargetField] = converted
		}

	case "calculate":
		// Calculated field
		calculated, err := e.calculateValue(record, transformation.Rule, transformation.Parameters)
		if err != nil {
			return err
		}
		record[transformation.TargetField] = calculated
	}

	return nil
}

func (e *WMSExtractor) validateRecord(record map[string]interface{}) error {
	for _, rule := range e.Configuration.ValidationRules {
		if err := e.applyValidationRule(record, rule); err != nil {
			return err
		}
	}
	return nil
}

func (e *WMSExtractor) applyValidationRule(record map[string]interface{}, rule ValidationRule) error {
	value, exists := record[rule.Field]

	switch rule.Type {
	case "required":
		if !exists || value == nil {
			return fmt.Errorf("required field %s is missing or null", rule.Field)
		}

	case "format":
		if exists && value != nil {
			// Apply format validation based on rule.Rule
			// This would contain regex or format validation logic
		}

	case "range":
		if exists && value != nil {
			// Apply range validation based on rule.Parameters
		}

	case "custom":
		// Apply custom validation logic
		if err := e.evaluateCustomValidation(value, rule.Rule, rule.Parameters); err != nil {
			return err
		}
	}

	return nil
}

func (e *WMSExtractor) updateBookmark(record map[string]interface{}) {
	replicationKey := e.Configuration.ReplicationKey
	if replicationKey == "" {
		return
	}

	if bookmarkValue, exists := record[replicationKey]; exists {
		e.State.CurrentBookmark[replicationKey] = bookmarkValue
		e.LastBookmark[replicationKey] = bookmarkValue
	}
}

func (e *WMSExtractor) updateExtractionProgress(pageResponse *pagination.PageResponse, currentPage int) {
	e.mutex.Lock()
	defer e.mutex.Unlock()

	// Update progress metrics
	paginationState := pageResponse.PaginationInfo

	if paginationState.TotalRecords != nil {
		e.State.Progress.EstimatedTotal = paginationState.TotalRecords
		if *e.State.Progress.EstimatedTotal > 0 {
			e.State.Progress.ProgressPercent = float64(e.State.Progress.RecordsExtracted) / float64(*e.State.Progress.EstimatedTotal) * 100.0
		}
	}

	// Update timing
	if e.StartTime != nil {
		e.State.Progress.ElapsedTime = time.Since(*e.StartTime)

		// Estimate remaining time
		if e.State.Progress.ProgressPercent > 0 {
			totalEstimatedTime := time.Duration(float64(e.State.Progress.ElapsedTime) / (e.State.Progress.ProgressPercent / 100.0))
			remainingTime := totalEstimatedTime - e.State.Progress.ElapsedTime
			e.State.Progress.EstimatedTimeRemaining = &remainingTime
		}
	}

	// Update rates
	if e.State.Progress.ElapsedTime > 0 {
		seconds := e.State.Progress.ElapsedTime.Seconds()
		e.State.Progress.AverageRecordsPerSecond = float64(e.State.Progress.RecordsExtracted) / seconds
		e.State.Progress.CurrentBytesPerSecond = float64(e.State.Progress.BytesExtracted) / seconds
	}

	// Update stream progress
	if e.State.Progress.StreamProgress == nil {
		e.State.Progress.StreamProgress = make(map[string]int64)
	}
	e.State.Progress.StreamProgress[e.EntityName] = e.State.Progress.RecordsExtracted

	e.MarkAsUpdated()
}

func (e *WMSExtractor) updateResponseTimeMetrics(responseTime time.Duration) {
	e.Metrics.TotalRequestsMade++

	// Update average response time
	if e.Metrics.TotalRequestsMade == 1 {
		e.Metrics.AverageRequestTime = responseTime
	} else {
		// Rolling average
		totalTime := e.Metrics.AverageRequestTime * time.Duration(e.Metrics.TotalRequestsMade-1)
		e.Metrics.AverageRequestTime = (totalTime + responseTime) / time.Duration(e.Metrics.TotalRequestsMade)
	}

	// Update average page processing time
	if e.Metrics.TotalPagesProcessed == 0 {
		e.Metrics.AveragePageProcessingTime = responseTime
	} else {
		totalPageTime := e.Metrics.AveragePageProcessingTime * time.Duration(e.Metrics.TotalPagesProcessed)
		e.Metrics.AveragePageProcessingTime = (totalPageTime + responseTime) / time.Duration(e.Metrics.TotalPagesProcessed+1)
	}
}

func (e *WMSExtractor) handleExtractionError(err error) {
	e.mutex.Lock()
	defer e.mutex.Unlock()

	e.State.ErrorCount++
	e.Metrics.TotalErrors++

	// Use error handler for comprehensive analysis
	// TODO: Re-implement error analysis without import cycle
	// analysis := e.errorHandler.AnalyzeError(err)

	// Update metrics based on error type
	if e.Metrics.ErrorsByType == nil {
		e.Metrics.ErrorsByType = make(map[string]int)
	}
	// TODO: Use error analysis when available
	e.Metrics.ErrorsByType["unknown"]++

	// Create detailed extraction error
	// TODO: Re-enable when error handling is available
	/*
		context := map[string]interface{}{
			"entity_name":     e.EntityName,
			"extraction_type": string(e.ExtractionType),
			"current_page":    e.State.Progress.PagesProcessed,
			"records_so_far":  e.State.Progress.RecordsExtracted,
		}
	*/

	// TODO: Re-implement error creation without import cycle
	// e.State.LastError = e.errorHandler.CreateExtractionError(err, context)

	// Update client metrics
	// TODO: Re-implement client metrics update without import cycle
	// e.errorHandler.UpdateClientMetrics(e.Client, err)

	e.MarkAsUpdated()
}

func (e *WMSExtractor) isNonRecoverableError(err error) bool {
	nonRecoverablePatterns := []string{
		"authentication failed",
		"access denied",
		"entity not found",
		"invalid configuration",
	}

	errorMsg := strings.ToLower(err.Error())
	for _, pattern := range nonRecoverablePatterns {
		if strings.Contains(errorMsg, pattern) {
			return true
		}
	}
	return false
}

// Conversion and calculation helper methods

func (e *WMSExtractor) convertValue(value interface{}, conversionType string, params map[string]interface{}) (interface{}, error) {
	switch conversionType {
	case "string":
		return fmt.Sprintf("%v", value), nil
	case "int":
		if str, ok := value.(string); ok {
			return strconv.Atoi(str)
		}
		return value, nil
	case "float":
		if str, ok := value.(string); ok {
			return strconv.ParseFloat(str, 64)
		}
		return value, nil
	case "datetime":
		if str, ok := value.(string); ok {
			layout := "2006-01-02T15:04:05Z"
			if layoutParam, exists := params["layout"]; exists {
				layout = fmt.Sprintf("%v", layoutParam)
			}
			return time.Parse(layout, str)
		}
		return value, nil
	default:
		return value, nil
	}
}

func (e *WMSExtractor) calculateValue(record map[string]interface{}, calculation string, params map[string]interface{}) (interface{}, error) {
	// Simple calculation implementation
	// In a real implementation, this would support expressions like "field1 + field2"
	if sourceField, exists := params["source_field"]; exists {
		if value, fieldExists := record[fmt.Sprintf("%v", sourceField)]; fieldExists {
			return value, nil
		}
	}
	return nil, fmt.Errorf("calculation not supported: %s", calculation)
}

func (e *WMSExtractor) evaluateFilterRule(record map[string]interface{}, rule string, params map[string]interface{}) (bool, error) {
	// Simple filter rule evaluation
	// In a real implementation, this would support complex filter expressions
	return false, nil // Don't filter by default
}

func (e *WMSExtractor) evaluateCustomValidation(value interface{}, rule string, params map[string]interface{}) error {
	// Custom validation logic would go here
	return nil
}

func convertOrderByClauses(clauses []OrderByClause) []pagination.OrderByClause {
	result := make([]pagination.OrderByClause, len(clauses))
	for i, clause := range clauses {
		result[i] = pagination.OrderByClause{
			Field:     clause.Field,
			Direction: clause.Direction,
		}
	}
	return result
}

// Circuit breaker implementation for WMSExtractor

func (e *WMSExtractor) processPageWithCircuitBreaker(pageResponse *pagination.PageResponse, pageNumber int) error {
	// Check circuit breaker state
	if e.ErrorPolicy.UseCircuitBreaker && !e.canMakeRequest() {
		return fmt.Errorf("circuit breaker is open")
	}

	// Attempt to process the page
	err := e.processPage(pageResponse, pageNumber)

	// Update circuit breaker state based on result
	if err != nil {
		e.recordFailedOperation()
	} else {
		e.recordSuccessfulOperation()
	}

	return err
}

func (e *WMSExtractor) canMakeRequest() bool {
	if !e.ErrorPolicy.UseCircuitBreaker {
		return true
	}

	return e.Client.CircuitBreaker.CanAttemptCall()
}

func (e *WMSExtractor) recordSuccessfulOperation() {
	if e.ErrorPolicy.UseCircuitBreaker {
		e.Client.CircuitBreaker.CallSucceeded()
	}
}

func (e *WMSExtractor) recordFailedOperation() {
	if e.ErrorPolicy.UseCircuitBreaker {
		e.Client.CircuitBreaker.CallFailed()
	}
}

// Additional event types for extractor
// Note: WMSExtractorCreated is defined in wms_events.go to avoid duplication

// WMSDataExtractionStopped is emitted when extraction is stopped
type WMSDataExtractionStopped struct {
	domain.BaseDomainEvent
	ExtractorID      uuid.UUID `json:"extractor_id"`
	ClientID         uuid.UUID `json:"client_id"`
	EntityName       string    `json:"entity_name"`
	StoppedAt        time.Time `json:"stopped_at"`
	RecordsExtracted int64     `json:"records_extracted"`
}

// WMSDataExtractionPaused is emitted when extraction is paused
type WMSDataExtractionPaused struct {
	domain.BaseDomainEvent
	ExtractorID      uuid.UUID `json:"extractor_id"`
	ClientID         uuid.UUID `json:"client_id"`
	EntityName       string    `json:"entity_name"`
	PausedAt         time.Time `json:"paused_at"`
	RecordsExtracted int64     `json:"records_extracted"`
}

// WMSDataExtractionResumed is emitted when extraction is resumed
type WMSDataExtractionResumed struct {
	domain.BaseDomainEvent
	ExtractorID      uuid.UUID `json:"extractor_id"`
	ClientID         uuid.UUID `json:"client_id"`
	EntityName       string    `json:"entity_name"`
	ResumedAt        time.Time `json:"resumed_at"`
	RecordsExtracted int64     `json:"records_extracted"`
}

// WMSDataExtractionProgress is defined in wms_events.go to avoid duplication
