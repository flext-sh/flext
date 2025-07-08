package entities

import (
	"context"
	"testing"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/wms/domain/value_objects"
	"github.com/google/uuid"
)

func TestNewWMSExtractor(t *testing.T) {
	// Create test client
	client, err := NewWMSClient("https://test-wms.oracle.com", "testuser", "testpass")
	if err != nil {
		t.Fatalf("Failed to create test client: %v", err)
	}

	// Create factories
	queryBuilderFactory := &mockQueryBuilderFactory{}
	errorHandlerFactory := &mockErrorHandlerFactory{}

	tests := []struct {
		name           string
		client         *WMSClient
		entityName     string
		extractionType ExtractionType
		wantErr        bool
	}{
		{
			name:           "Valid incremental extractor",
			client:         client,
			entityName:     "test_entity",
			extractionType: ExtractionTypeIncremental,
			wantErr:        false,
		},
		{
			name:           "Valid full extractor",
			client:         client,
			entityName:     "test_entity",
			extractionType: ExtractionTypeFull,
			wantErr:        false,
		},
		{
			name:           "Nil client",
			client:         nil,
			entityName:     "test_entity",
			extractionType: ExtractionTypeIncremental,
			wantErr:        true,
		},
		{
			name:           "Empty entity name",
			client:         client,
			entityName:     "",
			extractionType: ExtractionTypeIncremental,
			wantErr:        true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			extractor, err := NewWMSExtractor(tt.client, tt.entityName, tt.extractionType, queryBuilderFactory, errorHandlerFactory)

			if tt.wantErr {
				if err == nil {
					t.Errorf("NewWMSExtractor() expected error, got nil")
				}
				return
			}

			if err != nil {
				t.Errorf("NewWMSExtractor() unexpected error: %v", err)
				return
			}

			if extractor == nil {
				t.Errorf("NewWMSExtractor() returned nil extractor")
				return
			}

			// Verify extractor properties
			if extractor.EntityName != tt.entityName {
				t.Errorf("EntityName = %v, want %v", extractor.EntityName, tt.entityName)
			}

			if extractor.ExtractionType != tt.extractionType {
				t.Errorf("ExtractionType = %v, want %v", extractor.ExtractionType, tt.extractionType)
			}

			if extractor.Client != tt.client {
				t.Errorf("Client mismatch")
			}

			// Verify default configuration
			if extractor.Configuration == nil {
				t.Errorf("Configuration should not be nil")
			}

			if extractor.State == nil {
				t.Errorf("State should not be nil")
			}

			// Verify events were created
			events := extractor.GetUncommittedEvents()
			if len(events) == 0 {
				t.Errorf("Expected creation event to be emitted")
			}
		})
	}
}

func TestWMSExtractor_GetExtractionStatus(t *testing.T) {
	client, _ := NewWMSClient("https://test-wms.oracle.com", "testuser", "testpass")
	queryBuilderFactory := &mockQueryBuilderFactory{}
	errorHandlerFactory := &mockErrorHandlerFactory{}

	extractor, err := NewWMSExtractor(client, "test_entity", ExtractionTypeIncremental, queryBuilderFactory, errorHandlerFactory)
	if err != nil {
		t.Fatalf("Failed to create extractor: %v", err)
	}

	// Test initial status
	status := extractor.GetExtractionStatus()
	if status != ExtractionStatusPending {
		t.Errorf("Initial status = %v, want %v", status, ExtractionStatusPending)
	}

	// Test status change
	extractor.State.Status = ExtractionStatusRunning
	status = extractor.GetExtractionStatus()
	if status != ExtractionStatusRunning {
		t.Errorf("Status after change = %v, want %v", status, ExtractionStatusRunning)
	}
}

