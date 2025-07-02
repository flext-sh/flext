package entities

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/wms/infrastructure/auth"
	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/google/uuid"
)

// WMSClient represents an advanced Oracle WMS client with dynamic entity discovery
type WMSClient struct {
	domain.AggregateRoot

	// Client configuration
	BaseURL    string            `json:"base_url" validate:"required,url"`
	APIVersion string            `json:"api_version"`
	Username   string            `json:"username" validate:"required"`
	Password   string            `json:"password" validate:"required"`
	Timeout    time.Duration     `json:"timeout"`
	Headers    map[string]string `json:"headers"`

	// Authentication
	AuthToken     string    `json:"auth_token,omitempty"`
	TokenExpiry   time.Time `json:"token_expiry,omitempty"`
	RefreshToken  string    `json:"refresh_token,omitempty"`

	// Client state
	Status        ClientStatus      `json:"status"`
	LastConnected *time.Time        `json:"last_connected,omitempty"`
	ConnectionID  string            `json:"connection_id"`

	// Circuit breaker pattern
	CircuitBreaker *CircuitBreaker `json:"circuit_breaker"`

	// Caching configuration
	CacheConfig CacheConfig `json:"cache_config"`

	// Entity discovery
	DiscoveredEntities map[string]*WMSEntity `json:"discovered_entities"`
	LastDiscovery      *time.Time            `json:"last_discovery,omitempty"`

	// Performance monitoring
	Metrics ClientMetrics `json:"metrics"`

	// HTTP client and authentication (not serialized)
	httpClient    *http.Client           `json:"-"`
	authenticator *auth.WMSAuthenticator `json:"-"`
	mutex         sync.RWMutex           `json:"-"`
}

// ClientStatus define os status possíveis de um cliente WMS
type ClientStatus string

const (
	ClientStatusDisconnected ClientStatus = "disconnected"
	ClientStatusConnecting   ClientStatus = "connecting"
	ClientStatusConnected    ClientStatus = "connected"
	ClientStatusError        ClientStatus = "error"
	ClientStatusMaintenance  ClientStatus = "maintenance"
)

// CircuitBreaker implements circuit breaker pattern for resilient API calls
type CircuitBreaker struct {
	FailureThreshold int           `json:"failure_threshold"`
	RecoveryTimeout  time.Duration `json:"recovery_timeout"`
	FailureCount     int           `json:"failure_count"`
	LastFailureTime  *time.Time    `json:"last_failure_time,omitempty"`
	State            string        `json:"state"` // "closed", "open", "half-open"
}

// CacheConfig configures caching behavior
type CacheConfig struct {
	EntityCacheTTL   time.Duration `json:"entity_cache_ttl"`
	SchemaCacheTTL   time.Duration `json:"schema_cache_ttl"`
	AccessCacheTTL   time.Duration `json:"access_cache_ttl"`
	EnableCaching    bool          `json:"enable_caching"`
	MaxCacheSize     int           `json:"max_cache_size"`
}

// ClientMetrics contains performance and usage metrics
type ClientMetrics struct {
	// Connection metrics
	TotalRequests      int64         `json:"total_requests"`
	SuccessfulRequests int64         `json:"successful_requests"`
	FailedRequests     int64         `json:"failed_requests"`
	AverageResponseTime time.Duration `json:"average_response_time"`

	// Discovery metrics
	EntitiesDiscovered int               `json:"entities_discovered"`
	SchemasGenerated   int               `json:"schemas_generated"`
	LastDiscoveryTime  time.Duration     `json:"last_discovery_time"`

	// Performance metrics
	RecordsExtracted   int64             `json:"records_extracted"`
	TotalBytesTransferred int64          `json:"total_bytes_transferred"`
	
	// Error tracking
	ErrorsByType       map[string]int    `json:"errors_by_type"`
	LastError          *time.Time        `json:"last_error,omitempty"`
	
	// Cache metrics
	CacheHits          int64             `json:"cache_hits"`
	CacheMisses        int64             `json:"cache_misses"`
}

