package container

import (
	"context"

	"github.com/flext/flexcore/internal/infrastructure/events"
)

// EventPublisherAdapter adapta o EventPublisher para as interfaces esperadas pelos bounded contexts
type EventPublisherAdapter struct {
	publisher events.EventPublisher
}

// NewEventPublisherAdapter cria um novo adaptador
func NewEventPublisherAdapter(publisher events.EventPublisher) *EventPublisherAdapter {
	return &EventPublisherAdapter{
		publisher: publisher,
	}
}

// PublishEvent publica um único evento (interface pipeline/plugin)
func (a *EventPublisherAdapter) PublishEvent(ctx context.Context, event interface{}) error {
	return a.publisher.Publish(ctx, event)
}

// PublishEvents publica múltiplos eventos
func (a *EventPublisherAdapter) PublishEvents(ctx context.Context, events ...interface{}) error {
	for _, event := range events {
		if err := a.publisher.Publish(ctx, event); err != nil {
			return err
		}
	}
	return nil
}

// Publish implementa a interface mais genérica
func (a *EventPublisherAdapter) Publish(ctx context.Context, event interface{}) error {
	return a.publisher.Publish(ctx, event)
}
