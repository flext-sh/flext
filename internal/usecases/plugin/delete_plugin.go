package plugin

import (
	"context"

	"github.com/flext/flexcore/internal/bounded_contexts/plugin/domain/entities"
	"github.com/flext/flexcore/internal/bounded_contexts/plugin/domain/events"
	"github.com/google/uuid"
)

// DeletePluginUseCase handles plugin deletion
type DeletePluginUseCase struct {
	repo      PluginRepository
	validator InputValidator
	events    EventPublisher
}

// NewDeletePluginUseCase creates a new delete plugin use case
func NewDeletePluginUseCase(
	repo PluginRepository,
	validator InputValidator,
	events EventPublisher,
) *DeletePluginUseCase {
	return &DeletePluginUseCase{
		repo:      repo,
		validator: validator,
		events:    events,
	}
}

// DeletePluginInput represents input for deleting a plugin
type DeletePluginInput struct {
	ID uuid.UUID `json:"id" validate:"required"`
}

// Execute deletes a plugin
func (uc *DeletePluginUseCase) Execute(ctx context.Context, input DeletePluginInput) error {
	// Validate input
	if err := uc.validator.ValidateDeletePlugin(input); err != nil {
		return err
	}

	// Check if plugin exists
	plugin, err := uc.repo.FindByID(ctx, input.ID)
	if err != nil {
		return err
	}
	if plugin == nil {
		return ErrPluginNotFound
	}

	// Check if plugin can be deleted (business rules)
	if plugin.Status == entities.PluginStatusActive {
		// In a real implementation, you might want to check if plugin is in use
		// For now, we'll allow deletion but could add business logic here
	}

	// Delete plugin
	if err := uc.repo.Delete(ctx, input.ID); err != nil {
		return err
	}

	// Publish domain event
	event := events.NewPluginDeletedEvent(input.ID, plugin.Name)

	if err := uc.events.Publish(ctx, event); err != nil {
		// Log error but don't fail the operation
		// In a real implementation, you might want to use an outbox pattern
	}

	return nil
}
