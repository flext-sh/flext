package shared

import (
	"github.com/google/uuid"
)

// DomainEvent represents something that happened in the domain
// Events are immutable facts about the past
type DomainEvent interface {
	// AggregateID returns the ID of the aggregate that produced this event
	AggregateID() uuid.UUID
	
	// EventType returns a string identifier for the event type
	EventType() string
	
	// EventVersion returns the version of this event schema
	EventVersion() int
}

// BaseEvent provides common functionality for domain events
type BaseEvent struct {
	aggregateID uuid.UUID
	eventType   string
	version     int
}

// NewBaseEvent creates a new base event
func NewBaseEvent(aggregateID uuid.UUID, eventType string, version int) BaseEvent {
	return BaseEvent{
		aggregateID: aggregateID,
		eventType:   eventType,
		version:     version,
	}
}

// AggregateID returns the aggregate ID
func (e BaseEvent) AggregateID() uuid.UUID {
	return e.aggregateID
}

// EventType returns the event type
func (e BaseEvent) EventType() string {
	return e.eventType
}

// EventVersion returns the event version
func (e BaseEvent) EventVersion() int {
	return e.version
}