package persistence

import (
	"context"
	"errors"
)

// Common errors
var (
	ErrNotFound          = errors.New("record not found")
	ErrAlreadyExists     = errors.New("record already exists")
	ErrInvalidData       = errors.New("invalid data")
	ErrTransactionFailed = errors.New("transaction failed")
)

// PipelineModel represents the database model for pipeline
type PipelineModel struct {
	ID            string                 `db:"id"`
	Name          string                 `db:"name"`
	Description   string                 `db:"description"`
	IsActive      bool                   `db:"is_active"`
	Tags          []string               `db:"tags"`
	Configuration map[string]interface{} `db:"configuration"`
	Steps         []StepModel            `db:"-"` // Loaded separately
	Version       int                    `db:"version"`
	CreatedAt     string                 `db:"created_at"`
	UpdatedAt     string                 `db:"updated_at"`
}

// StepModel represents the database model for pipeline step
type StepModel struct {
	ID            string                 `db:"id"`
	PipelineID    string                 `db:"pipeline_id"`
	Name          string                 `db:"name"`
	PluginID      string                 `db:"plugin_id"`
	Configuration map[string]interface{} `db:"configuration"`
	DependsOn     []string               `db:"depends_on"`
	Order         int                    `db:"step_order"`
	CreatedAt     string                 `db:"created_at"`
	UpdatedAt     string                 `db:"updated_at"`
}

// PipelineFilter represents filtering options for pipelines
type PipelineFilter struct {
	Limit    int
	Offset   int
	Active   *bool
	Tags     []string
	OrderBy  string
	OrderDir string
}

// PipelineStore defines low-level persistence operations
// This is an infrastructure interface, NOT a domain interface
type PipelineStore interface {
	// Create inserts a new pipeline
	Create(ctx context.Context, model *PipelineModel) error

	// GetByID retrieves a pipeline by ID
	GetByID(ctx context.Context, id string) (*PipelineModel, error)

	// GetByName retrieves a pipeline by name
	GetByName(ctx context.Context, name string) (*PipelineModel, error)

	// Update updates an existing pipeline
	Update(ctx context.Context, model *PipelineModel) error

	// Delete removes a pipeline
	Delete(ctx context.Context, id string) error

	// List retrieves pipelines with filtering
	List(ctx context.Context, filter PipelineFilter) ([]*PipelineModel, int, error)

	// ExistsByName checks if a pipeline exists with the given name
	ExistsByName(ctx context.Context, name string) (bool, error)

	// Transaction support
	BeginTx(ctx context.Context) (Transaction, error)
}

// Transaction represents a database transaction
type Transaction interface {
	Commit() error
	Rollback() error

	// Pipeline operations within transaction
	CreatePipeline(ctx context.Context, model *PipelineModel) error
	UpdatePipeline(ctx context.Context, model *PipelineModel) error

	// Step operations within transaction
	CreateStep(ctx context.Context, model *StepModel) error
	DeleteStepsByPipelineID(ctx context.Context, pipelineID string) error
}

// PluginModel represents the database model for plugin
type PluginModel struct {
	ID            string                 `db:"id"`
	Name          string                 `db:"name"`
	Type          string                 `db:"type"`
	Version       string                 `db:"version"`
	Description   string                 `db:"description"`
	Author        string                 `db:"author"`
	Status        string                 `db:"status"`
	EntryPoint    string                 `db:"entry_point"`
	Dependencies  []string               `db:"dependencies"`
	Configuration map[string]interface{} `db:"configuration"`
	Metadata      map[string]interface{} `db:"metadata"`
	Capabilities  []string               `db:"capabilities"`
	CreatedAt     string                 `db:"created_at"`
	UpdatedAt     string                 `db:"updated_at"`
}

// PluginStore defines low-level persistence operations for plugins
type PluginStore interface {
	// Create inserts a new plugin
	Create(ctx context.Context, model *PluginModel) error

	// GetByID retrieves a plugin by ID
	GetByID(ctx context.Context, id string) (*PluginModel, error)

	// GetByName retrieves a plugin by name
	GetByName(ctx context.Context, name string) (*PluginModel, error)

	// Update updates an existing plugin
	Update(ctx context.Context, model *PluginModel) error

	// Delete removes a plugin
	Delete(ctx context.Context, id string) error

	// List retrieves plugins with filtering
	List(ctx context.Context, limit, offset int) ([]*PluginModel, int, error)

	// ListByType retrieves plugins by type
	ListByType(ctx context.Context, pluginType string, limit, offset int) ([]*PluginModel, int, error)

	// ListActive retrieves active plugins
	ListActive(ctx context.Context, limit, offset int) ([]*PluginModel, int, error)

	// ExistsByName checks if a plugin exists with the given name
	ExistsByName(ctx context.Context, name string) (bool, error)
}
