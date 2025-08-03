package pipeline

import (
	"context"
	"time"

	"github.com/flext-sh/flext/pkg/domain/pipeline/domain/entities"
)

// CreatePipelineUseCase handles pipeline creation business logic
type CreatePipelineUseCase struct {
	repo      PipelineRepository
	validator InputValidator
	events    EventPublisher
}

// NewCreatePipelineUseCase creates a new use case instance
func NewCreatePipelineUseCase(
	repo PipelineRepository,
	validator InputValidator,
	events EventPublisher,
) *CreatePipelineUseCase {
	return &CreatePipelineUseCase{
		repo:      repo,
		validator: validator,
		events:    events,
	}
}

// Execute performs the pipeline creation
func (uc *CreatePipelineUseCase) Execute(ctx context.Context, input CreatePipelineInput) (*CreatePipelineOutput, error) {
	// Validate input
	if err := uc.validator.ValidateCreatePipelineInput(input); err != nil {
		return nil, err
	}

	// Check if pipeline with same name already exists
	existing, err := uc.repo.GetByName(ctx, input.Name)
	if err == nil && existing != nil {
		return nil, ErrPipelineNameAlreadyExists
	}

	// Create domain entity using the correct constructor
	pipelineEntity, err := entities.NewPipeline(input.Name, input.Description)
	if err != nil {
		return nil, err
	}

	// Set optional fields
	if len(input.Tags) > 0 {
		pipelineEntity.Tags = input.Tags
	}

	// Persist the pipeline
	_, err = uc.repo.Create(ctx, pipelineEntity)
	if err != nil {
		return nil, err
	}

	// Publish domain event
	event := PipelineCreatedEvent{
		PipelineID:  pipelineEntity.ID,
		Name:        pipelineEntity.Name,
		Description: pipelineEntity.Description,
		OccurredAt:  time.Now(),
	}

	if err := uc.events.Publish(ctx, event); err != nil {
		// Log error but don't fail the operation
		// Event publishing should be eventually consistent
	}

	// Return output
	return &CreatePipelineOutput{
		ID:          pipelineEntity.ID.String(),
		Name:        pipelineEntity.Name,
		Description: pipelineEntity.Description,
		Tags:        pipelineEntity.Tags,
		IsActive:    pipelineEntity.IsActive,
		CreatedAt:   time.Now().Format(time.RFC3339),
	}, nil
}

// Business errors defined in interfaces.go
