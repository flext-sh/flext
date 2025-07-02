package dbt

import (
	"context"
	"github.com/flext-sh/flext/internal/bounded_contexts/dbt/domain/events"
	"github.com/google/uuid"
)

// DeleteProjectUseCase handles DBT project deletion
type DeleteProjectUseCase struct {
	repo      ProjectRepository
	validator InputValidator
	events    EventPublisher
}

// NewDeleteProjectUseCase creates a new delete project use case
func NewDeleteProjectUseCase(repo ProjectRepository, validator InputValidator, events EventPublisher) *DeleteProjectUseCase {
	return &DeleteProjectUseCase{
		repo:      repo,
		validator: validator,
		events:    events,
	}
}

// DeleteProjectInput represents the input for deleting a project
type DeleteProjectInput struct {
	ID uuid.UUID `json:"id" validate:"required"`
}

// Execute deletes a project
func (uc *DeleteProjectUseCase) Execute(ctx context.Context, input DeleteProjectInput) error {
	// Validate input
	if err := uc.validator.ValidateDeleteProject(input); err != nil {
		return err
	}

	// Check if project exists
	project, err := uc.repo.FindByID(ctx, input.ID)
	if err != nil {
		return err
	}
	if project == nil {
		return ErrProjectNotFound
	}

	// Delete project
	if err := uc.repo.Delete(ctx, input.ID); err != nil {
		return err
	}

	// Publish domain event
	event := events.NewProjectDeletedEvent(input.ID, project.Name)
	
	if err := uc.events.Publish(ctx, event); err != nil {
		// Log error but don't fail the operation
		// In a real implementation, you might want to use an outbox pattern
	}

	return nil
}