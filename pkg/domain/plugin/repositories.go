package domain

import (
	"context"

	"github.com/flext-sh/flext/pkg/domain/plugin/domain/entities"
	"github.com/google/uuid"
)

// PluginRepository defines the interface for plugin persistence
type PluginRepository interface {
	Save(ctx context.Context, plugin *entities.Plugin) error
	FindByID(ctx context.Context, id uuid.UUID) (*entities.Plugin, error)
	FindAll(ctx context.Context, limit, offset int) ([]*entities.Plugin, error)
	Update(ctx context.Context, plugin *entities.Plugin) error
	Delete(ctx context.Context, id uuid.UUID) error
	FindByName(ctx context.Context, name string) (*entities.Plugin, error)
	FindByType(ctx context.Context, pluginType string) ([]*entities.Plugin, error)
	FindByStatus(ctx context.Context, status string) ([]*entities.Plugin, error)
}
