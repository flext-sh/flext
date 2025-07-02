# 🏗️ REFATORAÇÃO: DE HEXAGONAL/DDD PARA CLEAN ARCHITECTURE

## 📐 NOVA ESTRUTURA PROPOSTA

```
internal/
├── domain/                      # Entities (Enterprise Business Rules)
│   ├── pipeline/
│   │   ├── entity.go           # Pipeline entity pura
│   │   ├── value_objects.go    # Step, Configuration, etc
│   │   └── rules.go            # Business rules/invariants
│   ├── plugin/
│   │   ├── entity.go
│   │   └── types.go
│   └── shared/
│       ├── entity.go           # Base entity (sem infraestrutura!)
│       └── events.go           # Domain events
│
├── usecases/                   # Use Cases (Application Business Rules)
│   ├── pipeline/
│   │   ├── create_pipeline.go
│   │   ├── add_step.go
│   │   ├── execute_pipeline.go
│   │   ├── get_pipeline.go
│   │   ├── list_pipelines.go
│   │   └── ports/              # Interfaces (declaradas pelo use case!)
│   │       ├── repository.go
│   │       ├── executor.go
│   │       └── event_bus.go
│   └── plugin/
│       ├── register_plugin.go
│       └── ports/
│           └── repository.go
│
├── adapters/                   # Interface Adapters
│   ├── controllers/            # HTTP/gRPC/CLI controllers
│   │   ├── http/
│   │   │   ├── pipeline_controller.go
│   │   │   └── dto/
│   │   │       ├── requests.go
│   │   │       └── responses.go
│   │   └── grpc/
│   │       └── pipeline_service.go
│   │
│   ├── presenters/            # Output formatting
│   │   ├── pipeline_presenter.go
│   │   └── json_presenter.go
│   │
│   └── gateways/              # Implementations of use case interfaces
│       ├── pipeline_repository.go      # Implements usecases.PipelineRepository
│       ├── plugin_repository.go
│       └── event_publisher.go
│
└── infrastructure/            # Frameworks & Drivers
    ├── persistence/
    │   ├── postgres/
    │   │   ├── connection.go
    │   │   ├── pipeline_store.go    # Low-level DB operations
    │   │   └── models.go            # DB models
    │   └── memory/
    │       └── pipeline_store.go
    ├── web/
    │   ├── server.go
    │   └── router.go
    └── config/
        └── config.go
```

## 🔄 FLUXO DE DEPENDÊNCIAS (Clean Architecture)

```
[External] → [Infrastructure] → [Adapters] → [Use Cases] → [Domain]
                                    ↓              ↓
                                [DTOs]      [Interfaces]
```

## 📝 EXEMPLO DE REFATORAÇÃO: CREATE PIPELINE

### 1️⃣ DOMAIN LAYER (Entities)

```go
// internal/domain/pipeline/entity.go
package pipeline

import (
    "errors"
    "github.com/google/uuid"
)

// Pipeline - Pure domain entity (NO infrastructure concerns!)
type Pipeline struct {
    id          uuid.UUID
    name        string
    description string
    isActive    bool
    steps       []Step
    tags        []string
}

// NewPipeline - Factory with business rules
func NewPipeline(name, description string) (*Pipeline, error) {
    if err := validateName(name); err != nil {
        return nil, err
    }

    return &Pipeline{
        id:          uuid.New(),
        name:        name,
        description: description,
        isActive:    true,
        steps:       make([]Step, 0),
        tags:        make([]string, 0),
    }, nil
}

// Business methods
func (p *Pipeline) AddStep(step Step) error {
    if err := p.validateStep(step); err != nil {
        return err
    }
    p.steps = append(p.steps, step)
    return nil
}

// Getters (encapsulation)
func (p *Pipeline) ID() uuid.UUID { return p.id }
func (p *Pipeline) Name() string { return p.name }
```

### 2️⃣ USE CASES LAYER

