package validation

import (
	"errors"
	"github.com/google/uuid"

	pipelineUC "github.com/flext/flexcore/internal/usecases/pipeline"
	pluginUC "github.com/flext/flexcore/internal/usecases/plugin"
)

// SimpleValidator implements basic validation for Clean Architecture
type SimpleValidator struct{}

// NewValidator creates a new validator
func NewValidator() *SimpleValidator {
	return &SimpleValidator{}
}

// ValidateCreatePipeline validates pipeline creation input
func (v *SimpleValidator) ValidateCreatePipeline(input pipelineUC.CreatePipelineInput) error {
	if input.Name == "" {
		return errors.New("pipeline name is required")
	}
	if len(input.Name) > 100 {
		return errors.New("pipeline name too long")
	}
	return nil
}

// ValidateAddStep validates add step input
func (v *SimpleValidator) ValidateAddStep(input pipelineUC.AddStepInput) error {
	if input.PipelineID == uuid.Nil {
		return errors.New("pipeline ID is required")
	}
	if input.Name == "" {
		return errors.New("step name is required")
	}
	if input.PluginID == uuid.Nil {
		return errors.New("plugin ID is required")
	}
	return nil
}

// ValidateExecutePipeline validates pipeline execution input
func (v *SimpleValidator) ValidateExecutePipeline(input pipelineUC.ExecutePipelineInput) error {
	if input.PipelineID == uuid.Nil {
		return errors.New("pipeline ID is required")
	}
	return nil
}

// ValidateRegisterPlugin validates plugin registration input
func (v *SimpleValidator) ValidateRegisterPlugin(input pluginUC.RegisterPluginInput) error {
	if input.Name == "" {
		return errors.New("plugin name is required")
	}
	if input.Type == "" {
		return errors.New("plugin type is required")
	}
	if input.Version == "" {
		return errors.New("plugin version is required")
	}
	return nil
}

// ValidateActivatePlugin validates plugin activation input
func (v *SimpleValidator) ValidateActivatePlugin(input pluginUC.ActivatePluginInput) error {
	if input.PluginID == uuid.Nil {
		return errors.New("plugin ID is required")
	}
	return nil
}

// ValidateUpdatePlugin validates plugin update input
func (v *SimpleValidator) ValidateUpdatePlugin(input pluginUC.UpdatePluginInput) error {
	if input.ID == uuid.Nil {
		return errors.New("plugin ID is required")
	}
	return nil
}
