package gateways

import (
	"context"
	"errors"

	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	"github.com/flext-sh/flext/internal/infrastructure/persistence"
	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	pipelineUseCases "github.com/flext-sh/flext/internal/usecases/pipeline"
	pluginUseCases "github.com/flext-sh/flext/internal/usecases/plugin"
	"github.com/google/uuid"
)

// PluginRepositoryGateway adapts the infrastructure persistence to the use case interface
type PluginRepositoryGateway struct {
	store persistence.PluginStore
}

// NewPluginRepositoryGateway creates a new repository gateway
func NewPluginRepositoryGateway(store persistence.PluginStore) *PluginRepositoryGateway {
	return &PluginRepositoryGateway{
		store: store,
	}
}

// Save persists a plugin
func (g *PluginRepositoryGateway) Save(ctx context.Context, p *entities.Plugin) error {
	// Convert domain entity to persistence model
	model := g.domainToPersistence(p)

	// Check if it's an update or create
	existing, err := g.store.GetByID(ctx, p.ID.String())
	if err != nil && !errors.Is(err, persistence.ErrNotFound) {
		return err
	}

	if existing != nil {
		// Update
		return g.store.Update(ctx, model)
	}

	// Create
	return g.store.Create(ctx, model)
}

// FindByID retrieves a plugin by ID
func (g *PluginRepositoryGateway) FindByID(ctx context.Context, id uuid.UUID) (*entities.Plugin, error) {
	// Fetch from store
	model, err := g.store.GetByID(ctx, id.String())
	if err != nil {
		if errors.Is(err, persistence.ErrNotFound) {
			return nil, nil
		}
		return nil, err
	}

	// Convert to domain entity
	return g.persistenceToDomain(model)
}

// FindByName retrieves a plugin by name
func (g *PluginRepositoryGateway) FindByName(ctx context.Context, name string) (*entities.Plugin, error) {
	// Fetch from store
	model, err := g.store.GetByName(ctx, name)
	if err != nil {
		if errors.Is(err, persistence.ErrNotFound) {
			return nil, nil
		}
		return nil, err
	}

	// Convert to domain entity
	return g.persistenceToDomain(model)
}

// ExistsByName checks if a plugin exists with the given name
func (g *PluginRepositoryGateway) ExistsByName(ctx context.Context, name string) (bool, error) {
	_, err := g.store.GetByName(ctx, name)
	if err != nil {
		if errors.Is(err, persistence.ErrNotFound) {
			return false, nil
		}
		return false, err
	}
	return true, nil
}

// List retrieves plugins based on criteria
func (g *PluginRepositoryGateway) List(ctx context.Context, criteria pluginUseCases.ListCriteria) ([]*entities.Plugin, int, error) {
	// For simplicity, using basic list with pagination
	models, total, err := g.store.List(ctx, criteria.Limit, criteria.Offset)
	if err != nil {
		return nil, 0, err
	}

	// Convert to domain entities
	plugins := make([]*entities.Plugin, 0, len(models))
	for _, model := range models {
		p, err := g.persistenceToDomain(model)
		if err != nil {
			return nil, 0, err
		}

		// Apply filters
		if criteria.Type != nil && p.Type != *criteria.Type {
			continue
		}
		if criteria.Status != nil && p.Status != *criteria.Status {
			continue
		}

		plugins = append(plugins, p)
	}

	return plugins, total, nil
}

// ListByType retrieves plugins by type
func (g *PluginRepositoryGateway) ListByType(ctx context.Context, pluginType entities.PluginType) ([]*entities.Plugin, error) {
	// Fetch from store with default pagination (all results)
	models, _, err := g.store.ListByType(ctx, string(pluginType), 1000, 0)
	if err != nil {
		return nil, err
	}

	// Convert to domain entities
	plugins := make([]*entities.Plugin, len(models))
	for i, model := range models {
		p, err := g.persistenceToDomain(model)
		if err != nil {
			return nil, err
		}
		plugins[i] = p
	}

	return plugins, nil
}

// ListActive retrieves active plugins
func (g *PluginRepositoryGateway) ListActive(ctx context.Context) ([]*entities.Plugin, error) {
	// Fetch from store with default pagination (all results)
	models, _, err := g.store.ListActive(ctx, 1000, 0)
	if err != nil {
		return nil, err
	}

	// Convert to domain entities
	plugins := make([]*entities.Plugin, len(models))
	for i, model := range models {
		p, err := g.persistenceToDomain(model)
		if err != nil {
			return nil, err
		}
		plugins[i] = p
	}

	return plugins, nil
}

// Delete removes a plugin
func (g *PluginRepositoryGateway) Delete(ctx context.Context, id uuid.UUID) error {
	return g.store.Delete(ctx, id.String())
}

// Conversion methods

func (g *PluginRepositoryGateway) domainToPersistence(p *entities.Plugin) *persistence.PluginModel {
	return &persistence.PluginModel{
		ID:            p.ID.String(),
		Name:          p.Name,
		Type:          string(p.Type),
		Version:       p.Version,
		Status:        string(p.Status),
		Configuration: p.Configuration,
		Capabilities:  p.Capabilities,
	}
}

func (g *PluginRepositoryGateway) persistenceToDomain(model *persistence.PluginModel) (*entities.Plugin, error) {
	// Parse ID
	id, err := uuid.Parse(model.ID)
	if err != nil {
		return nil, err
	}

	// Parse type
	pluginType := entities.PluginType(model.Type)

	// Parse status
	status := entities.PluginStatus(model.Status)

	// Create plugin directly with struct literal
	plugin := &entities.Plugin{
		AggregateRoot: domain.NewAggregateRoot(),
		Name:          model.Name,
		Type:          pluginType,
		Version:       model.Version,
		Status:        status,
		Configuration: model.Configuration,
		Capabilities:  model.Capabilities,
	}
	
	// Set the ID (which is part of AggregateRoot)
	plugin.ID = id

	return plugin, nil
}

// Implement PluginRegistry interface methods (for pipeline use cases)

// GetPlugin retrieves plugin information
func (g *PluginRepositoryGateway) GetPlugin(ctx context.Context, id uuid.UUID) (*pipelineUseCases.PluginInfo, error) {
	p, err := g.FindByID(ctx, id)
	if err != nil {
		return nil, err
	}
	if p == nil {
		return nil, errors.New("plugin not found")
	}

	return &pipelineUseCases.PluginInfo{
		ID:           p.ID,
		Name:         p.Name,
		Type:         string(p.Type),
		Version:      p.Version,
		IsActive:     p.Status == entities.PluginStatusActive,
		Capabilities: p.Capabilities,
	}, nil
}

// ValidatePlugin checks if a plugin is valid
func (g *PluginRepositoryGateway) ValidatePlugin(ctx context.Context, id uuid.UUID) error {
	p, err := g.FindByID(ctx, id)
	if err != nil {
		return err
	}
	if p == nil {
		return errors.New("plugin not found")
	}

	return p.CanExecute()
}
