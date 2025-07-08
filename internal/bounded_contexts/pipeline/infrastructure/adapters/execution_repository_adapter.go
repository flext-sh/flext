package adapters

import (
	"context"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
	"github.com/flext-sh/flext/internal/infrastructure/database"
	"github.com/google/uuid"
)

// ExecutionRepositoryAdapter adapts the database execution repository to the application port
type ExecutionRepositoryAdapter struct {
	dbRepo *database.ExecutionRepository
}

// NewExecutionRepositoryAdapter creates a new execution repository adapter
func NewExecutionRepositoryAdapter(dbRepo *database.ExecutionRepository) *ExecutionRepositoryAdapter {
	return &ExecutionRepositoryAdapter{
		dbRepo: dbRepo,
	}
}

// Save persists an execution record
func (a *ExecutionRepositoryAdapter) Save(ctx context.Context, execution *ports.ExecutionRecord) error {
	// Convert from port type to database type
	dbExecution := &database.Execution{
		ID:           execution.ID,
		PipelineID:   execution.PipelineID,
		Status:       execution.Status,
		StartedAt:    execution.StartedAt,
		CompletedAt:  execution.CompletedAt,
		Duration:     execution.Duration,
		Success:      execution.Success,
		ErrorMessage: execution.ErrorMessage,
		Logs:         convertLogsToDatabase(execution.Logs),
		Metrics:      execution.Metrics,
		CreatedAt:    execution.CreatedAt,
	}

	return a.dbRepo.Save(ctx, dbExecution)
}

// FindByID retrieves an execution by ID
func (a *ExecutionRepositoryAdapter) FindByID(ctx context.Context, id uuid.UUID) (*ports.ExecutionRecord, error) {
	dbExecution, err := a.dbRepo.FindByID(ctx, id)
	if err != nil {
		return nil, err
	}

	if dbExecution == nil {
		return nil, nil
	}

	// Convert from database type to port type
	return &ports.ExecutionRecord{
		ID:           dbExecution.ID,
		PipelineID:   dbExecution.PipelineID,
		Status:       dbExecution.Status,
		StartedAt:    dbExecution.StartedAt,
		CompletedAt:  dbExecution.CompletedAt,
		Duration:     dbExecution.Duration,
		Success:      dbExecution.Success,
		ErrorMessage: dbExecution.ErrorMessage,
		Logs:         convertLogsFromDatabase(dbExecution.Logs),
		Metrics:      dbExecution.Metrics,
		CreatedAt:    dbExecution.CreatedAt,
	}, nil
}

// Delete removes an execution record
func (a *ExecutionRepositoryAdapter) Delete(ctx context.Context, id uuid.UUID) error {
	return a.dbRepo.Delete(ctx, id)
}

// FindByPipelineID retrieves executions for a specific pipeline
func (a *ExecutionRepositoryAdapter) FindByPipelineID(ctx context.Context, pipelineID uuid.UUID, limit, offset int) ([]*ports.ExecutionRecord, error) {
	dbExecutions, err := a.dbRepo.FindByPipelineID(ctx, pipelineID, limit, offset)
	if err != nil {
		return nil, err
	}

	// Convert from database types to port types
	executions := make([]*ports.ExecutionRecord, len(dbExecutions))
	for i, dbExecution := range dbExecutions {
		executions[i] = &ports.ExecutionRecord{
			ID:           dbExecution.ID,
			PipelineID:   dbExecution.PipelineID,
			Status:       dbExecution.Status,
			StartedAt:    dbExecution.StartedAt,
			CompletedAt:  dbExecution.CompletedAt,
			Duration:     dbExecution.Duration,
			Success:      dbExecution.Success,
			ErrorMessage: dbExecution.ErrorMessage,
			Logs:         convertLogsFromDatabase(dbExecution.Logs),
			Metrics:      dbExecution.Metrics,
			CreatedAt:    dbExecution.CreatedAt,
		}
	}

	return executions, nil
}

// FindByStatus retrieves executions by status
func (a *ExecutionRepositoryAdapter) FindByStatus(ctx context.Context, status string, limit, offset int) ([]*ports.ExecutionRecord, error) {
	dbExecutions, err := a.dbRepo.FindByStatus(ctx, status, limit, offset)
	if err != nil {
		return nil, err
	}

	// Convert from database types to port types
	executions := make([]*ports.ExecutionRecord, len(dbExecutions))
	for i, dbExecution := range dbExecutions {
		executions[i] = &ports.ExecutionRecord{
			ID:           dbExecution.ID,
			PipelineID:   dbExecution.PipelineID,
			Status:       dbExecution.Status,
			StartedAt:    dbExecution.StartedAt,
			CompletedAt:  dbExecution.CompletedAt,
			Duration:     dbExecution.Duration,
			Success:      dbExecution.Success,
			ErrorMessage: dbExecution.ErrorMessage,
			Logs:         convertLogsFromDatabase(dbExecution.Logs),
			Metrics:      dbExecution.Metrics,
			CreatedAt:    dbExecution.CreatedAt,
		}
	}

	return executions, nil
}

