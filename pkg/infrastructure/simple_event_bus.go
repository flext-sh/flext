package events

import (
	"context"
	"log"
)

// SimpleEventBus implements a basic event bus for Clean Architecture
type SimpleEventBus struct{}

// NewEventBus creates a new simple event bus
func NewEventBus() *SimpleEventBus {
	return &SimpleEventBus{}
}

// Publish publishes an event (simple logging implementation)
func (eb *SimpleEventBus) Publish(ctx context.Context, event interface{}) error {
	// For now, just log the event
	log.Printf("Event published: %T", event)
	return nil
}
