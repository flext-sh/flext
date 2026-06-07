package entities

import (
	"errors"

	"github.com/google/uuid"
)

// AddStep adds a step to the pipeline - UNIFIED IMPLEMENTATION
func (p *UnifiedPipeline) AddStep(step UnifiedPipelineStep) error {
	if step.Name == "" {
		return errors.New("step name cannot be empty")
	}

	for _, existingStep := range p.Steps {
		if existingStep.Name == step.Name {
			return errors.New("step with name " + step.Name + " already exists")
		}
	}

	if step.Order == 0 {
		step.Order = len(p.Steps) + 1
	}
	if step.ID == uuid.Nil {
		step.ID = uuid.New()
	}
	for _, dependency := range step.DependsOn {
		if !p.hasStepByID(dependency) {
			return errors.New("dependency step not found")
		}
	}

	p.Steps = append(p.Steps, step)
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("step.added", p.GetID(), map[string]interface{}{
		"step_id":   step.ID,
		"step_name": step.Name,
	}, p.GetVersion()))

	return nil
}

// RemoveStep removes a step from the pipeline
func (p *UnifiedPipeline) RemoveStep(stepName string) error {
	stepIndex := -1
	for i, step := range p.Steps {
		if step.Name == stepName {
			stepIndex = i
			break
		}
	}

	if stepIndex == -1 {
		return errors.New("step " + stepName + " not found")
	}

	stepID := p.Steps[stepIndex].ID
	for _, step := range p.Steps {
		for _, dependency := range step.DependsOn {
			if dependency == stepID {
				return errors.New("cannot remove step: other steps depend on it")
			}
		}
	}

	p.Steps = append(p.Steps[:stepIndex], p.Steps[stepIndex+1:]...)
	p.IncrementVersion()

	p.AddDomainEvent(NewBaseDomainEvent("step.removed", p.GetID(), map[string]interface{}{
		"step_name": stepName,
	}, p.GetVersion()))

	return nil
}

// GetStepByName returns a step by name
func (p *UnifiedPipeline) GetStepByName(stepName string) (*UnifiedPipelineStep, error) {
	for _, step := range p.Steps {
		if step.Name == stepName {
			return &step, nil
		}
	}
	return nil, errors.New("step " + stepName + " not found")
}

// GetStepByID returns a step by ID
func (p *UnifiedPipeline) GetStepByID(stepID uuid.UUID) (*UnifiedPipelineStep, error) {
	for _, step := range p.Steps {
		if step.ID == stepID {
			return &step, nil
		}
	}
	return nil, errors.New("step not found")
}

func (p *UnifiedPipeline) hasStepByID(stepID uuid.UUID) bool {
	for _, step := range p.Steps {
		if step.ID == stepID {
			return true
		}
	}
	return false
}