// FindAll retrieves all executions with pagination
func (a *ExecutionRepositoryAdapter) FindAll(ctx context.Context, limit, offset int) ([]*ports.ExecutionRecord, error) {
	dbExecutions, err := a.dbRepo.FindAll(ctx, limit, offset)
	if err != nil {
		return nil, err
	}

	// Convert from database types to port types
	executions := make([]*ports.ExecutionRecord, len(dbExecutions))
	for i, dbExecution := range dbExecutions {
		executions[i] = &ports.ExecutionRecord{
			ID:           dbExecution.ID,
			PipelineID:   dbExecution.PipelineID,
			Status:       dbExecution.Status,
			StartedAt:    dbExecution.StartedAt,
			CompletedAt:  dbExecution.CompletedAt,
			Duration:     dbExecution.Duration,
			Success:      dbExecution.Success,
			ErrorMessage: dbExecution.ErrorMessage,
			Logs:         convertLogsFromDatabase(dbExecution.Logs),
			Metrics:      dbExecution.Metrics,
			CreatedAt:    dbExecution.CreatedAt,
		}
	}

	return executions, nil
}

// Count returns the total number of executions
func (a *ExecutionRepositoryAdapter) Count(ctx context.Context) (int, error) {
	return a.dbRepo.Count(ctx)
}

// CountByPipelineID returns the number of executions for a pipeline
func (a *ExecutionRepositoryAdapter) CountByPipelineID(ctx context.Context, pipelineID uuid.UUID) (int, error) {
	return a.dbRepo.CountByPipelineID(ctx, pipelineID)
}

// GetExecutionStats returns global execution statistics
func (a *ExecutionRepositoryAdapter) GetExecutionStats(ctx context.Context) (map[string]interface{}, error) {
	return a.dbRepo.GetExecutionStats(ctx)
}

// GetPipelineStats returns execution statistics for a specific pipeline
func (a *ExecutionRepositoryAdapter) GetPipelineStats(ctx context.Context, pipelineID uuid.UUID) (*ports.ExecutionStats, error) {
	// Get basic counts
	totalCount, err := a.dbRepo.CountByPipelineID(ctx, pipelineID)
	if err != nil {
		return nil, err
	}

	// Get recent executions to calculate detailed stats
	executions, err := a.dbRepo.FindByPipelineID(ctx, pipelineID, 1000, 0) // Last 1000 executions
	if err != nil {
		return nil, err
	}

	stats := &ports.ExecutionStats{
		TotalExecutions: totalCount,
	}

	if len(executions) > 0 {
		successCount := 0
		var totalDuration time.Duration
		durationCount := 0
		var lastExecution *time.Time

		for _, exec := range executions {
			if exec.Success {
				successCount++
			}

			// Track last execution
			if exec.StartedAt != nil && (lastExecution == nil || exec.StartedAt.After(*lastExecution)) {
				lastExecution = exec.StartedAt
			}

			// Calculate duration stats
			if exec.Duration > 0 {
				totalDuration += exec.Duration
				durationCount++
			}
		}

		stats.SuccessfulExecutions = successCount
		stats.FailedExecutions = len(executions) - successCount
		stats.LastExecution = lastExecution

		// Calculate success rate
		if len(executions) > 0 {
			stats.SuccessRate = float64(successCount) / float64(len(executions)) * 100
		}

		// Calculate average execution time
		if durationCount > 0 {
			avgDuration := totalDuration / time.Duration(durationCount)
			stats.AverageExecutionTime = &avgDuration
		}
	}

	return stats, nil
}

// Helper functions for log conversion

func convertLogsToDatabase(portLogs []ports.ExecutionLog) []database.ExecutionLog {
	dbLogs := make([]database.ExecutionLog, len(portLogs))
	for i, log := range portLogs {
		dbLogs[i] = database.ExecutionLog{
			Timestamp: log.Timestamp,
			Level:     log.Level,
			Message:   log.Message,
			StepID:    log.StepID,
		}
	}
	return dbLogs
}

func convertLogsFromDatabase(dbLogs []database.ExecutionLog) []ports.ExecutionLog {
	portLogs := make([]ports.ExecutionLog, len(dbLogs))
	for i, log := range dbLogs {
		portLogs[i] = ports.ExecutionLog{
			Timestamp: log.Timestamp,
			Level:     log.Level,
			Message:   log.Message,
			StepID:    log.StepID,
		}
	}
	return portLogs
}
