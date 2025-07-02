package monitoring

import (
	"context"
	"fmt"
	"runtime"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
)

// TraceManager manages distributed tracing
type TraceManager struct {
	logger logging.Logger
	mu     sync.RWMutex
	traces map[string]*Trace
	spans  map[string]*Span
}

// Trace represents a distributed trace
type Trace struct {
	ID          string                 `json:"id"`
	Name        string                 `json:"name"`
	StartTime   time.Time              `json:"start_time"`
	EndTime     *time.Time             `json:"end_time,omitempty"`
	Duration    *time.Duration         `json:"duration,omitempty"`
	Status      TraceStatus            `json:"status"`
	Tags        map[string]string      `json:"tags"`
	Annotations []TraceAnnotation      `json:"annotations"`
	Spans       []*Span                `json:"spans"`
	Metadata    map[string]interface{} `json:"metadata"`
}

// Span represents a span within a trace
type Span struct {
	ID          string                 `json:"id"`
	TraceID     string                 `json:"trace_id"`
	ParentID    *string                `json:"parent_id,omitempty"`
	Name        string                 `json:"name"`
	Operation   string                 `json:"operation"`
	StartTime   time.Time              `json:"start_time"`
	EndTime     *time.Time             `json:"end_time,omitempty"`
	Duration    *time.Duration         `json:"duration,omitempty"`
	Status      SpanStatus             `json:"status"`
	Tags        map[string]string      `json:"tags"`
	Logs        []SpanLog              `json:"logs"`
	Component   string                 `json:"component"`
	Service     string                 `json:"service"`
	Metadata    map[string]interface{} `json:"metadata"`
}

// TraceAnnotation represents a trace annotation
type TraceAnnotation struct {
	Timestamp time.Time `json:"timestamp"`
	Value     string    `json:"value"`
	Endpoint  string    `json:"endpoint,omitempty"`
}

// SpanLog represents a log entry within a span
type SpanLog struct {
	Timestamp time.Time              `json:"timestamp"`
	Level     string                 `json:"level"`
	Message   string                 `json:"message"`
	Fields    map[string]interface{} `json:"fields,omitempty"`
}

type TraceStatus string
type SpanStatus string

const (
	TraceStatusActive    TraceStatus = "active"
	TraceStatusCompleted TraceStatus = "completed"
	TraceStatusError     TraceStatus = "error"

	SpanStatusActive    SpanStatus = "active"
	SpanStatusCompleted SpanStatus = "completed"
	SpanStatusError     SpanStatus = "error"
	SpanStatusCancelled SpanStatus = "cancelled"
)

// TraceContext provides tracing context
type TraceContext struct {
	TraceID string
	SpanID  string
	Baggage map[string]string
}

// NewTraceManager creates a new trace manager
func NewTraceManager(logger logging.Logger) *TraceManager {
	return &TraceManager{
		logger: logger,
		traces: make(map[string]*Trace),
		spans:  make(map[string]*Span),
	}
}

// StartTrace starts a new trace
func (tm *TraceManager) StartTrace(ctx context.Context, name string) (*Trace, context.Context) {
	traceID := uuid.New().String()
	
	trace := &Trace{
		ID:          traceID,
		Name:        name,
		StartTime:   time.Now(),
		Status:      TraceStatusActive,
		Tags:        make(map[string]string),
		Annotations: make([]TraceAnnotation, 0),
		Spans:       make([]*Span, 0),
		Metadata: map[string]interface{}{
			"created_by": "trace_manager",
			"go_version": runtime.Version(),
		},
	}

	tm.mu.Lock()
	tm.traces[traceID] = trace
	tm.mu.Unlock()

	// Create trace context
	traceCtx := &TraceContext{
		TraceID: traceID,
		Baggage: make(map[string]string),
	}

	// Add to context
	ctx = context.WithValue(ctx, "trace", traceCtx)

	tm.logger.Debug("Trace started",
		logging.F("trace_id", traceID),
		logging.F("name", name),
	)

	return trace, ctx
}

// FinishTrace finishes a trace
func (tm *TraceManager) FinishTrace(traceID string, status TraceStatus) {
	tm.mu.Lock()
	defer tm.mu.Unlock()

	trace, exists := tm.traces[traceID]
	if !exists {
		tm.logger.Warn("Trace not found", logging.F("trace_id", traceID))
		return
	}

	endTime := time.Now()
	duration := endTime.Sub(trace.StartTime)

	trace.EndTime = &endTime
	trace.Duration = &duration
	trace.Status = status

	tm.logger.Debug("Trace finished",
		logging.F("trace_id", traceID),
		logging.F("duration", duration.String()),
		logging.F("status", string(status)),
	)
}