// WMSEntity represents a dynamically discovered WMS entity
type WMSEntity struct {
	Name               string                 `json:"name" validate:"required"`
	URL                string                 `json:"url" validate:"required,url"`
	Schema             *WMSEntitySchema       `json:"schema,omitempty"`
	Metadata           map[string]interface{} `json:"metadata"`
	LastAccessed       *time.Time             `json:"last_accessed,omitempty"`
	AccessCount        int64                  `json:"access_count"`
	
	// Entity configuration
	ReplicationMethod  string                 `json:"replication_method"` // "INCREMENTAL", "FULL_TABLE"
	ReplicationKey     string                 `json:"replication_key"`
	SafetyOverlapMin   int                    `json:"safety_overlap_minutes"`
	
	// Filtering capabilities
	SupportedFilters   []string               `json:"supported_filters"`
	FilterOperators    map[string][]string    `json:"filter_operators"`
	
	// Pagination configuration
	PaginationMode     string                 `json:"pagination_mode"` // "cursor", "offset"
	MaxPageSize        int                    `json:"max_page_size"`
	OptimalPageSize    int                    `json:"optimal_page_size"`
	
	// Performance characteristics
	AvgRecordsPerPage  int                    `json:"avg_records_per_page"`
	AvgResponseTime    time.Duration          `json:"avg_response_time"`
	
	// Data patterns
	HasTimestamps      bool                   `json:"has_timestamps"`
	HasIDField         bool                   `json:"has_id_field"`
	HasStatusField     bool                   `json:"has_status_field"`
	
	// Field information
	Fields             []*EntityField         `json:"fields"`
}

// WMSEntitySchema represents a JSON schema for a WMS entity
type WMSEntitySchema struct {
	Type                 string                            `json:"type"`
	Properties           map[string]*SchemaProperty        `json:"properties"`
	Required             []string                          `json:"required"`
	AdditionalProperties bool                              `json:"additionalProperties"`
	
	// Schema metadata
	Title                string                            `json:"title,omitempty"`
	Description          string                            `json:"description,omitempty"`
	Version              string                            `json:"version,omitempty"`
	GeneratedAt          time.Time                         `json:"generated_at"`
	GenerationMethod     string                            `json:"generation_method"` // "metadata", "sample", "hybrid"
	
	// Validation rules
	ValidationRules      map[string]interface{}            `json:"validation_rules,omitempty"`
}

// SchemaProperty represents a property in a JSON schema
type SchemaProperty struct {
	Type        interface{}            `json:"type"` // string or []string for multiple types
	Format      string                 `json:"format,omitempty"`
	Description string                 `json:"description,omitempty"`
	Pattern     string                 `json:"pattern,omitempty"`
	Minimum     *float64               `json:"minimum,omitempty"`
	Maximum     *float64               `json:"maximum,omitempty"`
	MinLength   *int                   `json:"minLength,omitempty"`
	MaxLength   *int                   `json:"maxLength,omitempty"`
	Enum        []interface{}          `json:"enum,omitempty"`
	Default     interface{}            `json:"default,omitempty"`
	Examples    []interface{}          `json:"examples,omitempty"`
	
	// Additional metadata
	FieldType   string                 `json:"fieldType,omitempty"` // WMS field type
	Nullable    bool                   `json:"nullable,omitempty"`
	PrimaryKey  bool                   `json:"primaryKey,omitempty"`
	ForeignKey  string                 `json:"foreignKey,omitempty"`
}

// EntityField represents field metadata for a WMS entity
type EntityField struct {
	Name         string      `json:"name" validate:"required"`
	Type         string      `json:"type"` // "string", "integer", "number", "boolean", "datetime"
	Format       string      `json:"format,omitempty"`
	Required     bool        `json:"required"`
	Nullable     bool        `json:"nullable"`
	PrimaryKey   bool        `json:"primary_key"`
	ForeignKey   string      `json:"foreign_key,omitempty"`
	
	// Field constraints
	MinLength    *int        `json:"min_length,omitempty"`
	MaxLength    *int        `json:"max_length,omitempty"`
	Pattern      string      `json:"pattern,omitempty"`
	Minimum      *float64    `json:"minimum,omitempty"`
	Maximum      *float64    `json:"maximum,omitempty"`
	
	// Business metadata
	Description  string      `json:"description,omitempty"`
	BusinessName string      `json:"business_name,omitempty"`
	Category     string      `json:"category,omitempty"`
	
	// Usage patterns
	IsFilterable bool        `json:"is_filterable"`
	IsSortable   bool        `json:"is_sortable"`
	IsSearchable bool        `json:"is_searchable"`
	
	// Statistical information
	UniqueValues int64       `json:"unique_values,omitempty"`
	NullCount    int64       `json:"null_count,omitempty"`
	SampleValues []string    `json:"sample_values,omitempty"`
}

