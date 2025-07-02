package pipeline

import (
	"context"
	"fmt"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	"github.com/flext-sh/flext/internal/shared_kernel/domain/value_objects"
	"github.com/google/uuid"
)

// AddStepUseCase handles adding steps to pipelines
type AddStepUseCase struct {
	repo           PipelineRepository
	validator      InputValidator
	eventPublisher EventPublisher
}

// NewAddStepUseCase creates a new AddStepUseCase
func NewAddStepUseCase(repo PipelineRepository, validator InputValidator, eventPublisher EventPublisher) *AddStepUseCase {
	return &AddStepUseCase{
		repo:           repo,
		validator:      validator,
		eventPublisher: eventPublisher,
	}
}

// AddStepInput type already defined in interfaces.go

// AddStepOutput represents output after adding a step
type AddStepOutput struct {
	PipelineID uuid.UUID `json:"pipeline_id"`
	StepID     uuid.UUID `json:"step_id"`
	StepName   string    `json:"step_name"`
	Order      int       `json:"order"`
}

// Execute adds a step to a pipeline
func (uc *AddStepUseCase) Execute(ctx context.Context, input AddStepInput) (*AddStepOutput, error) {
	// Validate input
	if uc.validator != nil {
		if err := uc.validator.ValidateAddStepInput(input); err != nil {
			return nil, &value_objects.DomainError{
				Code:        "VALIDATION_FAILED",
				Message:     "Step input validation failed",
				Description: err.Error(),
			}
		}
	}

	// Find pipeline
	pipeline, err := uc.repo.GetByID(ctx, input.PipelineID)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_NOT_FOUND",
			Message:     "Pipeline not found",
			Description: err.Error(),
		}
	}
	if pipeline == nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_NOT_FOUND",
			Message:     "Pipeline does not exist",
			Description: fmt.Sprintf("Pipeline with ID %s not found", input.PipelineID),
		}
	}

	// Create new step
	step := entities.PipelineStep{
		ID:            uuid.New(),
		Name:          input.Name,
		PluginID:      input.PluginID,
		Configuration: input.Configuration,
		Order:         input.Order,
		DependsOn:     input.DependsOn,
	}

	// Add step to pipeline
	if err := pipeline.AddStep(step); err != nil {
		return nil, fmt.Errorf("failed to add step: %w", err)
	}

	// Save pipeline
	if _, err := uc.repo.Update(ctx, pipeline); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_UPDATE_FAILED",
			Message:     "Failed to save pipeline with new step",
			Description: err.Error(),
		}
	}

	// Publish step added event
	if uc.eventPublisher != nil {
		event := StepAddedEvent{
			PipelineID: pipeline.ID,
			StepID:     step.ID,
			StepName:   step.Name,
			PluginID:   step.PluginID,
			Order:      step.Order,
			OccurredAt: time.Now(),
		}
		if err := uc.eventPublisher.Publish(ctx, event); err != nil {
			// Log error but don't fail the operation
		}
	}

	return &AddStepOutput{
		PipelineID: pipeline.ID,
		StepID:     step.ID,
		StepName:   step.Name,
		Order:      step.Order,
	}, nil
}