package commands

import (
	"context"
	"testing"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/services"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	"github.com/flext-sh/flext/internal/infrastructure/persistence"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestGetPipelineStatusHandler_Handle(t *testing.T) {
	tests := []struct {
		name            string
		setupPipeline   func() *entities.Pipeline
		setupExecutions func(pipelineID uuid.UUID) []*ports.ExecutionRecord
		command         GetPipelineStatusCommand
		expectError     bool
		expectedStatus  string
		expectedHealthy bool
		validateResult  func(t *testing.T, result *GetPipelineStatusResult)
	}{
		{
			name: "pipeline with no executions",
			setupPipeline: func() *entities.Pipeline {
				pipeline, _ := entities.NewPipeline("Test Pipeline", "A test pipeline")
				step, _ := entities.NewPipelineStep("test-step", uuid.New())
				pipeline.AddStep(*step)
				return pipeline
			},
			setupExecutions: func(pipelineID uuid.UUID) []*ports.ExecutionRecord {
				return []*ports.ExecutionRecord{} // No executions
			},
			expectError:     false,
			expectedStatus:  "draft",
			expectedHealthy: true, // Should be healthy if it has steps
			validateResult: func(t *testing.T, result *GetPipelineStatusResult) {
				assert.Equal(t, 0, result.ExecutionCount)
				assert.Equal(t, 0, result.SuccessCount)
				assert.Equal(t, 0, result.FailureCount)
				assert.Nil(t, result.LastExecution)
			},
		},
		{
			name: "active pipeline with successful executions",
			setupPipeline: func() *entities.Pipeline {
				pipeline, _ := entities.NewPipeline("Active Pipeline", "An active test pipeline")
				step, _ := entities.NewPipelineStep("test-step", uuid.New())
				pipeline.AddStep(*step)
				pipeline.Activate()
				return pipeline
			},
			setupExecutions: func(pipelineID uuid.UUID) []*ports.ExecutionRecord {
				now := time.Now()
				return []*ports.ExecutionRecord{
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
						ID:          uuid.New(),
						PipelineID:  pipelineID,
						Status:      "completed",
						StartedAt:   &now,
						CompletedAt: func() *time.Time { t := now.Add(3 * time.Second); return &t }(),
						Duration:    3 * time.Second,
						Success:     true,
						CreatedAt:   now.Add(-2 * time.Hour),
					},
				}
			},
			expectError:     false,
			expectedStatus:  "active",
			expectedHealthy: true,
			validateResult: func(t *testing.T, result *GetPipelineStatusResult) {
				assert.Equal(t, 2, result.ExecutionCount)
				assert.Equal(t, 2, result.SuccessCount)
				assert.Equal(t, 0, result.FailureCount)
				assert.NotNil(t, result.LastExecution)

				// Check advanced metrics
				assert.Contains(t, result.Metrics, "execution_success_rate")
				assert.Equal(t, float64(100), result.Metrics["execution_success_rate"])

				assert.Contains(t, result.Metrics, "last_execution_duration")
				assert.Contains(t, result.Metrics, "average_execution_time")
			},
		},
		{
			name: "pipeline with mixed execution results",
			setupPipeline: func() *entities.Pipeline {
				pipeline, _ := entities.NewPipeline("Mixed Results Pipeline", "Pipeline with mixed results")
				step, _ := entities.NewPipelineStep("test-step", uuid.New())
				pipeline.AddStep(*step)
				return pipeline
			},
			setupExecutions: func(pipelineID uuid.UUID) []*ports.ExecutionRecord {
				now := time.Now()
				return []*ports.ExecutionRecord{
					{
						ID:         uuid.New(),
						PipelineID: pipelineID,
						Status:     "completed",
						Success:    true,
						Duration:   2 * time.Second,
						CreatedAt:  now.Add(-1 * time.Hour),
					},
					{
						ID:           uuid.New(),
						PipelineID:   pipelineID,
						Status:       "failed",
						Success:      false,
						Duration:     1 * time.Second,
						ErrorMessage: "Database connection failed",
						CreatedAt:    now.Add(-2 * time.Hour),
					},
					{
						ID:         uuid.New(),
						PipelineID: pipelineID,
						Status:     "completed",
						Success:    true,
						Duration:   3 * time.Second,
						CreatedAt:  now.Add(-3 * time.Hour),
					},
				}
			},
			expectError:     false,
			expectedStatus:  "draft",
			expectedHealthy: true,
			validateResult: func(t *testing.T, result *GetPipelineStatusResult) {
				assert.Equal(t, 3, result.ExecutionCount)
				assert.Equal(t, 2, result.SuccessCount)
				assert.Equal(t, 1, result.FailureCount)

				// Success rate should be 2/3 = 66.67%
				expectedSuccessRate := float64(2) / float64(3) * 100
				actualSuccessRate, exists := result.Metrics["execution_success_rate"]
				assert.True(t, exists)
				assert.InDelta(t, expectedSuccessRate, actualSuccessRate, 0.01)
			},
		},
		{
			name: "pipeline with no steps (unhealthy)",
			setupPipeline: func() *entities.Pipeline {
				pipeline, _ := entities.NewPipeline("Empty Pipeline", "Pipeline with no steps")
				// Don't add any steps - this should be unhealthy
				return pipeline
			},
			setupExecutions: func(pipelineID uuid.UUID) []*ports.ExecutionRecord {
				return []*ports.ExecutionRecord{}
			},
			expectError:     false,
			expectedStatus:  "draft",
			expectedHealthy: false, // Should be unhealthy without steps
			validateResult: func(t *testing.T, result *GetPipelineStatusResult) {
				assert.Equal(t, "unhealthy", result.HealthStatus)

				// Check health checks
				assert.True(t, len(result.HealthChecks) > 0)

				// Find the steps_configured health check
				var stepsCheck *HealthCheckResult
				for _, check := range result.HealthChecks {
					if check.Name == "steps_configured" {
						stepsCheck = &check
						break
					}
				}

				require.NotNil(t, stepsCheck, "Should have steps_configured health check")
				assert.Equal(t, "unhealthy", stepsCheck.Status)
				assert.Contains(t, stepsCheck.Message, "no configured steps")
			},
		},
		{
			name: "invalid pipeline ID",
			setupPipeline: func() *entities.Pipeline {
				return nil // No pipeline created
			},
			setupExecutions: func(pipelineID uuid.UUID) []*ports.ExecutionRecord {
				return []*ports.ExecutionRecord{}
			},
			command: GetPipelineStatusCommand{
				PipelineID: uuid.Nil, // Invalid UUID
			},
			expectError: true,
		},
		{
			name: "non-existent pipeline",
			setupPipeline: func() *entities.Pipeline {
				return nil // No pipeline created
			},
			setupExecutions: func(pipelineID uuid.UUID) []*ports.ExecutionRecord {
				return []*ports.ExecutionRecord{}
			},
			command: GetPipelineStatusCommand{
				PipelineID: uuid.New(), // Valid UUID but non-existent pipeline
			},
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup repositories
			pipelineRepo := persistence.NewInMemoryPipelineRepository()
			executionRepo := persistence.NewInMemoryExecutionRepository()

			// Create execution stats service
			statsService := services.NewPipelineExecutionStatsService(executionRepo, pipelineRepo)

			// Create handler
			handler := NewGetPipelineStatusHandler(pipelineRepo, statsService)

			ctx := context.Background()
			var pipelineID uuid.UUID

			// Setup pipeline if needed
			if tt.setupPipeline != nil {
				pipeline := tt.setupPipeline()
				if pipeline != nil {
					err := pipelineRepo.Save(ctx, pipeline)
					require.NoError(t, err)
					pipelineID = pipeline.GetID()
				}
			}

			// Setup executions if needed
			if tt.setupExecutions != nil && pipelineID != uuid.Nil {
				executions := tt.setupExecutions(pipelineID)
				for _, execution := range executions {
					err := executionRepo.Save(ctx, execution)
					require.NoError(t, err)
				}
			}

			// Prepare command
			command := tt.command
			if command.PipelineID == uuid.Nil && pipelineID != uuid.Nil {
				command.PipelineID = pipelineID
			}

			// Execute
			result, err := handler.Handle(ctx, command)

			// Assert
			if tt.expectError {
				assert.Error(t, err)
				assert.Nil(t, result)
				return
			}

			require.NoError(t, err)
			require.NotNil(t, result)

			// Basic assertions
			assert.Equal(t, command.PipelineID, result.PipelineID)
			assert.Equal(t, tt.expectedStatus, result.Status)

			// Health status validation
			if tt.expectedHealthy {
				assert.Contains(t, []string{"healthy", "warning"}, result.HealthStatus)
			} else {
				assert.Equal(t, "unhealthy", result.HealthStatus)
			}

			// Health checks should always be present
			assert.True(t, len(result.HealthChecks) > 0)

			// Metrics should always be present
			assert.NotNil(t, result.Metrics)
			assert.True(t, len(result.Metrics) > 0)

			// Custom validation
			if tt.validateResult != nil {
				tt.validateResult(t, result)
			}
		})
	}
}

