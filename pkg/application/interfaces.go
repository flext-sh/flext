package pipeline

import (
	"context"
	"errors"

	"github.com/flext-sh/flext/pkg/domain/pipeline/domain/entities"
	"github.com/google/uuid"
)

// Common business errors
var (
	ErrPipelineNotFound          = errors.New("pipeline not found")
	ErrPipelineNameAlreadyExists = errors.New("pipeline name already exists")
	ErrPipelineStepNotFound      = errors.New("pipeline step not found")
	ErrInvalidInput              = errors.New("invalid input")
)

// PipelineRepository interface for pipeline persistence
type PipelineRepository interface {
	Save(ctx context.Context, pipeline *entities.Pipeline) error
	Create(ctx context.Context, pipeline *entities.Pipeline) (*entities.Pipeline, error)
	FindByID(ctx context.Context, id uuid.UUID) (*entities.Pipeline, error)
	FindByName(ctx context.Context, name string) (*entities.Pipeline, error)
	GetByID(ctx context.Context, id uuid.UUID) (*entities.Pipeline, error)
	GetByName(ctx context.Context, name string) (*entities.Pipeline, error)
	List(ctx context.Context, criteria ListCriteria) ([]*entities.Pipeline, int, error)
	Update(ctx context.Context, pipeline *entities.Pipeline) (*entities.Pipeline, error)
	Delete(ctx context.Context, id uuid.UUID) error
	Count(ctx context.Context) (int, error)
}

// InputValidator interface for input validation
type InputValidator interface {
	ValidateCreatePipelineInput(input CreatePipelineInput) error
	ValidateCreatePipeline(input CreatePipelineInput) error
	ValidateUpdatePipelineInput(input UpdatePipelineInput) error
	ValidateDeletePipelineInput(input DeletePipelineInput) error
	ValidateGetPipelineInput(input GetPipelineInput) error
	ValidateGetPipeline(input GetPipelineInput) error
	ValidateListPipelinesInput(input ListPipelinesInput) error
	ValidateListPipelines(input ListPipelinesInput) error
	ValidateGetPipelineByNameInput(input GetPipelineByNameInput) error
	ValidateGetPipelineByName(input GetPipelineByNameInput) error
	ValidateAddStepInput(input AddStepInput) error
	ValidateAddStep(input AddStepInput) error
	ValidateExecutePipelineInput(input ExecutePipelineInput) error
	ValidateExecutePipeline(input ExecutePipelineInput) error
	ValidateDeletePipeline(input DeletePipelineInput) error
}

// EventPublisher interface for domain events
type EventPublisher interface {
	Publish(ctx context.Context, event interface{}) error
}

// PluginRegistry interface for plugin management
type PluginRegistry interface {
	GetPlugin(ctx context.Context, id uuid.UUID) (interface{}, error)
	ListPlugins(ctx context.Context) ([]interface{}, error)
}

// Input types for various use cases

type CreatePipelineInput struct {
	Name        string   `json:"name"`
	Description string   `json:"description"`
	Tags        []string `json:"tags"`
}

type UpdatePipelineInput struct {
	ID          uuid.UUID              `json:"id" validate:"required"`
	Name        string                 `json:"name,omitempty"`
	Description string                 `json:"description,omitempty"`
	IsActive    *bool                  `json:"is_active,omitempty"`
	Tags        []string               `json:"tags,omitempty"`
	Config      map[string]interface{} `json:"configuration,omitempty"`
}

type DeletePipelineInput struct {
	ID uuid.UUID `json:"id" validate:"required"`
}

type GetPipelineInput struct {
	ID uuid.UUID `json:"id" validate:"required"`
}

type GetPipelineByNameInput struct {
	Name string `json:"name" validate:"required"`
}

type ListPipelinesInput struct {
	Limit    int      `json:"limit"`
	Offset   int      `json:"offset"`
	Search   string   `json:"search"`
	Active   *bool    `json:"active,omitempty"`
	Tags     []string `json:"tags,omitempty"`
	OrderBy  string   `json:"order_by,omitempty"`
	OrderDir string   `json:"order_dir,omitempty"`
}

type AddStepInput struct {
	PipelineID    uuid.UUID              `json:"pipeline_id" validate:"required"`
	Name          string                 `json:"name" validate:"required"`
	PluginID      uuid.UUID              `json:"plugin_id" validate:"required"`
	Configuration map[string]interface{} `json:"configuration"`
	Order         int                    `json:"order"`
	DependsOn     []uuid.UUID            `json:"depends_on"`
}

type ExecutePipelineInput struct {
	PipelineID uuid.UUID              `json:"pipeline_id" validate:"required"`
	Context    map[string]interface{} `json:"context"`
}

// ListCriteria represents criteria for listing pipelines
type ListCriteria struct {
	Limit    int
	Offset   int
	Active   *bool
	Tags     []string
	OrderBy  string
	OrderDir string
}

// Output types

type GetPipelineOutput struct {
	ID          string       `json:"id"`
	Name        string       `json:"name"`
	Description string       `json:"description"`
	IsActive    bool         `json:"is_active"`
	Status      string       `json:"status"`
	Tags        []string     `json:"tags"`
	Steps       []StepOutput `json:"steps"`
	Schedule    string       `json:"schedule,omitempty"`
	CreatedAt   string       `json:"created_at"`
	UpdatedAt   string       `json:"updated_at"`
}

type StepOutput struct {
	ID            string                 `json:"id"`
	Name          string                 `json:"name"`
	PluginID      string                 `json:"plugin_id"`
	Configuration map[string]interface{} `json:"configuration"`
	Order         int                    `json:"order"`
	DependsOn     []string               `json:"depends_on"`
}

type CreatePipelineOutput struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Description string   `json:"description"`
	Tags        []string `json:"tags"`
	IsActive    bool     `json:"is_active"`
	CreatedAt   string   `json:"created_at"`
}

// PluginInfo representa informações de um plugin
type PluginInfo struct {
	ID           uuid.UUID `json:"id"`
	Name         string    `json:"name"`
	Type         string    `json:"type"`
	Version      string    `json:"version"`
	IsActive     bool      `json:"is_active"`
	Capabilities []string  `json:"capabilities"`
}
