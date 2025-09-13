# Clean Architecture Implementation

This document describes how FLEXT Control Panel implements Clean Architecture principles, providing a maintainable, testable, and scalable codebase.

## Table of Contents

- [Overview](#overview)
- [Architecture Layers](#architecture-layers)
- [Dependency Rules](#dependency-rules)
- [Implementation Details](#implementation-details)
- [Design Patterns](#design-patterns)
- [Testing Strategy](#testing-strategy)

## Overview

FLEXT Control Panel implements Clean Architecture as defined by Robert C. Martin, with adaptations for Go ecosystem and business data integration requirements.

### Core Principles

1. **Independence of Frameworks**: Business logic doesn't depend on frameworks
2. **Testable**: Business logic can be tested without UI, database, web server
3. **Independence of UI**: UI can change without changing business logic
4. **Independence of Database**: Business logic isn't bound to specific database
5. **Independence of External Agencies**: Business logic doesn't know about external systems

### Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FLEXT CLEAN ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────┤
│  Interfaces Layer                                           │
│  ├─ REST API        ├─ CLI            ├─ Web Interface      │
│  └─ External Communication Protocols                        │
├─────────────────────────────────────────────────────────────┤
│  Adapters Layer                                             │
│  ├─ Controllers     ├─ Gateways       ├─ Presenters         │
│  └─ Interface Implementations                               │
├─────────────────────────────────────────────────────────────┤
│  Application Layer                                          │
│  ├─ Use Cases       ├─ Services       ├─ Commands/Queries   │
│  └─ Business Workflows                                      │
├─────────────────────────────────────────────────────────────┤
│  Domain Layer (Core)                                        │
│  ├─ Entities        ├─ Events         ├─ Value Objects      │
│  ├─ Repositories    ├─ Services       ├─ Business Rules     │
│  └─ Pure Business Logic                                     │
└─────────────────────────────────────────────────────────────┘
```

## Architecture Layers

### Domain Layer (Inner Core)

**Location**: `pkg/domain/`  
**Purpose**: Contains business business rules and entities  
**Dependencies**: None (only Go standard library)

```go
// pkg/domain/pipeline/entities/pipeline.go
package entities

type Pipeline struct {
    ID          PipelineID
    Name        string
    Description string
    Status      PipelineStatus
    Steps       []PipelineStep
    CreatedAt   time.Time
    UpdatedAt   time.Time
}

// Business logic with no external dependencies
func (p *Pipeline) AddStep(step PipelineStep) error {
    if step.Name == "" {
        return ErrInvalidStepName
    }

    if p.Status == StatusRunning {
        return ErrCannotModifyRunningPipeline
    }

    p.Steps = append(p.Steps, step)
    p.UpdatedAt = time.Now()

    // Raise domain event
    p.raiseEvent(NewStepAddedEvent(p.ID, step))
    return nil
}

func (p *Pipeline) Execute() error {
    if len(p.Steps) == 0 {
        return ErrEmptyPipeline
    }

    p.Status = StatusRunning
    p.raiseEvent(NewPipelineStartedEvent(p.ID))
    return nil
}
```

**Key Characteristics:**

- No external dependencies
- Pure business logic
- Domain events for communication
- Rich domain model with behavior

### Application Layer

**Location**: `pkg/application/`  
**Purpose**: Contains application business rules and use cases  
**Dependencies**: Domain layer only

```go
// pkg/application/pipeline/services/pipeline_service.go
package services

type PipelineService struct {
    repo     ports.PipelineRepository
    eventBus ports.EventBus
    logger   ports.Logger
}

func (s *PipelineService) CreatePipeline(cmd commands.CreatePipelineCommand) error {
    // Validate input
    if err := cmd.Validate(); err != nil {
        return fmt.Errorf("invalid command: %w", err)
    }

    // Create domain entity
    pipeline := entities.NewPipeline(cmd.Name, cmd.Description)

    // Apply business rules
    if err := pipeline.Validate(); err != nil {
        return fmt.Errorf("invalid pipeline: %w", err)
    }

    // Save through port (interface)
    if err := s.repo.Save(pipeline); err != nil {
        return fmt.Errorf("failed to save pipeline: %w", err)
    }

    // Publish domain events
    for _, event := range pipeline.Events() {
        if err := s.eventBus.Publish(event); err != nil {
            s.logger.Error("failed to publish event", "event", event, "error", err)
        }
    }

    return nil
}
```

**Key Characteristics:**

- Orchestrates business workflows
- Uses dependency injection through ports
- No knowledge of implementation details
- Coordinates between domain objects

### Adapters Layer

**Location**: `pkg/adapters/`  
**Purpose**: Converts data between external systems and internal use cases  
**Dependencies**: Application and Domain layers

```go
// pkg/adapters/controllers/http/pipeline_controller.go
package http

type PipelineController struct {
    pipelineService *services.PipelineService
    validator       *validator.Validator
    logger          *logger.Logger
}

func (c *PipelineController) CreatePipeline(w http.ResponseWriter, r *http.Request) {
    // Parse HTTP request into DTO
    var dto CreatePipelineDTO
    if err := json.NewDecoder(r.Body).Decode(&dto); err != nil {
        c.writeError(w, http.StatusBadRequest, "invalid request body")
        return
    }

    // Validate DTO
    if err := c.validator.Validate(dto); err != nil {
        c.writeError(w, http.StatusBadRequest, err.Error())
        return
    }

    // Convert DTO to command
    cmd := commands.CreatePipelineCommand{
        Name:        dto.Name,
        Description: dto.Description,
        CreatedBy:   getUserFromContext(r.Context()),
    }

    // Execute use case
    if err := c.pipelineService.CreatePipeline(cmd); err != nil {
        c.logger.Error("failed to create pipeline", "error", err)
        c.writeError(w, http.StatusInternalServerError, "failed to create pipeline")
        return
    }

    // Return success response
    c.writeJSON(w, http.StatusCreated, map[string]string{
        "message": "pipeline created successfully",
    })
}
```

**Key Characteristics:**

- Handles external communication protocols
- Converts between external formats and internal models
- Implements interfaces defined by application layer
- No business logic

### Interfaces Layer

**Location**: `pkg/interfaces/`  
**Purpose**: Defines external communication mechanisms  
**Dependencies**: All other layers (orchestrates communication)

```go
// pkg/interfaces/api/pipeline_routes.go
package api

func (s *Server) registerPipelineRoutes() {
    pipelineGroup := s.router.Group("/api/v1/pipelines")
    pipelineGroup.Use(s.authMiddleware.Authenticate())

    pipelineGroup.POST("/", s.pipelineController.CreatePipeline)
    pipelineGroup.GET("/", s.pipelineController.ListPipelines)
    pipelineGroup.GET("/:id", s.pipelineController.GetPipeline)
    pipelineGroup.PUT("/:id", s.pipelineController.UpdatePipeline)
    pipelineGroup.DELETE("/:id", s.pipelineController.DeletePipeline)
    pipelineGroup.POST("/:id/execute", s.pipelineController.ExecutePipeline)
}
```

### Infrastructure Layer

**Location**: `pkg/infrastructure/`  
**Purpose**: Implements technical concerns and external system integrations  
**Dependencies**: Can import from any layer for implementation

```go
// pkg/infrastructure/database/pipeline_repository.go
package database

type PipelineRepository struct {
    db     *sql.DB
    logger *logger.Logger
}

func (r *PipelineRepository) Save(pipeline *entities.Pipeline) error {
    query := `
        INSERT INTO pipelines (id, name, description, status, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            status = EXCLUDED.status,
            updated_at = EXCLUDED.updated_at
    `

    _, err := r.db.Exec(query,
        pipeline.ID.String(),
        pipeline.Name,
        pipeline.Description,
        string(pipeline.Status),
        pipeline.CreatedAt,
        pipeline.UpdatedAt,
    )

    if err != nil {
        r.logger.Error("failed to save pipeline", "pipeline_id", pipeline.ID, "error", err)
        return fmt.Errorf("database error: %w", err)
    }

    return nil
}

func (r *PipelineRepository) FindByID(id entities.PipelineID) (*entities.Pipeline, error) {
    query := `
        SELECT id, name, description, status, created_at, updated_at
        FROM pipelines WHERE id = $1
    `

    var pipeline entities.Pipeline
    err := r.db.QueryRow(query, id.String()).Scan(
        &pipeline.ID,
        &pipeline.Name,
        &pipeline.Description,
        &pipeline.Status,
        &pipeline.CreatedAt,
        &pipeline.UpdatedAt,
    )

    if err != nil {
        if err == sql.ErrNoRows {
            return nil, entities.ErrPipelineNotFound
        }
        return nil, fmt.Errorf("database error: %w", err)
    }

    return &pipeline, nil
}
```

## Dependency Rules

### The Dependency Rule

Dependencies must point inward. Inner layers cannot know about outer layers.

```
Interfaces ──→ Adapters ──→ Application ──→ Domain
     │              │           │
     └──────────────┼───────────┘
                    │
               Infrastructure
```

### Port and Adapter Pattern

Application layer defines ports (interfaces), infrastructure implements them.

```go
// pkg/application/pipeline/ports/repository.go
package ports

type PipelineRepository interface {
    Save(pipeline *entities.Pipeline) error
    FindByID(id entities.PipelineID) (*entities.Pipeline, error)
    FindByName(name string) (*entities.Pipeline, error)
    List(filter PipelineFilter) ([]*entities.Pipeline, error)
    Delete(id entities.PipelineID) error
}

type EventBus interface {
    Publish(events ...events.DomainEvent) error
    Subscribe(eventType string, handler EventHandler) error
}

type Logger interface {
    Info(msg string, fields ...Field)
    Error(msg string, fields ...Field)
    Debug(msg string, fields ...Field)
}
```

```go
// pkg/infrastructure/events/memory_event_bus.go
package events

type MemoryEventBus struct {
    handlers map[string][]ports.EventHandler
    mutex    sync.RWMutex
}

func (bus *MemoryEventBus) Publish(events ...events.DomainEvent) error {
    bus.mutex.RLock()
    defer bus.mutex.RUnlock()

    for _, event := range events {
        eventType := event.Type()
        if handlers, exists := bus.handlers[eventType]; exists {
            for _, handler := range handlers {
                go func(h ports.EventHandler, e events.DomainEvent) {
                    if err := h.Handle(e); err != nil {
                        // Log error, don't fail the publish
                        log.Printf("event handler error: %v", err)
                    }
                }(handler, event)
            }
        }
    }

    return nil
}
```

## Design Patterns

### Command Query Responsibility Segregation (CQRS)

Separate read and write operations for better scalability.

```go
// pkg/application/commands/create_pipeline_command.go
package commands

type CreatePipelineCommand struct {
    Name        string `json:"name" validate:"required,min=3,max=100"`
    Description string `json:"description" validate:"max=500"`
    CreatedBy   string `json:"created_by" validate:"required"`
}

func (cmd CreatePipelineCommand) Validate() error {
    return validator.Validate(cmd)
}
```

```go
// pkg/application/queries/get_pipeline_query.go
package queries

type GetPipelineQuery struct {
    ID     string `json:"id" validate:"required,uuid"`
    UserID string `json:"user_id" validate:"required"`
}

type PipelineQueryResult struct {
    ID          string    `json:"id"`
    Name        string    `json:"name"`
    Description string    `json:"description"`
    Status      string    `json:"status"`
    CreatedAt   time.Time `json:"created_at"`
    UpdatedAt   time.Time `json:"updated_at"`
}
```

### Domain Events

Enable loose coupling between bounded contexts.

```go
// pkg/domain/pipeline/events/pipeline_events.go
package events

type PipelineCreatedEvent struct {
    BaseEvent
    PipelineID  string    `json:"pipeline_id"`
    Name        string    `json:"name"`
    CreatedBy   string    `json:"created_by"`
    CreatedAt   time.Time `json:"created_at"`
}

func NewPipelineCreatedEvent(pipelineID, name, createdBy string) *PipelineCreatedEvent {
    return &PipelineCreatedEvent{
        BaseEvent:  NewBaseEvent("pipeline.created"),
        PipelineID: pipelineID,
        Name:       name,
        CreatedBy:  createdBy,
        CreatedAt:  time.Now(),
    }
}
```

### Repository Pattern

Abstract data access behind interfaces.

```go
// pkg/domain/pipeline/repositories/pipeline_repository.go
package repositories

type PipelineRepository interface {
    Save(pipeline *entities.Pipeline) error
    FindByID(id entities.PipelineID) (*entities.Pipeline, error)
    FindByUserID(userID string) ([]*entities.Pipeline, error)
    Delete(id entities.PipelineID) error
}
```

### Factory Pattern

Create complex domain objects with proper validation.

```go
// pkg/domain/pipeline/factories/pipeline_factory.go
package factories

type PipelineFactory struct {
    validator *validator.Validator
}

func (f *PipelineFactory) CreatePipeline(name, description, createdBy string) (*entities.Pipeline, error) {
    // Validate inputs
    if err := f.validatePipelineData(name, description, createdBy); err != nil {
        return nil, err
    }

    // Create pipeline with business rules
    pipeline := &entities.Pipeline{
        ID:          entities.NewPipelineID(),
        Name:        name,
        Description: description,
        Status:      entities.StatusDraft,
        CreatedBy:   createdBy,
        CreatedAt:   time.Now(),
        UpdatedAt:   time.Now(),
    }

    // Apply domain events
    pipeline.RaiseEvent(events.NewPipelineCreatedEvent(
        pipeline.ID.String(),
        pipeline.Name,
        pipeline.CreatedBy,
    ))

    return pipeline, nil
}
```

## Testing Strategy

### Unit Testing (Domain Layer)

Test business logic in isolation.

```go
// pkg/domain/pipeline/entities/pipeline_test.go
package entities_test

func TestPipeline_AddStep(t *testing.T) {
    tests := []struct {
        name          string
        pipeline      *entities.Pipeline
        step          entities.PipelineStep
        expectedError error
    }{
        {
            name:     "should add step to draft pipeline",
            pipeline: entities.NewPipeline("test", "description"),
            step:     entities.PipelineStep{Name: "step1", Type: "extract"},
            expectedError: nil,
        },
        {
            name:     "should reject empty step name",
            pipeline: entities.NewPipeline("test", "description"),
            step:     entities.PipelineStep{Name: "", Type: "extract"},
            expectedError: entities.ErrInvalidStepName,
        },
        {
            name: "should reject step on running pipeline",
            pipeline: &entities.Pipeline{
                Status: entities.StatusRunning,
            },
            step: entities.PipelineStep{Name: "step1", Type: "extract"},
            expectedError: entities.ErrCannotModifyRunningPipeline,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := tt.pipeline.AddStep(tt.step)
            assert.Equal(t, tt.expectedError, err)
        })
    }
}
```

### Integration Testing (Application Layer)

Test use cases with mocked dependencies.

```go
// pkg/application/pipeline/services/pipeline_service_test.go
package services_test

func TestPipelineService_CreatePipeline(t *testing.T) {
    // Setup mocks
    repo := mocks.NewPipelineRepository()
    eventBus := mocks.NewEventBus()
    logger := mocks.NewLogger()

    service := services.NewPipelineService(repo, eventBus, logger)

    // Test data
    cmd := commands.CreatePipelineCommand{
        Name:        "test-pipeline",
        Description: "test description",
        CreatedBy:   "user123",
    }

    // Execute
    err := service.CreatePipeline(cmd)

    // Verify
    assert.NoError(t, err)
    assert.True(t, repo.SaveCalled())
    assert.True(t, eventBus.PublishCalled())
}
```

### End-to-End Testing (Full Stack)

Test complete workflows through HTTP API.

```go
// tests/e2e/pipeline_test.go
package e2e_test

func TestCreatePipeline_E2E(t *testing.T) {
    // Setup test server
    server := setupTestServer(t)
    defer server.Close()

    // Test data
    payload := map[string]interface{}{
        "name":        "test-pipeline",
        "description": "test description",
    }

    // Make request
    resp := makeRequest(t, server, "POST", "/api/v1/pipelines", payload)

    // Verify response
    assert.Equal(t, http.StatusCreated, resp.StatusCode)

    // Verify in database
    pipeline := getPipelineFromDB(t, "test-pipeline")
    assert.NotNil(t, pipeline)
    assert.Equal(t, "test-pipeline", pipeline.Name)
}
```

## Benefits of Clean Architecture

### 1. Testability

- Domain logic can be tested without external dependencies
- Application logic can be tested with mocked ports
- Each layer can be tested independently

### 2. Maintainability

- Clear separation of concerns
- Changes in one layer don't affect others
- Easy to understand and modify

### 3. Flexibility

- Can change UI without affecting business logic
- Can change database without affecting business logic
- Can change external APIs without affecting core functionality

### 4. Independence

- Framework independence
- Database independence
- UI independence
- External service independence

### 5. Scalability

- CQRS enables read/write scaling
- Event-driven architecture supports distributed systems
- Clear boundaries enable microservice extraction

---

**Version**: 0.9.0
**Last Updated**: 2025-08-02  
**Author**: FLEXT Development Team
