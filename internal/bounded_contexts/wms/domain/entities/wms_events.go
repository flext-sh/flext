package entities

import (
	"time"

	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/google/uuid"
)

// WMS Client Events

// WMSClientCreated is emitted when a new WMS client is created
type WMSClientCreated struct {
	domain.BaseDomainEvent
	ClientID     uuid.UUID `json:"client_id"`
	BaseURL      string    `json:"base_url"`
	Username     string    `json:"username"`
	ConnectionID string    `json:"connection_id"`
}

// WMSClientConnecting is emitted when client starts connecting
type WMSClientConnecting struct {
	domain.BaseDomainEvent
	ClientID     uuid.UUID `json:"client_id"`
	ConnectionID string    `json:"connection_id"`
}

// WMSClientConnected is emitted when client successfully connects
type WMSClientConnected struct {
	domain.BaseDomainEvent
	ClientID     uuid.UUID `json:"client_id"`
	ConnectionID string    `json:"connection_id"`
	ConnectedAt  time.Time `json:"connected_at"`
}

// WMSClientConnectionFailed is emitted when client connection fails
type WMSClientConnectionFailed struct {
	domain.BaseDomainEvent
	ClientID     uuid.UUID `json:"client_id"`
	ConnectionID string    `json:"connection_id"`
	Error        string    `json:"error"`
}

// WMSClientDisconnected is emitted when client disconnects
type WMSClientDisconnected struct {
	domain.BaseDomainEvent
	ClientID       uuid.UUID `json:"client_id"`
	ConnectionID   string    `json:"connection_id"`
	DisconnectedAt time.Time `json:"disconnected_at"`
}

// WMSClientConfigurationUpdated is emitted when client configuration changes
type WMSClientConfigurationUpdated struct {
	domain.BaseDomainEvent
	ClientID      uuid.UUID `json:"client_id"`
	UpdatedFields []string  `json:"updated_fields"`
}

// WMS Entity Discovery Events

// WMSEntityDiscoveryStarted is emitted when entity discovery begins
type WMSEntityDiscoveryStarted struct {
	domain.BaseDomainEvent
	ClientID     uuid.UUID `json:"client_id"`
	ForceRefresh bool      `json:"force_refresh"`
}

// WMSEntityDiscoveryCompleted is emitted when entity discovery completes
type WMSEntityDiscoveryCompleted struct {
	domain.BaseDomainEvent
	ClientID           uuid.UUID `json:"client_id"`
	EntitiesDiscovered int       `json:"entities_discovered"`
	DurationMs         int64     `json:"duration_ms"`
}

// WMSEntityDiscoveryFailed is emitted when entity discovery fails
type WMSEntityDiscoveryFailed struct {
	domain.BaseDomainEvent
	ClientID uuid.UUID `json:"client_id"`
	Error    string    `json:"error"`
}

// WMS Entity Access Events

// WMSEntityAccessed is emitted when an entity is accessed
type WMSEntityAccessed struct {
	domain.BaseDomainEvent
	ClientID   uuid.UUID `json:"client_id"`
	EntityName string    `json:"entity_name"`
	AccessType string    `json:"access_type"` // "read", "schema", "metadata"
}

// WMSEntitySchemaGenerated is emitted when an entity schema is generated
type WMSEntitySchemaGenerated struct {
	domain.BaseDomainEvent
	ClientID         uuid.UUID `json:"client_id"`
	EntityName       string    `json:"entity_name"`
	GenerationMethod string    `json:"generation_method"` // "metadata", "sample", "hybrid"
	FieldCount       int       `json:"field_count"`
	DurationMs       int64     `json:"duration_ms"`
}

// WMSEntitySchemaGenerationFailed is emitted when schema generation fails
type WMSEntitySchemaGenerationFailed struct {
	domain.BaseDomainEvent
	ClientID   uuid.UUID `json:"client_id"`
	EntityName string    `json:"entity_name"`
	Error      string    `json:"error"`
}

// WMS Data Extraction Events

