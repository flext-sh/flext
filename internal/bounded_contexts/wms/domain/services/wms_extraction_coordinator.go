// Package services provides domain services for WMS extraction following SOLID principles
// This file ELIMINATES SRP violations by separating concerns
package services

import (
	"context"
	"errors"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/wms/domain/entities"
	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/google/uuid"
)

// WMSExtractionCoordinator coordinates extraction operations following Single Responsibility Principle
// SOLID: S - Single responsibility (coordination only)
type WMSExtractionCoordinator struct {
	domain.AggregateRoot

	// Core identification
	ExtractionID   uuid.UUID               `json:"extraction_id"`
	EntityName     string                  `json:"entity_name"`
	ExtractionType entities.ExtractionType `json:"extraction_type"`

	// Dependency injection for SOLID compliance
	client        WMSClientInterface
	stateManager  ExtractionStateManagerInterface
	metricService MetricServiceInterface
	errorHandler  ErrorHandlerInterface

	// Configuration
	config *ExtractionConfiguration
}

// WMSClientInterface defines client contract - SOLID: I - Interface Segregation
type WMSClientInterface interface {
	ExecuteQuery(ctx context.Context, query string, params map[string]interface{}) (*QueryResult, error)
	GetEntitySchema(entityName string) (*EntitySchema, error)
	ValidateConnection() error
}

// ExtractionStateManagerInterface manages extraction state - SOLID: I - Interface Segregation
type ExtractionStateManagerInterface interface {
	SaveState(extractionID uuid.UUID, state *ExtractionState) error
	LoadState(extractionID uuid.UUID) (*ExtractionState, error)
	UpdateBookmark(extractionID uuid.UUID, bookmark map[string]interface{}) error
}

// MetricServiceInterface handles metrics collection - SOLID: I - Interface Segregation
type MetricServiceInterface interface {
	StartExtraction(extractionID uuid.UUID) error
	UpdateProgress(extractionID uuid.UUID, metrics ExtractionMetrics) error
	FinishExtraction(extractionID uuid.UUID, success bool) error
}

// ErrorHandlerInterface manages error handling - SOLID: I - Interface Segregation
type ErrorHandlerInterface interface {
	HandleError(extractionID uuid.UUID, err error) (*ErrorResponse, error)
	ShouldRetry(err error, attemptCount int) bool
	GetBackoffDelay(attemptCount int) time.Duration
}

// ExtractionConfiguration holds extraction configuration
type ExtractionConfiguration struct {
	BatchSize        int                    `json:"batch_size"`
	MaxConcurrency   int                    `json:"max_concurrency"`
	Timeout          time.Duration          `json:"timeout"`
	RetryPolicy      RetryPolicy            `json:"retry_policy"`
	Filters          map[string]interface{} `json:"filters"`
	PaginationConfig *PaginationConfig      `json:"pagination_config"`
}

// ExtractionState represents current extraction state
type ExtractionState struct {
	Status           ExtractionStatus       `json:"status"`
	Progress         float64                `json:"progress"`
	ProcessedRecords int64                  `json:"processed_records"`
	TotalRecords     int64                  `json:"total_records"`
	LastBookmark     map[string]interface{} `json:"last_bookmark"`
	StartedAt        time.Time              `json:"started_at"`
	UpdatedAt        time.Time              `json:"updated_at"`
}

// ExtractionStatus represents extraction status
type ExtractionStatus string

const (
	ExtractionStatusPending   ExtractionStatus = "pending"
	ExtractionStatusRunning   ExtractionStatus = "running"
	ExtractionStatusCompleted ExtractionStatus = "completed"
	ExtractionStatusFailed    ExtractionStatus = "failed"
	ExtractionStatusCancelled ExtractionStatus = "cancelled"
)

// RetryPolicy defines retry behavior
type RetryPolicy struct {
	MaxAttempts   int           `json:"max_attempts"`
	InitialDelay  time.Duration `json:"initial_delay"`
	MaxDelay      time.Duration `json:"max_delay"`
	BackoffFactor float64       `json:"backoff_factor"`
}

// PaginationConfig defines pagination settings
type PaginationConfig struct {
	PageSize   int    `json:"page_size"`
	Strategy   string `json:"strategy"` // "offset", "cursor", "keyset"
	SortColumn string `json:"sort_column"`
	SortOrder  string `json:"sort_order"`
}

// ExtractionMetrics tracks extraction performance
type ExtractionMetrics struct {
	RecordsExtracted  int64         `json:"records_extracted"`
	RecordsPerSecond  float64       `json:"records_per_second"`
	BytesTransferred  int64         `json:"bytes_transferred"`
	Duration          time.Duration `json:"duration"`
	ErrorCount        int           `json:"error_count"`
	RetryCount        int           `json:"retry_count"`
	PeakMemoryUsage   int64         `json:"peak_memory_usage"`
	NetworkLatencyP95 time.Duration `json:"network_latency_p95"`
}

// QueryResult represents query execution result
type QueryResult struct {
	Data          []map[string]interface{} `json:"data"`
	TotalCount    int64                    `json:"total_count"`
	HasMore       bool                     `json:"has_more"`
	NextBookmark  map[string]interface{}   `json:"next_bookmark"`
	ExecutionTime time.Duration            `json:"execution_time"`
}

// EntitySchema represents entity schema information
type EntitySchema struct {
	TableName   string                 `json:"table_name"`
	Columns     []ColumnDefinition     `json:"columns"`
	PrimaryKeys []string               `json:"primary_keys"`
	Indexes     []IndexDefinition      `json:"indexes"`
	Constraints []ConstraintDefinition `json:"constraints"`
}

