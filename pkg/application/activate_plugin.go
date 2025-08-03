package plugin

import (
	"context"
	"errors"
	"time"

	"github.com/google/uuid"
)

// ActivatePluginUseCase handles plugin activation
type ActivatePluginUseCase struct {
	repo      PluginRepository
	validator InputValidator
	events    EventPublisher
}

// NewActivatePluginUseCase creates a new activate plugin use case
func NewActivatePluginUseCase(
	repo PluginRepository,
	validator InputValidator,
	events EventPublisher,
) *ActivatePluginUseCase {
	return &ActivatePluginUseCase{
		repo:      repo,
		validator: validator,
		events:    events,
	}
}

// ActivatePluginInput represents the input for activating a plugin
type ActivatePluginInput struct {
	PluginID uuid.UUID
}

// ActivatePluginOutput represents the output after activating a plugin
type ActivatePluginOutput struct {
	ID          string
	Name        string
	Status      string
	ActivatedAt string
}

// Execute activates a plugin
func (uc *ActivatePluginUseCase) Execute(ctx context.Context, input ActivatePluginInput) (*ActivatePluginOutput, error) {
	// Validate input
	if err := uc.validator.ValidateActivatePlugin(input); err != nil {
		return nil, err
	}

	// Get the plugin
	pluginEntity, err := uc.repo.FindByID(ctx, input.PluginID)
	if err != nil {
		return nil, err
	}
	if pluginEntity == nil {
		return nil, ErrPluginNotFound
	}

	// Activate the plugin
	if err := pluginEntity.Activate(); err != nil {
		return nil, err
	}

	// Save the updated plugin
	if err := uc.repo.Save(ctx, pluginEntity); err != nil {
		return nil, errors.New("failed to save plugin")
	}

	// Publish event
	event := PluginActivatedEvent{
		PluginID:    pluginEntity.ID,
		ActivatedAt: time.Now(),
	}

	if err := uc.events.Publish(ctx, event); err != nil {
		// Log error but don't fail
	}

	return &ActivatePluginOutput{
		ID:          pluginEntity.ID.String(),
		Name:        pluginEntity.Name,
		Status:      string(pluginEntity.Status),
		ActivatedAt: time.Now().Format(time.RFC3339),
	}, nil
}

// UpdatePluginInput represents the input for updating a plugin
type UpdatePluginInput struct {
	ID            uuid.UUID              `json:"id" validate:"required"`
	Version       string                 `json:"version,omitempty"`
	Status        string                 `json:"status,omitempty"`
	IsActive      *bool                  `json:"is_active,omitempty"`
	Configuration map[string]interface{} `json:"configuration,omitempty"`
	Metadata      map[string]interface{} `json:"metadata,omitempty"`
	Capabilities  []string               `json:"capabilities,omitempty"`
}

// UpdatePluginOutput represents the output after updating a plugin
type UpdatePluginOutput struct {
	ID        string
	Name      string
	UpdatedAt string
}

// Business errors
var (
	ErrPluginNotFound = errors.New("plugin not found")
)
