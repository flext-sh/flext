package events

import (
	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/google/uuid"
)

const (
	PipelineCreatedEventType     = "pipeline.created"
	PipelineStepAddedEventType   = "pipeline.step.added"
	PipelineActivatedEventType   = "pipeline.activated"
	PipelineDeactivatedEventType = "pipeline.deactivated"
)

// PipelineCreatedEvent é emitido quando um novo pipeline é criado
type PipelineCreatedEvent struct {
	domain.BaseDomainEvent
	PipelineName string `json:"pipeline_name"`
	Description  string `json:"description"`
}

// NewPipelineCreatedEvent cria um novo evento de pipeline criado
func NewPipelineCreatedEvent(pipelineID uuid.UUID, pipelineName, description string) PipelineCreatedEvent {
	return PipelineCreatedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent(PipelineCreatedEventType, pipelineID),
		PipelineName:    pipelineName,
		Description:     description,
	}
}

// PipelineStepAddedEvent é emitido quando um passo é adicionado ao pipeline
type PipelineStepAddedEvent struct {
	domain.BaseDomainEvent
	StepID   uuid.UUID `json:"step_id"`
	StepName string    `json:"step_name"`
}

// NewPipelineStepAddedEvent cria um novo evento de passo adicionado
func NewPipelineStepAddedEvent(pipelineID, stepID uuid.UUID, stepName string) PipelineStepAddedEvent {
	return PipelineStepAddedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent(PipelineStepAddedEventType, pipelineID),
		StepID:          stepID,
		StepName:        stepName,
	}
}

// PipelineActivatedEvent é emitido quando um pipeline é ativado
type PipelineActivatedEvent struct {
	domain.BaseDomainEvent
}

// NewPipelineActivatedEvent cria um novo evento de pipeline ativado
func NewPipelineActivatedEvent(pipelineID uuid.UUID) PipelineActivatedEvent {
	return PipelineActivatedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent(PipelineActivatedEventType, pipelineID),
	}
}

// PipelineDeactivatedEvent é emitido quando um pipeline é desativado
type PipelineDeactivatedEvent struct {
	domain.BaseDomainEvent
}

// NewPipelineDeactivatedEvent cria um novo evento de pipeline desativado
func NewPipelineDeactivatedEvent(pipelineID uuid.UUID) PipelineDeactivatedEvent {
	return PipelineDeactivatedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent(PipelineDeactivatedEventType, pipelineID),
	}
}