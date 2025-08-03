package repositories

import (
	"context"

	"github.com/flext-sh/flext/pkg/domain/pipeline/domain/entities"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel/value_objects"
)

// PipelineRepository defines the repository interface for Pipeline aggregate
type PipelineRepository interface {
	application.Repository[*entities.Pipeline]

	// Additional methods for compatibility
	Save(ctx context.Context, pipeline *entities.Pipeline) error

	// Pipeline-specific queries
	FindByName(ctx context.Context, name string) (*entities.Pipeline, error)
	FindByStatus(ctx context.Context, status entities.PipelineStatus, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error)
	FindByType(ctx context.Context, pipelineType entities.PipelineType, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error)
	FindByCreatedBy(ctx context.Context, createdBy string, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error)
	FindActiveScheduled(ctx context.Context, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error)
	FindByTags(ctx context.Context, tags []string, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error)

	// Analytics and metrics
	CountByStatus(ctx context.Context) (map[entities.PipelineStatus]int64, error)
	CountByType(ctx context.Context) (map[entities.PipelineType]int64, error)
	GetSuccessRateStats(ctx context.Context) (*PipelineSuccessStats, error)
	GetExecutionStats(ctx context.Context, pipelineID string) (*PipelineExecutionStats, error)

	// Advanced queries
	FindDueTasks(ctx context.Context) ([]*entities.Pipeline, error)
	FindByExtractorID(ctx context.Context, extractorID string, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error)
	FindByLoaderID(ctx context.Context, loaderID string, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error)
	Search(ctx context.Context, query *PipelineSearchQuery, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error)
}

// PipelineSearchQuery defines search criteria for pipelines
type PipelineSearchQuery struct {
	Name           *string                   `json:"name,omitempty"`
	Description    *string                   `json:"description,omitempty"`
	Status         []entities.PipelineStatus `json:"status,omitempty"`
	Type           []entities.PipelineType   `json:"type,omitempty"`
	Tags           []string                  `json:"tags,omitempty"`
	CreatedBy      *string                   `json:"created_by,omitempty"`
	UpdatedBy      *string                   `json:"updated_by,omitempty"`
	ExtractorID    *string                   `json:"extractor_id,omitempty"`
	LoaderID       *string                   `json:"loader_id,omitempty"`
	IsScheduled    *bool                     `json:"is_scheduled,omitempty"`
	HasErrors      *bool                     `json:"has_errors,omitempty"`
	DateRange      *DateRange                `json:"date_range,omitempty"`
	SuccessRate    *RangeFilter              `json:"success_rate,omitempty"`
	ExecutionCount *RangeFilter              `json:"execution_count,omitempty"`
}

// DateRange defines a date range filter
type DateRange struct {
	From *string `json:"from,omitempty"` // ISO 8601 format
	To   *string `json:"to,omitempty"`   // ISO 8601 format
}

// RangeFilter defines a numeric range filter
type RangeFilter struct {
	Min *float64 `json:"min,omitempty"`
	Max *float64 `json:"max,omitempty"`
}

// PipelineSuccessStats represents success rate statistics
type PipelineSuccessStats struct {
	TotalPipelines     int64                  `json:"total_pipelines"`
	ActivePipelines    int64                  `json:"active_pipelines"`
	TotalExecutions    int64                  `json:"total_executions"`
	SuccessfulRuns     int64                  `json:"successful_runs"`
	FailedRuns         int64                  `json:"failed_runs"`
	OverallSuccessRate float64                `json:"overall_success_rate"`
	AvgSuccessRate     float64                `json:"avg_success_rate"`
	TopPerformers      []*PipelinePerformance `json:"top_performers"`
	WorstPerformers    []*PipelinePerformance `json:"worst_performers"`
}

// PipelinePerformance represents individual pipeline performance
type PipelinePerformance struct {
	PipelineID     string  `json:"pipeline_id"`
	Name           string  `json:"name"`
	SuccessRate    float64 `json:"success_rate"`
	ExecutionCount int64   `json:"execution_count"`
	AvgRuntime     int64   `json:"avg_runtime_ms"`
}

// PipelineExecutionStats represents execution statistics for a pipeline
type PipelineExecutionStats struct {
	PipelineID       string              `json:"pipeline_id"`
	Name             string              `json:"name"`
	TotalExecutions  int64               `json:"total_executions"`
	SuccessfulRuns   int64               `json:"successful_runs"`
	FailedRuns       int64               `json:"failed_runs"`
	SuccessRate      float64             `json:"success_rate"`
	AvgRuntime       int64               `json:"avg_runtime_ms"`
	MinRuntime       int64               `json:"min_runtime_ms"`
	MaxRuntime       int64               `json:"max_runtime_ms"`
	LastExecution    *string             `json:"last_execution,omitempty"`
	NextExecution    *string             `json:"next_execution,omitempty"`
	RecentExecutions []*ExecutionRecord  `json:"recent_executions"`
	RuntimeTrend     []*RuntimeDataPoint `json:"runtime_trend"`
	SuccessTrend     []*SuccessDataPoint `json:"success_trend"`
}

// ExecutionRecord represents a single execution record
type ExecutionRecord struct {
	ExecutionID string `json:"execution_id"`
	Success     bool   `json:"success"`
	Runtime     int64  `json:"runtime_ms"`
	ExecutedAt  string `json:"executed_at"`
	ErrorMsg    string `json:"error_message,omitempty"`
}

// RuntimeDataPoint represents a point in the runtime trend
type RuntimeDataPoint struct {
	Date       string `json:"date"`
	AvgRuntime int64  `json:"avg_runtime_ms"`
	Executions int64  `json:"executions"`
}

// SuccessDataPoint represents a point in the success rate trend
type SuccessDataPoint struct {
	Date        string  `json:"date"`
	SuccessRate float64 `json:"success_rate"`
	Successful  int64   `json:"successful"`
	Failed      int64   `json:"failed"`
}
