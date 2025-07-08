package validation

import (
	"errors"
	"fmt"
	"strings"

	"github.com/flext-sh/flext/internal/usecases/pipeline"
	"github.com/flext-sh/flext/internal/usecases/plugin"
	"github.com/google/uuid"
)

// DefaultValidator implements validation for all use cases
type DefaultValidator struct{}

// NewDefaultValidator creates a new default validator
func NewDefaultValidator() *DefaultValidator {
	return &DefaultValidator{}
}

// Pipeline validations

// ValidateCreatePipeline validates create pipeline input
func (v *DefaultValidator) ValidateCreatePipeline(input pipeline.CreatePipelineInput) error {
	var errs []string

	// Validate name
	if input.Name == "" {
		errs = append(errs, "name is required")
	} else if len(input.Name) > 100 {
		errs = append(errs, "name must not exceed 100 characters")
	} else if !isValidName(input.Name) {
		errs = append(errs, "name contains invalid characters")
	}

	// Validate description
	if len(input.Description) > 500 {
		errs = append(errs, "description must not exceed 500 characters")
	}

	// Validate tags
	for i, tag := range input.Tags {
		if tag == "" {
			errs = append(errs, fmt.Sprintf("tag at index %d is empty", i))
		} else if len(tag) > 50 {
			errs = append(errs, fmt.Sprintf("tag '%s' exceeds 50 characters", tag))
		} else if !isValidTag(tag) {
			errs = append(errs, fmt.Sprintf("tag '%s' contains invalid characters", tag))
		}
	}

	if len(errs) > 0 {
		return errors.New(strings.Join(errs, "; "))
	}

	return nil
}

// ValidateAddStep validates add step input
func (v *DefaultValidator) ValidateAddStep(input pipeline.AddStepInput) error {
	var errs []string

	// Validate pipeline ID
	if input.PipelineID == uuid.Nil {
		errs = append(errs, "pipeline ID is required")
	}

	// Validate name
	if input.Name == "" {
		errs = append(errs, "step name is required")
	} else if len(input.Name) > 100 {
		errs = append(errs, "step name must not exceed 100 characters")
	}

	// Validate plugin ID
	if input.PluginID == uuid.Nil {
		errs = append(errs, "plugin ID is required")
	}

	// Validate dependencies
	for i, depID := range input.DependsOn {
		if depID == uuid.Nil {
			errs = append(errs, fmt.Sprintf("dependency at index %d is invalid", i))
		}
		if depID == input.PluginID {
			errs = append(errs, "step cannot depend on itself")
		}
	}

	if len(errs) > 0 {
		return errors.New(strings.Join(errs, "; "))
	}

	return nil
}

// ValidateExecutePipeline validates execute pipeline input
func (v *DefaultValidator) ValidateExecutePipeline(input pipeline.ExecutePipelineInput) error {
	if input.PipelineID == uuid.Nil {
		return errors.New("pipeline ID is required")
	}

	// Additional parameter validation can be added here
	return nil
}

// Plugin validations

// ValidateRegisterPlugin validates register plugin input
func (v *DefaultValidator) ValidateRegisterPlugin(input plugin.RegisterPluginInput) error {
	var errs []string

	// Validate name
	if input.Name == "" {
		errs = append(errs, "name is required")
	} else if len(input.Name) > 100 {
		errs = append(errs, "name must not exceed 100 characters")
	} else if !isValidName(input.Name) {
		errs = append(errs, "name contains invalid characters")
	}

	// Validate type
	validTypes := map[string]bool{
		"source":       true,
		"destination":  true,
		"transform":    true,
		"orchestrator": true,
	}
	if input.Type == "" {
		errs = append(errs, "type is required")
	} else if !validTypes[input.Type] {
		errs = append(errs, fmt.Sprintf("invalid type '%s'", input.Type))
	}

	// Validate version
	if input.Version == "" {
		errs = append(errs, "version is required")
	} else if !isValidVersion(input.Version) {
		errs = append(errs, "version format is invalid")
	}

	// Validate capabilities
	for i, capability := range input.Capabilities {
		if capability == "" {
			errs = append(errs, fmt.Sprintf("capability at index %d is empty", i))
		}
	}

	if len(errs) > 0 {
		return errors.New(strings.Join(errs, "; "))
	}

	return nil
}

// ValidateActivatePlugin validates activate plugin input
func (v *DefaultValidator) ValidateActivatePlugin(input plugin.ActivatePluginInput) error {
	if input.PluginID == uuid.Nil {
		return errors.New("plugin ID is required")
	}
	return nil
}

// ValidateUpdatePlugin validates update plugin input
func (v *DefaultValidator) ValidateUpdatePlugin(input plugin.UpdatePluginInput) error {
	if input.ID == uuid.Nil {
		return errors.New("plugin ID is required")
	}
	// Additional validation for configuration and capabilities
	return nil
}

// Helper functions

func isValidName(name string) bool {
	// Allow alphanumeric, spaces, hyphens, underscores
	for _, r := range name {
		if !((r >= 'a' && r <= 'z') ||
			(r >= 'A' && r <= 'Z') ||
			(r >= '0' && r <= '9') ||
			r == ' ' || r == '-' || r == '_') {
			return false
		}
	}
	return true
}

func isValidTag(tag string) bool {
	// Allow alphanumeric, hyphens, underscores (no spaces in tags)
	for _, r := range tag {
		if !((r >= 'a' && r <= 'z') ||
			(r >= 'A' && r <= 'Z') ||
			(r >= '0' && r <= '9') ||
			r == '-' || r == '_') {
			return false
		}
	}
	return true
}

func isValidVersion(version string) bool {
	// Simple version validation (can be enhanced for semver)
	if version == "" {
		return false
	}

	// Basic check: must contain only alphanumeric, dots, hyphens
	for _, r := range version {
		if !((r >= 'a' && r <= 'z') ||
			(r >= 'A' && r <= 'Z') ||
			(r >= '0' && r <= '9') ||
			r == '.' || r == '-' || r == '+') {
			return false
		}
	}

	return true
}
