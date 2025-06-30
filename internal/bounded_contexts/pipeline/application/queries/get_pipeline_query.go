package queries

import (
	"context"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
	"github.com/google/uuid"
)

// GetPipelineQuery consulta para obter um pipeline por ID
type GetPipelineQuery struct {
	ID uuid.UUID `json:"id" validate:"required"`
}

// PipelineStepDTO representa um passo do pipeline na resposta
type PipelineStepDTO struct {
	ID            uuid.UUID              `json:"id"`
	Name          string                 `json:"name"`
	PluginID      uuid.UUID              `json:"plugin_id"`
	Configuration map[string]interface{} `json:"configuration"`
	Order         int                    `json:"order"`
	DependsOn     []uuid.UUID            `json:"depends_on"`
}

// PipelineDTO representa um pipeline na resposta
type PipelineDTO struct {
	ID            uuid.UUID              `json:"id"`
	Name          string                 `json:"name"`
	Description   string                 `json:"description"`
	IsActive      bool                   `json:"is_active"`
	Steps         []PipelineStepDTO      `json:"steps"`
	Tags          []string               `json:"tags"`
	Configuration map[string]interface{} `json:"configuration"`
	Schedule      *string                `json:"schedule,omitempty"`
	CreatedAt     time.Time              `json:"created_at"`
	UpdatedAt     time.Time              `json:"updated_at"`
	Version       int                    `json:"version"`
}

// GetPipelineHandler manipula consultas de pipeline
type GetPipelineHandler struct {
	repo ports.PipelineRepository
}

// NewGetPipelineHandler cria um novo handler
func NewGetPipelineHandler(repo ports.PipelineRepository) *GetPipelineHandler {
	return &GetPipelineHandler{
		repo: repo,
	}
}

// Handle executa a consulta
func (h *GetPipelineHandler) Handle(ctx context.Context, query GetPipelineQuery) (*PipelineDTO, error) {
	pipeline, err := h.repo.GetByID(ctx, query.ID)
	if err != nil {
		return nil, err
	}

	// Converter steps para DTO
	stepsDTO := make([]PipelineStepDTO, len(pipeline.Steps))
	for i, step := range pipeline.Steps {
		stepsDTO[i] = PipelineStepDTO{
			ID:            step.ID,
			Name:          step.Name,
			PluginID:      step.PluginID,
			Configuration: step.Configuration,
			Order:         step.Order,
			DependsOn:     step.DependsOn,
		}
	}

	return &PipelineDTO{
		ID:            pipeline.ID,
		Name:          pipeline.Name,
		Description:   pipeline.Description,
		IsActive:      pipeline.IsActive,
		Steps:         stepsDTO,
		Tags:          pipeline.Tags,
		Configuration: pipeline.Configuration,
		Schedule:      pipeline.Schedule,
		CreatedAt:     pipeline.CreatedAt,
		UpdatedAt:     pipeline.UpdatedAt,
		Version:       pipeline.Version,
	}, nil
}