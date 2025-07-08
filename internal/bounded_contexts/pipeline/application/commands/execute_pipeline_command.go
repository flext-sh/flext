package commands

import (
	"context"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/services"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	pipelineServices "github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/services"
	"github.com/flext-sh/flext/internal/shared_kernel/domain/value_objects"
	"github.com/google/uuid"
)

// ExecutePipelineCommand representa o comando para executar um pipeline
type ExecutePipelineCommand struct {
	PipelineID uuid.UUID              `json:"pipeline_id" validate:"required"`
	Context    map[string]interface{} `json:"context,omitempty"`
}

// ExecutePipelineResult resultado do comando
type ExecutePipelineResult struct {
	ExecutionID   uuid.UUID                `json:"execution_id"`
	PipelineID    uuid.UUID                `json:"pipeline_id"`
	Status        string                   `json:"status"`
	StartedAt     time.Time                `json:"started_at"`
	CompletedAt   *time.Time               `json:"completed_at,omitempty"`
	Duration      *string                  `json:"duration,omitempty"`
	StepsExecuted int                      `json:"steps_executed"`
	StepsTotal    int                      `json:"steps_total"`
	StepResults   []map[string]interface{} `json:"step_results,omitempty"`
	Error         *string                  `json:"error,omitempty"`
	Message       string                   `json:"message,omitempty"`
}

// ExecutePipelineHandler manipula o comando de execução de pipeline
type ExecutePipelineHandler struct {
	pipelineRepo          ports.PipelineRepository
	pipelineExecutor      *pipelineServices.PipelineExecutor
	executionStatsService *services.PipelineExecutionStatsService
}

// NewExecutePipelineHandler cria um novo handler
func NewExecutePipelineHandler(
	pipelineRepo ports.PipelineRepository,
	pipelineExecutor *pipelineServices.PipelineExecutor,
	executionStatsService *services.PipelineExecutionStatsService,
) *ExecutePipelineHandler {
	return &ExecutePipelineHandler{
		pipelineRepo:          pipelineRepo,
		pipelineExecutor:      pipelineExecutor,
		executionStatsService: executionStatsService,
	}
}

// Handle executa o comando
func (h *ExecutePipelineHandler) Handle(ctx context.Context, cmd ExecutePipelineCommand) (*ExecutePipelineResult, error) {
	// Validate command
	if err := h.validateCommand(cmd); err != nil {
		return nil, err
	}

	// Buscar o pipeline
	pipeline, err := h.pipelineRepo.GetByID(ctx, cmd.PipelineID)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "REPOSITORY_ERROR",
			Message:     "Failed to retrieve pipeline",
			Description: err.Error(),
		}
	}

	if pipeline == nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_NOT_FOUND",
			Message:     "Pipeline not found",
			Description: "The specified pipeline does not exist",
		}
	}

	// Verificar se o pipeline pode ser executado
	if err := pipeline.CanExecute(); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_CANNOT_EXECUTE",
			Message:     "Pipeline cannot be executed",
			Description: err.Error(),
		}
	}

	// Verificar se o executor está disponível
	if h.pipelineExecutor == nil {
		return nil, &value_objects.DomainError{
			Code:        "EXECUTOR_NOT_AVAILABLE",
			Message:     "Pipeline executor is not available",
			Description: "The pipeline execution engine is not properly initialized",
		}
	}

	// Executar pipeline usando o domain service
	startedAt := time.Now().UTC()
	execution, err := h.pipelineExecutor.Execute(ctx, pipeline)
	if err != nil {
		// Pipeline execution failed
		errorStr := err.Error()
		return &ExecutePipelineResult{
			ExecutionID:   uuid.New(),
			PipelineID:    cmd.PipelineID,
			Status:        "failed",
			StartedAt:     startedAt,
			CompletedAt:   &startedAt,
			StepsExecuted: 0,
			StepsTotal:    len(pipeline.Steps),
			Error:         &errorStr,
			Message:       "Pipeline execution failed",
		}, nil // Return result even if execution failed
	}

	// Build comprehensive result from execution
	result := &ExecutePipelineResult{
		ExecutionID:   execution.ID,
		PipelineID:    execution.PipelineID,
		Status:        string(execution.Status),
		StartedAt:     execution.StartedAt,
		CompletedAt:   execution.CompletedAt,
		StepsExecuted: 0,                          // TODO: Implement when StepExecution is properly defined
		StepsTotal:    0,                          // TODO: Implement when StepExecution is properly defined
		StepResults:   []map[string]interface{}{}, // TODO: Implement when StepExecution is properly defined
	}

	// Add duration if completed
	if execution.CompletedAt != nil {
		duration := execution.CompletedAt.Sub(execution.StartedAt)
		durationStr := duration.String()
		result.Duration = &durationStr
	}

	// Add error if failed
	if execution.Error != nil {
		result.Error = execution.Error
		result.Message = "Pipeline execution completed with errors"
	} else {
		result.Message = "Pipeline execution completed successfully"
	}

	// Log execution completion
	h.logExecutionComplete(pipeline, execution)

	// Record execution in stats service if available
	if h.executionStatsService != nil {
		executionRecord := &ports.ExecutionRecord{
			ID:           execution.ID,
			PipelineID:   execution.PipelineID,
			Status:       string(execution.Status),
			StartedAt:    &execution.StartedAt,
			CompletedAt:  execution.CompletedAt,
			Duration:     0, // Will be calculated by the service
			Success:      execution.Status == pipelineServices.StatusCompleted,
			ErrorMessage: "",
			Logs:         []ports.ExecutionLog{},
			Metrics:      make(map[string]interface{}),
			CreatedAt:    time.Now(),
		}

		// Add error if execution failed
		if execution.Error != nil {
			executionRecord.ErrorMessage = *execution.Error
		}

		// Convert step logs to execution logs
		for _, step := range execution.Steps {
			for _, logMsg := range step.Logs {
				executionRecord.Logs = append(executionRecord.Logs, ports.ExecutionLog{
					Timestamp: time.Now(), // Use current time since step doesn't have timestamp
					Level:     "info",
					Message:   logMsg,
					StepID:    &step.StepID,
				})
			}
		}

		// Record the execution (ignore errors to not break pipeline execution)
		if err := h.executionStatsService.RecordExecution(ctx, executionRecord); err != nil {
			// Log error but don't fail the pipeline execution
			// TODO: Add proper logging when logger is available
		}
	}

	return result, nil
}

