package validation

import (
	"errors"
	"strings"

	pipelineUC "github.com/flext/flexcore/internal/usecases/pipeline"
	"github.com/google/uuid"
)

// PipelineValidator implements all validation methods for the pipeline InputValidator interface
type PipelineValidator struct{}

// NewPipelineValidator creates a new pipeline validator
func NewPipelineValidator() *PipelineValidator {
	return &PipelineValidator{}
}

// ValidateCreatePipelineInput validates create pipeline input
func (v *PipelineValidator) ValidateCreatePipelineInput(input pipelineUC.CreatePipelineInput) error {
	return v.ValidateCreatePipeline(input)
}

// ValidateCreatePipeline validates create pipeline input
func (v *PipelineValidator) ValidateCreatePipeline(input pipelineUC.CreatePipelineInput) error {
	if strings.TrimSpace(input.Name) == "" {
		return errors.New("pipeline name is required")
	}
	if len(input.Name) < 3 {
		return errors.New("pipeline name must be at least 3 characters")
	}
	if len(input.Name) > 100 {
		return errors.New("pipeline name must be less than 100 characters")
	}
	return nil
}

// ValidateUpdatePipelineInput validates update pipeline input
func (v *PipelineValidator) ValidateUpdatePipelineInput(input pipelineUC.UpdatePipelineInput) error {
	if input.ID == uuid.Nil {
		return errors.New("pipeline ID is required")
	}
	if input.Name != "" && len(input.Name) < 3 {
		return errors.New("pipeline name must be at least 3 characters")
	}
	if input.Name != "" && len(input.Name) > 100 {
		return errors.New("pipeline name must be less than 100 characters")
	}
	return nil
}

// ValidateDeletePipelineInput validates delete pipeline input
func (v *PipelineValidator) ValidateDeletePipelineInput(input pipelineUC.DeletePipelineInput) error {
	if input.ID == uuid.Nil {
		return errors.New("pipeline ID is required")
	}
	return nil
}

// ValidateGetPipelineInput validates get pipeline input
func (v *PipelineValidator) ValidateGetPipelineInput(input pipelineUC.GetPipelineInput) error {
	return v.ValidateGetPipeline(input)
}

// ValidateGetPipeline validates get pipeline input
func (v *PipelineValidator) ValidateGetPipeline(input pipelineUC.GetPipelineInput) error {
	if input.ID == uuid.Nil {
		return errors.New("pipeline ID is required")
	}
	return nil
}

// ValidateListPipelinesInput validates list pipelines input
func (v *PipelineValidator) ValidateListPipelinesInput(input pipelineUC.ListPipelinesInput) error {
	return v.ValidateListPipelines(input)
}

// ValidateListPipelines validates list pipelines input
func (v *PipelineValidator) ValidateListPipelines(input pipelineUC.ListPipelinesInput) error {
	if input.Limit < 0 || input.Limit > 1000 {
		return errors.New("limit must be between 0 and 1000")
	}
	if input.Offset < 0 {
		return errors.New("offset must be >= 0")
	}
	return nil
}

// ValidateGetPipelineByNameInput validates get pipeline by name input
func (v *PipelineValidator) ValidateGetPipelineByNameInput(input pipelineUC.GetPipelineByNameInput) error {
	return v.ValidateGetPipelineByName(input)
}

// ValidateGetPipelineByName validates get pipeline by name input
func (v *PipelineValidator) ValidateGetPipelineByName(input pipelineUC.GetPipelineByNameInput) error {
	if strings.TrimSpace(input.Name) == "" {
		return errors.New("pipeline name is required")
	}
	return nil
}

// ValidateAddStepInput validates add step input
func (v *PipelineValidator) ValidateAddStepInput(input pipelineUC.AddStepInput) error {
	return v.ValidateAddStep(input)
}

// ValidateAddStep validates add step input
func (v *PipelineValidator) ValidateAddStep(input pipelineUC.AddStepInput) error {
	if input.PipelineID == uuid.Nil {
		return errors.New("pipeline ID is required")
	}
	if strings.TrimSpace(input.Name) == "" {
		return errors.New("step name is required")
	}
	if input.PluginID == uuid.Nil {
		return errors.New("plugin ID is required")
	}
	if input.Order < 0 {
		return errors.New("step order must be >= 0")
	}
	return nil
}

// ValidateExecutePipelineInput validates execute pipeline input
func (v *PipelineValidator) ValidateExecutePipelineInput(input pipelineUC.ExecutePipelineInput) error {
	return v.ValidateExecutePipeline(input)
}

// ValidateExecutePipeline validates execute pipeline input
func (v *PipelineValidator) ValidateExecutePipeline(input pipelineUC.ExecutePipelineInput) error {
	if input.PipelineID == uuid.Nil {
		return errors.New("pipeline ID is required")
	}
	return nil
}

// ValidateDeletePipeline validates delete pipeline input (alias for consistency)
func (v *PipelineValidator) ValidateDeletePipeline(input pipelineUC.DeletePipelineInput) error {
	return v.ValidateDeletePipelineInput(input)
}
