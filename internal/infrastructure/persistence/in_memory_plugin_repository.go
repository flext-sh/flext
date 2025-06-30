package persistence

import (
	"context"
	"errors"
	"sync"

	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/application/ports"
	"github.com/google/uuid"
)

// InMemoryPluginRepository implementação em memória do repositório de plugins
type InMemoryPluginRepository struct {
	mu      sync.RWMutex
	plugins map[uuid.UUID]*entities.Plugin
	byName  map[string]*entities.Plugin
}

// NewInMemoryPluginRepository cria um novo repositório em memória
func NewInMemoryPluginRepository() *InMemoryPluginRepository {
	return &InMemoryPluginRepository{
		plugins: make(map[uuid.UUID]*entities.Plugin),
		byName:  make(map[string]*entities.Plugin),
	}
}

// GetByID busca um plugin por ID
func (r *InMemoryPluginRepository) GetByID(ctx context.Context, id uuid.UUID) (*entities.Plugin, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	plugin, exists := r.plugins[id]
	if !exists {
		return nil, errors.New("plugin not found")
	}
	
	return plugin, nil
}

// Save persiste um plugin
func (r *InMemoryPluginRepository) Save(ctx context.Context, plugin *entities.Plugin) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	// Verificar se nome já existe (para outro plugin)
	if existingPlugin, exists := r.byName[plugin.Name]; exists && existingPlugin.ID != plugin.ID {
		return errors.New("plugin name already exists")
	}
	
	r.plugins[plugin.ID] = plugin
	r.byName[plugin.Name] = plugin
	
	return nil
}

// Delete remove um plugin
func (r *InMemoryPluginRepository) Delete(ctx context.Context, id uuid.UUID) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	plugin, exists := r.plugins[id]
	if !exists {
		return errors.New("plugin not found")
	}
	
	delete(r.plugins, id)
	delete(r.byName, plugin.Name)
	
	return nil
}

// List lista plugins com filtros
func (r *InMemoryPluginRepository) List(ctx context.Context, filter ports.ListPluginsFilter) ([]*entities.Plugin, int, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	var result []*entities.Plugin
	
	// Aplicar filtros
	for _, plugin := range r.plugins {
		// Filtro por tipo
		if filter.Type != nil && plugin.Type != *filter.Type {
			continue
		}
		
		// Filtro por status
		if filter.Status != nil && plugin.Status != *filter.Status {
			continue
		}
		
		// Filtro por autor
		if filter.Author != "" && plugin.Author != filter.Author {
			continue
		}
		
		result = append(result, plugin)
	}
	
	total := len(result)
	
	// Aplicar paginação
	start := filter.Offset
	end := filter.Offset + filter.Limit
	
	if start > len(result) {
		return []*entities.Plugin{}, total, nil
	}
	
	if end > len(result) {
		end = len(result)
	}
	
	return result[start:end], total, nil
}

// GetByName busca um plugin por nome
func (r *InMemoryPluginRepository) GetByName(ctx context.Context, name string) (*entities.Plugin, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	plugin, exists := r.byName[name]
	if !exists {
		return nil, errors.New("plugin not found")
	}
	
	return plugin, nil
}

// ExistsByName verifica se existe um plugin com o nome
func (r *InMemoryPluginRepository) ExistsByName(ctx context.Context, name string) (bool, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	_, exists := r.byName[name]
	return exists, nil
}

// GetActivePlugins busca todos os plugins ativos
func (r *InMemoryPluginRepository) GetActivePlugins(ctx context.Context) ([]*entities.Plugin, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	var result []*entities.Plugin
	
	for _, plugin := range r.plugins {
		if plugin.Status == entities.PluginStatusActive {
			result = append(result, plugin)
		}
	}
	
	return result, nil
}

// GetByType busca plugins por tipo
func (r *InMemoryPluginRepository) GetByType(ctx context.Context, pluginType entities.PluginType) ([]*entities.Plugin, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	var result []*entities.Plugin
	
	for _, plugin := range r.plugins {
		if plugin.Type == pluginType {
			result = append(result, plugin)
		}
	}
	
	return result, nil
}