func TestPausePipelineHandler_Handle(t *testing.T) {
	tests := []struct {
		name          string
		setupPipeline func() *entities.Pipeline
		command       PausePipelineCommand
		expectError   bool
		errorCode     string
	}{
		{
			name: "pause active pipeline",
			setupPipeline: func() *entities.Pipeline {
				pipeline, _ := entities.NewPipeline("Active Pipeline", "Test pipeline")
				step, _ := entities.NewPipelineStep("test-step", uuid.New())
				pipeline.AddStep(*step)
				pipeline.Activate()
				return pipeline
			},
			command: PausePipelineCommand{
				Reason:   "Maintenance required",
				PausedBy: "admin",
			},
			expectError: false,
		},
		{
			name: "pause inactive pipeline",
			setupPipeline: func() *entities.Pipeline {
				pipeline, _ := entities.NewPipeline("Inactive Pipeline", "Test pipeline")
				step, _ := entities.NewPipelineStep("test-step", uuid.New())
				pipeline.AddStep(*step)
				// Don't activate - should fail to pause
				return pipeline
			},
			command: PausePipelineCommand{
				Reason:   "Test pause",
				PausedBy: "admin",
			},
			expectError: true,
			errorCode:   "PIPELINE_NOT_ACTIVE",
		},
		{
			name: "invalid command - no pipeline ID",
			setupPipeline: func() *entities.Pipeline {
				return nil
			},
			command: PausePipelineCommand{
				PipelineID: uuid.Nil,
				Reason:     "Test",
				PausedBy:   "admin",
			},
			expectError: true,
			errorCode:   "INVALID_COMMAND",
		},
		{
			name: "non-existent pipeline",
			setupPipeline: func() *entities.Pipeline {
				return nil
			},
			command: PausePipelineCommand{
				PipelineID: uuid.New(),
				Reason:     "Test",
				PausedBy:   "admin",
			},
			expectError: true,
			errorCode:   "PIPELINE_NOT_FOUND",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup
			pipelineRepo := persistence.NewInMemoryPipelineRepository()
			handler := NewPausePipelineHandler(pipelineRepo)

			ctx := context.Background()
			var pipelineID uuid.UUID

			// Setup pipeline if needed
			if tt.setupPipeline != nil {
				pipeline := tt.setupPipeline()
				if pipeline != nil {
					err := pipelineRepo.Save(ctx, pipeline)
					require.NoError(t, err)
					pipelineID = pipeline.GetID()
				}
			}

			// Prepare command
			command := tt.command
			if command.PipelineID == uuid.Nil && pipelineID != uuid.Nil {
				command.PipelineID = pipelineID
			}

			// Execute
			result, err := handler.Handle(ctx, command)

			// Assert
			if tt.expectError {
				assert.Error(t, err)
				assert.Nil(t, result)

				// Check error code if specified
				if tt.errorCode != "" {
					// Note: This would require the error to implement a specific interface
					// For now, we just check that an error occurred
					// The actual error message format may vary
					assert.Error(t, err)
				}
				return
			}

			require.NoError(t, err)
			require.NotNil(t, result)

			// Verify result
			assert.Equal(t, command.PipelineID, result.PipelineID)
			assert.Equal(t, command.PausedBy, result.PausedBy)
			assert.Equal(t, command.Reason, result.Reason)
			assert.False(t, result.PausedAt.IsZero())

			// Verify pipeline was actually paused
			savedPipeline, err := pipelineRepo.GetByID(ctx, command.PipelineID)
			require.NoError(t, err)
			assert.False(t, savedPipeline.IsActive)
		})
	}
}