// StartSpan starts a new span
func (tm *TraceManager) StartSpan(ctx context.Context, name, operation, component string) (*Span, context.Context) {
	spanID := uuid.New().String()

	// Get trace context
	traceCtx := tm.getTraceContext(ctx)
	if traceCtx == nil {
		tm.logger.Warn("No trace context found, creating new trace")
		_, ctx = tm.StartTrace(ctx, "auto_trace")
		traceCtx = tm.getTraceContext(ctx)
	}

	// Get parent span ID if exists
	var parentID *string
	if traceCtx.SpanID != "" {
		parentID = &traceCtx.SpanID
	}

	span := &Span{
		ID:        spanID,
		TraceID:   traceCtx.TraceID,
		ParentID:  parentID,
		Name:      name,
		Operation: operation,
		StartTime: time.Now(),
		Status:    SpanStatusActive,
		Tags:      make(map[string]string),
		Logs:      make([]SpanLog, 0),
		Component: component,
		Service:   "flext",
		Metadata: map[string]interface{}{
			"created_by": "trace_manager",
			"goroutine":  runtime.NumGoroutine(),
		},
	}

	tm.mu.Lock()
	tm.spans[spanID] = span
	
	// Add span to trace
	if trace, exists := tm.traces[traceCtx.TraceID]; exists {
		trace.Spans = append(trace.Spans, span)
	}
	tm.mu.Unlock()

	// Update trace context with current span
	newTraceCtx := &TraceContext{
		TraceID: traceCtx.TraceID,
		SpanID:  spanID,
		Baggage: traceCtx.Baggage,
	}
	ctx = context.WithValue(ctx, "trace", newTraceCtx)

	tm.logger.Debug("Span started",
		logging.F("span_id", spanID),
		logging.F("trace_id", traceCtx.TraceID),
		logging.F("name", name),
		logging.F("operation", operation),
		logging.F("component", component),
	)

	return span, ctx
}

// FinishSpan finishes a span
func (tm *TraceManager) FinishSpan(spanID string, status SpanStatus) {
	tm.mu.Lock()
	defer tm.mu.Unlock()

	span, exists := tm.spans[spanID]
	if !exists {
		tm.logger.Warn("Span not found", logging.F("span_id", spanID))
		return
	}

	endTime := time.Now()
	duration := endTime.Sub(span.StartTime)

	span.EndTime = &endTime
	span.Duration = &duration
	span.Status = status

	tm.logger.Debug("Span finished",
		logging.F("span_id", spanID),
		logging.F("trace_id", span.TraceID),
		logging.F("duration", duration.String()),
		logging.F("status", string(status)),
	)
}

// AddSpanTag adds a tag to a span
func (tm *TraceManager) AddSpanTag(spanID, key, value string) {
	tm.mu.Lock()
	defer tm.mu.Unlock()

	if span, exists := tm.spans[spanID]; exists {
		span.Tags[key] = value
	}
}

// AddSpanLog adds a log entry to a span
func (tm *TraceManager) AddSpanLog(spanID, level, message string, fields map[string]interface{}) {
	tm.mu.Lock()
	defer tm.mu.Unlock()

	if span, exists := tm.spans[spanID]; exists {
		log := SpanLog{
			Timestamp: time.Now(),
			Level:     level,
			Message:   message,
			Fields:    fields,
		}
		span.Logs = append(span.Logs, log)
	}
}

// AddTraceAnnotation adds an annotation to a trace
func (tm *TraceManager) AddTraceAnnotation(traceID, value, endpoint string) {
	tm.mu.Lock()
	defer tm.mu.Unlock()

	if trace, exists := tm.traces[traceID]; exists {
		annotation := TraceAnnotation{
			Timestamp: time.Now(),
			Value:     value,
			Endpoint:  endpoint,
		}
		trace.Annotations = append(trace.Annotations, annotation)
	}
}

// GetTrace gets a trace by ID
func (tm *TraceManager) GetTrace(traceID string) (*Trace, bool) {
	tm.mu.RLock()
	defer tm.mu.RUnlock()

	trace, exists := tm.traces[traceID]
	return trace, exists
}

// GetSpan gets a span by ID
func (tm *TraceManager) GetSpan(spanID string) (*Span, bool) {
	tm.mu.RLock()
	defer tm.mu.RUnlock()

	span, exists := tm.spans[spanID]
	return span, exists
}

