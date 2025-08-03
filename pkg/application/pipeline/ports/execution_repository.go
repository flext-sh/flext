package ports

import (
	"context"
	"time"

	"github.com/google/uuid"
)

// ExecutionRecord represents a pipeline execution record
type ExecutionRecord struct {
	ID           uuid.UUID              `json:"id"`
	PipelineID   uuid.UUID              `json:"pipeline_id"`
	Status       string                 `json:"status"`
	StartedAt    *time.Time             `json:"started_at"`
	CompletedAt  *time.Time             `json:"completed_at"`
	Duration     time.Duration          `json:"duration"`
	Success      bool                   `json:"success"`
	ErrorMessage string                 `json:"error_message"`
	Logs         []ExecutionLog         `json:"logs"`
	Metrics      map[string]interface{} `json:"metrics"`
	CreatedAt    time.Time              `json:"created_at"`
}

// ExecutionLog represents a log entry for an execution
type ExecutionLog struct {
	Timestamp time.Time  `json:"timestamp"`
	Level     string     `json:"level"`
	Message   string     `json:"message"`
	StepID    *uuid.UUID `json:"step_id,omitempty"`
}

// ExecutionStats represents aggregated execution statistics
type ExecutionStats struct {
	TotalExecutions      int            `json:"total_executions"`
	SuccessfulExecutions int            `json:"successful_executions"`
	FailedExecutions     int            `json:"failed_executions"`
	SuccessRate          float64        `json:"success_rate"`
	LastExecution        *time.Time     `json:"last_execution"`
	AverageExecutionTime *time.Duration `json:"average_execution_time"`
}

// ExecutionRepository defines the interface for execution data access
type ExecutionRepository interface {
	// Core CRUD operations
	Save(ctx context.Context, execution *ExecutionRecord) error
	FindByID(ctx context.Context, id uuid.UUID) (*ExecutionRecord, error)
	Delete(ctx context.Context, id uuid.UUID) error

	// Query operations
	FindByPipelineID(ctx context.Context, pipelineID uuid.UUID, limit, offset int) ([]*ExecutionRecord, error)
	FindByStatus(ctx context.Context, status string, limit, offset int) ([]*ExecutionRecord, error)
	FindAll(ctx context.Context, limit, offset int) ([]*ExecutionRecord, error)

	// Statistics operations
	Count(ctx context.Context) (int, error)
	CountByPipelineID(ctx context.Context, pipelineID uuid.UUID) (int, error)
	GetExecutionStats(ctx context.Context) (map[string]interface{}, error)
	GetPipelineStats(ctx context.Context, pipelineID uuid.UUID) (*ExecutionStats, error)
}
