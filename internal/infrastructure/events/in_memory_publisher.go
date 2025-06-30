package events

import (
	"context"
	"log"
)

// InMemoryEventPublisher implementação em memória do publicador de eventos
type InMemoryEventPublisher struct {
	events []interface{}
}

// NewInMemoryEventPublisher cria um novo publicador em memória
func NewInMemoryEventPublisher() InMemoryEventPublisher {
	return InMemoryEventPublisher{
		events: make([]interface{}, 0),
	}
}

// PublishEvents publica múltiplos eventos
func (p *InMemoryEventPublisher) PublishEvents(ctx context.Context, events ...interface{}) error {
	for _, event := range events {
		if err := p.PublishEvent(ctx, event); err != nil {
			return err
		}
	}
	return nil
}

// PublishEvent publica um único evento
func (p *InMemoryEventPublisher) PublishEvent(ctx context.Context, event interface{}) error {
	// Por enquanto, apenas loggar o evento
	log.Printf("Event published: %+v", event)
	
	// Armazenar em memória para debug
	p.events = append(p.events, event)
	
	return nil
}

// GetEvents retorna todos os eventos publicados (para debug/teste)
func (p *InMemoryEventPublisher) GetEvents() []interface{} {
	return p.events
}

// Clear limpa todos os eventos (para teste)
func (p *InMemoryEventPublisher) Clear() {
	p.events = make([]interface{}, 0)
}

// EventPublisher interface type alias
type EventPublisher = InMemoryEventPublisher