func TestWMSExtractor_GetExtractionProgress(t *testing.T) {
	client, _ := NewWMSClient("https://test-wms.oracle.com", "testuser", "testpass")
	queryBuilderFactory := &mockQueryBuilderFactory{}
	errorHandlerFactory := &mockErrorHandlerFactory{}

	extractor, err := NewWMSExtractor(client, "test_entity", ExtractionTypeIncremental, queryBuilderFactory, errorHandlerFactory)
	if err != nil {
		t.Fatalf("Failed to create extractor: %v", err)
	}

	progress := extractor.GetExtractionProgress()
	if progress.RecordsExtracted != 0 {
		t.Errorf("Initial RecordsExtracted = %v, want 0", progress.RecordsExtracted)
	}

	// Test progress update
	extractor.State.Progress.RecordsExtracted = 100
	extractor.State.Progress.BytesExtracted = 1024
	extractor.State.Progress.PagesProcessed = 1

	progress = extractor.GetExtractionProgress()
	if progress.RecordsExtracted != 100 {
		t.Errorf("RecordsExtracted = %v, want 100", progress.RecordsExtracted)
	}
	if progress.BytesExtracted != 1024 {
		t.Errorf("BytesExtracted = %v, want 1024", progress.BytesExtracted)
	}
	if progress.PagesProcessed != 1 {
		t.Errorf("PagesProcessed = %v, want 1", progress.PagesProcessed)
	}
}

func TestWMSExtractor_GetExtractionMetrics(t *testing.T) {
	client, _ := NewWMSClient("https://test-wms.oracle.com", "testuser", "testpass")
	queryBuilderFactory := &mockQueryBuilderFactory{}
	errorHandlerFactory := &mockErrorHandlerFactory{}

	extractor, err := NewWMSExtractor(client, "test_entity", ExtractionTypeIncremental, queryBuilderFactory, errorHandlerFactory)
	if err != nil {
		t.Fatalf("Failed to create extractor: %v", err)
	}

	metrics := extractor.GetExtractionMetrics()
	if metrics.TotalRecordsExtracted != 0 {
		t.Errorf("Initial TotalRecordsExtracted = %v, want 0", metrics.TotalRecordsExtracted)
	}

	// Test metrics update
	extractor.Metrics.TotalRecordsExtracted = 500
	extractor.Metrics.TotalBytesExtracted = 2048
	extractor.Metrics.TotalRequestsMade = 5

	metrics = extractor.GetExtractionMetrics()
	if metrics.TotalRecordsExtracted != 500 {
		t.Errorf("TotalRecordsExtracted = %v, want 500", metrics.TotalRecordsExtracted)
	}
	if metrics.TotalBytesExtracted != 2048 {
		t.Errorf("TotalBytesExtracted = %v, want 2048", metrics.TotalBytesExtracted)
	}
	if metrics.TotalRequestsMade != 5 {
		t.Errorf("TotalRequestsMade = %v, want 5", metrics.TotalRequestsMade)
	}
}

func TestWMSExtractor_StateCheckpoints(t *testing.T) {
	client, _ := NewWMSClient("https://test-wms.oracle.com", "testuser", "testpass")
	queryBuilderFactory := &mockQueryBuilderFactory{}
	errorHandlerFactory := &mockErrorHandlerFactory{}

	extractor, err := NewWMSExtractor(client, "test_entity", ExtractionTypeIncremental, queryBuilderFactory, errorHandlerFactory)
	if err != nil {
		t.Fatalf("Failed to create extractor: %v", err)
	}

	// Test creating checkpoint
	bookmark := map[string]interface{}{
		"timestamp": time.Now().Format(time.RFC3339),
		"record_id": "12345",
	}

	checkpoint := StateCheckpoint{
		ID:               uuid.New(),
		Timestamp:        time.Now(),
		Bookmark:         bookmark,
		RecordsExtracted: 100,
		BytesExtracted:   1024,
		Metadata:         map[string]interface{}{"page": 1},
	}

	extractor.State.StateCheckpoints = append(extractor.State.StateCheckpoints, checkpoint)

	// Verify checkpoint was added
	if len(extractor.State.StateCheckpoints) != 1 {
		t.Errorf("Expected 1 checkpoint, got %d", len(extractor.State.StateCheckpoints))
	}

	savedCheckpoint := extractor.State.StateCheckpoints[0]
	if savedCheckpoint.ID != checkpoint.ID {
		t.Errorf("Checkpoint ID mismatch")
	}
	if savedCheckpoint.RecordsExtracted != 100 {
		t.Errorf("Checkpoint RecordsExtracted = %v, want 100", savedCheckpoint.RecordsExtracted)
	}
}

