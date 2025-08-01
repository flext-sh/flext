package services

import (
	"context"
	"fmt"
	"time"

	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/application/ports"
	"github.com/google/uuid"
)

// PipelineExecutionStatsService provides execution statistics for pipelines
type PipelineExecutionStatsService struct {
	executionRepo ports.ExecutionRepository
	pipelineRepo  ports.PipelineRepository
}

// NewPipelineExecutionStatsService creates a new execution stats service
func NewPipelineExecutionStatsService(
	executionRepo ports.ExecutionRepository,
	pipelineRepo ports.PipelineRepository,
) *PipelineExecutionStatsService {
	return &PipelineExecutionStatsService{
		executionRepo: executionRepo,
		pipelineRepo:  pipelineRepo,
	}
}

// PipelineExecutionMetrics represents pipeline execution metrics
type PipelineExecutionMetrics struct {
	ExecutionCount        int                    `json:"execution_count"`
	SuccessCount          int                    `json:"success_count"`
	FailureCount          int                    `json:"failure_count"`
	LastExecution         *time.Time             `json:"last_execution,omitempty"`
	NextExecution         *time.Time             `json:"next_execution,omitempty"`
	LastExecutionDuration *time.Duration         `json:"last_execution_duration,omitempty"`
	AverageExecutionTime  *time.Duration         `json:"average_execution_time,omitempty"`
	ExecutionSuccessRate  float64                `json:"execution_success_rate"`
	RecentExecutions      []*ExecutionSummary    `json:"recent_executions"`
	ExecutionTrend        []*ExecutionTrendPoint `json:"execution_trend"`
}

// ExecutionSummary represents a summary of an execution
type ExecutionSummary struct {
	ID          uuid.UUID     `json:"id"`
	Status      string        `json:"status"`
	Success     bool          `json:"success"`
	StartedAt   *time.Time    `json:"started_at"`
	CompletedAt *time.Time    `json:"completed_at"`
	Duration    time.Duration `json:"duration"`
	Error       string        `json:"error,omitempty"`
}

// ExecutionTrendPoint represents a point in execution trend data
type ExecutionTrendPoint struct {
	Date        time.Time      `json:"date"`
	Executions  int            `json:"executions"`
	Successful  int            `json:"successful"`
	Failed      int            `json:"failed"`
	SuccessRate float64        `json:"success_rate"`
	AvgDuration *time.Duration `json:"avg_duration,omitempty"`
}

// GetPipelineExecutionMetrics retrieves comprehensive execution metrics for a pipeline
func (s *PipelineExecutionStatsService) GetPipelineExecutionMetrics(ctx context.Context, pipelineID uuid.UUID) (*PipelineExecutionMetrics, error) {
	// Get total execution count
	executionCount, err := s.executionRepo.CountByPipelineID(ctx, pipelineID)
	if err != nil {
		return nil, fmt.Errorf("failed to get execution count: %w", err)
	}

	// Get recent executions for detailed analysis
	recentExecutions, err := s.executionRepo.FindByPipelineID(ctx, pipelineID, 100, 0) // Get last 100 executions
	if err != nil {
		return nil, fmt.Errorf("failed to get recent executions: %w", err)
	}

	// Calculate metrics
	metrics := &PipelineExecutionMetrics{
		ExecutionCount:   executionCount,
		RecentExecutions: make([]*ExecutionSummary, 0),
		ExecutionTrend:   make([]*ExecutionTrendPoint, 0),
	}

	if len(recentExecutions) > 0 {
		metrics.LastExecution = recentExecutions[0].StartedAt

		// Calculate success/failure counts and other metrics
		successCount := 0
		var totalDuration time.Duration
		durationCount := 0

		// Process executions for metrics
		for _, exec := range recentExecutions {
			if exec.Success {
				successCount++
			}

			// Calculate duration if both timestamps are available
			if exec.StartedAt != nil && exec.CompletedAt != nil {
				duration := exec.CompletedAt.Sub(*exec.StartedAt)
				totalDuration += duration
				durationCount++

				// Set last execution duration (from most recent execution)
				if metrics.LastExecutionDuration == nil {
					metrics.LastExecutionDuration = &duration
				}
			}

			// Add to recent executions summary (limit to 10 most recent)
			if len(metrics.RecentExecutions) < 10 {
				summary := &ExecutionSummary{
					ID:          exec.ID,
					Status:      exec.Status,
					Success:     exec.Success,
					StartedAt:   exec.StartedAt,
					CompletedAt: exec.CompletedAt,
					Duration:    exec.Duration,
					Error:       exec.ErrorMessage,
				}
				metrics.RecentExecutions = append(metrics.RecentExecutions, summary)
			}
		}

		metrics.SuccessCount = successCount
		metrics.FailureCount = len(recentExecutions) - successCount

		// Calculate success rate
		if len(recentExecutions) > 0 {
			metrics.ExecutionSuccessRate = float64(successCount) / float64(len(recentExecutions)) * 100
		}

		// Calculate average execution time
		if durationCount > 0 {
			avgDuration := totalDuration / time.Duration(durationCount)
			metrics.AverageExecutionTime = &avgDuration
		}

		// Generate execution trend (last 30 days)
		metrics.ExecutionTrend = s.calculateExecutionTrend(recentExecutions)
	}

	// TODO: Calculate next execution based on pipeline schedule
	// This would require accessing the pipeline's schedule configuration
	// For now, we'll leave it nil

	return metrics, nil
}