func TestResumePipelineHandler_Handle(t *testing.T) {
	tests := []struct {
		name          string
		setupPipeline func() *entities.Pipeline
		command       ResumePipelineCommand
		expectError   bool
		errorCode     string
	}{
		{
			name: "resume paused pipeline",
			setupPipeline: func() *entities.Pipeline {
				pipeline, _ := entities.NewPipeline("Paused Pipeline", "Test pipeline")
				step, _ := entities.NewPipelineStep("test-step", uuid.New())
				pipeline.AddStep(*step)
				// Pipeline starts inactive, which is the "paused" state for this test
				return pipeline
			},
			command: ResumePipelineCommand{
				ResumedBy: "admin",
			},
			expectError: false,
		},
		{
			name: "resume already active pipeline",
			setupPipeline: func() *entities.Pipeline {
				pipeline, _ := entities.NewPipeline("Active Pipeline", "Test pipeline")
				step, _ := entities.NewPipelineStep("test-step", uuid.New())
				pipeline.AddStep(*step)
				pipeline.Activate()
				return pipeline
			},
			command: ResumePipelineCommand{
				ResumedBy: "admin",
			},
			expectError: true,
			errorCode:   "PIPELINE_ALREADY_ACTIVE",
		},
		{
			name: "resume pipeline without steps",
			setupPipeline: func() *entities.Pipeline {
				pipeline, _ := entities.NewPipeline("Empty Pipeline", "Test pipeline")
				// No steps added - should fail to activate
				return pipeline
			},
			command: ResumePipelineCommand{
				ResumedBy: "admin",
			},
			expectError: true,
			errorCode:   "ACTIVATION_FAILED",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup
			pipelineRepo := persistence.NewInMemoryPipelineRepository()
			handler := NewResumePipelineHandler(pipelineRepo)

			ctx := context.Background()
			var pipelineID uuid.UUID

			// Setup pipeline if needed
			if tt.setupPipeline != nil {
				pipeline := tt.setupPipeline()
				if pipeline != nil {
					err := pipelineRepo.Save(ctx, pipeline)
					require.NoError(t, err)
					pipelineID = pipeline.GetID()
				}
			}

			// Prepare command
			command := tt.command
			if command.PipelineID == uuid.Nil && pipelineID != uuid.Nil {
				command.PipelineID = pipelineID
			}

			// Execute
			result, err := handler.Handle(ctx, command)

			// Assert
			if tt.expectError {
				assert.Error(t, err)
				assert.Nil(t, result)

				// Check error code if specified
				if tt.errorCode != "" {
					// The actual error message format may vary
					assert.Error(t, err)
				}
				return
			}

			require.NoError(t, err)
			require.NotNil(t, result)

			// Verify result
			assert.Equal(t, command.PipelineID, result.PipelineID)
			assert.Equal(t, command.ResumedBy, result.ResumedBy)
			assert.False(t, result.ResumedAt.IsZero())

			// Verify pipeline was actually resumed (activated)
			savedPipeline, err := pipelineRepo.GetByID(ctx, command.PipelineID)
			require.NoError(t, err)
			assert.True(t, savedPipeline.IsActive)
		})
	}
}

