package domain

import (
	"time"

	"github.com/google/uuid"
)

// AggregateRoot é a base para todos os agregados de domínio
type AggregateRoot struct {
	ID        uuid.UUID     `json:"id"`
	Version   int           `json:"version"`
	CreatedAt time.Time     `json:"created_at"`
	UpdatedAt time.Time     `json:"updated_at"`
	events    []DomainEvent `json:"-"`
}

// NewAggregateRoot cria um novo agregado raiz
func NewAggregateRoot() AggregateRoot {
	now := time.Now()
	return AggregateRoot{
		ID:        uuid.New(),
		Version:   1,
		CreatedAt: now,
		UpdatedAt: now,
		events:    make([]DomainEvent, 0),
	}
}

// AddEvent adiciona um evento de domínio
func (ar *AggregateRoot) AddEvent(event DomainEvent) {
	ar.events = append(ar.events, event)
}

// GetEvents retorna todos os eventos de domínio
func (ar *AggregateRoot) GetEvents() []DomainEvent {
	return ar.events
}

// ClearEvents limpa todos os eventos de domínio
func (ar *AggregateRoot) ClearEvents() {
	ar.events = make([]DomainEvent, 0)
}

// UpdateTimestamp atualiza o timestamp de modificação
func (ar *AggregateRoot) UpdateTimestamp() {
	ar.UpdatedAt = time.Now()
	ar.Version++
}