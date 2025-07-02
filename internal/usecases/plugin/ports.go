package plugin

import (
	"context"
	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	"github.com/google/uuid"
)

// PluginRepository defines the interface for plugin persistence
// This interface is declared by the use case layer (Dependency Inversion)
type PluginRepository interface {
	Save(ctx context.Context, plugin *entities.Plugin) error
	FindByID(ctx context.Context, id uuid.UUID) (*entities.Plugin, error)
	FindByName(ctx context.Context, name string) (*entities.Plugin, error)
	ExistsByName(ctx context.Context, name string) (bool, error)
	List(ctx context.Context, criteria ListCriteria) ([]*entities.Plugin, int, error)
	ListByType(ctx context.Context, pluginType entities.PluginType) ([]*entities.Plugin, error)
	ListActive(ctx context.Context) ([]*entities.Plugin, error)
	Delete(ctx context.Context, id uuid.UUID) error
}

// EventPublisher defines the interface for publishing domain events
type EventPublisher interface {
	Publish(ctx context.Context, event interface{}) error
}

// InputValidator defines the interface for validating use case inputs
type InputValidator interface {
	ValidateRegisterPlugin(input RegisterPluginInput) error
	ValidateActivatePlugin(input ActivatePluginInput) error
	ValidateUpdatePlugin(input UpdatePluginInput) error
	ValidateGetPlugin(input GetPluginInput) error
	ValidateGetPluginByName(input GetPluginByNameInput) error
	ValidateListPlugins(input ListPluginsInput) error
	ValidateListPluginsByType(input ListPluginsByTypeInput) error
	ValidateDeletePlugin(input DeletePluginInput) error
	ValidatePluginHealthCheck(input PluginHealthCheckInput) error
}

// ListCriteria represents criteria for listing plugins
type ListCriteria struct {
	Limit    int
	Offset   int
	Type     *entities.PluginType
	Status   *entities.PluginStatus
	OrderBy  string
	OrderDir string
}