// NewWMSClient creates a new WMS client with advanced capabilities
func NewWMSClient(baseURL, username, password string) (*WMSClient, error) {
	if err := validateClientParameters(baseURL, username, password); err != nil {
		return nil, err
	}

	client, err := createWMSClientInstance(baseURL, username, password)
	if err != nil {
		return nil, err
	}

	configureClientDefaults(client)
	initializeClientAuthentication(client, baseURL, username, password)
	emitClientCreatedEvent(client, baseURL, username)

	return client, nil
}

// validateClientParameters validates the input parameters for client creation
func validateClientParameters(baseURL, username, password string) error {
	if baseURL == "" {
		return fmt.Errorf("base URL cannot be empty")
	}
	if username == "" {
		return fmt.Errorf("username cannot be empty")
	}
	if password == "" {
		return fmt.Errorf("password cannot be empty")
	}

	// Validate URL format
	parsedURL, err := url.Parse(baseURL)
	if err != nil {
		return fmt.Errorf("invalid base URL: %w", err)
	}
	if parsedURL.Scheme == "" {
		return fmt.Errorf("base URL must include scheme (http/https)")
	}

	return nil
}

// createWMSClientInstance creates the basic client instance with core configuration
func createWMSClientInstance(baseURL, username, password string) (*WMSClient, error) {
	client := &WMSClient{
		AggregateRoot:      domain.NewAggregateRoot(),
		BaseURL:            strings.TrimRight(baseURL, "/"),
		APIVersion:         "v10",
		Username:           username,
		Password:           password,
		Timeout:            30 * time.Second,
		Headers:            make(map[string]string),
		Status:             ClientStatusDisconnected,
		ConnectionID:       uuid.New().String(),
		DiscoveredEntities: make(map[string]*WMSEntity),
		
		// Default circuit breaker configuration
		CircuitBreaker: &CircuitBreaker{
			FailureThreshold: 5,
			RecoveryTimeout:  60 * time.Second,
			State:           "closed",
		},
		
		// Default cache configuration
		CacheConfig: CacheConfig{
			EntityCacheTTL:  2 * time.Hour,
			SchemaCacheTTL:  1 * time.Hour,
			AccessCacheTTL:  30 * time.Minute,
			EnableCaching:   true,
			MaxCacheSize:    1000,
		},
		
		// Initialize metrics
		Metrics: ClientMetrics{
			ErrorsByType: make(map[string]int),
		},
		
		// HTTP client configuration
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
			Transport: &http.Transport{
				MaxIdleConns:        100,
				MaxIdleConnsPerHost: 10,
				IdleConnTimeout:     90 * time.Second,
			},
		},
	}

	return client, nil
}

// configureClientDefaults sets up default headers and configurations
func configureClientDefaults(client *WMSClient) {
	client.Headers["Content-Type"] = "application/json"
	client.Headers["Accept"] = "application/json"
	client.Headers["User-Agent"] = "flext-wms-client/1.0"
}

// initializeClientAuthentication sets up the authenticator
func initializeClientAuthentication(client *WMSClient, baseURL, username, password string) {
	authConfig := auth.AuthConfig{
		AuthType:           auth.AuthTypeBasic,
		TokenRefreshBuffer: 5 * time.Minute,
		MaxRetries:         3,
		RetryDelay:         1 * time.Second,
		ConnectTimeout:     30 * time.Second,
		RequestTimeout:     30 * time.Second,
	}
	
	client.authenticator = auth.NewWMSAuthenticator(baseURL, username, password, authConfig)
}

