package shared

import (
	"github.com/google/uuid"
)

// Entity represents a base entity without infrastructure concerns
// No timestamps, no version - these are persistence concerns
type Entity struct {
	id uuid.UUID
}

// NewEntity creates a new entity with a generated ID
func NewEntity() Entity {
	return Entity{
		id: uuid.New(),
	}
}

// NewEntityWithID creates an entity with a specific ID (for restoration from persistence)
func NewEntityWithID(id uuid.UUID) Entity {
	return Entity{
		id: id,
	}
}

// ID returns the entity ID
func (e Entity) ID() uuid.UUID {
	return e.id
}

// Equals checks if two entities are equal based on ID
func (e Entity) Equals(other Entity) bool {
	return e.id == other.id
}

// AggregateRoot represents the root of an aggregate
// It can hold domain events but has no infrastructure concerns
type AggregateRoot struct {
	Entity
	events []DomainEvent
}

// NewAggregateRoot creates a new aggregate root
func NewAggregateRoot() AggregateRoot {
	return AggregateRoot{
		Entity: NewEntity(),
		events: make([]DomainEvent, 0),
	}
}

// NewAggregateRootWithID creates an aggregate root with specific ID
func NewAggregateRootWithID(id uuid.UUID) AggregateRoot {
	return AggregateRoot{
		Entity: NewEntityWithID(id),
		events: make([]DomainEvent, 0),
	}
}

// AddEvent adds a domain event
func (ar *AggregateRoot) AddEvent(event DomainEvent) {
	ar.events = append(ar.events, event)
}

// Events returns all uncommitted events
func (ar *AggregateRoot) Events() []DomainEvent {
	return append([]DomainEvent{}, ar.events...)
}

// ClearEvents removes all events (typically after persistence)
func (ar *AggregateRoot) ClearEvents() {
	ar.events = make([]DomainEvent, 0)
}

// HasEvents checks if there are uncommitted events
func (ar *AggregateRoot) HasEvents() bool {
	return len(ar.events) > 0
}