```go
// internal/usecases/pipeline/create_pipeline.go
package pipeline

import (
    "context"
    "github.com/flext-sh/flext/internal/domain/pipeline"
)

// CreatePipelineUseCase - Application business rule
type CreatePipelineUseCase struct {
    repo      PipelineRepository  // Interface declared here!
    events    EventPublisher      // Interface declared here!
    validator InputValidator      // Interface declared here!
}

// Input/Output DTOs
type CreatePipelineInput struct {
    Name        string
    Description string
    Tags        []string
}

type CreatePipelineOutput struct {
    ID          string
    Name        string
    Description string
    CreatedAt   string
}

// Execute - The use case
func (uc *CreatePipelineUseCase) Execute(ctx context.Context, input CreatePipelineInput) (*CreatePipelineOutput, error) {
    // Validate input
    if err := uc.validator.Validate(input); err != nil {
        return nil, err
    }

    // Check if name exists
    exists, err := uc.repo.ExistsByName(ctx, input.Name)
    if err != nil {
        return nil, err
    }
    if exists {
        return nil, ErrPipelineNameExists
    }

    // Create domain entity
    pipeline, err := pipeline.NewPipeline(input.Name, input.Description)
    if err != nil {
        return nil, err
    }

    // Add tags
    for _, tag := range input.Tags {
        pipeline.AddTag(tag)
    }

    // Persist
    if err := uc.repo.Save(ctx, pipeline); err != nil {
        return nil, err
    }

    // Publish event
    uc.events.Publish(ctx, PipelineCreatedEvent{
        PipelineID: pipeline.ID(),
        Name:       pipeline.Name(),
    })

    // Return output
    return &CreatePipelineOutput{
        ID:          pipeline.ID().String(),
        Name:        pipeline.Name(),
        Description: pipeline.Description(),
        CreatedAt:   time.Now().Format(time.RFC3339),
    }, nil
}
```

```go
// internal/usecases/pipeline/ports/repository.go
package ports

// PipelineRepository - Interface declared by use case
type PipelineRepository interface {
    Save(ctx context.Context, pipeline *pipeline.Pipeline) error
    FindByID(ctx context.Context, id uuid.UUID) (*pipeline.Pipeline, error)
    ExistsByName(ctx context.Context, name string) (bool, error)
}
```

### 3️⃣ ADAPTERS LAYER

```go
// internal/adapters/controllers/http/pipeline_controller.go
package http

type PipelineController struct {
    createUseCase *pipeline.CreatePipelineUseCase
    presenter     PipelinePresenter
}

func (c *PipelineController) Create(w http.ResponseWriter, r *http.Request) {
    // Parse request
    var req dto.CreatePipelineRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        c.presenter.PresentError(w, err)
        return
    }

    // Map to use case input
    input := pipeline.CreatePipelineInput{
        Name:        req.Name,
        Description: req.Description,
        Tags:        req.Tags,
    }

    // Execute use case
    output, err := c.createUseCase.Execute(r.Context(), input)
    if err != nil {
        c.presenter.PresentError(w, err)
        return
    }

    // Present response
    c.presenter.PresentPipelineCreated(w, output)
}
```

```go
// internal/adapters/gateways/pipeline_repository.go
package gateways

// PipelineRepositoryGateway - Implements use case interface
type PipelineRepositoryGateway struct {
    store persistence.PipelineStore  // Infrastructure interface
}

func (g *PipelineRepositoryGateway) Save(ctx context.Context, p *pipeline.Pipeline) error {
    // Convert domain to persistence model
    model := &persistence.PipelineModel{
        ID:          p.ID().String(),
        Name:        p.Name(),
        Description: p.Description(),
        // ... mapping
    }

    return g.store.Create(ctx, model)
}
```

### 4️⃣ INFRASTRUCTURE LAYER

```go
// internal/infrastructure/persistence/postgres/pipeline_store.go
package postgres

type PipelineStore struct {
    db *sql.DB
}

func (s *PipelineStore) Create(ctx context.Context, model *PipelineModel) error {
    query := `INSERT INTO pipelines (id, name, description) VALUES ($1, $2, $3)`
    _, err := s.db.ExecContext(ctx, query, model.ID, model.Name, model.Description)
    return err
}
```

## 🎯 BENEFÍCIOS DA REFATORAÇÃO

1. **Testabilidade**: Use cases podem ser testados sem infraestrutura
2. **Independência**: Domain não conhece nada externo
3. **Flexibilidade**: Fácil trocar banco, framework web, etc
4. **Clareza**: Cada camada tem responsabilidade clara
5. **DIP**: Dependency Inversion Principle aplicado corretamente

## 🔧 PASSOS PARA REFATORAÇÃO

1. **Criar nova estrutura** sem quebrar a existente
2. **Refatorar um bounded context** por vez
3. **Começar pelo domain** removendo dependências
4. **Criar use cases** extraindo lógica dos services
5. **Implementar adapters** para conectar camadas
6. **Mover infraestrutura** para camada externa
7. **Atualizar testes** para nova estrutura
8. **Remover código antigo** após validação
