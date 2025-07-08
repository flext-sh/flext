package ports

import (
	"context"

	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	"github.com/google/uuid"
)

// ListPluginsFilter filtros para consulta de plugins
type ListPluginsFilter struct {
	Limit  int
	Offset int
	Type   *entities.PluginType
	Status *entities.PluginStatus
	Author string
}

// PluginRepository define a interface do repositório de plugins
type PluginRepository interface {
	// GetByID busca um plugin por ID
	GetByID(ctx context.Context, id uuid.UUID) (*entities.Plugin, error)

	// Save persiste um plugin
	Save(ctx context.Context, plugin *entities.Plugin) error

	// Delete remove um plugin
	Delete(ctx context.Context, id uuid.UUID) error

	// List lista plugins com filtros
	List(ctx context.Context, filter ListPluginsFilter) ([]*entities.Plugin, int, error)

	// GetByName busca um plugin por nome
	GetByName(ctx context.Context, name string) (*entities.Plugin, error)

	// ExistsByName verifica se existe um plugin com o nome
	ExistsByName(ctx context.Context, name string) (bool, error)

	// GetActivePlugins busca todos os plugins ativos
	GetActivePlugins(ctx context.Context) ([]*entities.Plugin, error)

	// GetByType busca plugins por tipo
	GetByType(ctx context.Context, pluginType entities.PluginType) ([]*entities.Plugin, error)
}