// WMSExtractorCreated is emitted when a new extractor is created
type WMSExtractorCreated struct {
	domain.BaseDomainEvent
	ExtractorID    uuid.UUID `json:"extractor_id"`
	ClientID       uuid.UUID `json:"client_id"`
	EntityName     string    `json:"entity_name"`
	ExtractionType string    `json:"extraction_type"`
}

// WMSDataExtractionStarted is emitted when data extraction begins
type WMSDataExtractionStarted struct {
	domain.BaseDomainEvent
	ClientID         uuid.UUID              `json:"client_id"`
	EntityName       string                 `json:"entity_name"`
	ExtractionType   string                 `json:"extraction_type"` // "incremental", "full", "sample"
	Filters          map[string]interface{} `json:"filters"`
	PageSize         int                    `json:"page_size"`
	EstimatedRecords int64                  `json:"estimated_records,omitempty"`
}

// WMSDataExtractionProgress is emitted during data extraction for progress tracking
type WMSDataExtractionProgress struct {
	domain.BaseDomainEvent
	ClientID         uuid.UUID      `json:"client_id"`
	EntityName       string         `json:"entity_name"`
	RecordsExtracted int64          `json:"records_extracted"`
	BytesExtracted   int64          `json:"bytes_extracted"`
	ProgressPercent  float64        `json:"progress_percent"`
	CurrentPage      int            `json:"current_page"`
	EstimatedETA     *time.Duration `json:"estimated_eta,omitempty"`
}

// WMSDataExtractionCompleted is emitted when data extraction completes
type WMSDataExtractionCompleted struct {
	domain.BaseDomainEvent
	ClientID         uuid.UUID `json:"client_id"`
	EntityName       string    `json:"entity_name"`
	ExtractionType   string    `json:"extraction_type"`
	RecordsExtracted int64     `json:"records_extracted"`
	BytesExtracted   int64     `json:"bytes_extracted"`
	PagesProcessed   int       `json:"pages_processed"`
	DurationMs       int64     `json:"duration_ms"`
	Success          bool      `json:"success"`
}

// WMSDataExtractionFailed is emitted when data extraction fails
type WMSDataExtractionFailed struct {
	domain.BaseDomainEvent
	ClientID                      uuid.UUID `json:"client_id"`
	EntityName                    string    `json:"entity_name"`
	ExtractionType                string    `json:"extraction_type"`
	Error                         string    `json:"error"`
	RecordsExtractedBeforeFailure int64     `json:"records_extracted_before_failure"`
	FailedAtPage                  int       `json:"failed_at_page"`
}

// WMS Filtering Events

// WMSFilterApplied is emitted when filters are applied to an entity query
type WMSFilterApplied struct {
	domain.BaseDomainEvent
	ClientID    uuid.UUID              `json:"client_id"`
	EntityName  string                 `json:"entity_name"`
	FilterType  string                 `json:"filter_type"` // "simple", "advanced", "incremental", "full_sync"
	Filters     map[string]interface{} `json:"filters"`
	ResultCount int64                  `json:"result_count,omitempty"`
}

// WMSPaginationEvent is emitted during pagination operations
type WMSPaginationEvent struct {
	domain.BaseDomainEvent
	ClientID       uuid.UUID `json:"client_id"`
	EntityName     string    `json:"entity_name"`
	PaginationType string    `json:"pagination_type"` // "cursor", "offset"
	PageNumber     int       `json:"page_number"`
	PageSize       int       `json:"page_size"`
	TotalPages     *int      `json:"total_pages,omitempty"`
	HasNextPage    bool      `json:"has_next_page"`
	CursorToken    string    `json:"cursor_token,omitempty"`
}

// WMS Performance Events

// WMSPerformanceMetricsUpdated is emitted when performance metrics are updated
type WMSPerformanceMetricsUpdated struct {
	domain.BaseDomainEvent
	ClientID            uuid.UUID     `json:"client_id"`
	EntityName          string        `json:"entity_name,omitempty"`
	AverageResponseTime time.Duration `json:"average_response_time"`
	TotalRequests       int64         `json:"total_requests"`
	SuccessRate         float64       `json:"success_rate"`
	ThroughputRPS       float64       `json:"throughput_rps"`
}