// emitClientCreatedEvent emits the domain event for client creation
func emitClientCreatedEvent(client *WMSClient, baseURL, username string) {
	client.AddEvent(&WMSClientCreated{
		BaseDomainEvent: domain.NewBaseDomainEvent("wms.client.created", client.GetID()),
		ClientID:        client.GetID(),
		BaseURL:         baseURL,
		Username:        username,
		ConnectionID:    client.ConnectionID,
	})
}

// Connect establishes connection to WMS API and performs initial discovery
func (c *WMSClient) Connect(ctx context.Context) error {
	c.mutex.Lock()
	defer c.mutex.Unlock()

	if c.Status == ClientStatusConnected {
		return nil // Already connected
	}

	// Check circuit breaker
	if !c.CircuitBreaker.CanAttemptCall() {
		return fmt.Errorf("circuit breaker is open, cannot attempt connection")
	}

	c.Status = ClientStatusConnecting
	c.MarkAsUpdated()

	// Emit connecting event
	c.AddEvent(&WMSClientConnecting{
		BaseDomainEvent: domain.NewBaseDomainEvent("wms.client.connecting", c.GetID()),
		ClientID:        c.GetID(),
		ConnectionID:    c.ConnectionID,
	})

	// Perform authentication
	if err := c.authenticate(ctx); err != nil {
		c.CircuitBreaker.CallFailed()
		c.Status = ClientStatusError
		c.MarkAsUpdated()
		
		c.AddEvent(&WMSClientConnectionFailed{
			BaseDomainEvent: domain.NewBaseDomainEvent("wms.client.connection.failed", c.GetID()),
			ClientID:        c.GetID(),
			ConnectionID:    c.ConnectionID,
			Error:           err.Error(),
		})
		
		return fmt.Errorf("authentication failed: %w", err)
	}

	// Test API connectivity
	if err := c.testConnectivity(ctx); err != nil {
		c.CircuitBreaker.CallFailed()
		c.Status = ClientStatusError
		c.MarkAsUpdated()
		
		c.AddEvent(&WMSClientConnectionFailed{
			BaseDomainEvent: domain.NewBaseDomainEvent("wms.client.connection.failed", c.GetID()),
			ClientID:        c.GetID(),
			ConnectionID:    c.ConnectionID,
			Error:           err.Error(),
		})
		
		return fmt.Errorf("connectivity test failed: %w", err)
	}

	// Connection successful
	now := time.Now()
	c.Status = ClientStatusConnected
	c.LastConnected = &now
	c.CircuitBreaker.CallSucceeded()
	c.MarkAsUpdated()

	// Emit connected event
	c.AddEvent(&WMSClientConnected{
		BaseDomainEvent: domain.NewBaseDomainEvent("wms.client.connected", c.GetID()),
		ClientID:        c.GetID(),
		ConnectionID:    c.ConnectionID,
		ConnectedAt:     now,
	})

	return nil
}

// DiscoverEntities performs dynamic entity discovery from WMS API
func (c *WMSClient) DiscoverEntities(ctx context.Context, forceRefresh bool) error {
	c.mutex.Lock()
	defer c.mutex.Unlock()

	if err := c.validateConnectionForDiscovery(); err != nil {
		return err
	}

	if c.shouldSkipDiscovery(forceRefresh) {
		return nil
	}

	startTime := time.Now()
	c.emitDiscoveryStartedEvent(forceRefresh)

	entityList, err := c.fetchEntityListWithErrorHandling(ctx)
	if err != nil {
		return err
	}

	c.prepareForDiscovery(forceRefresh)
	discoveredCount := c.processEntityList(ctx, entityList)
	c.finalizeDiscovery(discoveredCount, startTime)

	return nil
}

// GetEntity retrieves a specific entity with its metadata
func (c *WMSClient) GetEntity(entityName string) (*WMSEntity, error) {
	c.mutex.RLock()
	defer c.mutex.RUnlock()

	entity, exists := c.DiscoveredEntities[entityName]
	if !exists {
		return nil, fmt.Errorf("entity %s not found in discovered entities", entityName)
	}

	// Update access statistics
	now := time.Now()
	entity.LastAccessed = &now
	entity.AccessCount++

	return entity, nil
}

