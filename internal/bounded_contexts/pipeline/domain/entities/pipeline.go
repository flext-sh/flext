package entities

import (
	"errors"

	"github.com/flext-sh/flext/internal/shared_kernel/domain/entities"
	"github.com/google/uuid"
)

// PipelineStatus represents the status of a pipeline
type PipelineStatus string

const (
	PipelineStatusDraft     PipelineStatus = "draft"
	PipelineStatusActive    PipelineStatus = "active"
	PipelineStatusPaused    PipelineStatus = "paused"
	PipelineStatusCompleted PipelineStatus = "completed"
	PipelineStatusFailed    PipelineStatus = "failed"
)

// PipelineType represents the type of a pipeline
type PipelineType string

const (
	PipelineTypeETL       PipelineType = "etl"
	PipelineTypeELT       PipelineType = "elt"
	PipelineTypeStream    PipelineType = "stream"
	PipelineTypeBatch     PipelineType = "batch"
	PipelineTypeRealTime  PipelineType = "realtime"
	PipelineTypeAnalytics PipelineType = "analytics"
)

// PipelineStep represents a step in a pipeline
type PipelineStep struct {
	ID            uuid.UUID              `json:"id"`
	Name          string                 `json:"name"`
	PluginID      uuid.UUID              `json:"plugin_id"`
	Configuration map[string]interface{} `json:"configuration"`
	Order         int                    `json:"order"`
	DependsOn     []uuid.UUID            `json:"depends_on"`
}

// NewPipelineStep creates a new pipeline step
func NewPipelineStep(name string, pluginID uuid.UUID) (*PipelineStep, error) {
	if name == "" {
		return nil, errors.New("step name cannot be empty")
	}
	if pluginID == uuid.Nil {
		return nil, errors.New("plugin ID cannot be empty")
	}

	return &PipelineStep{
		ID:            uuid.New(),
		Name:          name,
		PluginID:      pluginID,
		Configuration: make(map[string]interface{}),
		Order:         0, // Will be set when added to pipeline
		DependsOn:     make([]uuid.UUID, 0),
	}, nil
}

// Pipeline represents a data pipeline entity and aggregate root
type Pipeline struct {
	entities.BaseAggregateRoot

	// Core pipeline data
	Name          string                 `json:"name" gorm:"uniqueIndex;not null"`
	Description   string                 `json:"description"`
	Type          PipelineType           `json:"type" gorm:"index"`
	IsActive      bool                   `json:"is_active" gorm:"default:false"`
	Status        PipelineStatus         `json:"status" gorm:"default:draft"`
	Steps         []PipelineStep         `json:"steps" gorm:"-"`
	Tags          []string               `json:"tags" gorm:"type:text[]"`
	Configuration map[string]interface{} `json:"configuration" gorm:"type:jsonb"`
	Schedule      string                 `json:"schedule,omitempty"`
}

// NewPipeline creates a new pipeline
func NewPipeline(name, description string) (*Pipeline, error) {
	if name == "" {
		return nil, errors.New("pipeline name cannot be empty")
	}

	pipeline := &Pipeline{
		BaseAggregateRoot: *entities.NewBaseAggregateRoot("pipeline"),
		Name:              name,
		Description:       description,
		Type:              PipelineTypeETL, // Default type
		IsActive:          false,
		Status:            PipelineStatusDraft,
		Steps:             make([]PipelineStep, 0),
		Tags:              make([]string, 0),
		Configuration:     make(map[string]interface{}),
	}

	// Skip domain event for now to avoid interface conflicts
	// TODO: Fix domain event interface compatibility

	return pipeline, nil
}

// AddStep adds a step to the pipeline
func (p *Pipeline) AddStep(step PipelineStep) error {
	if step.Name == "" {
		return errors.New("step name cannot be empty")
	}
	if step.PluginID == uuid.Nil {
		return errors.New("step plugin ID cannot be empty")
	}

	// Set order if not specified
	if step.Order == 0 {
		step.Order = len(p.Steps) + 1
	}

	// Generate ID if not provided
	if step.ID == uuid.Nil {
		step.ID = uuid.New()
	}

	p.Steps = append(p.Steps, step)
	p.IncrementVersion()
	p.AddDomainEvent(entities.NewBaseDomainEvent("step.added", p.GetID(), map[string]interface{}{
		"step_id":   step.ID,
		"step_name": step.Name,
	}, p.GetVersion()))

	return nil
}

// Activate activates the pipeline
func (p *Pipeline) Activate() error {
	if len(p.Steps) == 0 {
		return errors.New("cannot activate pipeline without steps")
	}

	p.IsActive = true
	p.Status = PipelineStatusActive
	p.IncrementVersion()
	p.AddDomainEvent(entities.NewBaseDomainEvent("pipeline.activated", p.GetID(), map[string]interface{}{}, p.GetVersion()))

	return nil
}

// Deactivate deactivates the pipeline
func (p *Pipeline) Deactivate() {
	p.IsActive = false
	p.Status = PipelineStatusPaused
	p.IncrementVersion()
	p.AddDomainEvent(entities.NewBaseDomainEvent("pipeline.deactivated", p.GetID(), map[string]interface{}{}, p.GetVersion()))
}

// UpdateConfiguration updates the pipeline configuration
func (p *Pipeline) UpdateConfiguration(config map[string]interface{}) {
	if p.Configuration == nil {
		p.Configuration = make(map[string]interface{})
	}

	for k, v := range config {
		p.Configuration[k] = v
	}

	p.IncrementVersion()
	p.AddDomainEvent(entities.NewBaseDomainEvent("pipeline.configuration.updated", p.GetID(), map[string]interface{}{
		"configuration": config,
	}, p.GetVersion()))
}

// SetSchedule sets the pipeline schedule
func (p *Pipeline) SetSchedule(schedule string) {
	p.Schedule = schedule
	p.IncrementVersion()
	p.AddDomainEvent(entities.NewBaseDomainEvent("pipeline.schedule.updated", p.GetID(), map[string]interface{}{
		"schedule": schedule,
	}, p.GetVersion()))
}

// CanExecute checks if the pipeline can be executed
func (p *Pipeline) CanExecute() error {
	if !p.IsActive {
		return errors.New("pipeline is not active")
	}
	if len(p.Steps) == 0 {
		return errors.New("pipeline has no steps")
	}
	return nil
}
