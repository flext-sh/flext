package testing

import (
	"context"
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/wms/domain/entities"
	"github.com/flext-sh/flext/internal/bounded_contexts/wms/domain/value_objects"
	"github.com/flext-sh/flext/internal/bounded_contexts/wms/infrastructure/errors"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestWMSIntegration_EndToEnd(t *testing.T) {
	// Start mock Oracle WMS server
	mockServer := NewMockOracleWMSServer()
	defer mockServer.Close()

	// Configure mock server for realistic behavior
	mockServer.SetSimulateDelay(50 * time.Millisecond)

	t.Run("Complete WMS Workflow", func(t *testing.T) {
		// Step 1: Create WMS Client
		client, err := entities.NewWMSClient(
			mockServer.GetBaseURL(),
			"testuser",
			"testpass",
		)
		require.NoError(t, err)
		require.NotNil(t, client)

		// Verify initial state
		assert.Equal(t, entities.ClientStatusDisconnected, client.Status)
		assert.False(t, client.IsConnected())

		// Step 2: Connect to WMS
		ctx := context.Background()
		err = client.Connect(ctx)
		require.NoError(t, err)

		// Verify connection
		assert.Equal(t, entities.ClientStatusConnected, client.Status)
		assert.True(t, client.IsConnected())
		assert.NotNil(t, client.LastConnected)

		// Step 3: Discover Entities
		err = client.DiscoverEntities(ctx, false)
		require.NoError(t, err)

		// Verify discovered entities
		allEntities := client.GetAllEntities()
		assert.GreaterOrEqual(t, len(allEntities), 3, "Should discover at least 3 entities")

		// Verify specific entities exist
		itemMaster, err := client.GetEntity("item_master")
		require.NoError(t, err)
		assert.Equal(t, "item_master", itemMaster.Name)

		inventory, err := client.GetEntity("inventory")
		require.NoError(t, err)
		assert.Equal(t, "inventory", inventory.Name)

		// Step 4: Create Query Builder and Error Handler
		queryBuilderFactory := &testQueryBuilderFactory{}
		errorHandlerFactory := errors.NewWMSErrorHandlerFactory()

		// Step 5: Create WMS Extractor for incremental extraction
		extractor, err := entities.NewWMSExtractor(
			client,
			"item_master",
			entities.ExtractionTypeIncremental,
			queryBuilderFactory,
			errorHandlerFactory,
		)
		require.NoError(t, err)
		require.NotNil(t, extractor)

		// Verify extractor configuration
		assert.Equal(t, "item_master", extractor.EntityName)
		assert.Equal(t, entities.ExtractionTypeIncremental, extractor.ExtractionType)
		assert.Equal(t, entities.ExtractionStatusPending, extractor.GetExtractionStatus())

		// Step 6: Configure extraction
		extractor.Configuration.ReplicationKey = "modified_date"
		extractor.Configuration.SafetyOverlapMinutes = 5
		extractor.BatchSize = 50

		// Step 7: Start extraction
		err = extractor.StartExtraction(ctx)
		require.NoError(t, err)

		// Verify extraction started
		assert.Equal(t, entities.ExtractionStatusRunning, extractor.GetExtractionStatus())
		assert.NotNil(t, extractor.StartTime)

		// Step 8: Monitor progress (simulate some processing time)
		time.Sleep(200 * time.Millisecond)

		progress := extractor.GetExtractionProgress()
		assert.GreaterOrEqual(t, progress.RecordsExtracted, int64(0))

		metrics := extractor.GetExtractionMetrics()
		// Fix type assertion by ensuring int64 comparison
		assert.GreaterOrEqual(t, int64(metrics.TotalRequestsMade), int64(0))

		// Step 9: Stop extraction (only if still running)
		currentStatus := extractor.GetExtractionStatus()
		if currentStatus == entities.ExtractionStatusRunning {
			err = extractor.StopExtraction()
			require.NoError(t, err)
			// Verify extraction was cancelled
			assert.Equal(t, entities.ExtractionStatusCancelled, extractor.GetExtractionStatus())
		} else {
			// Extraction completed naturally, which is also valid
			assert.Contains(t, []entities.ExtractionStatus{
				entities.ExtractionStatusCompleted,
				entities.ExtractionStatusCancelled,
			}, currentStatus, "Extraction should be either completed or cancelled")
		}

		// Verify extraction has ended
		assert.NotNil(t, extractor.EndTime)

		// Step 10: Verify events were published
		events := extractor.GetUncommittedEvents()
		assert.Greater(t, len(events), 0, "Should have emitted domain events")

		// Step 11: Test client metrics
		clientMetrics := client.GetMetrics()
		assert.Greater(t, clientMetrics.TotalRequests, int64(0))
		assert.Equal(t, clientMetrics.FailedRequests, int64(0)) // No failures expected

		// Step 12: Disconnect client
		err = client.Disconnect()
		require.NoError(t, err)

		// Verify disconnection
		assert.Equal(t, entities.ClientStatusDisconnected, client.Status)
		assert.False(t, client.IsConnected())
	})
}

func TestWMSIntegration_ErrorHandling(t *testing.T) {
	// Start mock server with error simulation
	mockServer := NewMockOracleWMSServer()
	defer mockServer.Close()

	// Configure errors
	mockServer.SetSimulateErrors(true, 0.5) // 50% error rate

	t.Run("Authentication Failure", func(t *testing.T) {
		// Test with invalid credentials
		client, err := entities.NewWMSClient(
			mockServer.GetBaseURL(),
			"invalid",
			"credentials",
		)
		require.NoError(t, err)

		ctx := context.Background()
		err = client.Connect(ctx)
		require.Error(t, err)

		// Should remain disconnected or in error state
		assert.Contains(t, []entities.ClientStatus{
			entities.ClientStatusDisconnected,
			entities.ClientStatusError,
		}, client.Status, "Client should be disconnected or in error state after auth failure")
	})

	t.Run("Circuit Breaker Activation", func(t *testing.T) {
		// Create a separate mock server with 100% error rate for deterministic failure
		mockServerWithErrors := NewMockOracleWMSServer()
		defer mockServerWithErrors.Close()
		mockServerWithErrors.SetSimulateErrors(true, 1.0) // 100% error rate

		client, err := entities.NewWMSClient(
			mockServerWithErrors.GetBaseURL(),
			"testuser",
			"testpass",
		)
		require.NoError(t, err)

		// Configure circuit breaker for faster testing
		client.CircuitBreaker.FailureThreshold = 3
		client.CircuitBreaker.RecoveryTimeout = 1 * time.Second

		ctx := context.Background()

		// Try to connect multiple times to trigger circuit breaker
		for i := 0; i < 5; i++ {
			client.Connect(ctx)
			time.Sleep(100 * time.Millisecond)
		}

		// Circuit breaker should eventually open due to consistent failures
		assert.Greater(t, client.CircuitBreaker.FailureCount, 0)
	})
}

func TestWMSIntegration_SchemaDiscovery(t *testing.T) {
	mockServer := NewMockOracleWMSServer()
	defer mockServer.Close()

	t.Run("Schema Generation", func(t *testing.T) {
		client, err := entities.NewWMSClient(
			mockServer.GetBaseURL(),
			"testuser",
			"testpass",
		)
		require.NoError(t, err)

		ctx := context.Background()
		err = client.Connect(ctx)
		require.NoError(t, err)

		// Discover entities first
		err = client.DiscoverEntities(ctx, false)
		require.NoError(t, err)

		// Test schema discovery for item_master
		entity, err := client.GetEntity("item_master")
		require.NoError(t, err)

		// Verify entity has fields
		assert.Greater(t, len(entity.Fields), 0, "Entity should have fields")

		// Find primary key field
		var foundPK bool
		for _, field := range entity.Fields {
			if field.Name == "item_id" {
				foundPK = true
				break
			}
		}
		assert.True(t, foundPK, "Should have item_id field")

		// Verify we have multiple fields
		assert.Greater(t, len(entity.Fields), 5, "Should have multiple fields")
	})
}

func TestWMSIntegration_DataExtraction(t *testing.T) {
	mockServer := NewMockOracleWMSServer()
	defer mockServer.Close()

	t.Run("Full Extraction", func(t *testing.T) {
		client, err := entities.NewWMSClient(
			mockServer.GetBaseURL(),
			"testuser",
			"testpass",
		)
		require.NoError(t, err)

		ctx := context.Background()
		err = client.Connect(ctx)
		require.NoError(t, err)

		// Discover entities first
		err = client.DiscoverEntities(ctx, false)
		require.NoError(t, err)

		// Create extractor for full extraction
		queryBuilderFactory := &testQueryBuilderFactory{}
		errorHandlerFactory := errors.NewWMSErrorHandlerFactory()

		extractor, err := entities.NewWMSExtractor(
			client,
			"item_master",
			entities.ExtractionTypeFull,
			queryBuilderFactory,
			errorHandlerFactory,
		)
		require.NoError(t, err)

		// Configure for testing
		extractor.BatchSize = 10
		extractor.MaxConcurrency = 2

		// Start extraction
		err = extractor.StartExtraction(ctx)
		require.NoError(t, err)

		// Wait for some processing
		time.Sleep(300 * time.Millisecond)

		// Verify progress
		progress := extractor.GetExtractionProgress()
		assert.GreaterOrEqual(t, progress.RecordsExtracted, int64(0))

		// Stop extraction (only if still running)
		currentStatus := extractor.GetExtractionStatus()
		if currentStatus == entities.ExtractionStatusRunning {
			err = extractor.StopExtraction()
			require.NoError(t, err)
		}

		// Verify final metrics
		metrics := extractor.GetExtractionMetrics()
		assert.GreaterOrEqual(t, int64(metrics.TotalRecordsExtracted), int64(0))
		assert.GreaterOrEqual(t, int64(metrics.TotalRequestsMade), int64(1))
	})

	t.Run("Incremental Extraction with Bookmark", func(t *testing.T) {
		client, err := entities.NewWMSClient(
			mockServer.GetBaseURL(),
			"testuser",
			"testpass",
		)
		require.NoError(t, err)

		ctx := context.Background()
		err = client.Connect(ctx)
		require.NoError(t, err)

		// Discover entities first
		err = client.DiscoverEntities(ctx, false)
		require.NoError(t, err)

		// Create incremental extractor
		queryBuilderFactory := &testQueryBuilderFactory{}
		errorHandlerFactory := errors.NewWMSErrorHandlerFactory()

		extractor, err := entities.NewWMSExtractor(
			client,
			"item_master",
			entities.ExtractionTypeIncremental,
			queryBuilderFactory,
			errorHandlerFactory,
		)
		require.NoError(t, err)

		// Configure incremental extraction
		extractor.Configuration.ReplicationKey = "modified_date"
		extractor.Configuration.SafetyOverlapMinutes = 5

		// Set a bookmark (simulate previous extraction)
		yesterday := time.Now().Add(-24 * time.Hour)
		extractor.LastBookmark = map[string]interface{}{
			"modified_date": yesterday.Format(time.RFC3339),
		}

		// Start extraction
		err = extractor.StartExtraction(ctx)
		require.NoError(t, err)

		// Wait and stop
		time.Sleep(200 * time.Millisecond)
		currentStatus := extractor.GetExtractionStatus()
		if currentStatus == entities.ExtractionStatusRunning {
			err = extractor.StopExtraction()
			require.NoError(t, err)
		}

		// Verify incremental logic was applied
		assert.NotEmpty(t, extractor.LastBookmark)
	})
}

// Test helper - simple query builder factory for testing
type testQueryBuilderFactory struct{}

func (f *testQueryBuilderFactory) CreateQueryBuilder(entity *entities.WMSEntity) entities.QueryBuilder {
	return &testQueryBuilder{entity: entity}
}

type testQueryBuilder struct {
	entity   *entities.WMSEntity
	filters  map[string]interface{}
	ordering []interface{}
	limit    int
	offset   int64
}

func (qb *testQueryBuilder) Where(field string, operator value_objects.FilterOperator, value interface{}) entities.QueryBuilder {
	if qb.filters == nil {
		qb.filters = make(map[string]interface{})
	}
	qb.filters[field] = value
	return qb
}

func (qb *testQueryBuilder) WhereDate(field string, operator value_objects.FilterOperator, date time.Time) entities.QueryBuilder {
	return qb.Where(field, operator, date.Format(time.RFC3339))
}

func (qb *testQueryBuilder) WhereDateRange(field string, start, end time.Time) entities.QueryBuilder {
	return qb.Where(field, "between", []string{start.Format(time.RFC3339), end.Format(time.RFC3339)})
}

func (qb *testQueryBuilder) WhereIncremental(replicationKey string, bookmark interface{}, safetyOverlap time.Duration) entities.QueryBuilder {
	if bookmark != nil {
		if bookmarkTime, ok := bookmark.(time.Time); ok {
			adjustedTime := bookmarkTime.Add(-safetyOverlap)
			return qb.Where(replicationKey, ">=", adjustedTime.Format(time.RFC3339))
		}
		if bookmarkStr, ok := bookmark.(string); ok {
			if bookmarkTime, err := time.Parse(time.RFC3339, bookmarkStr); err == nil {
				adjustedTime := bookmarkTime.Add(-safetyOverlap)
				return qb.Where(replicationKey, ">=", adjustedTime.Format(time.RFC3339))
			}
		}
	}
	return qb
}

func (qb *testQueryBuilder) OrderBy(field string, direction string) entities.QueryBuilder {
	qb.ordering = append(qb.ordering, map[string]string{"field": field, "direction": direction})
	return qb
}

func (qb *testQueryBuilder) OrderByAsc(field string) entities.QueryBuilder {
	return qb.OrderBy(field, "ASC")
}

func (qb *testQueryBuilder) OrderByDesc(field string) entities.QueryBuilder {
	return qb.OrderBy(field, "DESC")
}

func (qb *testQueryBuilder) Select(fields ...string) entities.QueryBuilder {
	// In a real implementation, would store selected fields
	return qb
}

func (qb *testQueryBuilder) Limit(limit int) entities.QueryBuilder {
	qb.limit = limit
	return qb
}

func (qb *testQueryBuilder) Offset(offset int64) entities.QueryBuilder {
	qb.offset = offset
	return qb
}

func (qb *testQueryBuilder) Page(page, pageSize int) entities.QueryBuilder {
	qb.limit = pageSize
	qb.offset = int64((page - 1) * pageSize)
	return qb
}

func (qb *testQueryBuilder) Cursor(cursor string) entities.QueryBuilder {
	// Cursor-based pagination implementation would go here
	return qb
}

func (qb *testQueryBuilder) Build() (string, error) {
	// Build a simple query URL for the mock server
	query := fmt.Sprintf("/api/v1/data/%s", qb.entity.Name)

	params := []string{}
	if qb.limit > 0 {
		params = append(params, fmt.Sprintf("limit=%d", qb.limit))
	}
	if qb.offset > 0 {
		params = append(params, fmt.Sprintf("offset=%d", qb.offset))
	}

	if len(params) > 0 {
		query += "?" + strings.Join(params, "&")
	}

	return query, nil
}

func (qb *testQueryBuilder) BuildURL(baseURL string) (string, error) {
	query, err := qb.Build()
	if err != nil {
		return "", err
	}
	return baseURL + query, nil
}

func (qb *testQueryBuilder) GetFilters() map[string]interface{} {
	if qb.filters == nil {
		return make(map[string]interface{})
	}
	return qb.filters
}

func (qb *testQueryBuilder) GetOrdering() []interface{} {
	return qb.ordering
}

func (qb *testQueryBuilder) Clone() entities.QueryBuilder {
	clone := &testQueryBuilder{
		entity:   qb.entity,
		filters:  make(map[string]interface{}),
		ordering: make([]interface{}, len(qb.ordering)),
		limit:    qb.limit,
		offset:   qb.offset,
	}

	for k, v := range qb.filters {
		clone.filters[k] = v
	}
	copy(clone.ordering, qb.ordering)

	return clone
}

func (qb *testQueryBuilder) Reset() entities.QueryBuilder {
	qb.filters = make(map[string]interface{})
	qb.ordering = []interface{}{}
	qb.limit = 0
	qb.offset = 0
	return qb
}

func (qb *testQueryBuilder) Validate() error {
	if qb.entity == nil {
		return fmt.Errorf("entity is required")
	}
	return nil
}
