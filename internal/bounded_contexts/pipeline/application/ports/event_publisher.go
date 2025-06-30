package ports

import "context"

// EventPublisher define a interface para publicação de eventos
type EventPublisher interface {
	// PublishEvents publica múltiplos eventos
	PublishEvents(ctx context.Context, events ...interface{}) error
	
	// PublishEvent publica um único evento
	PublishEvent(ctx context.Context, event interface{}) error
}