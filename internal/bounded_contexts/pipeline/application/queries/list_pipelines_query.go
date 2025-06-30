package queries

import (
	"context"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
)

// ListPipelinesQuery consulta para listar pipelines
type ListPipelinesQuery struct {
	Limit  int      `json:"limit,omitempty"`
	Offset int      `json:"offset,omitempty"`
	Tags   []string `json:"tags,omitempty"`
	Active *bool    `json:"active,omitempty"`
}

// ListPipelinesResult resultado da consulta
type ListPipelinesResult struct {
	Pipelines []PipelineDTO `json:"pipelines"`
	Total     int           `json:"total"`
}

// ListPipelinesHandler manipula consultas de listagem de pipelines
type ListPipelinesHandler struct {
	repo ports.PipelineRepository
}

// NewListPipelinesHandler cria um novo handler
func NewListPipelinesHandler(repo ports.PipelineRepository) *ListPipelinesHandler {
	return &ListPipelinesHandler{
		repo: repo,
	}
}

// Handle executa a consulta
func (h *ListPipelinesHandler) Handle(ctx context.Context, query ListPipelinesQuery) (*ListPipelinesResult, error) {
	// Aplicar valores padrão
	if query.Limit == 0 {
		query.Limit = 50
	}

	pipelines, total, err := h.repo.List(ctx, ports.ListPipelinesFilter{
		Limit:  query.Limit,
		Offset: query.Offset,
		Tags:   query.Tags,
		Active: query.Active,
	})
	if err != nil {
		return nil, err
	}

	// Converter para DTOs
	pipelineDTOs := make([]PipelineDTO, len(pipelines))
	for i, pipeline := range pipelines {
		stepsDTO := make([]PipelineStepDTO, len(pipeline.Steps))
		for j, step := range pipeline.Steps {
			stepsDTO[j] = PipelineStepDTO{
				ID:            step.ID,
				Name:          step.Name,
				PluginID:      step.PluginID,
				Configuration: step.Configuration,
				Order:         step.Order,
				DependsOn:     step.DependsOn,
			}
		}

		pipelineDTOs[i] = PipelineDTO{
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
		}
	}

	return &ListPipelinesResult{
		Pipelines: pipelineDTOs,
		Total:     total,
	}, nil
}