// ColumnDefinition defines a database column
type ColumnDefinition struct {
	Name         string `json:"name"`
	DataType     string `json:"data_type"`
	IsNullable   bool   `json:"is_nullable"`
	DefaultValue string `json:"default_value"`
	MaxLength    int    `json:"max_length"`
}

// IndexDefinition defines a database index
type IndexDefinition struct {
	Name     string   `json:"name"`
	Columns  []string `json:"columns"`
	IsUnique bool     `json:"is_unique"`
}

// ConstraintDefinition defines a database constraint
type ConstraintDefinition struct {
	Name              string   `json:"name"`
	Type              string   `json:"type"`
	Columns           []string `json:"columns"`
	ReferencedTable   string   `json:"referenced_table"`
	ReferencedColumns []string `json:"referenced_columns"`
}

// ErrorResponse represents error handling response
type ErrorResponse struct {
	ShouldRetry  bool          `json:"should_retry"`
	RetryAfter   time.Duration `json:"retry_after"`
	ErrorCode    string        `json:"error_code"`
	ErrorMessage string        `json:"error_message"`
	CanContinue  bool          `json:"can_continue"`
}

// NewWMSExtractionCoordinator creates a new extraction coordinator
// SOLID: D - Dependency Inversion (depends on interfaces, not concrete types)
func NewWMSExtractionCoordinator(
	extractionID uuid.UUID,
	entityName string,
	extractionType entities.ExtractionType,
	client WMSClientInterface,
	stateManager ExtractionStateManagerInterface,
	metricService MetricServiceInterface,
	errorHandler ErrorHandlerInterface,
	config *ExtractionConfiguration,
) (*WMSExtractionCoordinator, error) {

	if extractionID == uuid.Nil {
		return nil, errors.New("extraction ID cannot be nil")
	}
	if entityName == "" {
		return nil, errors.New("entity name cannot be empty")
	}
	if client == nil {
		return nil, errors.New("client cannot be nil")
	}
	if stateManager == nil {
		return nil, errors.New("state manager cannot be nil")
	}
	if metricService == nil {
		return nil, errors.New("metric service cannot be nil")
	}
	if errorHandler == nil {
		return nil, errors.New("error handler cannot be nil")
	}
	if config == nil {
		return nil, errors.New("configuration cannot be nil")
	}

	coordinator := &WMSExtractionCoordinator{
		AggregateRoot:  domain.NewAggregateRoot(),
		ExtractionID:   extractionID,
		EntityName:     entityName,
		ExtractionType: extractionType,
		client:         client,
		stateManager:   stateManager,
		metricService:  metricService,
		errorHandler:   errorHandler,
		config:         config,
	}

	return coordinator, nil
}

// StartExtraction starts the extraction process
// SOLID: S - Single responsibility (only coordinates, doesn't do extraction)
func (c *WMSExtractionCoordinator) StartExtraction(ctx context.Context) error {
	// Validate client connection
	if err := c.client.ValidateConnection(); err != nil {
		return err
	}

	// Initialize metrics
	if err := c.metricService.StartExtraction(c.ExtractionID); err != nil {
		return err
	}

	// Initialize state
	state := &ExtractionState{
		Status:           ExtractionStatusRunning,
		Progress:         0.0,
		ProcessedRecords: 0,
		StartedAt:        time.Now(),
		UpdatedAt:        time.Now(),
	}

	if err := c.stateManager.SaveState(c.ExtractionID, state); err != nil {
		return err
	}

	// Note: Domain events would be added here in full implementation

	return nil
}

// GetExtractionStatus returns current extraction status
func (c *WMSExtractionCoordinator) GetExtractionStatus() (*ExtractionState, error) {
	return c.stateManager.LoadState(c.ExtractionID)
}

// UpdateProgress updates extraction progress
func (c *WMSExtractionCoordinator) UpdateProgress(processedRecords, totalRecords int64) error {
	// Calculate progress percentage
	_ = float64(processedRecords) / float64(totalRecords) * 100.0

	metrics := ExtractionMetrics{
		RecordsExtracted: processedRecords,
		// Other metrics would be calculated by metric service
	}

	return c.metricService.UpdateProgress(c.ExtractionID, metrics)
}

// CompleteExtraction marks extraction as completed
func (c *WMSExtractionCoordinator) CompleteExtraction() error {
	if err := c.metricService.FinishExtraction(c.ExtractionID, true); err != nil {
		return err
	}

	// Note: Domain events would be added here in full implementation

	return nil
}

// FailExtraction marks extraction as failed
func (c *WMSExtractionCoordinator) FailExtraction(reason error) error {
	if err := c.metricService.FinishExtraction(c.ExtractionID, false); err != nil {
		return err
	}

	// Handle error through error handler
	_, err := c.errorHandler.HandleError(c.ExtractionID, reason)
	if err != nil {
		return err
	}

	// Note: Domain events would be added here in full implementation

	return nil
}

// GetConfiguration returns extraction configuration
func (c *WMSExtractionCoordinator) GetConfiguration() *ExtractionConfiguration {
	return c.config
}

// UpdateConfiguration updates extraction configuration
func (c *WMSExtractionCoordinator) UpdateConfiguration(config *ExtractionConfiguration) error {
	if config == nil {
		return errors.New("configuration cannot be nil")
	}

	c.config = config
	// Note: Version increment and domain events would be added here in full implementation

	return nil
}