// WMSCircuitBreakerStateChanged is emitted when circuit breaker state changes
type WMSCircuitBreakerStateChanged struct {
	domain.BaseDomainEvent
	ClientID      uuid.UUID `json:"client_id"`
	PreviousState string    `json:"previous_state"`
	NewState      string    `json:"new_state"`
	FailureCount  int       `json:"failure_count"`
	Reason        string    `json:"reason"`
}

// WMS Cache Events

// WMSCacheHit is emitted when a cache hit occurs
type WMSCacheHit struct {
	domain.BaseDomainEvent
	ClientID   uuid.UUID `json:"client_id"`
	CacheType  string    `json:"cache_type"` // "entity", "schema", "access"
	CacheKey   string    `json:"cache_key"`
	EntityName string    `json:"entity_name,omitempty"`
}

// WMSCacheMiss is emitted when a cache miss occurs
type WMSCacheMiss struct {
	domain.BaseDomainEvent
	ClientID   uuid.UUID `json:"client_id"`
	CacheType  string    `json:"cache_type"` // "entity", "schema", "access"
	CacheKey   string    `json:"cache_key"`
	EntityName string    `json:"entity_name,omitempty"`
}

// WMSCacheExpired is emitted when cached data expires
type WMSCacheExpired struct {
	domain.BaseDomainEvent
	ClientID   uuid.UUID `json:"client_id"`
	CacheType  string    `json:"cache_type"`
	CacheKey   string    `json:"cache_key"`
	EntityName string    `json:"entity_name,omitempty"`
	ExpiredAt  time.Time `json:"expired_at"`
	CachedAt   time.Time `json:"cached_at"`
}

// WMS Error Events

// WMSAPIError is emitted when an API error occurs
type WMSAPIError struct {
	domain.BaseDomainEvent
	ClientID     uuid.UUID `json:"client_id"`
	EntityName   string    `json:"entity_name,omitempty"`
	HTTPStatus   int       `json:"http_status"`
	ErrorCode    string    `json:"error_code"`
	ErrorMessage string    `json:"error_message"`
	RequestURL   string    `json:"request_url"`
	RetryAttempt int       `json:"retry_attempt"`
}

// WMSRateLimitExceeded is emitted when rate limit is exceeded
type WMSRateLimitExceeded struct {
	domain.BaseDomainEvent
	ClientID     uuid.UUID `json:"client_id"`
	EntityName   string    `json:"entity_name,omitempty"`
	LimitType    string    `json:"limit_type"` // "requests_per_minute", "requests_per_hour"
	CurrentCount int       `json:"current_count"`
	LimitValue   int       `json:"limit_value"`
	ResetTime    time.Time `json:"reset_time"`
}

// WMSTimeoutError is emitted when a timeout occurs
type WMSTimeoutError struct {
	domain.BaseDomainEvent
	ClientID     uuid.UUID     `json:"client_id"`
	EntityName   string        `json:"entity_name,omitempty"`
	Operation    string        `json:"operation"` // "connect", "read", "write"
	TimeoutValue time.Duration `json:"timeout_value"`
	ElapsedTime  time.Duration `json:"elapsed_time"`
	RequestURL   string        `json:"request_url"`
}

// WMS State Management Events

// WMSStateBookmarkUpdated is emitted when a replication bookmark is updated
type WMSStateBookmarkUpdated struct {
	domain.BaseDomainEvent
	ClientID         uuid.UUID   `json:"client_id"`
	EntityName       string      `json:"entity_name"`
	ReplicationKey   string      `json:"replication_key"`
	PreviousValue    interface{} `json:"previous_value,omitempty"`
	NewValue         interface{} `json:"new_value"`
	RecordsProcessed int64       `json:"records_processed"`
}

// WMSStateSaved is emitted when state is persisted
type WMSStateSaved struct {
	domain.BaseDomainEvent
	ClientID     uuid.UUID              `json:"client_id"`
	StateType    string                 `json:"state_type"` // "incremental", "full_sync", "discovery"
	EntityStates map[string]interface{} `json:"entity_states"`
	SavedAt      time.Time              `json:"saved_at"`
	StateSize    int64                  `json:"state_size_bytes"`
}

