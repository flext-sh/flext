package events

import (
	"context"
	"fmt"
	"reflect"
	"sync"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
)

// EventBus defines the interface for event publishing and subscription
type EventBus interface {
	// Publish publishes an event to all subscribers
	Publish(ctx context.Context, event interface{}) error

	// Subscribe registers a handler for a specific event type
	Subscribe(eventType reflect.Type, handler func(ctx context.Context, event interface{}) error) error

	// Unsubscribe removes a handler for a specific event type
	Unsubscribe(eventType reflect.Type, handler func(ctx context.Context, event interface{}) error) error
}

// InMemoryEventBus implements EventBus with in-memory pub/sub
type InMemoryEventBus struct {
	mu       sync.RWMutex
	handlers map[reflect.Type][]func(ctx context.Context, event interface{}) error
	logger   logging.Logger
}

// NewInMemoryEventBus creates a new in-memory event bus
func NewInMemoryEventBus(logger logging.Logger) *InMemoryEventBus {
	return &InMemoryEventBus{
		handlers: make(map[reflect.Type][]func(ctx context.Context, event interface{}) error),
		logger:   logger,
	}
}

// Publish publishes an event to all subscribers
func (eb *InMemoryEventBus) Publish(ctx context.Context, event interface{}) error {
	if event == nil {
		return fmt.Errorf("cannot publish nil event")
	}

	eventType := reflect.TypeOf(event)

	eb.mu.RLock()
	handlers := eb.handlers[eventType]
	eb.mu.RUnlock()

	if len(handlers) == 0 {
		// No handlers for this event type
		eb.logger.Debug("No handlers registered for event type",
			logging.F("event_type", eventType.String()),
		)
		return nil
	}

	// Create a copy of handlers to avoid holding the lock during execution
	handlersCopy := make([]func(ctx context.Context, event interface{}) error, len(handlers))
	copy(handlersCopy, handlers)

	// Execute handlers concurrently
	var wg sync.WaitGroup
	errors := make(chan error, len(handlersCopy))

	for _, handler := range handlersCopy {
		wg.Add(1)
		go func(h func(ctx context.Context, event interface{}) error) {
			defer wg.Done()

			// Recover from panics in handlers
			defer func() {
				if r := recover(); r != nil {
					err := fmt.Errorf("handler panic: %v", r)
					errors <- err
					eb.logger.Error("Event handler panicked",
						logging.F("event_type", eventType.String()),
						logging.F("panic", r),
					)
				}
			}()

			if err := h(ctx, event); err != nil {
				errors <- err
				eb.logger.Error("Event handler failed",
					logging.F("event_type", eventType.String()),
					logging.F("error", err.Error()),
				)
			}
		}(handler)
	}

	wg.Wait()
	close(errors)

	// Collect errors
	var errs []error
	for err := range errors {
		if err != nil {
			errs = append(errs, err)
		}
	}

	if len(errs) > 0 {
		return fmt.Errorf("event handling failed with %d errors", len(errs))
	}

	eb.logger.Debug("Event published successfully",
		logging.F("event_type", eventType.String()),
		logging.F("handlers_count", len(handlersCopy)),
	)

	return nil
}

// Subscribe registers a handler for a specific event type
func (eb *InMemoryEventBus) Subscribe(eventType reflect.Type, handler func(ctx context.Context, event interface{}) error) error {
	if eventType == nil {
		return fmt.Errorf("event type cannot be nil")
	}
	if handler == nil {
		return fmt.Errorf("handler cannot be nil")
	}

	eb.mu.Lock()
	defer eb.mu.Unlock()

	eb.handlers[eventType] = append(eb.handlers[eventType], handler)

	eb.logger.Debug("Handler subscribed to event",
		logging.F("event_type", eventType.String()),
		logging.F("handlers_count", len(eb.handlers[eventType])),
	)

	return nil
}

// SubscribeFunc is a helper to subscribe with type inference
func (eb *InMemoryEventBus) SubscribeFunc(eventExample interface{}, handler func(ctx context.Context, event interface{}) error) error {
	return eb.Subscribe(reflect.TypeOf(eventExample), handler)
}

