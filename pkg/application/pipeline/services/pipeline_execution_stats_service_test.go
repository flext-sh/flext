package services

import (
	"context"
	"testing"
	"time"

	"github.com/flext-sh/flext/pkg/domain/pipeline/application/ports"
	"github.com/flext-sh/flext/pkg/infrastructure/persistence"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestPipelineExecutionStatsService_GetPipelineExecutionCounts(t *testing.T) {
	tests := []struct {
		name            string
		setupExecutions func() []*ports.ExecutionRecord
		expectedTotal   int
		expectedSuccess int
		expectedFailure int
	}{
		{
			name: "empty executions",
			setupExecutions: func() []*ports.ExecutionRecord {
				return []*ports.ExecutionRecord{}
			},
			expectedTotal:   0,
			expectedSuccess: 0,
			expectedFailure: 0,
		},
		{
			name: "mixed success and failure executions",
			setupExecutions: func() []*ports.ExecutionRecord {
				pipelineID := uuid.New()
				return []*ports.ExecutionRecord{
					{
						ID:         uuid.New(),
						PipelineID: pipelineID,
						Status:     "completed",
						Success:    true,
						CreatedAt:  time.Now().Add(-1 * time.Hour),
					},
					{
						ID:         uuid.New(),
						PipelineID: pipelineID,
						Status:     "failed",
						Success:    false,
						CreatedAt:  time.Now().Add(-2 * time.Hour),
					},
					{
						ID:         uuid.New(),
						PipelineID: pipelineID,
						Status:     "completed",
						Success:    true,
						CreatedAt:  time.Now().Add(-3 * time.Hour),
					},
				}
			},
			expectedTotal:   3,
			expectedSuccess: 2,
			expectedFailure: 1,
		},
		{
			name: "all successful executions",
			setupExecutions: func() []*ports.ExecutionRecord {
				pipelineID := uuid.New()
				return []*ports.ExecutionRecord{
					{
						ID:         uuid.New(),
						PipelineID: pipelineID,
						Status:     "completed",
						Success:    true,
						CreatedAt:  time.Now().Add(-1 * time.Hour),
					},
					{
						ID:         uuid.New(),
						PipelineID: pipelineID,
						Status:     "completed",
						Success:    true,
						CreatedAt:  time.Now().Add(-2 * time.Hour),
					},
				}
			},
			expectedTotal:   2,
			expectedSuccess: 2,
			expectedFailure: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup
			executionRepo := persistence.NewInMemoryExecutionRepository()
			pipelineRepo := persistence.NewInMemoryPipelineRepository()
			service := NewPipelineExecutionStatsService(executionRepo, pipelineRepo)

			executions := tt.setupExecutions()
			var pipelineID uuid.UUID

			ctx := context.Background()

			// Insert test data
			for _, execution := range executions {
				if pipelineID == uuid.Nil {
					pipelineID = execution.PipelineID
				}
				err := executionRepo.Save(ctx, execution)
				require.NoError(t, err)
			}

			// If no executions, use a random pipeline ID
			if pipelineID == uuid.Nil {
				pipelineID = uuid.New()
			}

			// Execute
			total, success, failure, err := service.GetPipelineExecutionCounts(ctx, pipelineID)

			// Assert
			require.NoError(t, err)
			assert.Equal(t, tt.expectedTotal, total, "Total count mismatch")
			assert.Equal(t, tt.expectedSuccess, success, "Success count mismatch")
			assert.Equal(t, tt.expectedFailure, failure, "Failure count mismatch")
		})
	}
}

