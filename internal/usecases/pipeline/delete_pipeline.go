package pipeline

import (
	"context"

	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/domain/events"
)

// DeletePipelineUseCase handles pipeline deletion
type DeletePipelineUseCase struct {
	repo      PipelineRepository
	validator InputValidator
	events    EventPublisher
}

// NewDeletePipelineUseCase creates a new delete pipeline use case
func NewDeletePipelineUseCase(
	repo PipelineRepository,
	validator InputValidator,
	events EventPublisher,
) *DeletePipelineUseCase {
	return &DeletePipelineUseCase{
		repo:      repo,
		validator: validator,
		events:    events,
	}
}

// Execute deletes a pipeline
func (uc *DeletePipelineUseCase) Execute(ctx context.Context, input DeletePipelineInput) error {
	// Validate input
	if err := uc.validator.ValidateDeletePipelineInput(input); err != nil {
		return err
	}

	// Check if pipeline exists
	pipeline, err := uc.repo.GetByID(ctx, input.ID)
	if err != nil {
		return err
	}
	if pipeline == nil {
		return ErrPipelineNotFound
	}

	// Delete pipeline
	if err := uc.repo.Delete(ctx, input.ID); err != nil {
		return err
	}

	// Publish domain event
	event := events.NewPipelineDeletedEvent(input.ID, pipeline.Name)

	if err := uc.events.Publish(ctx, event); err != nil {
		// Log error but don't fail the operation
		// In a real implementation, you might want to use an outbox pattern
	}

	return nil
}
