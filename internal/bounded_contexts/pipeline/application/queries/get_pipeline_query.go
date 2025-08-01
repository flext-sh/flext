package queries

import (
	"context"

	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/application/ports"
	"github.com/google/uuid"
)

// GetPipelineQuery represents a query to get a pipeline by ID
type GetPipelineQuery struct {
	PipelineID uuid.UUID `json:"pipeline_id" validate:"required"`
}

// GetPipelineHandler handles getting a pipeline by ID
type GetPipelineHandler struct {
	repo ports.PipelineRepository
}

// NewGetPipelineHandler creates a new GetPipelineHandler
func NewGetPipelineHandler(repo ports.PipelineRepository) *GetPipelineHandler {
	return &GetPipelineHandler{
		repo: repo,
	}
}

// Handle executes the GetPipelineQuery
func (h *GetPipelineHandler) Handle(ctx context.Context, query GetPipelineQuery) (*PipelineDTO, error) {
	pipeline, err := h.repo.GetByID(ctx, query.PipelineID)
	if err != nil {
		return nil, err
	}

	if pipeline == nil {
		return nil, nil
	}

	// Convert domain entity to DTO
	dto := &PipelineDTO{
		ID:            pipeline.GetID(),
		Name:          pipeline.Name,
		Description:   pipeline.Description,
		IsActive:      pipeline.IsActive,
		Tags:          pipeline.Tags,
		Configuration: pipeline.Configuration,
		CreatedAt:     pipeline.GetCreatedAt(),
		UpdatedAt:     pipeline.GetUpdatedAt(),
		Version:       int(pipeline.GetVersion()),
	}

	// Convert steps to DTOs
	for _, step := range pipeline.Steps {
		stepDTO := PipelineStepDTO{
			ID:            step.ID,
			Name:          step.Name,
			PluginID:      step.PluginID,
			Configuration: step.Configuration,
			Order:         step.Order,
			DependsOn:     step.DependsOn,
		}
		dto.Steps = append(dto.Steps, stepDTO)
	}

	// Convert schedule if exists
	if pipeline.Schedule != "" {
		dto.Schedule = &PipelineScheduleDTO{
			CronExpression: pipeline.Schedule,
			IsActive:       pipeline.IsActive,
		}
	}

	return dto, nil
}
