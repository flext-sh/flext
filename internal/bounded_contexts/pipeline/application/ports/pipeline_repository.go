package ports

import (
	"context"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	"github.com/google/uuid"
)

// ListPipelinesFilter filtros para consulta de pipelines
type ListPipelinesFilter struct {
	Limit  int
	Offset int
	Tags   []string
	Active *bool
}

// PipelineRepository define a interface do repositório de pipelines
type PipelineRepository interface {
	// GetByID busca um pipeline por ID
	GetByID(ctx context.Context, id uuid.UUID) (*entities.Pipeline, error)
	
	// Save persiste um pipeline
	Save(ctx context.Context, pipeline *entities.Pipeline) error
	
	// Delete remove um pipeline
	Delete(ctx context.Context, id uuid.UUID) error
	
	// List lista pipelines com filtros
	List(ctx context.Context, filter ListPipelinesFilter) ([]*entities.Pipeline, int, error)
	
	// GetByName busca um pipeline por nome
	GetByName(ctx context.Context, name string) (*entities.Pipeline, error)
	
	// ExistsByName verifica se existe um pipeline com o nome
	ExistsByName(ctx context.Context, name string) (bool, error)
}