func TestWMSExtractor_ErrorHandling(t *testing.T) {
	client, _ := NewWMSClient("https://test-wms.oracle.com", "testuser", "testpass")
	queryBuilderFactory := &mockQueryBuilderFactory{}
	errorHandlerFactory := &mockErrorHandlerFactory{}

	extractor, err := NewWMSExtractor(client, "test_entity", ExtractionTypeIncremental, queryBuilderFactory, errorHandlerFactory)
	if err != nil {
		t.Fatalf("Failed to create extractor: %v", err)
	}

	// Test error creation
	testErr := &ExtractionError{
		Message:   "Test error",
		Type:      ErrorTypeNetwork,
		Code:      "NETWORK_ERROR",
		Timestamp: time.Now(),
		Retryable: true,
	}

	extractor.State.LastError = testErr
	extractor.State.ErrorCount = 1

	// Verify error state
	if extractor.State.LastError == nil {
		t.Errorf("Expected error to be set")
	}
	if extractor.State.LastError.Message != "Test error" {
		t.Errorf("Error message = %v, want 'Test error'", extractor.State.LastError.Message)
	}
	if extractor.State.ErrorCount != 1 {
		t.Errorf("ErrorCount = %v, want 1", extractor.State.ErrorCount)
	}
}

func TestWMSExtractor_Configuration(t *testing.T) {
	client, _ := NewWMSClient("https://test-wms.oracle.com", "testuser", "testpass")
	queryBuilderFactory := &mockQueryBuilderFactory{}
	errorHandlerFactory := &mockErrorHandlerFactory{}

	extractor, err := NewWMSExtractor(client, "test_entity", ExtractionTypeIncremental, queryBuilderFactory, errorHandlerFactory)
	if err != nil {
		t.Fatalf("Failed to create extractor: %v", err)
	}

	// Test default configuration
	config := extractor.Configuration
	if config == nil {
		t.Fatalf("Configuration should not be nil")
	}

	if config.ReplicationKey != "mod_ts" {
		t.Errorf("Default ReplicationKey = %v, want 'mod_ts'", config.ReplicationKey)
	}

	if config.SafetyOverlapMinutes != 5 {
		t.Errorf("Default SafetyOverlapMinutes = %v, want 5", config.SafetyOverlapMinutes)
	}

	// Test configuration update
	config.ReplicationKey = "updated_at"
	config.SafetyOverlapMinutes = 10

	if extractor.Configuration.ReplicationKey != "updated_at" {
		t.Errorf("Updated ReplicationKey = %v, want 'updated_at'", extractor.Configuration.ReplicationKey)
	}
}

// Mock factories for testing
type mockQueryBuilderFactory struct{}

func (f *mockQueryBuilderFactory) CreateQueryBuilder(entity *WMSEntity) QueryBuilder {
	return &mockQueryBuilder{}
}

type mockQueryBuilder struct{}

