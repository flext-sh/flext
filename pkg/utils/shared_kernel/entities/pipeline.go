// Package entities provides shared domain entities for the FlexT ecosystem
// This eliminates code duplication across bounded contexts
package entities

import (
	"errors"
	"time"

	"github.com/google/uuid"
)

// UnifiedPipelineStatus represents the status of a pipeline - SINGLE SOURCE OF TRUTH
type UnifiedPipelineStatus string

const (
	UnifiedPipelineStatusDraft     UnifiedPipelineStatus = "draft"
	UnifiedPipelineStatusActive    UnifiedPipelineStatus = "active"
	UnifiedPipelineStatusRunning   UnifiedPipelineStatus = "running"
	UnifiedPipelineStatusCompleted UnifiedPipelineStatus = "completed"
	UnifiedPipelineStatusFailed    UnifiedPipelineStatus = "failed"
	UnifiedPipelineStatusPaused    UnifiedPipelineStatus = "paused"
	UnifiedPipelineStatusArchived  UnifiedPipelineStatus = "archived"
)

// UnifiedPipelineType represents the type of a pipeline - SINGLE SOURCE OF TRUTH
type UnifiedPipelineType string

const (
	UnifiedPipelineTypeETL       UnifiedPipelineType = "etl"
	UnifiedPipelineTypeELT       UnifiedPipelineType = "elt"
	UnifiedPipelineTypeStream    UnifiedPipelineType = "stream"
	UnifiedPipelineTypeBatch     UnifiedPipelineType = "batch"
	UnifiedPipelineTypeRealTime  UnifiedPipelineType = "realtime"
	UnifiedPipelineTypeAnalytics UnifiedPipelineType = "analytics"
)

// UnifiedPipelineStep represents a step in a pipeline - ELIMINATING DUPLICATION
type UnifiedPipelineStep struct {
	ID            uuid.UUID              `json:"id"`
	Name          string                 `json:"name"`
	Type          string                 `json:"type"`
	PluginID      uuid.UUID              `json:"plugin_id,omitempty"`
	Configuration map[string]interface{} `json:"configuration"`
	Order         int                    `json:"order"`
	DependsOn     []uuid.UUID            `json:"depends_on"`
	RetryCount    int                    `json:"retry_count"`
	MaxRetries    int                    `json:"max_retries"`
	Timeout       time.Duration          `json:"timeout"`
	IsEnabled     bool                   `json:"is_enabled"`
	CreatedAt     time.Time              `json:"created_at"`
}

// NewUnifiedPipelineStep creates a new pipeline step
func NewUnifiedPipelineStep(name, stepType string) *UnifiedPipelineStep {
	return &UnifiedPipelineStep{
		ID:            uuid.New(),
		Name:          name,
		Type:          stepType,
		Configuration: make(map[string]interface{}),
		DependsOn:     make([]uuid.UUID, 0),
		RetryCount:    0,
		MaxRetries:    3,
		Timeout:       30 * time.Minute,
		IsEnabled:     true,
		CreatedAt:     time.Now(),
	}
}

// UnifiedPipeline represents a data pipeline entity - SINGLE SOURCE OF TRUTH
// This eliminates the duplication between flexcore and bounded_contexts
type UnifiedPipeline struct {
	BaseAggregateRoot

	// Core pipeline data
	Name          string                 `json:"name"`
	Description   string                 `json:"description"`
	Type          UnifiedPipelineType    `json:"type"`
	Status        UnifiedPipelineStatus  `json:"status"`
	Steps         []UnifiedPipelineStep  `json:"steps"`
	Tags          []string               `json:"tags"`
	Owner         string                 `json:"owner"`
	Configuration map[string]interface{} `json:"configuration"`
	Schedule      string                 `json:"schedule,omitempty"`
	LastRunAt     *time.Time             `json:"last_run_at,omitempty"`
	NextRunAt     *time.Time             `json:"next_run_at,omitempty"`
	IsActive      bool                   `json:"is_active"`
}

