# FLEXT Go Architecture Guide

## 🏗️ Domain-Driven Design Implementation in Go

This document describes the Go implementation of FLEXT following Clean Architecture and Domain-Driven Design principles.

### Architecture Overview

```
cmd/flext/           # Application entry point
internal/
├── bounded_contexts/    # Domain boundaries
│   ├── pipeline/       # Pipeline domain
│   └── plugin/         # Plugin domain
├── infrastructure/     # Infrastructure layer
│   ├── config/        # Configuration
│   ├── http/          # HTTP handlers and middleware
│   ├── persistence/   # Data persistence
│   └── logging/       # Structured logging
└── shared_kernel/     # Shared domain concepts
    ├── domain/        # Common domain types
    └── errors/        # Error handling
```

### Bounded Contexts

#### Pipeline Context
- **Domain**: Pipeline management and execution
- **Entities**: Pipeline, Step, Execution
- **Commands**: CreatePipeline, AddStep
- **Queries**: GetPipeline, ListPipelines

#### Plugin Context
- **Domain**: Plugin registration and lifecycle
- **Entities**: Plugin, Port, Configuration
- **Commands**: RegisterPlugin, UpdatePlugin
- **Queries**: GetPlugin, ListPlugins

### Clean Architecture Layers

#### 1. Domain Layer
```go
// Domain entities with business rules
type Pipeline struct {
    ID          string    `json:"id"`
    Name        string    `json:"name"`
    Description string    `json:"description"`
    Steps       []Step    `json:"steps"`
    CreatedAt   time.Time `json:"created_at"`
}

// Domain events for integration
type PipelineCreated struct {
    PipelineID string
    Name       string
    Timestamp  time.Time
}
```

#### 2. Application Layer
```go
// Commands for state changes
type CreatePipelineCommand struct {
    Name        string   `json:"name"`
    Description string   `json:"description"`
    Tags        []string `json:"tags"`
}

// Application services orchestrate use cases
type PipelineService struct {
    repo      ports.PipelineRepository
    publisher ports.EventPublisher
}
```

#### 3. Infrastructure Layer
```go
// HTTP handlers
func (h *PipelineHandler) CreatePipeline(c echo.Context) error {
    var cmd CreatePipelineCommand
    if err := c.Bind(&cmd); err != nil {
        return err
    }
    
    pipeline, err := h.service.CreatePipeline(cmd)
    if err != nil {
        return err
    }
    
    return c.JSON(http.StatusCreated, pipeline)
}
```

### API Endpoints

#### Pipeline Management
- `POST /api/v1/pipelines` - Create pipeline
- `GET /api/v1/pipelines` - List pipelines
- `GET /api/v1/pipelines/:id` - Get pipeline
- `POST /api/v1/pipelines/:id/steps` - Add step

#### Plugin Management
- `POST /api/v1/plugins` - Register plugin
- `GET /api/v1/plugins` - List plugins
- `GET /api/v1/plugins/:id` - Get plugin

#### System Endpoints
- `GET /health` - Health check
- `GET /` - API information

### Repository Pattern

```go
type PipelineRepository interface {
    Save(pipeline *Pipeline) error
    FindByID(id string) (*Pipeline, error)
    FindAll() ([]*Pipeline, error)
    Delete(id string) error
}

type InMemoryPipelineRepository struct {
    pipelines map[string]*Pipeline
    mutex     sync.RWMutex
}
```

### Event Publishing

```go
type EventPublisher interface {
    Publish(event DomainEvent) error
}

type InMemoryPublisher struct {
    handlers map[string][]EventHandler
}
```

### Configuration

The Go application uses environment-based configuration:

```bash
# Server configuration
FLEXT_PORT=8081
FLEXT_HOST=localhost

# Database configuration
FLEXT_DB_TYPE=memory  # or postgres, mysql
FLEXT_DB_URL=postgres://user:pass@localhost/flext

# Logging configuration
FLEXT_LOG_LEVEL=info
FLEXT_LOG_FORMAT=json
```

### Building and Running

#### Build Binary
```bash
go build -o flext cmd/flext/main.go
```

#### Run Application
```bash
./flext
```

#### Run with Environment Variables
```bash
FLEXT_PORT=8082 ./flext
```

### Testing

#### Unit Tests
```bash
go test ./internal/...
```

#### Integration Tests
```bash
go test ./tests/...
```

#### API Validation
```bash
./validate_api.sh
```

### Dependencies

#### Core Dependencies
- `github.com/labstack/echo/v4` - HTTP framework
- `github.com/google/uuid` - UUID generation

#### Development Dependencies
- `github.com/stretchr/testify` - Testing framework

### Error Handling

```go
type DomainError struct {
    Code    string `json:"code"`
    Message string `json:"message"`
    Details string `json:"details,omitempty"`
}

func (e DomainError) Error() string {
    return e.Message
}
```

### Best Practices

#### 1. Dependency Injection
```go
// Use constructor pattern for dependencies
func NewPipelineService(
    repo ports.PipelineRepository,
    publisher ports.EventPublisher,
) *PipelineService {
    return &PipelineService{
        repo:      repo,
        publisher: publisher,
    }
}
```

#### 2. Interface Segregation
```go
// Small, focused interfaces
type PipelineReader interface {
    FindByID(id string) (*Pipeline, error)
    FindAll() ([]*Pipeline, error)
}

type PipelineWriter interface {
    Save(pipeline *Pipeline) error
    Delete(id string) error
}
```

#### 3. Immutable Domain Events
```go
type DomainEvent interface {
    EventType() string
    Timestamp() time.Time
    AggregateID() string
}
```

### Integration with Python Components

The Go API serves as the gateway to Python-based FLEXT components:

1. **Pipeline Execution** → Delegates to `flext-meltano`
2. **Authentication** → Integrates with `flext-auth`
3. **Plugin Management** → Coordinates with `flext-plugin`
4. **Observability** → Reports to `flext-observability`

### Deployment

#### Docker
```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o flext cmd/flext/main.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/flext .
CMD ["./flext"]
```

#### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flext-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flext-api
  template:
    metadata:
      labels:
        app: flext-api
    spec:
      containers:
      - name: flext-api
        image: flext/api:latest
        ports:
        - containerPort: 8081
        env:
        - name: FLEXT_PORT
          value: "8081"
```

This Go implementation provides a high-performance, type-safe API gateway for the FLEXT framework while maintaining clean architecture principles and seamless integration with Python components.