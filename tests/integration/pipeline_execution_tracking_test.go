package integration

import (
	"context"
	"testing"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/commands"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/services"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/infrastructure/adapters"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/infrastructure/factory"
	"github.com/flext-sh/flext/internal/infrastructure/database"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestPipelineExecutionTracking(t *testing.T) {
	// Setup test database and logger
	db := setupTestDatabase(t)
	logger := logging.NewConsoleLogger()

	// Create execution stats factory
	factory := factory.NewExecutionStatsFactory(db, logger)

	// Create mock pipeline repository (you'll need to implement this)
	pipelineRepo := &mockPipelineRepository{}

	// Create execution stats service
	executionStatsService, err := factory.CreateExecutionStatsService(context.Background(), pipelineRepo)
	require.NoError(t, err)

	// Create test pipeline
	pipelineID := uuid.New()
	pipeline := &entities.Pipeline{
		ID:       pipelineID,
		Name:     "Test Pipeline",
		IsActive: true,
		Status:   entities.PipelineStatusActive,
	}
	pipelineRepo.SavePipeline(pipeline)

	t.Run("Record and retrieve execution stats", func(t *testing.T) {
		// Record some test executions
		executions := createTestExecutions(pipelineID, 10)
		
		for _, exec := range executions {
			err := executionStatsService.RecordExecution(context.Background(), exec)
			assert.NoError(t, err)
		}

		// Get execution metrics
		metrics, err := executionStatsService.GetPipelineExecutionMetrics(context.Background(), pipelineID)
		require.NoError(t, err)

		// Verify metrics
		assert.Equal(t, 10, metrics.ExecutionCount)
		assert.True(t, metrics.SuccessCount > 0)
		assert.True(t, metrics.FailureCount >= 0)
		assert.NotNil(t, metrics.LastExecution)
		assert.True(t, metrics.ExecutionSuccessRate >= 0 && metrics.ExecutionSuccessRate <= 100)
	})

	t.Run("Pipeline status command with execution data", func(t *testing.T) {
		// Create status handler with execution stats service
		statusHandler := commands.NewGetPipelineStatusHandler(pipelineRepo, executionStatsService)

		// Execute status command
		result, err := statusHandler.Handle(context.Background(), commands.GetPipelineStatusCommand{
			PipelineID: pipelineID,
		})
		require.NoError(t, err)

		// Verify execution counts are populated (not zero)
		assert.True(t, result.ExecutionCount > 0, "ExecutionCount should be populated")
		assert.True(t, result.SuccessCount >= 0, "SuccessCount should be populated")
		assert.True(t, result.FailureCount >= 0, "FailureCount should be populated")

		// Verify metrics contain execution data
		assert.Contains(t, result.Metrics, "execution_success_rate")
		
		// Check if advanced metrics are present
		if result.Metrics["last_execution_duration"] != nil {
			assert.NotEmpty(t, result.Metrics["last_execution_duration"])
		}
		
		if result.Metrics["average_execution_time"] != nil {
			assert.NotEmpty(t, result.Metrics["average_execution_time"])
		}
	})

	t.Run("Execution trend calculation", func(t *testing.T) {
		// Get execution metrics with trend data
		metrics, err := executionStatsService.GetPipelineExecutionMetrics(context.Background(), pipelineID)
		require.NoError(t, err)

		// Verify trend data is generated
		assert.True(t, len(metrics.ExecutionTrend) > 0, "Should have execution trend data")
		
		for _, point := range metrics.ExecutionTrend {
			assert.True(t, point.Executions > 0, "Each trend point should have executions")
			assert.True(t, point.SuccessRate >= 0 && point.SuccessRate <= 100, "Success rate should be valid percentage")
		}
	})

	t.Run("Global execution statistics", func(t *testing.T) {
		// Get global stats
		globalStats, err := executionStatsService.GetGlobalExecutionStats(context.Background())
		require.NoError(t, err)

		// Verify global stats structure
		assert.Contains(t, globalStats, "total")
		assert.Contains(t, globalStats, "successful")
		assert.Contains(t, globalStats, "success_rate")

		// Verify values are reasonable
		total, ok := globalStats["total"].(int)
		assert.True(t, ok, "Total should be an integer")
		assert.True(t, total > 0, "Should have recorded executions")
	})
}

// Helper functions

func setupTestDatabase(t *testing.T) *database.Database {
	// Create in-memory SQLite database for testing
	db, err := database.NewDatabase(":memory:")
	require.NoError(t, err)
	return db
}

func createTestExecutions(pipelineID uuid.UUID, count int) []*ports.ExecutionRecord {
	executions := make([]*ports.ExecutionRecord, count)
	
	for i := 0; i < count; i++ {
		startTime := time.Now().Add(-time.Duration(count-i) * time.Hour)
		endTime := startTime.Add(time.Duration(10+i*5) * time.Minute)
		
		success := i%3 != 0 // Make roughly 2/3 successful
		status := "completed"
		errorMsg := ""
		
		if !success {
			status = "failed"
			errorMsg = "Test error message"
		}

		executions[i] = &ports.ExecutionRecord{
			ID:          uuid.New(),
			PipelineID:  pipelineID,
			Status:      status,
			StartedAt:   &startTime,
			CompletedAt: &endTime,
			Duration:    endTime.Sub(startTime),
			Success:     success,
			ErrorMessage: errorMsg,
			Logs:        []ports.ExecutionLog{
				{
					Timestamp: startTime,
					Level:     "info",
					Message:   "Execution started",
				},
				{
					Timestamp: endTime,
					Level:     "info",
					Message:   "Execution completed",
				},
			},
			Metrics:   make(map[string]interface{}),
			CreatedAt: startTime,
		}
	}
	
	return executions
}

// Mock pipeline repository for testing
type mockPipelineRepository struct {
	pipelines map[uuid.UUID]*entities.Pipeline
}

func (m *mockPipelineRepository) SavePipeline(pipeline *entities.Pipeline) {
	if m.pipelines == nil {
		m.pipelines = make(map[uuid.UUID]*entities.Pipeline)
	}
	m.pipelines[pipeline.ID] = pipeline
}

func (m *mockPipelineRepository) GetByID(ctx context.Context, id uuid.UUID) (*entities.Pipeline, error) {
	if pipeline, exists := m.pipelines[id]; exists {
		return pipeline, nil
	}
	return nil, nil
}

// Implement other required repository methods as stubs...
// (Add implementation as needed for the test)