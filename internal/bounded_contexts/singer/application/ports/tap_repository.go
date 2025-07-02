package ports

import (
	"context"

	"github.com/flext-sh/flext/internal/bounded_contexts/singer/domain/entities"
	"github.com/google/uuid"
)

// TapRepository define a interface para persistencia de taps
type TapRepository interface {
	// Basic CRUD operations
	Save(ctx context.Context, tap *entities.Tap) error
	GetByID(ctx context.Context, id uuid.UUID) (*entities.Tap, error)
	GetByName(ctx context.Context, name string) (*entities.Tap, error)
	Update(ctx context.Context, tap *entities.Tap) (*entities.Tap, error)
	Delete(ctx context.Context, id uuid.UUID) error

	// Query operations
	List(ctx context.Context, options QueryOptions) ([]*entities.Tap, error)
	Count(ctx context.Context, options QueryOptions) (int, error)

	// Business-specific operations
	GetInstalledTaps(ctx context.Context) ([]*entities.Tap, error)
	GetTapsByType(ctx context.Context, tapType entities.TapType) ([]*entities.Tap, error)
	GetTapsByStatus(ctx context.Context, status entities.TapStatus) ([]*entities.Tap, error)

	// Advanced queries
	SearchTaps(ctx context.Context, query string, options QueryOptions) ([]*entities.Tap, error)
	GetTapsByTags(ctx context.Context, tags []string) ([]*entities.Tap, error)
	GetMostUsedTaps(ctx context.Context, limit int) ([]*entities.Tap, error)
	GetRecentlyUsedTaps(ctx context.Context, limit int) ([]*entities.Tap, error)
}

// QueryOptions define opcoes para consultas
type QueryOptions struct {
	// Pagination
	Limit  int
	Offset int

	// Sorting
	SortBy    string
	SortOrder string // "asc" or "desc"

	// Filtering
	Filters map[string]interface{}

	// Include related data
	IncludeMetadata bool
	IncludeUsage    bool
}
