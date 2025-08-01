package events

import (
	"github.com/flext/flexcore/internal/shared_kernel/domain"
	"github.com/google/uuid"
)

// PipelineCreatedEvent evento emitido quando um pipeline é criado
type PipelineCreatedEvent struct {
	domain.BaseDomainEvent
	PipelineID  uuid.UUID `json:"pipeline_id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
}

// NewPipelineCreatedEvent cria um novo evento de pipeline criado
func NewPipelineCreatedEvent(pipelineID uuid.UUID, name, description string) *PipelineCreatedEvent {
	return &PipelineCreatedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent("pipeline.created", pipelineID),
		PipelineID:      pipelineID,
		Name:            name,
		Description:     description,
	}
}

// PipelineActivatedEvent evento emitido quando um pipeline é ativado
type PipelineActivatedEvent struct {
	domain.BaseDomainEvent
	PipelineID uuid.UUID `json:"pipeline_id"`
}

// NewPipelineActivatedEvent cria um novo evento de pipeline ativado
func NewPipelineActivatedEvent(pipelineID uuid.UUID) *PipelineActivatedEvent {
	return &PipelineActivatedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent("pipeline.activated", pipelineID),
		PipelineID:      pipelineID,
	}
}

// PipelineDeactivatedEvent evento emitido quando um pipeline é desativado
type PipelineDeactivatedEvent struct {
	domain.BaseDomainEvent
	PipelineID uuid.UUID `json:"pipeline_id"`
}

// NewPipelineDeactivatedEvent cria um novo evento de pipeline desativado
func NewPipelineDeactivatedEvent(pipelineID uuid.UUID) *PipelineDeactivatedEvent {
	return &PipelineDeactivatedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent("pipeline.deactivated", pipelineID),
		PipelineID:      pipelineID,
	}
}

// StepAddedEvent evento emitido quando um step é adicionado
type StepAddedEvent struct {
	domain.BaseDomainEvent
	PipelineID uuid.UUID `json:"pipeline_id"`
	StepID     uuid.UUID `json:"step_id"`
	StepName   string    `json:"step_name"`
}

// NewStepAddedEvent cria um novo evento de step adicionado
func NewStepAddedEvent(pipelineID, stepID uuid.UUID, stepName string) *StepAddedEvent {
	return &StepAddedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent("pipeline.step.added", pipelineID),
		PipelineID:      pipelineID,
		StepID:          stepID,
		StepName:        stepName,
	}
}

// PipelineExecutedEvent evento emitido quando um pipeline é executado
type PipelineExecutedEvent struct {
	domain.BaseDomainEvent
	PipelineID uuid.UUID `json:"pipeline_id"`
	Success    bool      `json:"success"`
	Duration   int64     `json:"duration_ms"`
}

// NewPipelineExecutedEvent cria um novo evento de pipeline executado
func NewPipelineExecutedEvent(pipelineID uuid.UUID, success bool, durationMs int64) *PipelineExecutedEvent {
	return &PipelineExecutedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent("pipeline.executed", pipelineID),
		PipelineID:      pipelineID,
		Success:         success,
		Duration:        durationMs,
	}
}

// PipelineDeletedEvent evento emitido quando um pipeline é deletado
type PipelineDeletedEvent struct {
	domain.BaseDomainEvent
	PipelineID uuid.UUID `json:"pipeline_id"`
	Name       string    `json:"name"`
}

// NewPipelineDeletedEvent cria um novo evento de pipeline deletado
func NewPipelineDeletedEvent(pipelineID uuid.UUID, name string) *PipelineDeletedEvent {
	return &PipelineDeletedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent("pipeline.deleted", pipelineID),
		PipelineID:      pipelineID,
		Name:            name,
	}
}
