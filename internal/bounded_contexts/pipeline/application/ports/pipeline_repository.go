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
	// Core CRUD operations
	Save(ctx context.Context, pipeline *entities.Pipeline) error
	Create(ctx context.Context, pipeline *entities.Pipeline) (*entities.Pipeline, error)
	Update(ctx context.Context, pipeline *entities.Pipeline) (*entities.Pipeline, error)
	Delete(ctx context.Context, id uuid.UUID) error

	// Query operations
	GetByID(ctx context.Context, id uuid.UUID) (*entities.Pipeline, error)
	GetByName(ctx context.Context, name string) (*entities.Pipeline, error)
	FindByID(ctx context.Context, id string) (*entities.Pipeline, error) // For string UUID compatibility
	FindByName(ctx context.Context, name string) (*entities.Pipeline, error)
	ExistsByName(ctx context.Context, name string) (bool, error)

	// List operations
	List(ctx context.Context, filter ListPipelinesFilter) ([]*entities.Pipeline, int, error)
	Count(ctx context.Context) (int, error)
}
