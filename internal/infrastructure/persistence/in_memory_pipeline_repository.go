package persistence

import (
	"context"
	"errors"
	"sync"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
	"github.com/google/uuid"
)

// InMemoryPipelineRepository implementação em memória do repositório de pipelines
type InMemoryPipelineRepository struct {
	mu        sync.RWMutex
	pipelines map[uuid.UUID]*entities.Pipeline
	byName    map[string]*entities.Pipeline
}

// NewInMemoryPipelineRepository cria um novo repositório em memória
func NewInMemoryPipelineRepository() *InMemoryPipelineRepository {
	return &InMemoryPipelineRepository{
		pipelines: make(map[uuid.UUID]*entities.Pipeline),
		byName:    make(map[string]*entities.Pipeline),
	}
}

// GetByID busca um pipeline por ID
func (r *InMemoryPipelineRepository) GetByID(ctx context.Context, id uuid.UUID) (*entities.Pipeline, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	pipeline, exists := r.pipelines[id]
	if !exists {
		return nil, errors.New("pipeline not found")
	}
	
	return pipeline, nil
}

// Save persiste um pipeline
func (r *InMemoryPipelineRepository) Save(ctx context.Context, pipeline *entities.Pipeline) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	// Verificar se nome já existe (para outro pipeline)
	if existingPipeline, exists := r.byName[pipeline.Name]; exists && existingPipeline.ID != pipeline.ID {
		return errors.New("pipeline name already exists")
	}
	
	r.pipelines[pipeline.ID] = pipeline
	r.byName[pipeline.Name] = pipeline
	
	return nil
}

// Delete remove um pipeline
func (r *InMemoryPipelineRepository) Delete(ctx context.Context, id uuid.UUID) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	pipeline, exists := r.pipelines[id]
	if !exists {
		return errors.New("pipeline not found")
	}
	
	delete(r.pipelines, id)
	delete(r.byName, pipeline.Name)
	
	return nil
}

// List lista pipelines com filtros
func (r *InMemoryPipelineRepository) List(ctx context.Context, filter ports.ListPipelinesFilter) ([]*entities.Pipeline, int, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	var result []*entities.Pipeline
	
	// Aplicar filtros
	for _, pipeline := range r.pipelines {
		// Filtro por status ativo
		if filter.Active != nil && pipeline.IsActive != *filter.Active {
			continue
		}
		
		// Filtro por tags (simplificado - verifica se pipeline tem pelo menos uma das tags)
		if len(filter.Tags) > 0 {
			hasTag := false
			for _, filterTag := range filter.Tags {
				for _, pipelineTag := range pipeline.Tags {
					if pipelineTag == filterTag {
						hasTag = true
						break
					}
				}
				if hasTag {
					break
				}
			}
			if !hasTag {
				continue
			}
		}
		
		result = append(result, pipeline)
	}
	
	total := len(result)
	
	// Aplicar paginação
	start := filter.Offset
	end := filter.Offset + filter.Limit
	
	if start > len(result) {
		return []*entities.Pipeline{}, total, nil
	}
	
	if end > len(result) {
		end = len(result)
	}
	
	return result[start:end], total, nil
}

// GetByName busca um pipeline por nome
func (r *InMemoryPipelineRepository) GetByName(ctx context.Context, name string) (*entities.Pipeline, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	pipeline, exists := r.byName[name]
	if !exists {
		return nil, errors.New("pipeline not found")
	}
	
	return pipeline, nil
}

// ExistsByName verifica se existe um pipeline com o nome
func (r *InMemoryPipelineRepository) ExistsByName(ctx context.Context, name string) (bool, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	_, exists := r.byName[name]
	return exists, nil
}