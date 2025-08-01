package pipeline

import (
	"context"

	"github.com/flext/flexcore/internal/shared_kernel/domain/value_objects"
)

// GetPipelineUseCase handles retrieving a pipeline by ID
type GetPipelineUseCase struct {
	repo           PipelineRepository
	inputValidator InputValidator
}

// NewGetPipelineUseCase creates a new GetPipelineUseCase
func NewGetPipelineUseCase(
	repo PipelineRepository,
	inputValidator InputValidator,
) *GetPipelineUseCase {
	return &GetPipelineUseCase{
		repo:           repo,
		inputValidator: inputValidator,
	}
}

// Execute retrieves a pipeline by ID
func (uc *GetPipelineUseCase) Execute(ctx context.Context, input GetPipelineInput) (*GetPipelineOutput, error) {
	// Validate input
	if uc.inputValidator != nil {
		if err := uc.inputValidator.ValidateGetPipelineInput(input); err != nil {
			return nil, err
		}
	}

	// Get pipeline by ID
	pipeline, err := uc.repo.GetByID(ctx, input.ID)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_NOT_FOUND",
			Message:     "Pipeline not found",
			Description: err.Error(),
		}
	}

	// Convert to output
	output := &GetPipelineOutput{
		ID:          pipeline.ID.String(),
		Name:        pipeline.Name,
		Description: pipeline.Description,
		IsActive:    pipeline.IsActive,
		Status:      string(pipeline.Status),
		Tags:        pipeline.Tags,
		Schedule:    pipeline.Schedule,
		CreatedAt:   pipeline.CreatedAt.Format("2006-01-02T15:04:05Z"),
		UpdatedAt:   pipeline.UpdatedAt.Format("2006-01-02T15:04:05Z"),
	}

	// Convert steps
	for _, step := range pipeline.Steps {
		stepOutput := StepOutput{
			ID:            step.ID.String(),
			Name:          step.Name,
			PluginID:      step.PluginID.String(),
			Configuration: step.Configuration,
			Order:         step.Order,
		}

		// Convert DependsOn UUIDs to strings
		for _, depID := range step.DependsOn {
			stepOutput.DependsOn = append(stepOutput.DependsOn, depID.String())
		}

		output.Steps = append(output.Steps, stepOutput)
	}

	return output, nil
}
