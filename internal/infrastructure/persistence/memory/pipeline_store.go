package memory

import (
	"context"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/persistence"
)

// PipelineStore implements persistence.PipelineStore in memory
type PipelineStore struct {
	mu        sync.RWMutex
	pipelines map[string]*persistence.PipelineModel
	byName    map[string]string // name -> id mapping
}

// NewPipelineStore creates a new in-memory pipeline store
func NewPipelineStore() *PipelineStore {
	return &PipelineStore{
		pipelines: make(map[string]*persistence.PipelineModel),
		byName:    make(map[string]string),
	}
}

// Create inserts a new pipeline
func (s *PipelineStore) Create(ctx context.Context, model *persistence.PipelineModel) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Check if already exists
	if _, exists := s.pipelines[model.ID]; exists {
		return persistence.ErrAlreadyExists
	}

	// Check if name already exists
	if _, exists := s.byName[model.Name]; exists {
		return persistence.ErrAlreadyExists
	}

	// Set timestamps if not set
	now := time.Now().Format(time.RFC3339)
	if model.CreatedAt == "" {
		model.CreatedAt = now
	}
	if model.UpdatedAt == "" {
		model.UpdatedAt = now
	}
	if model.Version == 0 {
		model.Version = 1
	}

	// Clone to avoid external modifications
	stored := s.cloneModel(model)
	s.pipelines[model.ID] = stored
	s.byName[model.Name] = model.ID

	return nil
}

// GetByID retrieves a pipeline by ID
func (s *PipelineStore) GetByID(ctx context.Context, id string) (*persistence.PipelineModel, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	model, exists := s.pipelines[id]
	if !exists {
		return nil, persistence.ErrNotFound
	}

	return s.cloneModel(model), nil
}

// GetByName retrieves a pipeline by name
func (s *PipelineStore) GetByName(ctx context.Context, name string) (*persistence.PipelineModel, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	id, exists := s.byName[name]
	if !exists {
		return nil, persistence.ErrNotFound
	}

	model, exists := s.pipelines[id]
	if !exists {
		return nil, persistence.ErrNotFound
	}

	return s.cloneModel(model), nil
}

// Update updates an existing pipeline
func (s *PipelineStore) Update(ctx context.Context, model *persistence.PipelineModel) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	existing, exists := s.pipelines[model.ID]
	if !exists {
		return persistence.ErrNotFound
	}

	// Check version for optimistic locking
	if existing.Version != model.Version {
		return persistence.ErrNotFound // Simulating version mismatch as not found
	}

	// If name changed, update mapping
	if existing.Name != model.Name {
		delete(s.byName, existing.Name)
		s.byName[model.Name] = model.ID
	}

	// Update
	model.Version++
	model.UpdatedAt = time.Now().Format(time.RFC3339)
	s.pipelines[model.ID] = s.cloneModel(model)

	return nil
}

// Delete removes a pipeline
func (s *PipelineStore) Delete(ctx context.Context, id string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	model, exists := s.pipelines[id]
	if !exists {
		return persistence.ErrNotFound
	}

	delete(s.pipelines, id)
	delete(s.byName, model.Name)

	return nil
}

// List retrieves pipelines with filtering
func (s *PipelineStore) List(ctx context.Context, filter persistence.PipelineFilter) ([]*persistence.PipelineModel, int, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	// Collect all matching pipelines
	var results []*persistence.PipelineModel
	for _, model := range s.pipelines {
		// Apply filters
		if filter.Active != nil && model.IsActive != *filter.Active {
			continue
		}

		if len(filter.Tags) > 0 && !s.hasAnyTag(model.Tags, filter.Tags) {
			continue
		}

		results = append(results, s.cloneModel(model))
	}

	total := len(results)

	// Apply pagination
	start := filter.Offset
	if start >= len(results) {
		return []*persistence.PipelineModel{}, total, nil
	}

	end := start + filter.Limit
	if end > len(results) {
		end = len(results)
	}

	return results[start:end], total, nil
}

// ExistsByName checks if a pipeline exists with the given name
func (s *PipelineStore) ExistsByName(ctx context.Context, name string) (bool, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	_, exists := s.byName[name]
	return exists, nil
}

// BeginTx starts a new transaction (not supported in memory)
func (s *PipelineStore) BeginTx(ctx context.Context) (persistence.Transaction, error) {
	// Transactions not supported in memory implementation
	return &memoryTx{store: s}, nil
}

// Helper methods

func (s *PipelineStore) cloneModel(model *persistence.PipelineModel) *persistence.PipelineModel {
	// Deep clone to prevent external modifications
	clone := *model
	
	// Clone slices
	clone.Tags = append([]string{}, model.Tags...)
	clone.Steps = make([]persistence.StepModel, len(model.Steps))
	copy(clone.Steps, model.Steps)
	
	// Clone maps
	if model.Configuration != nil {
		clone.Configuration = make(map[string]interface{})
		for k, v := range model.Configuration {
			clone.Configuration[k] = v
		}
	}
	
	return &clone
}

func (s *PipelineStore) hasAnyTag(modelTags, filterTags []string) bool {
	for _, filterTag := range filterTags {
		for _, modelTag := range modelTags {
			if modelTag == filterTag {
				return true
			}
		}
	}
	return false
}

// memoryTx implements persistence.Transaction for memory store
type memoryTx struct {
	store *PipelineStore
}

func (t *memoryTx) Commit() error {
	// No-op for memory store
	return nil
}

func (t *memoryTx) Rollback() error {
	// No-op for memory store
	return nil
}

func (t *memoryTx) CreatePipeline(ctx context.Context, model *persistence.PipelineModel) error {
	return t.store.Create(ctx, model)
}

func (t *memoryTx) UpdatePipeline(ctx context.Context, model *persistence.PipelineModel) error {
	return t.store.Update(ctx, model)
}

func (t *memoryTx) CreateStep(ctx context.Context, model *persistence.StepModel) error {
	// Not implemented for simplicity
	return nil
}

func (t *memoryTx) DeleteStepsByPipelineID(ctx context.Context, pipelineID string) error {
	// Not implemented for simplicity
	return nil
}