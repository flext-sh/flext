package domain

import (
	"time"

	"github.com/google/uuid"
)

// DomainEvent representa um evento de domínio
type DomainEvent interface {
	GetEventID() uuid.UUID
	GetEventType() string
	GetAggregateID() uuid.UUID
	GetOccurredAt() time.Time
}

// BaseDomainEvent implementação base para eventos de domínio
type BaseDomainEvent struct {
	EventID     uuid.UUID `json:"event_id"`
	EventType   string    `json:"event_type"`
	AggregateID uuid.UUID `json:"aggregate_id"`
	OccurredAt  time.Time `json:"occurred_at"`
}

// NewBaseDomainEvent cria um novo evento de domínio base
func NewBaseDomainEvent(eventType string, aggregateID uuid.UUID) BaseDomainEvent {
	return BaseDomainEvent{
		EventID:     uuid.New(),
		EventType:   eventType,
		AggregateID: aggregateID,
		OccurredAt:  time.Now(),
	}
}

// GetEventID retorna o ID do evento
func (e BaseDomainEvent) GetEventID() uuid.UUID {
	return e.EventID
}

// GetEventType retorna o tipo do evento
func (e BaseDomainEvent) GetEventType() string {
	return e.EventType
}

// GetAggregateID retorna o ID do agregado
func (e BaseDomainEvent) GetAggregateID() uuid.UUID {
	return e.AggregateID
}

// GetOccurredAt retorna quando o evento ocorreu
func (e BaseDomainEvent) GetOccurredAt() time.Time {
	return e.OccurredAt
}