// WMSStateRestored is emitted when state is restored
type WMSStateRestored struct {
	domain.BaseDomainEvent
	ClientID     uuid.UUID              `json:"client_id"`
	StateType    string                 `json:"state_type"`
	EntityStates map[string]interface{} `json:"entity_states"`
	RestoredAt   time.Time              `json:"restored_at"`
	StateAge     time.Duration          `json:"state_age"`
}

// Helper methods for event creation

// NewWMSClientCreated creates a new WMSClientCreated event
func NewWMSClientCreated(clientID uuid.UUID, baseURL, username, connectionID string) *WMSClientCreated {
	return &WMSClientCreated{
		BaseDomainEvent: domain.NewBaseDomainEvent("wms.client.created", clientID),
		ClientID:        clientID,
		BaseURL:         baseURL,
		Username:        username,
		ConnectionID:    connectionID,
	}
}

// NewWMSExtractorCreated creates a new WMSExtractorCreated event
func NewWMSExtractorCreated(extractorID, clientID uuid.UUID, entityName, extractionType string) *WMSExtractorCreated {
	return &WMSExtractorCreated{
		BaseDomainEvent: domain.NewBaseDomainEvent("wms.extractor.created", extractorID),
		ExtractorID:     extractorID,
		ClientID:        clientID,
		EntityName:      entityName,
		ExtractionType:  extractionType,
	}
}

// NewWMSEntityDiscoveryCompleted creates a new WMSEntityDiscoveryCompleted event
func NewWMSEntityDiscoveryCompleted(clientID uuid.UUID, entitiesDiscovered int, durationMs int64) *WMSEntityDiscoveryCompleted {
	return &WMSEntityDiscoveryCompleted{
		BaseDomainEvent:    domain.NewBaseDomainEvent("wms.entity.discovery.completed", clientID),
		ClientID:           clientID,
		EntitiesDiscovered: entitiesDiscovered,
		DurationMs:         durationMs,
	}
}

// NewWMSDataExtractionStarted creates a new WMSDataExtractionStarted event
func NewWMSDataExtractionStarted(clientID uuid.UUID, entityName, extractionType string, filters map[string]interface{}, pageSize int) *WMSDataExtractionStarted {
	return &WMSDataExtractionStarted{
		BaseDomainEvent: domain.NewBaseDomainEvent("wms.data.extraction.started", clientID),
		ClientID:        clientID,
		EntityName:      entityName,
		ExtractionType:  extractionType,
		Filters:         filters,
		PageSize:        pageSize,
	}
}

// NewWMSDataExtractionCompleted creates a new WMSDataExtractionCompleted event
func NewWMSDataExtractionCompleted(clientID uuid.UUID, entityName, extractionType string, recordsExtracted, bytesExtracted int64, pagesProcessed int, durationMs int64, success bool) *WMSDataExtractionCompleted {
	return &WMSDataExtractionCompleted{
		BaseDomainEvent:  domain.NewBaseDomainEvent("wms.data.extraction.completed", clientID),
		ClientID:         clientID,
		EntityName:       entityName,
		ExtractionType:   extractionType,
		RecordsExtracted: recordsExtracted,
		BytesExtracted:   bytesExtracted,
		PagesProcessed:   pagesProcessed,
		DurationMs:       durationMs,
		Success:          success,
	}
}

// NewWMSPerformanceMetricsUpdated creates a new WMSPerformanceMetricsUpdated event
func NewWMSPerformanceMetricsUpdated(clientID uuid.UUID, entityName string, avgResponseTime time.Duration, totalRequests int64, successRate, throughputRPS float64) *WMSPerformanceMetricsUpdated {
	return &WMSPerformanceMetricsUpdated{
		BaseDomainEvent:     domain.NewBaseDomainEvent("wms.performance.metrics.updated", clientID),
		ClientID:            clientID,
		EntityName:          entityName,
		AverageResponseTime: avgResponseTime,
		TotalRequests:       totalRequests,
		SuccessRate:         successRate,
		ThroughputRPS:       throughputRPS,
	}
}