// GetAllEntities returns all discovered entities
func (c *WMSClient) GetAllEntities() map[string]*WMSEntity {
	c.mutex.RLock()
	defer c.mutex.RUnlock()

	// Return a copy to prevent external modification
	entities := make(map[string]*WMSEntity)
	for name, entity := range c.DiscoveredEntities {
		entities[name] = entity
	}

	return entities
}

// GetEntityNames returns a list of all discovered entity names
func (c *WMSClient) GetEntityNames() []string {
	c.mutex.RLock()
	defer c.mutex.RUnlock()

	names := make([]string, 0, len(c.DiscoveredEntities))
	for name := range c.DiscoveredEntities {
		names = append(names, name)
	}

	return names
}

// GetAuthenticator returns the client's authenticator for internal use
func (c *WMSClient) GetAuthenticator() *auth.WMSAuthenticator {
	return c.authenticator
}

// Disconnect closes the connection to WMS API
func (c *WMSClient) Disconnect() error {
	c.mutex.Lock()
	defer c.mutex.Unlock()

	if c.Status == ClientStatusDisconnected {
		return nil // Already disconnected
	}

	c.Status = ClientStatusDisconnected
	c.AuthToken = ""
	c.TokenExpiry = time.Time{}
	c.RefreshToken = ""
	c.MarkAsUpdated()

	// Emit disconnected event
	c.AddEvent(&WMSClientDisconnected{
		BaseDomainEvent: domain.NewBaseDomainEvent("wms.client.disconnected", c.GetID()),
		ClientID:        c.GetID(),
		ConnectionID:    c.ConnectionID,
		DisconnectedAt:  time.Now(),
	})

	return nil
}

// IsConnected returns true if client is connected to WMS API
func (c *WMSClient) IsConnected() bool {
	c.mutex.RLock()
	defer c.mutex.RUnlock()

	return c.Status == ClientStatusConnected
}

// GetMetrics returns current client metrics
func (c *WMSClient) GetMetrics() ClientMetrics {
	c.mutex.RLock()
	defer c.mutex.RUnlock()

	return c.Metrics
}

// UpdateConfiguration updates client configuration
func (c *WMSClient) UpdateConfiguration(config map[string]interface{}) error {
	c.mutex.Lock()
	defer c.mutex.Unlock()

	// Update timeout if provided
	if timeout, ok := config["timeout"].(time.Duration); ok {
		c.Timeout = timeout
		c.httpClient.Timeout = timeout
	}

	// Update headers if provided
	if headers, ok := config["headers"].(map[string]string); ok {
		for key, value := range headers {
			c.Headers[key] = value
		}
	}

	// Update cache configuration if provided
	if cacheConfig, ok := config["cache_config"].(CacheConfig); ok {
		c.CacheConfig = cacheConfig
	}

	// Update circuit breaker configuration if provided
	if cbConfig, ok := config["circuit_breaker"].(CircuitBreaker); ok {
		c.CircuitBreaker = &cbConfig
	}

	c.MarkAsUpdated()

	// Emit configuration updated event
	c.AddEvent(&WMSClientConfigurationUpdated{
		BaseDomainEvent: domain.NewBaseDomainEvent("wms.client.configuration.updated", c.GetID()),
		ClientID:        c.GetID(),
		UpdatedFields:   getConfigurationKeys(config),
	})

	return nil
}

// Private helper methods

func (c *WMSClient) authenticate(ctx context.Context) error {
	if c.authenticator == nil {
		return fmt.Errorf("authenticator not initialized")
	}

	if err := c.authenticator.Authenticate(ctx); err != nil {
		c.Metrics.ErrorsByType["authentication"]++
		return fmt.Errorf("authentication failed: %w", err)
	}

	// Update metrics
	c.Metrics.SuccessfulRequests++
	
	return nil
}