// Unsubscribe removes a handler for a specific event type
func (eb *InMemoryEventBus) Unsubscribe(eventType reflect.Type, handler func(ctx context.Context, event interface{}) error) error {
	if eventType == nil {
		return fmt.Errorf("event type cannot be nil")
	}
	if handler == nil {
		return fmt.Errorf("handler cannot be nil")
	}

	eb.mu.Lock()
	defer eb.mu.Unlock()

	handlers := eb.handlers[eventType]
	if len(handlers) == 0 {
		return nil
	}

	// Find and remove the handler
	// Note: This is a simple implementation. In production, you might want to use
	// handler IDs or tokens for more reliable removal
	newHandlers := make([]func(ctx context.Context, event interface{}) error, 0, len(handlers))
	removed := false

	for _, h := range handlers {
		// Compare function pointers
		if reflect.ValueOf(h).Pointer() == reflect.ValueOf(handler).Pointer() {
			removed = true
			continue
		}
		newHandlers = append(newHandlers, h)
	}

	if removed {
		eb.handlers[eventType] = newHandlers
		eb.logger.Debug("Handler unsubscribed from event",
			logging.F("event_type", eventType.String()),
			logging.F("handlers_count", len(newHandlers)),
		)
	}

	return nil
}

// Clear removes all handlers (useful for testing)
func (eb *InMemoryEventBus) Clear() {
	eb.mu.Lock()
	defer eb.mu.Unlock()

	eb.handlers = make(map[reflect.Type][]func(ctx context.Context, event interface{}) error)
	eb.logger.Debug("All event handlers cleared")
}

// GetHandlerCount returns the number of handlers for a specific event type
func (eb *InMemoryEventBus) GetHandlerCount(eventType reflect.Type) int {
	eb.mu.RLock()
	defer eb.mu.RUnlock()

	return len(eb.handlers[eventType])
}

// AsyncEventBus wraps an EventBus to publish events asynchronously
type AsyncEventBus struct {
	bus    EventBus
	buffer chan eventWrapper
	ctx    context.Context
	cancel context.CancelFunc
	wg     sync.WaitGroup
}

type eventWrapper struct {
	ctx   context.Context
	event interface{}
}

// NewAsyncEventBus creates a new async event bus
func NewAsyncEventBus(bus EventBus, bufferSize int) *AsyncEventBus {
	ctx, cancel := context.WithCancel(context.Background())

	aeb := &AsyncEventBus{
		bus:    bus,
		buffer: make(chan eventWrapper, bufferSize),
		ctx:    ctx,
		cancel: cancel,
	}

	// Start worker
	aeb.wg.Add(1)
	go aeb.worker()

	return aeb
}

// Publish publishes an event asynchronously
func (aeb *AsyncEventBus) Publish(ctx context.Context, event interface{}) error {
	select {
	case aeb.buffer <- eventWrapper{ctx: ctx, event: event}:
		return nil
	case <-aeb.ctx.Done():
		return fmt.Errorf("event bus is shutting down")
	default:
		return fmt.Errorf("event buffer is full")
	}
}

// Subscribe delegates to the underlying bus
func (aeb *AsyncEventBus) Subscribe(eventType reflect.Type, handler func(ctx context.Context, event interface{}) error) error {
	return aeb.bus.Subscribe(eventType, handler)
}

// Unsubscribe delegates to the underlying bus
func (aeb *AsyncEventBus) Unsubscribe(eventType reflect.Type, handler func(ctx context.Context, event interface{}) error) error {
	return aeb.bus.Unsubscribe(eventType, handler)
}

// Close shuts down the async event bus
func (aeb *AsyncEventBus) Close() error {
	aeb.cancel()
	aeb.wg.Wait()
	close(aeb.buffer)
	return nil
}

func (aeb *AsyncEventBus) worker() {
	defer aeb.wg.Done()

	for {
		select {
		case wrapper := <-aeb.buffer:
			// Ignore errors in async mode
			_ = aeb.bus.Publish(wrapper.ctx, wrapper.event)
		case <-aeb.ctx.Done():
			// Drain remaining events
			for {
				select {
				case wrapper := <-aeb.buffer:
					_ = aeb.bus.Publish(wrapper.ctx, wrapper.event)
				default:
					return
				}
			}
		}
	}
}
