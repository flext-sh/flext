package events

import (
	"context"
	"fmt"
	"sync"

	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/samber/lo"
)

// EventPublisher interface para publicação de eventos
type EventPublisher interface {
	Publish(ctx context.Context, event interface{}) error
	Subscribe(eventType string, handler DomainEventHandler) error
	Unsubscribe(eventType string, handler DomainEventHandler) error
}

// DomainEventHandler função que processa eventos de domínio
type DomainEventHandler func(event domain.DomainEvent) error

// InMemoryEventPublisher implementação em memória do event publisher
type InMemoryEventPublisher struct {
	mu       sync.RWMutex
	handlers map[string][]DomainEventHandler
}

// Ensure it implements both interfaces
var _ EventPublisher = (*InMemoryEventPublisher)(nil)

// NewInMemoryEventPublisher cria um novo publisher em memória
func NewInMemoryEventPublisher() *InMemoryEventPublisher {
	return &InMemoryEventPublisher{
		handlers: make(map[string][]DomainEventHandler),
	}
}

// Publish publica um evento para todos os handlers registrados
func (p *InMemoryEventPublisher) Publish(ctx context.Context, event interface{}) error {
	// Convert to domain event
	domainEvent, ok := event.(domain.DomainEvent)
	if !ok {
		return fmt.Errorf("event does not implement DomainEvent interface")
	}

	p.mu.RLock()
	handlers := p.handlers[domainEvent.GetEventType()]
	p.mu.RUnlock()

	if len(handlers) == 0 {
		// Não há handlers registrados, mas não é um erro
		return nil
	}

	// Processa handlers em paralelo usando functional programming
	var wg sync.WaitGroup
	errorChan := make(chan error, len(handlers))

	lo.ForEach(handlers, func(handler DomainEventHandler, _ int) {
		wg.Add(1)
		go func(h DomainEventHandler) {
			defer wg.Done()
			if err := h(domainEvent); err != nil {
				errorChan <- fmt.Errorf("handler error for event %s: %w", domainEvent.GetEventType(), err)
			}
		}(handler)
	})

	wg.Wait()
	close(errorChan)

	// Coletar erros usando functional programming
	errors := lo.ChannelToSlice(errorChan)

	if len(errors) > 0 {
		return fmt.Errorf("event publication failed with %d errors: %v", len(errors), errors)
	}

	return nil
}

// PublishEvents publica múltiplos eventos (legacy support)
func (p *InMemoryEventPublisher) PublishEvents(ctx context.Context, events ...interface{}) error {
	for _, event := range events {
		if err := p.Publish(ctx, event); err != nil {
			return err
		}
	}
	return nil
}

// Subscribe registra um handler para um tipo de evento
func (p *InMemoryEventPublisher) Subscribe(eventType string, handler DomainEventHandler) error {
	if eventType == "" {
		return fmt.Errorf("event type cannot be empty")
	}
	if handler == nil {
		return fmt.Errorf("handler cannot be nil")
	}

	p.mu.Lock()
	defer p.mu.Unlock()

	p.handlers[eventType] = append(p.handlers[eventType], handler)
	return nil
}

// Unsubscribe remove um handler de um tipo de evento
func (p *InMemoryEventPublisher) Unsubscribe(eventType string, handler DomainEventHandler) error {
	if eventType == "" {
		return fmt.Errorf("event type cannot be empty")
	}
	if handler == nil {
		return fmt.Errorf("handler cannot be nil")
	}

	p.mu.Lock()
	defer p.mu.Unlock()

	handlers := p.handlers[eventType]
	for i, h := range handlers {
		// Comparação por ponteiro de função (limitada, mas funcional para casos simples)
		if fmt.Sprintf("%p", h) == fmt.Sprintf("%p", handler) {
			// Remove o handler da slice
			p.handlers[eventType] = append(handlers[:i], handlers[i+1:]...)
			return nil
		}
	}

	return fmt.Errorf("handler not found for event type %s", eventType)
}

// GetSubscribersCount retorna o número de subscribers para um evento
func (p *InMemoryEventPublisher) GetSubscribersCount(eventType string) int {
	p.mu.RLock()
	defer p.mu.RUnlock()
	return len(p.handlers[eventType])
}

// Clear remove todos os handlers
func (p *InMemoryEventPublisher) Clear() {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.handlers = make(map[string][]DomainEventHandler)
}

// GetEventTypes retorna todos os tipos de evento com handlers registrados
func (p *InMemoryEventPublisher) GetEventTypes() []string {
	p.mu.RLock()
	defer p.mu.RUnlock()

	types := make([]string, 0, len(p.handlers))
	for eventType := range p.handlers {
		types = append(types, eventType)
	}
	return types
}
