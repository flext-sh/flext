package entities

import (
	"errors"
	"fmt"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/events"
	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/google/uuid"
)

// Pipeline é o agregado raiz para o contexto de pipeline
type Pipeline struct {
	domain.AggregateRoot
	Name          string                 `json:"name"`
	Description   string                 `json:"description"`
	IsActive      bool                   `json:"is_active"`
	Steps         []PipelineStep         `json:"steps"`
	Tags          []string               `json:"tags"`
	Configuration map[string]interface{} `json:"configuration"`
	Schedule      *string                `json:"schedule,omitempty"`
}

// PipelineStep representa um passo no pipeline
type PipelineStep struct {
	ID            uuid.UUID              `json:"id"`
	Name          string                 `json:"name"`
	PluginID      uuid.UUID              `json:"plugin_id"`
	Configuration map[string]interface{} `json:"configuration"`
	Order         int                    `json:"order"`
	DependsOn     []uuid.UUID            `json:"depends_on"`
}

// NewPipeline cria um novo agregado pipeline
func NewPipeline(name, description string) (*Pipeline, error) {
	if name == "" {
		return nil, errors.New("pipeline name cannot be empty")
	}
	if len(name) > 100 {
		return nil, errors.New("pipeline name cannot exceed 100 characters")
	}

	p := &Pipeline{
		AggregateRoot: domain.NewAggregateRoot(),
		Name:          name,
		Description:   description,
		IsActive:      true,
		Steps:         make([]PipelineStep, 0),
		Tags:          make([]string, 0),
		Configuration: make(map[string]interface{}),
	}

	// Adicionar evento de domínio
	p.AddEvent(events.NewPipelineCreatedEvent(p.ID, p.Name, p.Description))
	
	return p, nil
}

// AddStep adiciona um passo ao pipeline
func (p *Pipeline) AddStep(step PipelineStep) error {
	if step.Name == "" {
		return errors.New("step name cannot be empty")
	}

	// Validar dependências existem
	for _, depID := range step.DependsOn {
		if !p.stepExists(depID) {
			return fmt.Errorf("dependency step %s does not exist", depID)
		}
	}

	step.ID = uuid.New()
	step.Order = len(p.Steps)
	p.Steps = append(p.Steps, step)
	
	p.UpdateTimestamp()
	p.AddEvent(events.NewPipelineStepAddedEvent(p.ID, step.ID, step.Name))
	
	return nil
}

// Activate ativa o pipeline
func (p *Pipeline) Activate() error {
	if p.IsActive {
		return errors.New("pipeline is already active")
	}

	if len(p.Steps) == 0 {
		return errors.New("cannot activate pipeline without steps")
	}

	p.IsActive = true
	p.UpdateTimestamp()
	p.AddEvent(events.NewPipelineActivatedEvent(p.ID))
	
	return nil
}

// Deactivate desativa o pipeline
func (p *Pipeline) Deactivate() {
	if !p.IsActive {
		return
	}

	p.IsActive = false
	p.UpdateTimestamp()
	p.AddEvent(events.NewPipelineDeactivatedEvent(p.ID))
}

// AddTag adiciona uma tag ao pipeline
func (p *Pipeline) AddTag(tag string) {
	if tag == "" {
		return
	}

	// Verificar se tag já existe
	for _, t := range p.Tags {
		if t == tag {
			return
		}
	}

	p.Tags = append(p.Tags, tag)
	p.UpdateTimestamp()
}

// UpdateConfiguration atualiza a configuração do pipeline
func (p *Pipeline) UpdateConfiguration(config map[string]interface{}) {
	if p.Configuration == nil {
		p.Configuration = make(map[string]interface{})
	}

	for k, v := range config {
		p.Configuration[k] = v
	}

	p.UpdateTimestamp()
}

// Helper methods

func (p *Pipeline) stepExists(id uuid.UUID) bool {
	for _, step := range p.Steps {
		if step.ID == id {
			return true
		}
	}
	return false
}