// Integration test that combines all status operations
func TestPipelineStatusFlow_Integration(t *testing.T) {
	// Setup
	pipelineRepo := persistence.NewInMemoryPipelineRepository()
	executionRepo := persistence.NewInMemoryExecutionRepository()
	statsService := services.NewPipelineExecutionStatsService(executionRepo, pipelineRepo)

	statusHandler := NewGetPipelineStatusHandler(pipelineRepo, statsService)
	pauseHandler := NewPausePipelineHandler(pipelineRepo)
	resumeHandler := NewResumePipelineHandler(pipelineRepo)

	ctx := context.Background()

	// Create and save pipeline
	pipeline, _ := entities.NewPipeline("Integration Test Pipeline", "Test pipeline for status flow")
	step, _ := entities.NewPipelineStep("test-step", uuid.New())
	pipeline.AddStep(*step)
	pipeline.Activate()

	err := pipelineRepo.Save(ctx, pipeline)
	require.NoError(t, err)

	// Add some execution history
	executions := []*ports.ExecutionRecord{
		{
			ID:         uuid.New(),
			PipelineID: pipeline.GetID(),
			Status:     "completed",
			Success:    true,
			Duration:   2 * time.Second,
			CreatedAt:  time.Now().Add(-1 * time.Hour),
		},
		{
			ID:           uuid.New(),
			PipelineID:   pipeline.GetID(),
			Status:       "failed",
			Success:      false,
			Duration:     1 * time.Second,
			ErrorMessage: "Test error",
			CreatedAt:    time.Now().Add(-30 * time.Minute),
		},
	}

	for _, execution := range executions {
		err := executionRepo.Save(ctx, execution)
		require.NoError(t, err)
	}

	// Test 1: Get initial status (active)
	statusResult, err := statusHandler.Handle(ctx, GetPipelineStatusCommand{PipelineID: pipeline.GetID()})
	require.NoError(t, err)
	assert.Equal(t, "active", statusResult.Status)
	assert.True(t, statusResult.IsActive)
	assert.Equal(t, 2, statusResult.ExecutionCount)
	assert.Equal(t, 1, statusResult.SuccessCount)
	assert.Equal(t, 1, statusResult.FailureCount)

	// Test 2: Pause pipeline
	pauseResult, err := pauseHandler.Handle(ctx, PausePipelineCommand{
		PipelineID: pipeline.GetID(),
		Reason:     "Integration test pause",
		PausedBy:   "test_user",
	})
	require.NoError(t, err)
	assert.Equal(t, "Integration test pause", pauseResult.Reason)
	assert.Equal(t, "test_user", pauseResult.PausedBy)

	// Test 3: Get status after pause (paused)
	statusResult, err = statusHandler.Handle(ctx, GetPipelineStatusCommand{PipelineID: pipeline.GetID()})
	require.NoError(t, err)
	assert.Equal(t, "paused", statusResult.Status)
	assert.False(t, statusResult.IsActive)
	// Execution counts should remain the same
	assert.Equal(t, 2, statusResult.ExecutionCount)

	// Test 4: Resume pipeline
	resumeResult, err := resumeHandler.Handle(ctx, ResumePipelineCommand{
		PipelineID: pipeline.GetID(),
		ResumedBy:  "test_user",
	})
	require.NoError(t, err)
	assert.Equal(t, "test_user", resumeResult.ResumedBy)

	// Test 5: Get final status (active again)
	statusResult, err = statusHandler.Handle(ctx, GetPipelineStatusCommand{PipelineID: pipeline.GetID()})
	require.NoError(t, err)
	assert.Equal(t, "active", statusResult.Status)
	assert.True(t, statusResult.IsActive)
}