// NewUnifiedPipeline creates a new pipeline - ELIMINATING CONSTRUCTOR DUPLICATION
func NewUnifiedPipeline(name, description, owner string) (*UnifiedPipeline, error) {
	if name == "" {
		return nil, errors.New("pipeline name cannot be empty")
	}
	if owner == "" {
		return nil, errors.New("pipeline owner cannot be empty")
	}

	pipeline := &UnifiedPipeline{
		BaseAggregateRoot: *NewBaseAggregateRoot("pipeline"),
		Name:              name,
		Description:       description,
		Type:              UnifiedPipelineTypeETL, // Default type
		Status:            UnifiedPipelineStatusDraft,
		Steps:             make([]UnifiedPipelineStep, 0),
		Tags:              make([]string, 0),
		Owner:             owner,
		Configuration:     make(map[string]interface{}),
		IsActive:          false,
	}

	// Add domain event
	pipeline.AddDomainEvent(NewBaseDomainEvent("pipeline.created", pipeline.GetID(), map[string]interface{}{
		"name":  name,
		"owner": owner,
	}, pipeline.GetVersion()))

	return pipeline, nil
}

// AddStep adds a step to the pipeline - UNIFIED IMPLEMENTATION
func (p *UnifiedPipeline) AddStep(step UnifiedPipelineStep) error {
	if step.Name == "" {
		return errors.New("step name cannot be empty")
	}

	// Check for duplicate step names
	for _, existingStep := range p.Steps {
		if existingStep.Name == step.Name {
			return errors.New("step with name " + step.Name + " already exists")
		}
	}

	// Set order if not specified
	if step.Order == 0 {
		step.Order = len(p.Steps) + 1
	}

	// Generate ID if not provided
	if step.ID == uuid.Nil {
		step.ID = uuid.New()
	}

	// Validate dependencies
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

	// Check if other steps depend on this step
	stepID := p.Steps[stepIndex].ID
	for _, step := range p.Steps {
		for _, dependency := range step.DependsOn {
			if dependency == stepID {
				return errors.New("cannot remove step: other steps depend on it")
			}
		}
	}

	// Remove the step
	p.Steps = append(p.Steps[:stepIndex], p.Steps[stepIndex+1:]...)
	p.IncrementVersion()

	p.AddDomainEvent(NewBaseDomainEvent("step.removed", p.GetID(), map[string]interface{}{
		"step_name": stepName,
	}, p.GetVersion()))

	return nil
}

// Activate activates the pipeline - UNIFIED BUSINESS LOGIC
func (p *UnifiedPipeline) Activate() error {
	if p.Status == UnifiedPipelineStatusActive {
		return errors.New("pipeline is already active")
	}

	if len(p.Steps) == 0 {
		return errors.New("cannot activate pipeline without steps")
	}

	p.Status = UnifiedPipelineStatusActive
	p.IsActive = true
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("pipeline.activated", p.GetID(), map[string]interface{}{
		"name": p.Name,
	}, p.GetVersion()))

	return nil
}

// Deactivate deactivates the pipeline
func (p *UnifiedPipeline) Deactivate() error {
	if p.Status == UnifiedPipelineStatusRunning {
		return errors.New("cannot deactivate running pipeline")
	}

	p.Status = UnifiedPipelineStatusDraft
	p.IsActive = false
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("pipeline.deactivated", p.GetID(), map[string]interface{}{
		"name": p.Name,
	}, p.GetVersion()))

	return nil
}

// Start starts the pipeline execution
func (p *UnifiedPipeline) Start() error {
	if p.Status != UnifiedPipelineStatusActive {
		return errors.New("can only start active pipelines")
	}

	if p.Status == UnifiedPipelineStatusRunning {
		return errors.New("pipeline is already running")
	}

	p.Status = UnifiedPipelineStatusRunning
	now := time.Now()
	p.LastRunAt = &now
	p.IncrementVersion()

	p.AddDomainEvent(NewBaseDomainEvent("pipeline.started", p.GetID(), map[string]interface{}{
		"name":      p.Name,
		"timestamp": now,
	}, p.GetVersion()))

	return nil
}

