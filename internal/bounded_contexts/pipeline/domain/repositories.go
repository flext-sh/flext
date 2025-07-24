// Pipeline Domain Repositories - Repository interfaces for Pipeline bounded context
package domain

import (
	"context"
	"time"
	"github.com/google/uuid"
)

// PipelineRepository defines the contract for pipeline persistence
type PipelineRepository interface {
	// Pipeline CRUD operations
	Save(ctx context.Context, pipeline *Pipeline) error
	FindByID(ctx context.Context, id uuid.UUID) (*Pipeline, error)
	FindByName(ctx context.Context, name string) (*Pipeline, error)
	FindAll(ctx context.Context) ([]*Pipeline, error)
	Update(ctx context.Context, pipeline *Pipeline) error
	Delete(ctx context.Context, id uuid.UUID) error
	
	// Pipeline queries
	FindByStatus(ctx context.Context, status PipelineStatus) ([]*Pipeline, error)
	FindByCreatedBy(ctx context.Context, createdBy string) ([]*Pipeline, error)
}

// PipelineExecutionRepository defines the contract for pipeline execution persistence
type PipelineExecutionRepository interface {
	// Execution CRUD operations
	Save(ctx context.Context, execution *PipelineExecution) error
	FindByID(ctx context.Context, id uuid.UUID) (*PipelineExecution, error)
	FindByPipelineID(ctx context.Context, pipelineID uuid.UUID) ([]*PipelineExecution, error)
	FindAll(ctx context.Context) ([]*PipelineExecution, error)
	Update(ctx context.Context, execution *PipelineExecution) error
	Delete(ctx context.Context, id uuid.UUID) error
	
	// Execution queries
	FindByStatus(ctx context.Context, status PipelineStatus) ([]*PipelineExecution, error)
	FindByExecutedBy(ctx context.Context, executedBy string) ([]*PipelineExecution, error)
	FindRecent(ctx context.Context, limit int) ([]*PipelineExecution, error)
	
	// Statistics
	GetExecutionStats(ctx context.Context, pipelineID uuid.UUID) (*ExecutionStats, error)
}

// ExecutionStats represents pipeline execution statistics
type ExecutionStats struct {
	TotalExecutions      int64
	SuccessfulExecutions int64
	FailedExecutions     int64
	AverageExecutionTime time.Duration
	TotalRowsProcessed   int64
	LastExecutionTime    *time.Time
}