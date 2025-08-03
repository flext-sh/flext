package domain

import (
	"time"

	"github.com/google/uuid"
)

// DomainEvent interface que todos os eventos de domínio devem implementar
type DomainEvent interface {
	GetEventID() string
	GetEventType() string
	GetAggregateID() string
	GetEventTime() time.Time
	GetVersion() int
	GetData() map[string]interface{}
}

// BaseDomainEvent implementação base para eventos de domínio
type BaseDomainEvent struct {
	ID           string                 `json:"id"`
	Type         string                 `json:"type"`
	AggregateId  string                 `json:"aggregate_id"`
	EventTime    time.Time              `json:"timestamp"`
	EventVersion int                    `json:"version"`
	EventData    map[string]interface{} `json:"data"`
}

// NewBaseDomainEvent cria um novo evento base
func NewBaseDomainEvent(eventType string, aggregateID uuid.UUID) BaseDomainEvent {
	return BaseDomainEvent{
		ID:           uuid.New().String(),
		Type:         eventType,
		AggregateId:  aggregateID.String(),
		EventTime:    time.Now().UTC(),
		EventVersion: 1,
		EventData:    make(map[string]interface{}),
	}
}

// Implementação da interface DomainEvent

func (e BaseDomainEvent) GetEventID() string {
	return e.ID
}

func (e BaseDomainEvent) GetEventType() string {
	return e.Type
}

func (e BaseDomainEvent) GetAggregateID() string {
	return e.AggregateId
}

func (e BaseDomainEvent) GetEventTime() time.Time {
	return e.EventTime
}

func (e BaseDomainEvent) GetVersion() int {
	return e.EventVersion
}

func (e BaseDomainEvent) GetData() map[string]interface{} {
	return e.EventData
}

// EventStream representa um stream de eventos
type EventStream struct {
	AggregateID string        `json:"aggregate_id"`
	Events      []DomainEvent `json:"events"`
	Version     int           `json:"version"`
	CreatedAt   time.Time     `json:"created_at"`
	UpdatedAt   time.Time     `json:"updated_at"`
}

// EventHandler interface para handlers de eventos
type EventHandler interface {
	Handle(event DomainEvent) error
	GetEventType() string
}

// EventPublisher interface para publicação de eventos
type EventPublisher interface {
	Publish(event DomainEvent) error
	Subscribe(eventType string, handler EventHandler) error
	Unsubscribe(eventType string, handler EventHandler) error
}

// EventStore interface para persistência de eventos (futuro)
type EventStore interface {
	SaveEvents(aggregateID string, events []DomainEvent, expectedVersion int) error
	GetEvents(aggregateID string) (*EventStream, error)
	GetEventsByType(eventType string) ([]DomainEvent, error)
}

// Snapshot interface para snapshots de agregados (futuro)
type Snapshot interface {
	GetAggregateID() string
	GetVersion() int
	GetData() interface{}
	GetTimestamp() time.Time
}

// Commands para CQRS (futuro)
type Command interface {
	GetCommandID() string
	GetCommandType() string
	GetAggregateID() string
	GetData() map[string]interface{}
}

// Query para CQRS (futuro)
type Query interface {
	GetQueryID() string
	GetQueryType() string
	GetParameters() map[string]interface{}
}

// EventMetadata contém metadados adicionais do evento
type EventMetadata struct {
	UserID        string            `json:"user_id,omitempty"`
	CorrelationID string            `json:"correlation_id,omitempty"`
	CausationID   string            `json:"causation_id,omitempty"`
	Source        string            `json:"source,omitempty"`
	Headers       map[string]string `json:"headers,omitempty"`
}

// EnrichedDomainEvent evento com metadados enriquecidos
type EnrichedDomainEvent struct {
	DomainEvent
	Metadata *EventMetadata `json:"metadata,omitempty"`
}

// NewEnrichedDomainEvent cria um evento enriquecido
func NewEnrichedDomainEvent(event DomainEvent, metadata *EventMetadata) *EnrichedDomainEvent {
	return &EnrichedDomainEvent{
		DomainEvent: event,
		Metadata:    metadata,
	}
}

// GetMetadata retorna os metadados do evento
func (e *EnrichedDomainEvent) GetMetadata() *EventMetadata {
	return e.Metadata
}

// SetMetadata define os metadados do evento
func (e *EnrichedDomainEvent) SetMetadata(metadata *EventMetadata) {
	e.Metadata = metadata
}

// AppendEvent adiciona um evento ao stream
func (s *EventStream) AppendEvent(event DomainEvent) {
	s.Events = append(s.Events, event)
	s.Version++
	s.UpdatedAt = time.Now().UTC()
}

// GetEvents retorna todos os eventos do stream
func (s *EventStream) GetEvents() []DomainEvent {
	return s.Events
}

// GetEventsAfterVersion retorna eventos após uma versão específica
func (s *EventStream) GetEventsAfterVersion(version int) []DomainEvent {
	var events []DomainEvent
	for _, event := range s.Events {
		if event.GetVersion() > version {
			events = append(events, event)
		}
	}
	return events
}

// GetLastEvent retorna o último evento do stream
func (s *EventStream) GetLastEvent() (DomainEvent, bool) {
	if len(s.Events) == 0 {
		return nil, false
	}
	return s.Events[len(s.Events)-1], true
}

// IsEmpty verifica se o stream está vazio
func (s *EventStream) IsEmpty() bool {
	return len(s.Events) == 0
}

// EventProjection interface para projeções de eventos
type EventProjection interface {
	ProjectEvent(event DomainEvent) error
	GetName() string
	GetVersion() string
}
