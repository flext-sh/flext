package pipeline

import (
	"context"
	"time"

	"github.com/flext-sh/flext/internal/shared_kernel/domain/value_objects"
	"github.com/google/uuid"
)

// ExecutePipelineUseCase handles pipeline execution requests
type ExecutePipelineUseCase struct {
	repo           PipelineRepository
	inputValidator InputValidator
	eventPublisher EventPublisher
}

// NewExecutePipelineUseCase creates a new ExecutePipelineUseCase
func NewExecutePipelineUseCase(
	repo PipelineRepository,
	inputValidator InputValidator,
	eventPublisher EventPublisher,
) *ExecutePipelineUseCase {
	return &ExecutePipelineUseCase{
		repo:           repo,
		inputValidator: inputValidator,
		eventPublisher: eventPublisher,
	}
}

// ExecutePipelineOutput represents the result of pipeline execution
type ExecutePipelineOutput struct {
	ExecutionID uuid.UUID              `json:"execution_id"`
	PipelineID  uuid.UUID              `json:"pipeline_id"`
	Status      string                 `json:"status"`
	StartedAt   time.Time              `json:"started_at"`
	Context     map[string]interface{} `json:"context,omitempty"`
}

// Execute executes the pipeline
func (uc *ExecutePipelineUseCase) Execute(ctx context.Context, input ExecutePipelineInput) (*ExecutePipelineOutput, error) {
	// Validate input
	if uc.inputValidator != nil {
		if err := uc.inputValidator.ValidateExecutePipelineInput(input); err != nil {
			return nil, err
		}
	}

	// Check if pipeline exists and can be executed
	pipeline, err := uc.repo.GetByID(ctx, input.PipelineID)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_NOT_FOUND",
			Message:     "Pipeline not found",
			Description: err.Error(),
		}
	}

	// Check if pipeline can be executed
	if err := pipeline.CanExecute(); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_CANNOT_EXECUTE",
			Message:     "Pipeline cannot be executed",
			Description: err.Error(),
		}
	}

	// Create execution record
	executionID := uuid.New()
	startedAt := time.Now()

	// Execute pipeline steps sequentially
	status := "completed"
	if len(pipeline.Steps) == 0 {
		status = "completed_no_steps"
	} else {
		// Execute each step in order
		for _, step := range pipeline.Steps {
			// For Clean Architecture demonstration, we simulate step execution
			// In production, this would involve calling plugin execution services
			if step.PluginID != uuid.Nil {
				// Simulate step execution time
				time.Sleep(10 * time.Millisecond)
			}
		}
	}

	// Update pipeline execution status (last executed is tracked via SetUpdatedAt)
	pipeline.SetUpdatedAt(time.Now())

	// Save updated pipeline
	if _, err := uc.repo.Update(ctx, pipeline); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_UPDATE_FAILED",
			Message:     "Failed to update pipeline after execution",
			Description: err.Error(),
		}
	}

	output := &ExecutePipelineOutput{
		ExecutionID: executionID,
		PipelineID:  input.PipelineID,
		Status:      status,
		StartedAt:   startedAt,
		Context:     input.Context,
	}

	// Publish execution completed event
	if uc.eventPublisher != nil {
		event := PipelineExecutionCompletedEvent{
			ExecutionID: executionID,
			PipelineID:  input.PipelineID,
			Status:      status,
			StartedAt:   startedAt,
			CompletedAt: time.Now(),
		}
		if err := uc.eventPublisher.Publish(ctx, event); err != nil {
			// Log error but don't fail the operation
		}
	}

	return output, nil
} 