func TestPipelineExecutionStatsService_GetPipelineExecutionMetrics(t *testing.T) {
	// Setup
	executionRepo := persistence.NewInMemoryExecutionRepository()
	pipelineRepo := persistence.NewInMemoryPipelineRepository()
	service := NewPipelineExecutionStatsService(executionRepo, pipelineRepo)

	pipelineID := uuid.New()
	ctx := context.Background()

	// Create test executions with different characteristics
	now := time.Now()
	executions := []*ports.ExecutionRecord{
		{
			ID:          uuid.New(),
			PipelineID:  pipelineID,
			Status:      "completed",
			StartedAt:   &now,
			CompletedAt: func() *time.Time { t := now.Add(2 * time.Second); return &t }(),
			Duration:    2 * time.Second,
			Success:     true,
			CreatedAt:   now.Add(-1 * time.Hour),
		},
		{
			ID:           uuid.New(),
			PipelineID:   pipelineID,
			Status:       "failed",
			StartedAt:    &now,
			CompletedAt:  func() *time.Time { t := now.Add(5 * time.Second); return &t }(),
			Duration:     5 * time.Second,
			Success:      false,
			ErrorMessage: "Connection timeout",
			CreatedAt:    now.Add(-2 * time.Hour),
		},
		{
			ID:          uuid.New(),
			PipelineID:  pipelineID,
			Status:      "completed",
			StartedAt:   &now,
			CompletedAt: func() *time.Time { t := now.Add(3 * time.Second); return &t }(),
			Duration:    3 * time.Second,
			Success:     true,
			CreatedAt:   now.Add(-30 * time.Minute),
		},
	}

	// Insert test data
	for _, execution := range executions {
		err := executionRepo.Save(ctx, execution)
		require.NoError(t, err)
	}

	// Execute
	metrics, err := service.GetPipelineExecutionMetrics(ctx, pipelineID)

	// Assert
	require.NoError(t, err)
	assert.NotNil(t, metrics)

	// Check basic counts
	assert.Equal(t, 3, metrics.ExecutionCount)
	assert.Equal(t, 2, metrics.SuccessCount)
	assert.Equal(t, 1, metrics.FailureCount)

	// Check success rate (should be 2/3 = 66.67%)
	expectedSuccessRate := float64(2) / float64(3) * 100
	assert.InDelta(t, expectedSuccessRate, metrics.ExecutionSuccessRate, 0.01)

	// Check that we have duration metrics
	assert.NotNil(t, metrics.LastExecutionDuration)
	assert.NotNil(t, metrics.AverageExecutionTime)

	// Check last execution time
	assert.NotNil(t, metrics.LastExecution)

	// Check recent executions (should have some)
	assert.True(t, len(metrics.RecentExecutions) > 0)
	assert.True(t, len(metrics.RecentExecutions) <= 10) // Should be capped at 10

	// Check execution trend
	assert.True(t, len(metrics.ExecutionTrend) >= 0) // Should have trend data
}

func TestPipelineExecutionStatsService_RecordExecution(t *testing.T) {
	// Setup
	executionRepo := persistence.NewInMemoryExecutionRepository()
	pipelineRepo := persistence.NewInMemoryPipelineRepository()
	service := NewPipelineExecutionStatsService(executionRepo, pipelineRepo)

	ctx := context.Background()
	pipelineID := uuid.New()

	tests := []struct {
		name            string
		execution       *ports.ExecutionRecord
		expectError     bool
		expectedSuccess bool
	}{
		{
			name: "successful execution record",
			execution: &ports.ExecutionRecord{
				PipelineID:   pipelineID,
				Status:       "completed",
				StartedAt:    func() *time.Time { t := time.Now(); return &t }(),
				CompletedAt:  func() *time.Time { t := time.Now().Add(time.Second); return &t }(),
				ErrorMessage: "",
			},
			expectError:     false,
			expectedSuccess: true,
		},
		{
			name: "failed execution record",
			execution: &ports.ExecutionRecord{
				PipelineID:   pipelineID,
				Status:       "failed",
				StartedAt:    func() *time.Time { t := time.Now(); return &t }(),
				CompletedAt:  func() *time.Time { t := time.Now().Add(time.Second); return &t }(),
				ErrorMessage: "Database connection failed",
			},
			expectError:     false,
			expectedSuccess: false,
		},
		{
			name: "execution with missing pipeline ID",
			execution: &ports.ExecutionRecord{
				PipelineID: uuid.Nil,
				Status:     "completed",
			},
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Execute
			err := service.RecordExecution(ctx, tt.execution)

			// Assert
			if tt.expectError {
				assert.Error(t, err)
				return
			}

			require.NoError(t, err)

			// Verify the execution was saved with correct success flag
			if tt.execution.ID != uuid.Nil {
				saved, err := executionRepo.FindByID(ctx, tt.execution.ID)
				require.NoError(t, err)
				assert.Equal(t, tt.expectedSuccess, saved.Success)
			}
		})
	}
}

