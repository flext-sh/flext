package plugin

import (
	"context"

	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	"github.com/google/uuid"
)

// GetPluginUseCase handles plugin retrieval
type GetPluginUseCase struct {
	repo      PluginRepository
	validator InputValidator
}

// NewGetPluginUseCase creates a new get plugin use case
func NewGetPluginUseCase(
	repo PluginRepository,
	validator InputValidator,
) *GetPluginUseCase {
	return &GetPluginUseCase{
		repo:      repo,
		validator: validator,
	}
}

// GetPluginInput represents input for getting a plugin
type GetPluginInput struct {
	ID uuid.UUID `json:"id" validate:"required"`
}

// GetPluginByNameInput represents input for getting a plugin by name
type GetPluginByNameInput struct {
	Name string `json:"name" validate:"required"`
}

// PluginHealthCheckInput represents input for plugin health check
type PluginHealthCheckInput struct {
	ID uuid.UUID `json:"id" validate:"required"`
}

// PluginResult represents the output of plugin operations
type PluginResult struct {
	ID            uuid.UUID              `json:"id"`
	Name          string                 `json:"name"`
	Type          string                 `json:"type"`
	Version       string                 `json:"version"`
	Description   string                 `json:"description"`
	Author        string                 `json:"author"`
	Status        string                 `json:"status"`
	EntryPoint    string                 `json:"entry_point"`
	Capabilities  []string               `json:"capabilities"`
	Configuration map[string]interface{} `json:"configuration"`
	Metadata      map[string]interface{} `json:"metadata"`
	IsActive      bool                   `json:"is_active"`
	CreatedAt     string                 `json:"created_at"`
	UpdatedAt     string                 `json:"updated_at"`
}

// PluginHealthResult represents plugin health check result
type PluginHealthResult struct {
	PluginID  uuid.UUID `json:"plugin_id"`
	Status    string    `json:"status"`
	Healthy   bool      `json:"healthy"`
	Message   string    `json:"message,omitempty"`
	CheckedAt string    `json:"checked_at"`
}

// Execute retrieves a plugin by ID
func (uc *GetPluginUseCase) Execute(ctx context.Context, input GetPluginInput) (*PluginResult, error) {
	// Validate input
	if err := uc.validator.ValidateGetPlugin(input); err != nil {
		return nil, err
	}

	// Find plugin
	plugin, err := uc.repo.FindByID(ctx, input.ID)
	if err != nil {
		return nil, err
	}
	if plugin == nil {
		return nil, ErrPluginNotFound
	}

	return uc.mapToResult(plugin), nil
}

// ExecuteByName retrieves a plugin by name
func (uc *GetPluginUseCase) ExecuteByName(ctx context.Context, input GetPluginByNameInput) (*PluginResult, error) {
	// Validate input
	if err := uc.validator.ValidateGetPluginByName(input); err != nil {
		return nil, err
	}

	// Find plugin
	plugin, err := uc.repo.FindByName(ctx, input.Name)
	if err != nil {
		return nil, err
	}
	if plugin == nil {
		return nil, ErrPluginNotFound
	}

	return uc.mapToResult(plugin), nil
}

// ExecuteHealthCheck performs a health check on a plugin
func (uc *GetPluginUseCase) ExecuteHealthCheck(ctx context.Context, input PluginHealthCheckInput) (*PluginHealthResult, error) {
	// Validate input
	if err := uc.validator.ValidatePluginHealthCheck(input); err != nil {
		return nil, err
	}

	// Find plugin
	plugin, err := uc.repo.FindByID(ctx, input.ID)
	if err != nil {
		return nil, err
	}
	if plugin == nil {
		return nil, ErrPluginNotFound
	}

	// Perform health check
	healthy := plugin.Status == entities.PluginStatusActive
	status := "healthy"
	message := ""

	if !healthy {
		status = "unhealthy"
		message = "Plugin is not in active status"
	}

	return &PluginHealthResult{
		PluginID:  plugin.ID,
		Status:    status,
		Healthy:   healthy,
		Message:   message,
		CheckedAt: "2024-01-01T00:00:00Z", // In real implementation, use current time
	}, nil
}

// mapToResult converts a plugin entity to result DTO
func (uc *GetPluginUseCase) mapToResult(plugin *entities.Plugin) *PluginResult {
	return &PluginResult{
		ID:            plugin.ID,
		Name:          plugin.Name,
		Type:          string(plugin.Type),
		Version:       plugin.Version,
		Description:   plugin.Description,
		Author:        plugin.Author,
		Status:        string(plugin.Status),
		EntryPoint:    plugin.EntryPoint,
		Capabilities:  plugin.Capabilities,
		Configuration: plugin.Configuration,
		Metadata:      plugin.Metadata,
		IsActive:      plugin.IsActive,
		CreatedAt:     plugin.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
		UpdatedAt:     plugin.UpdatedAt.Format("2006-01-02T15:04:05Z07:00"),
	}
}
