package memory

import (
	"context"
	"sync"

	"github.com/flext-sh/flext/internal/infrastructure/persistence"
)

// PluginStore implements persistence.PluginStore in memory
type PluginStore struct {
	mu      sync.RWMutex
	plugins map[string]*persistence.PluginModel
	byName  map[string]string // name -> id mapping
}

// NewPluginStore creates a new in-memory plugin store
func NewPluginStore() *PluginStore {
	return &PluginStore{
		plugins: make(map[string]*persistence.PluginModel),
		byName:  make(map[string]string),
	}
}

// Create inserts a new plugin
func (s *PluginStore) Create(ctx context.Context, model *persistence.PluginModel) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Check if already exists
	if _, exists := s.plugins[model.ID]; exists {
		return persistence.ErrAlreadyExists
	}

	// Check if name already exists
	if _, exists := s.byName[model.Name]; exists {
		return persistence.ErrAlreadyExists
	}

	// Clone to avoid external modifications
	stored := s.cloneModel(model)
	s.plugins[model.ID] = stored
	s.byName[model.Name] = model.ID

	return nil
}

// GetByID retrieves a plugin by ID
func (s *PluginStore) GetByID(ctx context.Context, id string) (*persistence.PluginModel, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	model, exists := s.plugins[id]
	if !exists {
		return nil, persistence.ErrNotFound
	}

	return s.cloneModel(model), nil
}

// GetByName retrieves a plugin by name
func (s *PluginStore) GetByName(ctx context.Context, name string) (*persistence.PluginModel, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	id, exists := s.byName[name]
	if !exists {
		return nil, persistence.ErrNotFound
	}

	model, exists := s.plugins[id]
	if !exists {
		return nil, persistence.ErrNotFound
	}

	return s.cloneModel(model), nil
}

// Update updates an existing plugin
func (s *PluginStore) Update(ctx context.Context, model *persistence.PluginModel) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	existing, exists := s.plugins[model.ID]
	if !exists {
		return persistence.ErrNotFound
	}

	// If name changed, update mapping
	if existing.Name != model.Name {
		delete(s.byName, existing.Name)
		s.byName[model.Name] = model.ID
	}

	// Update
	s.plugins[model.ID] = s.cloneModel(model)

	return nil
}

// Delete removes a plugin
func (s *PluginStore) Delete(ctx context.Context, id string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	model, exists := s.plugins[id]
	if !exists {
		return persistence.ErrNotFound
	}

	delete(s.plugins, id)
	delete(s.byName, model.Name)

	return nil
}

// List retrieves plugins with pagination
func (s *PluginStore) List(ctx context.Context, limit, offset int) ([]*persistence.PluginModel, int, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	// Collect all plugins
	var results []*persistence.PluginModel
	for _, model := range s.plugins {
		results = append(results, s.cloneModel(model))
	}

	total := len(results)

	// Apply pagination
	start := offset
	if start >= len(results) {
		return []*persistence.PluginModel{}, total, nil
	}

	end := start + limit
	if end > len(results) {
		end = len(results)
	}

	return results[start:end], total, nil
}

// ListByType retrieves plugins by type
func (s *PluginStore) ListByType(ctx context.Context, pluginType string) ([]*persistence.PluginModel, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	var results []*persistence.PluginModel
	for _, model := range s.plugins {
		if model.Type == pluginType {
			results = append(results, s.cloneModel(model))
		}
	}

	return results, nil
}

// ListActive retrieves active plugins
func (s *PluginStore) ListActive(ctx context.Context) ([]*persistence.PluginModel, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	var results []*persistence.PluginModel
	for _, model := range s.plugins {
		if model.Status == "active" {
			results = append(results, s.cloneModel(model))
		}
	}

	return results, nil
}

// Helper methods

func (s *PluginStore) cloneModel(model *persistence.PluginModel) *persistence.PluginModel {
	// Deep clone to prevent external modifications
	clone := *model

	// Clone slices
	clone.Capabilities = append([]string{}, model.Capabilities...)

	// Clone maps
	if model.Configuration != nil {
		clone.Configuration = make(map[string]interface{})
		for k, v := range model.Configuration {
			clone.Configuration[k] = v
		}
	}

	return &clone
}
