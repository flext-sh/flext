package pipeline

import (
	"context"
	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/domain/entities"
)

// GetPipelineByNameUseCase handles retrieving a pipeline by name
type GetPipelineByNameUseCase struct {
	repo      PipelineRepository
	validator InputValidator
}

// NewGetPipelineByNameUseCase creates a new get pipeline by name use case
func NewGetPipelineByNameUseCase(repo PipelineRepository, validator InputValidator) *GetPipelineByNameUseCase {
	return &GetPipelineByNameUseCase{
		repo:      repo,
		validator: validator,
	}
}

// Execute retrieves a pipeline by name
func (uc *GetPipelineByNameUseCase) Execute(ctx context.Context, input GetPipelineByNameInput) (*GetPipelineOutput, error) {
	// Validate input
	if err := uc.validator.ValidateGetPipelineByNameInput(input); err != nil {
		return nil, err
	}

	// Find pipeline
	pipeline, err := uc.repo.GetByName(ctx, input.Name)
	if err != nil {
		return nil, err
	}
	if pipeline == nil {
		return nil, ErrPipelineNotFound
	}

	return uc.mapToResult(pipeline), nil
}

// mapToResult converts entity to result format
func (uc *GetPipelineByNameUseCase) mapToResult(pipeline *entities.Pipeline) *GetPipelineOutput {
	steps := make([]StepOutput, len(pipeline.Steps))
	for i, step := range pipeline.Steps {
		dependsOn := make([]string, len(step.DependsOn))
		for j, dep := range step.DependsOn {
			dependsOn[j] = dep.String()
		}

		steps[i] = StepOutput{
			ID:            step.ID.String(),
			Name:          step.Name,
			PluginID:      step.PluginID.String(),
			Configuration: step.Configuration,
			Order:         step.Order,
			DependsOn:     dependsOn,
		}
	}

	return &GetPipelineOutput{
		ID:          pipeline.ID.String(),
		Name:        pipeline.Name,
		Description: pipeline.Description,
		IsActive:    pipeline.IsActive,
		Status:      string(pipeline.Status),
		Tags:        pipeline.Tags,
		Steps:       steps,
		Schedule:    pipeline.Schedule,
		CreatedAt:   pipeline.CreatedAt.Format("2006-01-02T15:04:05Z"),
		UpdatedAt:   pipeline.UpdatedAt.Format("2006-01-02T15:04:05Z"),
	}
}