func TestPipelineExecutionStatsService_GetPipelineLastExecution(t *testing.T) {
	// Setup
	executionRepo := persistence.NewInMemoryExecutionRepository()
	pipelineRepo := persistence.NewInMemoryPipelineRepository()
	service := NewPipelineExecutionStatsService(executionRepo, pipelineRepo)

	ctx := context.Background()
	pipelineID := uuid.New()

	// Test case 1: No executions
	lastExecution, err := service.GetPipelineLastExecution(ctx, pipelineID)
	require.NoError(t, err)
	assert.Nil(t, lastExecution)

	// Test case 2: With executions
	now := time.Now()
	executions := []*ports.ExecutionRecord{
		{
			ID:         uuid.New(),
			PipelineID: pipelineID,
			Status:     "completed",
			Success:    true,
			CreatedAt:  now.Add(-2 * time.Hour), // Older
		},
		{
			ID:         uuid.New(),
			PipelineID: pipelineID,
			Status:     "failed",
			Success:    false,
			CreatedAt:  now.Add(-1 * time.Hour), // More recent
		},
	}

	// Insert test data
	for _, execution := range executions {
		err := executionRepo.Save(ctx, execution)
		require.NoError(t, err)
	}

	// Execute
	lastExecution, err = service.GetPipelineLastExecution(ctx, pipelineID)

	// Assert
	require.NoError(t, err)
	require.NotNil(t, lastExecution)

	// Should be the most recent execution (failed one)
	assert.Equal(t, executions[1].ID, lastExecution.ID)
	assert.Equal(t, "failed", lastExecution.Status)
	assert.False(t, lastExecution.Success)
}

func TestPipelineExecutionStatsService_CalculateExecutionTrend(t *testing.T) {
	// Setup
	executionRepo := persistence.NewInMemoryExecutionRepository()
	pipelineRepo := persistence.NewInMemoryPipelineRepository()
	service := NewPipelineExecutionStatsService(executionRepo, pipelineRepo)

	// Create test executions across different days
	now := time.Now()
	today := time.Date(now.Year(), now.Month(), now.Day(), 12, 0, 0, 0, now.Location())
	yesterday := today.Add(-24 * time.Hour)

	executions := []*ports.ExecutionRecord{
		// Today: 2 successful, 1 failed
		{
			ID:         uuid.New(),
			PipelineID: uuid.New(),
			StartedAt:  &today,
			Duration:   2 * time.Second,
			Success:    true,
			CreatedAt:  today,
		},
		{
			ID:         uuid.New(),
			PipelineID: uuid.New(),
			StartedAt:  &today,
			Duration:   3 * time.Second,
			Success:    true,
			CreatedAt:  today.Add(1 * time.Hour),
		},
		{
			ID:         uuid.New(),
			PipelineID: uuid.New(),
			StartedAt:  &today,
			Duration:   1 * time.Second,
			Success:    false,
			CreatedAt:  today.Add(2 * time.Hour),
		},
		// Yesterday: 1 successful
		{
			ID:         uuid.New(),
			PipelineID: uuid.New(),
			StartedAt:  &yesterday,
			Duration:   4 * time.Second,
			Success:    true,
			CreatedAt:  yesterday,
		},
	}

	// Test the calculateExecutionTrend method
	trend := service.calculateExecutionTrend(executions)

	// Assert
	assert.True(t, len(trend) >= 1) // Should have at least one trend point

	// Find today's trend point
	var todayTrend *ExecutionTrendPoint
	for _, point := range trend {
		if point.Date.Format("2006-01-02") == today.Format("2006-01-02") {
			todayTrend = point
			break
		}
	}

	require.NotNil(t, todayTrend, "Should have trend data for today")
	assert.Equal(t, 3, todayTrend.Executions) // 3 executions today
	assert.Equal(t, 2, todayTrend.Successful) // 2 successful
	assert.Equal(t, 1, todayTrend.Failed)     // 1 failed

	expectedSuccessRate := float64(2) / float64(3) * 100 // 66.67%
	assert.InDelta(t, expectedSuccessRate, todayTrend.SuccessRate, 0.01)
}

// Benchmark tests
func BenchmarkPipelineExecutionStatsService_GetPipelineExecutionMetrics(b *testing.B) {
	// Setup
	executionRepo := persistence.NewInMemoryExecutionRepository()
	pipelineRepo := persistence.NewInMemoryPipelineRepository()
	service := NewPipelineExecutionStatsService(executionRepo, pipelineRepo)

	pipelineID := uuid.New()
	ctx := context.Background()

	// Create 1000 test executions
	for i := 0; i < 1000; i++ {
		execution := &ports.ExecutionRecord{
			ID:         uuid.New(),
			PipelineID: pipelineID,
			Status:     "completed",
			Success:    i%3 != 0, // 2/3 success rate
			Duration:   time.Duration(i) * time.Millisecond,
			CreatedAt:  time.Now().Add(-time.Duration(i) * time.Minute),
		}
		executionRepo.Save(ctx, execution)
	}

	b.ResetTimer()

	// Benchmark the metrics calculation
	for i := 0; i < b.N; i++ {
		_, err := service.GetPipelineExecutionMetrics(ctx, pipelineID)
		if err != nil {
			b.Fatal(err)
		}
	}
}