// GetActiveTraces returns all active traces
func (tm *TraceManager) GetActiveTraces() []*Trace {
	tm.mu.RLock()
	defer tm.mu.RUnlock()

	var activeTraces []*Trace
	for _, trace := range tm.traces {
		if trace.Status == TraceStatusActive {
			activeTraces = append(activeTraces, trace)
		}
	}

	return activeTraces
}

// GetRecentTraces returns recent traces (last 1 hour)
func (tm *TraceManager) GetRecentTraces() []*Trace {
	tm.mu.RLock()
	defer tm.mu.RUnlock()

	cutoff := time.Now().Add(-time.Hour)
	var recentTraces []*Trace

	for _, trace := range tm.traces {
		if trace.StartTime.After(cutoff) {
			recentTraces = append(recentTraces, trace)
		}
	}

	return recentTraces
}

// CleanupOldTraces removes traces older than the specified duration
func (tm *TraceManager) CleanupOldTraces(maxAge time.Duration) {
	tm.mu.Lock()
	defer tm.mu.Unlock()

	cutoff := time.Now().Add(-maxAge)
	cleanupCount := 0

	// Cleanup traces
	for traceID, trace := range tm.traces {
		if trace.StartTime.Before(cutoff) {
			delete(tm.traces, traceID)
			cleanupCount++

			// Cleanup spans for this trace
			for spanID, span := range tm.spans {
				if span.TraceID == traceID {
					delete(tm.spans, spanID)
				}
			}
		}
	}

	if cleanupCount > 0 {
		tm.logger.Info("Cleaned up old traces",
			logging.F("count", cleanupCount),
			logging.F("max_age", maxAge.String()),
		)
	}
}

// GetTracingStatistics returns tracing statistics
func (tm *TraceManager) GetTracingStatistics() map[string]interface{} {
	tm.mu.RLock()
	defer tm.mu.RUnlock()

	activeTraces := 0
	completedTraces := 0
	errorTraces := 0
	activeSpans := 0
	completedSpans := 0
	errorSpans := 0

	for _, trace := range tm.traces {
		switch trace.Status {
		case TraceStatusActive:
			activeTraces++
		case TraceStatusCompleted:
			completedTraces++
		case TraceStatusError:
			errorTraces++
		}
	}

	for _, span := range tm.spans {
		switch span.Status {
		case SpanStatusActive:
			activeSpans++
		case SpanStatusCompleted:
			completedSpans++
		case SpanStatusError:
			errorSpans++
		}
	}

	return map[string]interface{}{
		"traces": map[string]interface{}{
			"total":     len(tm.traces),
			"active":    activeTraces,
			"completed": completedTraces,
			"errors":    errorTraces,
		},
		"spans": map[string]interface{}{
			"total":     len(tm.spans),
			"active":    activeSpans,
			"completed": completedSpans,
			"errors":    errorSpans,
		},
		"memory_usage": map[string]interface{}{
			"traces_bytes": len(tm.traces) * 1024, // Approximate
			"spans_bytes":  len(tm.spans) * 512,   // Approximate
		},
	}
}

// getTraceContext extracts trace context from Go context
func (tm *TraceManager) getTraceContext(ctx context.Context) *TraceContext {
	if ctx == nil {
		return nil
	}

	traceCtx, ok := ctx.Value("trace").(*TraceContext)
	if !ok {
		return nil
	}

	return traceCtx
}

// TraceMiddleware creates middleware for automatic tracing
func (tm *TraceManager) TraceMiddleware(component string) func(next func(ctx context.Context) error) func(ctx context.Context) error {
	return func(next func(ctx context.Context) error) func(ctx context.Context) error {
		return func(ctx context.Context) error {
			// Start span
			span, ctx := tm.StartSpan(ctx, "middleware", "execute", component)
			
			// Execute next function
			err := next(ctx)
			
			// Finish span
			status := SpanStatusCompleted
			if err != nil {
				status = SpanStatusError
				tm.AddSpanLog(span.ID, "error", err.Error(), map[string]interface{}{
					"error_type": fmt.Sprintf("%T", err),
				})
			}
			tm.FinishSpan(span.ID, status)
			
			return err
		}
	}
}

// StartAutoCleanup starts automatic cleanup of old traces
func (tm *TraceManager) StartAutoCleanup(ctx context.Context, interval, maxAge time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	tm.logger.Info("Starting automatic trace cleanup",
		logging.F("interval", interval.String()),
		logging.F("max_age", maxAge.String()),
	)

	for {
		select {
		case <-ctx.Done():
			tm.logger.Info("Stopping automatic trace cleanup")
			return
		case <-ticker.C:
			tm.CleanupOldTraces(maxAge)
		}
	}
}