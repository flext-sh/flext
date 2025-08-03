package domain

// DEPRECATED: Este arquivo está sendo mantido temporariamente para compatibilidade
// Use internal/domain/shared/entity.go para a nova implementação Clean Architecture
//
// Este arquivo contém violações do DDD:
// - Version, CreatedAt, UpdatedAt são concerns de infraestrutura
// - Domain layer não deve conhecer detalhes de persistência
//
// TODO: Migrar todos os usos para a nova estrutura e remover este arquivo

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

// NewAggregateRootWithID cria um novo agregado raiz com ID específico (para reconstituição de persistência)
func NewAggregateRootWithID(id uuid.UUID, createdAt, updatedAt time.Time) AggregateRoot {
	return AggregateRoot{
		ID:        id,
		Version:   1,
		CreatedAt: createdAt,
		UpdatedAt: updatedAt,
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

// GetUncommittedEvents retorna eventos que ainda não foram commitados
func (ar *AggregateRoot) GetUncommittedEvents() []DomainEvent {
	return ar.events
}

// MarkEventsAsCommitted marca todos os eventos como commitados (limpa a lista)
func (ar *AggregateRoot) MarkEventsAsCommitted() {
	ar.events = make([]DomainEvent, 0)
}

// ClearEvents limpa todos os eventos de domínio
func (ar *AggregateRoot) ClearEvents() {
	ar.events = make([]DomainEvent, 0)
}

// GetID retorna o ID do agregado
func (ar *AggregateRoot) GetID() uuid.UUID {
	return ar.ID
}

// MarkAsUpdated marca o agregado como atualizado
func (ar *AggregateRoot) MarkAsUpdated() {
	ar.UpdatedAt = time.Now()
	ar.Version++
}

// UpdateTimestamp atualiza o timestamp de modificação
func (ar *AggregateRoot) UpdateTimestamp() {
	ar.UpdatedAt = time.Now()
	ar.Version++
}