// calculateExecutionTrend calculates execution trend data from recent executions
func (s *PipelineExecutionStatsService) calculateExecutionTrend(executions []*ports.ExecutionRecord) []*ExecutionTrendPoint {
	if len(executions) == 0 {
		return []*ExecutionTrendPoint{}
	}

	// Group executions by date
	dailyStats := make(map[string]*ExecutionTrendPoint)

	for _, exec := range executions {
		if exec.StartedAt == nil {
			continue
		}

		// Use date as key (YYYY-MM-DD format)
		dateKey := exec.StartedAt.Format("2006-01-02")

		if point, exists := dailyStats[dateKey]; exists {
			point.Executions++
			if exec.Success {
				point.Successful++
			} else {
				point.Failed++
			}

			// Update average duration if available
			if exec.Duration > 0 {
				if point.AvgDuration == nil {
					point.AvgDuration = &exec.Duration
				} else {
					// Simple moving average
					newAvg := (*point.AvgDuration + exec.Duration) / 2
					point.AvgDuration = &newAvg
				}
			}
		} else {
			point := &ExecutionTrendPoint{
				Date:       *exec.StartedAt,
				Executions: 1,
			}

			if exec.Success {
				point.Successful = 1
				point.Failed = 0
			} else {
				point.Successful = 0
				point.Failed = 1
			}

			if exec.Duration > 0 {
				point.AvgDuration = &exec.Duration
			}

			dailyStats[dateKey] = point
		}
	}

	// Convert map to slice and calculate success rates
	trend := make([]*ExecutionTrendPoint, 0, len(dailyStats))
	for _, point := range dailyStats {
		if point.Executions > 0 {
			point.SuccessRate = float64(point.Successful) / float64(point.Executions) * 100
		}
		trend = append(trend, point)
	}

	// Sort by date (most recent first)
	// TODO: Add proper sorting if needed

	return trend
}

// GetGlobalExecutionStats retrieves global execution statistics across all pipelines
func (s *PipelineExecutionStatsService) GetGlobalExecutionStats(ctx context.Context) (map[string]interface{}, error) {
	// Delegate to execution repository for global stats
	return s.executionRepo.GetExecutionStats(ctx)
}

// RecordExecution records a new execution result
func (s *PipelineExecutionStatsService) RecordExecution(ctx context.Context, execution *ports.ExecutionRecord) error {
	// Validate execution data
	if execution.PipelineID == uuid.Nil {
		return fmt.Errorf("pipeline ID is required")
	}

	if execution.ID == uuid.Nil {
		execution.ID = uuid.New()
	}

	if execution.CreatedAt.IsZero() {
		execution.CreatedAt = time.Now()
	}

	// Set success flag based on status and error
	execution.Success = (execution.Status == "completed" || execution.Status == "success") && execution.ErrorMessage == ""

	// Calculate duration if not set
	if execution.Duration == 0 && execution.StartedAt != nil && execution.CompletedAt != nil {
		execution.Duration = execution.CompletedAt.Sub(*execution.StartedAt)
	}

	// Save to repository
	return s.executionRepo.Save(ctx, execution)
}

// GetPipelineLastExecution retrieves the most recent execution for a pipeline
func (s *PipelineExecutionStatsService) GetPipelineLastExecution(ctx context.Context, pipelineID uuid.UUID) (*ports.ExecutionRecord, error) {
	// Get the most recent execution
	executions, err := s.executionRepo.FindByPipelineID(ctx, pipelineID, 1, 0)
	if err != nil {
		return nil, fmt.Errorf("failed to get last execution: %w", err)
	}

	if len(executions) == 0 {
		return nil, nil // No executions found
	}

	return executions[0], nil
}

// GetPipelineExecutionCounts retrieves basic execution counts for a pipeline
func (s *PipelineExecutionStatsService) GetPipelineExecutionCounts(ctx context.Context, pipelineID uuid.UUID) (int, int, int, error) {
	// Get recent executions to calculate success/failure counts
	executions, err := s.executionRepo.FindByPipelineID(ctx, pipelineID, 1000, 0) // Get last 1000 executions
	if err != nil {
		return 0, 0, 0, fmt.Errorf("failed to get executions: %w", err)
	}

	totalCount := len(executions)
	successCount := 0
	failureCount := 0

	for _, exec := range executions {
		if exec.Success {
			successCount++
		} else {
			failureCount++
		}
	}

	return totalCount, successCount, failureCount, nil
}