// Complete marks the pipeline as completed
func (p *UnifiedPipeline) Complete() error {
	if p.Status != UnifiedPipelineStatusRunning {
		return errors.New("can only complete running pipelines")
	}

	p.Status = UnifiedPipelineStatusCompleted
	p.IncrementVersion()

	p.AddDomainEvent(NewBaseDomainEvent("pipeline.completed", p.GetID(), map[string]interface{}{
		"name":      p.Name,
		"timestamp": time.Now(),
	}, p.GetVersion()))

	return nil
}

// Fail marks the pipeline as failed
func (p *UnifiedPipeline) Fail(reason string) error {
	if p.Status != UnifiedPipelineStatusRunning {
		return errors.New("can only fail running pipelines")
	}

	p.Status = UnifiedPipelineStatusFailed
	p.IncrementVersion()

	p.AddDomainEvent(NewBaseDomainEvent("pipeline.failed", p.GetID(), map[string]interface{}{
		"name":      p.Name,
		"reason":    reason,
		"timestamp": time.Now(),
	}, p.GetVersion()))

	return nil
}

// UpdateConfiguration updates the pipeline configuration
func (p *UnifiedPipeline) UpdateConfiguration(config map[string]interface{}) {
	if p.Configuration == nil {
		p.Configuration = make(map[string]interface{})
	}

	for k, v := range config {
		p.Configuration[k] = v
	}

	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("pipeline.configuration.updated", p.GetID(), map[string]interface{}{
		"configuration": config,
	}, p.GetVersion()))
}

// SetSchedule sets the pipeline schedule
func (p *UnifiedPipeline) SetSchedule(schedule string) {
	p.Schedule = schedule
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("pipeline.schedule.updated", p.GetID(), map[string]interface{}{
		"schedule": schedule,
	}, p.GetVersion()))
}

// AddTag adds a tag to the pipeline
func (p *UnifiedPipeline) AddTag(tag string) {
	for _, existingTag := range p.Tags {
		if existingTag == tag {
			return // Tag already exists
		}
	}
	p.Tags = append(p.Tags, tag)
	p.IncrementVersion()
}

// RemoveTag removes a tag from the pipeline
func (p *UnifiedPipeline) RemoveTag(tag string) {
	for i, existingTag := range p.Tags {
		if existingTag == tag {
			p.Tags = append(p.Tags[:i], p.Tags[i+1:]...)
			p.IncrementVersion()
			break
		}
	}
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

// CanExecute checks if the pipeline can be executed
func (p *UnifiedPipeline) CanExecute() error {
	if p.Status != UnifiedPipelineStatusActive {
		return errors.New("pipeline is not active")
	}
	if len(p.Steps) == 0 {
		return errors.New("pipeline has no steps")
	}
	return nil
}

// IsScheduled returns true if the pipeline has a schedule
func (p *UnifiedPipeline) IsScheduled() bool {
	return p.Schedule != ""
}

// HasTag checks if the pipeline has a specific tag
func (p *UnifiedPipeline) HasTag(tag string) bool {
	for _, t := range p.Tags {
		if t == tag {
			return true
		}
	}
	return false
}

// Validate validates the pipeline
func (p *UnifiedPipeline) Validate() error {
	if p.Name == "" {
		return errors.New("name is required")
	}

	if p.Owner == "" {
		return errors.New("owner is required")
	}

	if len(p.Steps) == 0 {
		return errors.New("at least one step is required")
	}

	return nil
}

// Helper methods

func (p *UnifiedPipeline) hasStepByID(stepID uuid.UUID) bool {
	for _, step := range p.Steps {
		if step.ID == stepID {
			return true
		}
	}
	return false
}
