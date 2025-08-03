package plugin

import (
	"context"

	"github.com/flext-sh/flext/pkg/domain/plugin/domain/entities"
)

// ListPluginsUseCase handles listing plugins with criteria
type ListPluginsUseCase struct {
	repo      PluginRepository
	validator InputValidator
}

// NewListPluginsUseCase creates a new list plugins use case
func NewListPluginsUseCase(
	repo PluginRepository,
	validator InputValidator,
) *ListPluginsUseCase {
	return &ListPluginsUseCase{
		repo:      repo,
		validator: validator,
	}
}

// ListPluginsInput represents input for listing plugins
type ListPluginsInput struct {
	Limit    int     `json:"limit" validate:"min=1,max=1000"`
	Offset   int     `json:"offset" validate:"min=0"`
	Type     *string `json:"type,omitempty"`
	Status   *string `json:"status,omitempty"`
	OrderBy  string  `json:"order_by,omitempty"`
	OrderDir string  `json:"order_dir,omitempty"`
}

// ListPluginsByTypeInput represents input for listing plugins by type
type ListPluginsByTypeInput struct {
	Type string `json:"type" validate:"required"`
}

// ListPluginsResult represents the result of listing plugins
type ListPluginsResult struct {
	Plugins []PluginListItem `json:"plugins"`
	Total   int              `json:"total"`
	Limit   int              `json:"limit"`
	Offset  int              `json:"offset"`
}

// PluginListItem represents a plugin in the list result
type PluginListItem struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	Type        string `json:"type"`
	Version     string `json:"version"`
	Description string `json:"description"`
	Author      string `json:"author"`
	Status      string `json:"status"`
	IsActive    bool   `json:"is_active"`
	CreatedAt   string `json:"created_at"`
	UpdatedAt   string `json:"updated_at"`
}

// Execute lists plugins based on criteria
func (uc *ListPluginsUseCase) Execute(ctx context.Context, input ListPluginsInput) (*ListPluginsResult, error) {
	// Set defaults
	if input.Limit == 0 {
		input.Limit = 10
	}
	if input.OrderBy == "" {
		input.OrderBy = "created_at"
	}
	if input.OrderDir == "" {
		input.OrderDir = "DESC"
	}

	// Validate input
	if err := uc.validator.ValidateListPlugins(input); err != nil {
		return nil, err
	}

	// Convert to repository criteria
	criteria := ListCriteria{
		Limit:    input.Limit,
		Offset:   input.Offset,
		OrderBy:  input.OrderBy,
		OrderDir: input.OrderDir,
	}

	// Set type filter if provided
	if input.Type != nil {
		pluginType := entities.PluginType(*input.Type)
		criteria.Type = &pluginType
	}

	// Set status filter if provided
	if input.Status != nil {
		pluginStatus := entities.PluginStatus(*input.Status)
		criteria.Status = &pluginStatus
	}

	// Get plugins from repository
	plugins, total, err := uc.repo.List(ctx, criteria)
	if err != nil {
		return nil, err
	}

	// Convert to result DTOs
	results := make([]PluginListItem, len(plugins))
	for i, plugin := range plugins {
		results[i] = PluginListItem{
			ID:          plugin.ID.String(),
			Name:        plugin.Name,
			Type:        string(plugin.Type),
			Version:     plugin.Version,
			Description: plugin.Description,
			Author:      plugin.Author,
			Status:      string(plugin.Status),
			IsActive:    plugin.IsActive,
			CreatedAt:   plugin.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
			UpdatedAt:   plugin.UpdatedAt.Format("2006-01-02T15:04:05Z07:00"),
		}
	}

	return &ListPluginsResult{
		Plugins: results,
		Total:   total,
		Limit:   input.Limit,
		Offset:  input.Offset,
	}, nil
}

// ExecuteActive lists all active plugins
func (uc *ListPluginsUseCase) ExecuteActive(ctx context.Context) (*ListPluginsResult, error) {
	// Get active plugins from repository
	plugins, err := uc.repo.ListActive(ctx)
	if err != nil {
		return nil, err
	}

	// Convert to result DTOs
	results := make([]PluginListItem, len(plugins))
	for i, plugin := range plugins {
		results[i] = PluginListItem{
			ID:          plugin.ID.String(),
			Name:        plugin.Name,
			Type:        string(plugin.Type),
			Version:     plugin.Version,
			Description: plugin.Description,
			Author:      plugin.Author,
			Status:      string(plugin.Status),
			IsActive:    true, // All active plugins
			CreatedAt:   plugin.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
			UpdatedAt:   plugin.UpdatedAt.Format("2006-01-02T15:04:05Z07:00"),
		}
	}

	return &ListPluginsResult{
		Plugins: results,
		Total:   len(results),
		Limit:   len(results),
		Offset:  0,
	}, nil
}

// ExecuteByType lists plugins by type
func (uc *ListPluginsUseCase) ExecuteByType(ctx context.Context, input ListPluginsByTypeInput) (*ListPluginsResult, error) {
	// Validate input
	if err := uc.validator.ValidateListPluginsByType(input); err != nil {
		return nil, err
	}

	// Convert type to entity type
	pluginType := entities.PluginType(input.Type)

	// Get plugins by type from repository
	plugins, err := uc.repo.ListByType(ctx, pluginType)
	if err != nil {
		return nil, err
	}

	// Convert to result DTOs
	results := make([]PluginListItem, len(plugins))
	for i, plugin := range plugins {
		results[i] = PluginListItem{
			ID:          plugin.ID.String(),
			Name:        plugin.Name,
			Type:        string(plugin.Type),
			Version:     plugin.Version,
			Description: plugin.Description,
			Author:      plugin.Author,
			Status:      string(plugin.Status),
			IsActive:    plugin.IsActive,
			CreatedAt:   plugin.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
			UpdatedAt:   plugin.UpdatedAt.Format("2006-01-02T15:04:05Z07:00"),
		}
	}

	return &ListPluginsResult{
		Plugins: results,
		Total:   len(results),
		Limit:   len(results),
		Offset:  0,
	}, nil
}
