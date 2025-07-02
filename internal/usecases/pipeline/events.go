package pipeline

import (
	"time"
	"github.com/google/uuid"
)

// Domain Events - These are part of the use case layer
// They represent business events that other parts of the system might be interested in

// PipelineCreatedEvent is published when a new pipeline is created
type PipelineCreatedEvent struct {
	PipelineID  uuid.UUID
	Name        string
	Description string
	OccurredAt  time.Time
}

// StepAddedEvent is published when a step is added to a pipeline
type StepAddedEvent struct {
	PipelineID uuid.UUID
	StepID     uuid.UUID
	StepName   string
	PluginID   uuid.UUID
	Order      int
	OccurredAt time.Time
}

// PipelineExecutionStartedEvent is published when pipeline execution starts
type PipelineExecutionStartedEvent struct {
	ExecutionID uuid.UUID
	PipelineID  uuid.UUID
	StartedAt   time.Time
}

// PipelineExecutionCompletedEvent is published when pipeline execution completes
type PipelineExecutionCompletedEvent struct {
	ExecutionID uuid.UUID
	PipelineID  uuid.UUID
	Status      string
	StartedAt   time.Time
	CompletedAt time.Time
	Error       string
}

// PipelineActivatedEvent is published when a pipeline is activated
type PipelineActivatedEvent struct {
	PipelineID uuid.UUID
	OccurredAt time.Time
}

// PipelineDeactivatedEvent is published when a pipeline is deactivated
type PipelineDeactivatedEvent struct {
	PipelineID uuid.UUID
	OccurredAt time.Time
}

// StepExecutionStartedEvent is published when a step execution starts
type StepExecutionStartedEvent struct {
	ExecutionID uuid.UUID
	PipelineID  uuid.UUID
	StepID      uuid.UUID
	StartedAt   time.Time
}

// StepExecutionCompletedEvent is published when a step execution completes
type StepExecutionCompletedEvent struct {
	ExecutionID uuid.UUID
	PipelineID  uuid.UUID
	StepID      uuid.UUID
	Status      string
	CompletedAt time.Time
	Output      map[string]interface{}
	Error       string
}