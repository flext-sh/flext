package pipeline

import (
	"errors"
	"github.com/google/uuid"
)

// Business errors
var (
	ErrEmptyName       = errors.New("pipeline name cannot be empty")
	ErrNameTooLong     = errors.New("pipeline name cannot exceed 100 characters")
	ErrStepNotFound    = errors.New("step not found")
	ErrDuplicateStep   = errors.New("step already exists")
	ErrInvalidStep     = errors.New("invalid step configuration")
	ErrInactiveExecute = errors.New("cannot execute inactive pipeline")
)

// Pipeline represents a pure domain entity
// No infrastructure concerns, no timestamps, no version
type Pipeline struct {
	id          uuid.UUID
	name        string
	description string
	isActive    bool
	steps       []Step
	tags        []string
	config      Configuration
}

// NewPipeline creates a new pipeline with business validation
func NewPipeline(name, description string) (*Pipeline, error) {
	if err := validateName(name); err != nil {
		return nil, err
	}

	return &Pipeline{
		id:          uuid.New(),
		name:        name,
		description: description,
		isActive:    true,
		steps:       make([]Step, 0),
		tags:        make([]string, 0),
		config:      NewConfiguration(),
	}, nil
}

// RestorePipeline recreates a pipeline from persistence
// Used by repositories to hydrate entities
func RestorePipeline(
	id uuid.UUID,
	name string,
	description string,
	isActive bool,
	steps []Step,
	tags []string,
	config Configuration,
) *Pipeline {
	return &Pipeline{
		id:          id,
		name:        name,
		description: description,
		isActive:    isActive,
		steps:       steps,
		tags:        tags,
		config:      config,
	}
}

// Business Methods

// AddStep adds a new step with validation
func (p *Pipeline) AddStep(step Step) error {
	if err := p.validateNewStep(step); err != nil {
		return err
	}

	p.steps = append(p.steps, step)
	return nil
}

// RemoveStep removes a step by ID
func (p *Pipeline) RemoveStep(stepID uuid.UUID) error {
	for i, step := range p.steps {
		if step.ID() == stepID {
			// Check if other steps depend on this one
			if p.hasStepDependencies(stepID) {
				return errors.New("cannot remove step with dependencies")
			}

			// Remove the step
			p.steps = append(p.steps[:i], p.steps[i+1:]...)
			return nil
		}
	}
	return ErrStepNotFound
}

// Activate activates the pipeline
func (p *Pipeline) Activate() error {
	if p.isActive {
		return errors.New("pipeline is already active")
	}

	if len(p.steps) == 0 {
		return errors.New("cannot activate pipeline without steps")
	}

	p.isActive = true
	return nil
}

// Deactivate deactivates the pipeline
func (p *Pipeline) Deactivate() {
	p.isActive = false
}

// CanExecute checks if pipeline can be executed
func (p *Pipeline) CanExecute() error {
	if !p.isActive {
		return ErrInactiveExecute
	}

	if len(p.steps) == 0 {
		return errors.New("cannot execute pipeline without steps")
	}

	// Validate all steps have valid configuration
	for _, step := range p.steps {
		if err := step.Validate(); err != nil {
			return err
		}
	}

	return nil
}

// AddTag adds a tag if not already present
func (p *Pipeline) AddTag(tag string) {
	tag = normalizeTag(tag)
	if tag == "" {
		return
	}

	for _, t := range p.tags {
		if t == tag {
			return
		}
	}

	p.tags = append(p.tags, tag)
}

// RemoveTag removes a tag
func (p *Pipeline) RemoveTag(tag string) {
	tag = normalizeTag(tag)
	for i, t := range p.tags {
		if t == tag {
			p.tags = append(p.tags[:i], p.tags[i+1:]...)
			return
		}
	}
}

// UpdateConfiguration updates pipeline configuration
func (p *Pipeline) UpdateConfiguration(key string, value interface{}) {
	p.config.Set(key, value)
}

// GetStepExecutionOrder returns steps in execution order
func (p *Pipeline) GetStepExecutionOrder() ([]Step, error) {
	// TODO: Implement topological sort based on dependencies
	// For now, return steps as-is
	return p.steps, nil
}

// Getters (encapsulation)

func (p *Pipeline) ID() uuid.UUID                { return p.id }
func (p *Pipeline) Name() string                 { return p.name }
func (p *Pipeline) Description() string          { return p.description }
func (p *Pipeline) IsActive() bool               { return p.isActive }
func (p *Pipeline) Steps() []Step                { return append([]Step{}, p.steps...) } // Return copy
func (p *Pipeline) Tags() []string               { return append([]string{}, p.tags...) }
func (p *Pipeline) Configuration() Configuration { return p.config.Clone() }

// HasTag checks if pipeline has a specific tag
func (p *Pipeline) HasTag(tag string) bool {
	tag = normalizeTag(tag)
	for _, t := range p.tags {
		if t == tag {
			return true
		}
	}
	return false
}

// GetStep returns a step by ID
func (p *Pipeline) GetStep(id uuid.UUID) (Step, bool) {
	for _, step := range p.steps {
		if step.ID() == id {
			return step, true
		}
	}
	return Step{}, false
}

// Private validation methods

func (p *Pipeline) validateNewStep(step Step) error {
	// Check for duplicate
	for _, existing := range p.steps {
		if existing.ID() == step.ID() {
			return ErrDuplicateStep
		}
	}

	// Validate dependencies exist
	for _, depID := range step.DependsOn() {
		found := false
		for _, s := range p.steps {
			if s.ID() == depID {
				found = true
				break
			}
		}
		if !found {
			return errors.New("dependency step not found: " + depID.String())
		}
	}

	return step.Validate()
}

func (p *Pipeline) hasStepDependencies(stepID uuid.UUID) bool {
	for _, step := range p.steps {
		for _, depID := range step.DependsOn() {
			if depID == stepID {
				return true
			}
		}
	}
	return false
}

// Business rule validations

func validateName(name string) error {
	if name == "" {
		return ErrEmptyName
	}
	if len(name) > 100 {
		return ErrNameTooLong
	}
	return nil
}

func normalizeTag(tag string) string {
	// Business logic for tag normalization
	// e.g., lowercase, trim spaces, etc
	return tag
}
