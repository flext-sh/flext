package plugin

import (
	"context"
	"errors"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
)

// RegisterPluginUseCase handles plugin registration
type RegisterPluginUseCase struct {
	repo      PluginRepository
	validator InputValidator
	events    EventPublisher
}

// NewRegisterPluginUseCase creates a new register plugin use case
func NewRegisterPluginUseCase(
	repo PluginRepository,
	validator InputValidator,
	events EventPublisher,
) *RegisterPluginUseCase {
	return &RegisterPluginUseCase{
		repo:      repo,
		validator: validator,
		events:    events,
	}
}

// RegisterPluginInput represents the input for registering a plugin
type RegisterPluginInput struct {
	Name         string
	Type         string
	Version      string
	Capabilities []string
	Configuration map[string]interface{}
}

// RegisterPluginOutput represents the output after registering a plugin
type RegisterPluginOutput struct {
	ID           string
	Name         string
	Type         string
	Version      string
	Status       string
	Capabilities []string
	RegisteredAt string
}

// Execute registers a new plugin
func (uc *RegisterPluginUseCase) Execute(ctx context.Context, input RegisterPluginInput) (*RegisterPluginOutput, error) {
	// Validate input
	if err := uc.validator.ValidateRegisterPlugin(input); err != nil {
		return nil, err
	}

	// Check if plugin already exists
	exists, err := uc.repo.ExistsByName(ctx, input.Name)
	if err != nil {
		return nil, errors.New("failed to check plugin existence")
	}
	if exists {
		return nil, ErrPluginAlreadyExists
	}

	// Convert string type to domain type
	pluginType, err := parsePluginType(input.Type)
	if err != nil {
		return nil, err
	}

	// Create domain entity using entities structure
	// Use a default entry point for now since it's not in the input
	entryPoint := "main.py"  // or whatever makes sense for your domain
	pluginEntity, err := entities.NewPlugin(input.Name, input.Version, entryPoint, pluginType)
	if err != nil {
		return nil, err
	}
	
	// Set capabilities
	pluginEntity.Capabilities = input.Capabilities
	
	// Set configuration
	pluginEntity.Configuration = input.Configuration

	// Save the plugin
	if err := uc.repo.Save(ctx, pluginEntity); err != nil {
		return nil, errors.New("failed to save plugin")
	}

	// Publish event
	event := PluginRegisteredEvent{
		PluginID:     pluginEntity.ID,
		Name:         pluginEntity.Name,
		Type:         string(pluginEntity.Type),
		Version:      pluginEntity.Version,
		RegisteredAt: time.Now(),
	}

	if err := uc.events.Publish(ctx, event); err != nil {
		// Log error but don't fail
	}

	return &RegisterPluginOutput{
		ID:           pluginEntity.ID.String(),
		Name:         pluginEntity.Name,
		Type:         string(pluginEntity.Type),
		Version:      pluginEntity.Version,
		Status:       string(pluginEntity.Status),
		Capabilities: pluginEntity.Capabilities,
		RegisteredAt: time.Now().Format(time.RFC3339),
	}, nil
}


// ExecuteUpdate updates an existing plugin
func (uc *RegisterPluginUseCase) ExecuteUpdate(ctx context.Context, input UpdatePluginInput) (*RegisterPluginOutput, error) {
	// Validate input
	if err := uc.validator.ValidateUpdatePlugin(input); err != nil {
		return nil, err
	}

	// Get existing plugin
	plugin, err := uc.repo.FindByID(ctx, input.ID)
	if err != nil {
		return nil, err
	}
	if plugin == nil {
		return nil, ErrPluginNotFound
	}

	// Update fields if provided
	if input.Version != "" {
		plugin.Version = input.Version
	}
	if input.Status != "" {
		if status, err := parsePluginStatus(input.Status); err == nil {
			plugin.Status = status
		}
	}
	if input.IsActive != nil {
		plugin.IsActive = *input.IsActive
	}
	if input.Configuration != nil {
		plugin.Configuration = input.Configuration
	}
	if input.Metadata != nil {
		plugin.Metadata = input.Metadata
	}
	if input.Capabilities != nil {
		plugin.Capabilities = input.Capabilities
	}

	// Update timestamp
	plugin.UpdateTimestamp()

	// Save updated plugin
	if err := uc.repo.Save(ctx, plugin); err != nil {
		return nil, err
	}

	// Publish update event
	event := PluginConfigurationUpdatedEvent{
		PluginID:  plugin.ID,
		UpdatedAt: time.Now(),
		Changes:   make(map[string]interface{}),
	}

	if err := uc.events.Publish(ctx, event); err != nil {
		// Log error but don't fail
	}

	return &RegisterPluginOutput{
		ID:           plugin.ID.String(),
		Name:         plugin.Name,
		Type:         string(plugin.Type),
		Version:      plugin.Version,
		Status:       string(plugin.Status),
		Capabilities: plugin.Capabilities,
		RegisteredAt: plugin.CreatedAt.Format(time.RFC3339),
	}, nil
}

// Helper functions

func parsePluginType(typeStr string) (entities.PluginType, error) {
	switch typeStr {
	case "source":
		return entities.PluginTypeSource, nil
	case "target", "destination":
		return entities.PluginTypeTarget, nil
	case "transform", "transformer":
		return entities.PluginTypeTransformer, nil
	case "utility":
		return entities.PluginTypeUtility, nil
	default:
		return "", errors.New("invalid plugin type")
	}
}

func parsePluginStatus(statusStr string) (entities.PluginStatus, error) {
	switch statusStr {
	case "active":
		return entities.PluginStatusActive, nil
	case "inactive":
		return entities.PluginStatusInactive, nil
	case "registered":
		return entities.PluginStatusRegistered, nil
	case "failed":
		return entities.PluginStatusFailed, nil
	default:
		return "", errors.New("invalid plugin status")
	}
}

// Business errors
var (
	ErrPluginAlreadyExists = errors.New("plugin with this name already exists")
)