// validateCommand performs comprehensive command validation
func (h *ExecutePipelineHandler) validateCommand(cmd ExecutePipelineCommand) error {
	if cmd.PipelineID == uuid.Nil {
		return &value_objects.DomainError{
			Code:        "INVALID_COMMAND",
			Message:     "Pipeline ID is required",
			Description: "PipelineID field cannot be empty",
		}
	}

	// Validate context if provided
	if cmd.Context != nil {
		// Validate context size (prevent huge payloads)
		if len(cmd.Context) > 100 {
			return &value_objects.DomainError{
				Code:        "INVALID_COMMAND",
				Message:     "Context payload too large",
				Description: "Context cannot contain more than 100 keys",
			}
		}

		// Validate context values (basic type checking)
		for key, value := range cmd.Context {
			if key == "" {
				return &value_objects.DomainError{
					Code:        "INVALID_COMMAND",
					Message:     "Invalid context key",
					Description: "Context keys cannot be empty",
				}
			}

			// Ensure value is JSON-serializable basic type
			switch value.(type) {
			case string, int, int64, float64, bool, map[string]interface{}, []interface{}, nil:
				// Valid types
			default:
				return &value_objects.DomainError{
					Code:        "INVALID_COMMAND",
					Message:     "Invalid context value type",
					Description: "Context values must be JSON-serializable",
				}
			}
		}
	}

	return nil
}

// logExecutionStart logs the execution start for audit/monitoring
func (h *ExecutePipelineHandler) logExecutionStart(pipeline *entities.Pipeline, executionID uuid.UUID, context map[string]interface{}) {
	// TODO: Implement proper logging when logger is available
	// For now, this is a placeholder for future logging implementation
	// Should log:
	// - Pipeline ID and name
	// - Execution ID
	// - Start time
	// - Context summary
	// - User/system that initiated execution
}

// validateExecutionPermissions checks if execution is allowed
func (h *ExecutePipelineHandler) validateExecutionPermissions(ctx context.Context, pipeline *entities.Pipeline) error {
	// TODO: Implement authorization checks when needed
	// For now, allow all executions
	// Future implementation should check:
	// - User permissions
	// - Pipeline access control
	// - Resource quotas
	// - Rate limiting
	return nil
}

// scheduleExecution would schedule the pipeline for actual execution
func (h *ExecutePipelineHandler) scheduleExecution(ctx context.Context, pipeline *entities.Pipeline, executionID uuid.UUID, executionContext map[string]interface{}) error {
	// TODO: Implement actual execution scheduling
	// This would:
	// 1. Create execution record in database
	// 2. Queue execution job
	// 3. Publish domain events
	// 4. Setup monitoring/tracking
	return nil
}

// countCompletedSteps counts the number of completed steps
func (h *ExecutePipelineHandler) countCompletedSteps(steps []interface{}) int {
	// Simple implementation for now
	return len(steps)
}

// convertStepResults converts step executions to map format for JSON response
func (h *ExecutePipelineHandler) convertStepResults(steps []interface{}) []map[string]interface{} {
	results := make([]map[string]interface{}, len(steps))
	for i := range steps {
		results[i] = map[string]interface{}{
			"step_id":      i,
			"status":       "completed",
			"started_at":   nil,
			"completed_at": nil,
			"error":        nil,
			"output":       nil,
			"logs":         nil,
		}
	}
	return results
}

// logExecutionComplete logs the execution completion for audit/monitoring
func (h *ExecutePipelineHandler) logExecutionComplete(pipeline *entities.Pipeline, execution interface{}) {
	// TODO: Implement proper logging when logger is available
	// For now, this is a placeholder for future logging implementation
	// Should log:
	// - Pipeline ID and name
	// - Execution ID
	// - Completion time
	// - Final status
	// - Steps executed vs total
	// - Duration
}