func (c *WMSClient) testConnectivity(ctx context.Context) error {
	// Test connectivity by calling the API info endpoint
	infoURL := fmt.Sprintf("%s/wms/lgfapi/%s/info", c.BaseURL, c.APIVersion)
	
	resp, err := c.authenticator.MakeAuthenticatedRequest(ctx, "GET", infoURL, nil)
	if err != nil {
		c.Metrics.FailedRequests++
		c.Metrics.ErrorsByType["connectivity"]++
		return fmt.Errorf("connectivity test failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		c.Metrics.FailedRequests++
		c.Metrics.ErrorsByType["connectivity"]++
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("connectivity test failed with status %d: %s", resp.StatusCode, string(body))
	}

	// Update metrics
	c.Metrics.SuccessfulRequests++
	c.Metrics.TotalRequests++
	
	return nil
}

func (c *WMSClient) fetchEntityList(ctx context.Context) ([]string, error) {
	entityURL := fmt.Sprintf("%s/wms/lgfapi/%s/entity", c.BaseURL, c.APIVersion)
	
	resp, err := c.authenticator.MakeAuthenticatedRequest(ctx, "GET", entityURL, nil)
	if err != nil {
		c.Metrics.FailedRequests++
		c.Metrics.ErrorsByType["entity_discovery"]++
		return nil, fmt.Errorf("failed to fetch entity list: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		c.Metrics.FailedRequests++
		c.Metrics.ErrorsByType["entity_discovery"]++
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("entity list request failed with status %d: %s", resp.StatusCode, string(body))
	}

	// Parse response
	var entities []string
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read entity list response: %w", err)
	}

	// Try to parse as JSON array first
	if err := json.Unmarshal(body, &entities); err != nil {
		// If that fails, try parsing as object with entities field
		var response struct {
			Entities []string `json:"entities"`
			Data     []string `json:"data"`
			Results  []string `json:"results"`
		}
		
		if err := json.Unmarshal(body, &response); err != nil {
			return nil, fmt.Errorf("failed to parse entity list response: %w", err)
		}
		
		// Use the first non-empty array found
		if len(response.Entities) > 0 {
			entities = response.Entities
		} else if len(response.Data) > 0 {
			entities = response.Data
		} else if len(response.Results) > 0 {
			entities = response.Results
		}
	}

	// Update metrics
	c.Metrics.SuccessfulRequests++
	c.Metrics.TotalRequests++
	
	return entities, nil
}

func (c *WMSClient) analyzeEntity(ctx context.Context, entityName string) (*WMSEntity, error) {
	entity := &WMSEntity{
		Name:              entityName,
		URL:               fmt.Sprintf("%s/wms/lgfapi/%s/entity/%s", c.BaseURL, c.APIVersion, entityName),
		Metadata:          make(map[string]interface{}),
		ReplicationMethod: "INCREMENTAL",
		ReplicationKey:    "mod_ts",
		SafetyOverlapMin:  5,
		SupportedFilters:  []string{"mod_ts__gte", "mod_ts__lte", "id__gte", "id__lt"},
		FilterOperators:   make(map[string][]string),
		PaginationMode:    "cursor",
		MaxPageSize:       5000,
		OptimalPageSize:   1000,
		HasTimestamps:     true,
		HasIDField:        true,
		HasStatusField:    true,
		Fields:            []*EntityField{},
	}

	// Try to get entity metadata
	metadataURL := fmt.Sprintf("%s/describe", entity.URL)
	
	resp, err := c.authenticator.MakeAuthenticatedRequest(ctx, "GET", metadataURL, nil)
	if err == nil && resp.StatusCode == http.StatusOK {
		defer resp.Body.Close()
		
		var metadata map[string]interface{}
		if err := json.NewDecoder(resp.Body).Decode(&metadata); err == nil {
			entity.Metadata = metadata
			
			// Extract field information if available
			if fields, ok := metadata["fields"].([]interface{}); ok {
				for _, fieldData := range fields {
					if fieldMap, ok := fieldData.(map[string]interface{}); ok {
						field := &EntityField{
							Name:         getStringFromMap(fieldMap, "name"),
							Type:         getStringFromMap(fieldMap, "type"),
							Required:     getBoolFromMap(fieldMap, "required"),
							Nullable:     getBoolFromMap(fieldMap, "nullable"),
							PrimaryKey:   getBoolFromMap(fieldMap, "primary_key"),
							Description:  getStringFromMap(fieldMap, "description"),
							IsFilterable: true, // Default to true
							IsSortable:   true, // Default to true
						}
						entity.Fields = append(entity.Fields, field)
					}
				}
			}
			
			// Analyze metadata to determine capabilities
			if tableInfo, ok := metadata["table_info"].(map[string]interface{}); ok {
				if primaryKeys, ok := tableInfo["primary_keys"].([]interface{}); ok && len(primaryKeys) > 0 {
					entity.HasIDField = true
				}
				
				// Check for timestamp fields
				entity.HasTimestamps = c.hasTimestampFields(entity.Fields)
			}
		}
	}

	// Test entity access with a small sample
	sampleURL := fmt.Sprintf("%s?page_size=1", entity.URL)
	
	resp, err = c.authenticator.MakeAuthenticatedRequest(ctx, "GET", sampleURL, nil)
	if err != nil {
		c.Metrics.ErrorsByType["entity_analysis"]++
		return entity, nil // Return entity even if sample fails
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		var sampleResponse map[string]interface{}
		if err := json.NewDecoder(resp.Body).Decode(&sampleResponse); err == nil {
			// Analyze sample response structure
			if results, ok := sampleResponse["results"].([]interface{}); ok && len(results) > 0 {
				if record, ok := results[0].(map[string]interface{}); ok {
					// Infer fields from sample record if not already populated
					if len(entity.Fields) == 0 {
						for fieldName, value := range record {
							field := &EntityField{
								Name:         fieldName,
								Type:         inferFieldType(value),
								Nullable:     value == nil,
								IsFilterable: true,
								IsSortable:   true,
							}
							
							// Check for common primary key patterns
							if strings.ToLower(fieldName) == "id" || 
							   strings.HasSuffix(strings.ToLower(fieldName), "_id") {
								field.PrimaryKey = true
								entity.HasIDField = true
							}
							
							// Check for timestamp patterns
							if strings.Contains(strings.ToLower(fieldName), "ts") ||
							   strings.Contains(strings.ToLower(fieldName), "time") ||
							   strings.Contains(strings.ToLower(fieldName), "date") {
								entity.HasTimestamps = true
							}
							
							entity.Fields = append(entity.Fields, field)
						}
					}
					
					// Update average records per page estimate
					entity.AvgRecordsPerPage = 1 // At least 1 record exists
				}
			}
			
			// Check pagination info
			if pageInfo, ok := sampleResponse["page_info"].(map[string]interface{}); ok {
				if nextPage, exists := pageInfo["next_page"]; exists && nextPage != nil {
					entity.PaginationMode = "cursor"
				} else if pageNum, exists := pageInfo["page_number"]; exists && pageNum != nil {
					entity.PaginationMode = "offset"
				}
			}
		}
	}

	// Update metrics
	c.Metrics.SuccessfulRequests++
	c.Metrics.TotalRequests++
	
	return entity, nil
}

func getConfigurationKeys(config map[string]interface{}) []string {
	keys := make([]string, 0, len(config))
	for key := range config {
		keys = append(keys, key)
	}
	return keys
}

// Helper functions for entity analysis

func getStringFromMap(m map[string]interface{}, key string) string {
	if value, ok := m[key].(string); ok {
		return value
	}
	return ""
}

func getBoolFromMap(m map[string]interface{}, key string) bool {
	if value, ok := m[key].(bool); ok {
		return value
	}
	return false
}

func (c *WMSClient) hasTimestampFields(fields []*EntityField) bool {
	for _, field := range fields {
		fieldName := strings.ToLower(field.Name)
		if strings.Contains(fieldName, "ts") ||
		   strings.Contains(fieldName, "time") ||
		   strings.Contains(fieldName, "date") ||
		   strings.Contains(fieldName, "created") ||
		   strings.Contains(fieldName, "modified") ||
		   strings.Contains(fieldName, "updated") {
			return true
		}
	}
	return false
}

func inferFieldType(value interface{}) string {
	if value == nil {
		return "string" // Default for null values
	}
	
	switch value.(type) {
	case bool:
		return "boolean"
	case int, int8, int16, int32, int64, uint, uint8, uint16, uint32, uint64:
		return "integer"
	case float32, float64:
		return "number"
	case string:
		return "string"
	case []interface{}:
		return "array"
	case map[string]interface{}:
		return "object"
	default:
		return "string"
	}
}

// CanAttemptCall checks if the circuit breaker allows calls
func (cb *CircuitBreaker) CanAttemptCall() bool {
	switch cb.State {
	case "closed":
		return true
	case "open":
		if cb.LastFailureTime != nil && 
			time.Since(*cb.LastFailureTime) > cb.RecoveryTimeout {
			cb.State = "half-open"
			return true
		}
		return false
	case "half-open":
		return true
	default:
		return true
	}
}

// CallSucceeded records a successful call
func (cb *CircuitBreaker) CallSucceeded() {
	cb.FailureCount = 0
	cb.State = "closed"
}

// CallFailed records a failed call
func (cb *CircuitBreaker) CallFailed() {
	cb.FailureCount++
	now := time.Now()
	cb.LastFailureTime = &now

	if cb.FailureCount >= cb.FailureThreshold {
		cb.State = "open"
	}
}

// Helper methods for DiscoverEntities

func (c *WMSClient) validateConnectionForDiscovery() error {
	if c.Status != ClientStatusConnected {
		return fmt.Errorf("client must be connected before discovering entities")
	}
	return nil
}

func (c *WMSClient) shouldSkipDiscovery(forceRefresh bool) bool {
	return !forceRefresh && c.LastDiscovery != nil && 
		time.Since(*c.LastDiscovery) < c.CacheConfig.EntityCacheTTL
}

func (c *WMSClient) emitDiscoveryStartedEvent(forceRefresh bool) {
	c.AddEvent(&WMSEntityDiscoveryStarted{
		BaseDomainEvent: domain.NewBaseDomainEvent("wms.entity.discovery.started", c.GetID()),
		ClientID:        c.GetID(),
		ForceRefresh:    forceRefresh,
	})
}

func (c *WMSClient) fetchEntityListWithErrorHandling(ctx context.Context) ([]string, error) {
	entityList, err := c.fetchEntityList(ctx)
	if err != nil {
		c.AddEvent(&WMSEntityDiscoveryFailed{
			BaseDomainEvent: domain.NewBaseDomainEvent("wms.entity.discovery.failed", c.GetID()),
			ClientID:        c.GetID(),
			Error:           err.Error(),
		})
		return nil, fmt.Errorf("failed to fetch entity list: %w", err)
	}
	return entityList, nil
}

func (c *WMSClient) prepareForDiscovery(forceRefresh bool) {
	if forceRefresh {
		c.DiscoveredEntities = make(map[string]*WMSEntity)
	}
}

func (c *WMSClient) processEntityList(ctx context.Context, entityList []string) int {
	discoveredCount := 0
	for _, entityName := range entityList {
		entity, err := c.analyzeEntity(ctx, entityName)
		if err != nil {
			c.Metrics.ErrorsByType["entity_analysis"]++
			continue
		}
		
		c.DiscoveredEntities[entityName] = entity
		discoveredCount++
	}
	return discoveredCount
}

func (c *WMSClient) finalizeDiscovery(discoveredCount int, startTime time.Time) {
	now := time.Now()
	c.LastDiscovery = &now
	c.Metrics.EntitiesDiscovered = discoveredCount
	c.Metrics.LastDiscoveryTime = time.Since(startTime)
	c.MarkAsUpdated()

	c.AddEvent(&WMSEntityDiscoveryCompleted{
		BaseDomainEvent:    domain.NewBaseDomainEvent("wms.entity.discovery.completed", c.GetID()),
		ClientID:           c.GetID(),
		EntitiesDiscovered: discoveredCount,
		DurationMs:         time.Since(startTime).Milliseconds(),
	})
}