func (qb *mockQueryBuilder) Where(field string, operator value_objects.FilterOperator, value interface{}) QueryBuilder {
	return qb
}
func (qb *mockQueryBuilder) WhereDate(field string, operator value_objects.FilterOperator, date time.Time) QueryBuilder {
	return qb
}
func (qb *mockQueryBuilder) WhereDateRange(field string, start, end time.Time) QueryBuilder {
	return qb
}
func (qb *mockQueryBuilder) WhereIncremental(replicationKey string, bookmark interface{}, safetyOverlap time.Duration) QueryBuilder {
	return qb
}
func (qb *mockQueryBuilder) OrderBy(field string, direction string) QueryBuilder { return qb }
func (qb *mockQueryBuilder) OrderByAsc(field string) QueryBuilder                { return qb }
func (qb *mockQueryBuilder) OrderByDesc(field string) QueryBuilder               { return qb }
func (qb *mockQueryBuilder) Select(fields ...string) QueryBuilder                { return qb }
func (qb *mockQueryBuilder) Limit(limit int) QueryBuilder                        { return qb }
func (qb *mockQueryBuilder) Offset(offset int64) QueryBuilder                    { return qb }
func (qb *mockQueryBuilder) Page(page, pageSize int) QueryBuilder                { return qb }
func (qb *mockQueryBuilder) Cursor(cursor string) QueryBuilder                   { return qb }
func (qb *mockQueryBuilder) Build() (string, error)                              { return "SELECT * FROM test_entity", nil }
func (qb *mockQueryBuilder) BuildURL(baseURL string) (string, error) {
	return baseURL + "/test_entity", nil
}
func (qb *mockQueryBuilder) GetFilters() map[string]interface{} { return map[string]interface{}{} }
func (qb *mockQueryBuilder) GetOrdering() []interface{}         { return []interface{}{} }
func (qb *mockQueryBuilder) Clone() QueryBuilder                { return &mockQueryBuilder{} }
func (qb *mockQueryBuilder) Reset() QueryBuilder                { return qb }
func (qb *mockQueryBuilder) Validate() error                    { return nil }

// Mock error handler factory for testing
type mockErrorHandlerFactory struct{}

func (f *mockErrorHandlerFactory) CreateErrorHandler() ErrorHandler {
	return &mockErrorHandler{}
}

type mockErrorHandler struct{}

func (h *mockErrorHandler) AnalyzeError(err error) ErrorAnalysis {
	return ErrorAnalysis{
		ErrorType:   ErrorTypeUnknown,
		IsRetryable: true,
		Category:    "test",
		Severity:    "low",
		Description: "Test error",
	}
}

func (h *mockErrorHandler) ShouldRetry(err error, attempt int) bool {
	return attempt < 3
}

func (h *mockErrorHandler) CreateExtractionError(err error, context map[string]interface{}) *ExtractionError {
	return &ExtractionError{
		Message:     err.Error(),
		Type:        ErrorTypeUnknown,
		Context:     context,
		Timestamp:   time.Now(),
		Retryable:   true,
		Recoverable: true,
	}
}

func (h *mockErrorHandler) UpdateClientMetrics(client *WMSClient, err error) {
	// Mock implementation
}

func (h *mockErrorHandler) ExecuteWithRetry(ctx context.Context, operation func() error) error {
	return operation()
}

func TestWMSExtractor_WithMockFactories(t *testing.T) {
	client, _ := NewWMSClient("https://test-wms.oracle.com", "testuser", "testpass")
	queryBuilderFactory := &mockQueryBuilderFactory{}
	errorHandlerFactory := &mockErrorHandlerFactory{}

	extractor, err := NewWMSExtractor(client, "test_entity", ExtractionTypeIncremental, queryBuilderFactory, errorHandlerFactory)
	if err != nil {
		t.Fatalf("Failed to create extractor with mock factories: %v", err)
	}

	if extractor == nil {
		t.Errorf("Extractor should not be nil")
	}

	// Test that the factories are properly set
	if extractor.queryBuilderFactory == nil {
		t.Errorf("QueryBuilderFactory should not be nil")
	}

	if extractor.errorHandler == nil {
		t.Errorf("ErrorHandler should not be nil")
	}
}
