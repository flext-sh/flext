# FLEXT Service - Enterprise Data Integration Engine

**Type**: Core Service | **Status**: Active Development | **Dependencies**: Go 1.24+, Python 3.13+, PostgreSQL, Redis

FLEXT Service is the enterprise-grade data integration engine serving as the primary Python bridge and multi-modal interface for the entire FLEXT ecosystem. Built with Go/Python hybrid architecture, it implements Clean Architecture, Domain-Driven Design, and Railway-oriented programming for production scalability.

> **⚠️ Critical Configuration**: FLEXT Service runs on **port 8081** (not 8080 - that's FlexCore). Ensure correct port configuration in deployment environments.

## Quick Start

```bash
# Build and run FLEXT Service
cd .
go build -o flext main.go
./flext --mode server --config ../../config.yaml

# Service will start on port 8081 (FLEXT Service standard)
# Health check: curl http://localhost:8081/health
```

## Current Reality

**What Actually Works:**

- ✅ **Multi-Modal Operation**: Server, CLI, and interactive modes with intelligent detection
- ✅ **Railway-Oriented Programming**: Comprehensive error handling with ServiceInitializationResult
- ✅ **DI Container**: Real dependency injection with plugin handlers registration
- ✅ **Enterprise Architecture**: Clean Architecture + DDD + CQRS patterns implemented
- ✅ **Python Bridge**: Unified Meltano/Singer/DBT integration via flext-meltano
- ✅ **FlexCore Coordination**: Bidirectional API communication (ports 8081 ↔ 8080)
- ✅ **Production Features**: Graceful shutdown, health monitoring, structured logging

**Architecture Validation:**

- ✅ **Clean Architecture**: Strict layered architecture with dependency inversion
- ✅ **Domain-Driven Design**: 5 bounded contexts (Pipeline, Plugin, Singer, Meltano, WMS)
- ✅ **Service Initialization**: Railway pattern with explicit error handling chain
- ✅ **Configuration Management**: Enterprise YAML configuration with environment overrides

## Architecture Role in FLEXT Ecosystem

### **Enterprise Hybrid Architecture**

FLEXT Service coordinates the entire ecosystem as the central integration engine:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM (32 Projects)                 │
├─────────────────────────────────────────────────────────────────┤
│ Services: [FLEXT SERVICE:8081] ↔ FlexCore:8080 | Control Panel  │
├─────────────────────────────────────────────────────────────────┤
│ Applications: API | Auth | Web | CLI | Quality | Observability  │
├─────────────────────────────────────────────────────────────────┤
│ Infrastructure: Oracle | LDAP | LDIF | gRPC | Plugin | WMS      │
├─────────────────────────────────────────────────────────────────┤
│ Singer Ecosystem: Taps(5) | Targets(5) | DBT(4) | Extensions(1) │
├─────────────────────────────────────────────────────────────────┤
│ Foundation: FLEXT-CORE (FlextCore.Result | DI | Domain Patterns)     │
└─────────────────────────────────────────────────────────────────┘
```

### **Key Responsibilities**

1. **Data Integration Engine**: Primary service for all ETL/ELT operations
2. **Python-Go Bridge**: Native integration with Python ecosystem (Meltano, Singer, DBT)
3. **Service Orchestration**: Coordination with FlexCore and ecosystem services
4. **Multi-Modal Interface**: Server, CLI, and interactive modes with auto-detection

## Installation & Usage

### Multi-Modal Operation

**Automatic Mode Detection** (implemented in main.go):

```bash
# Server Mode (Production)
./flext                          # Auto-detects container environment → Server Mode
./flext --mode server            # Explicit server mode
FLEXT_MODE=server ./flext        # Environment variable

# CLI Mode (Automation)
./flext pipeline list            # Auto-detects TTY + args → CLI Mode
./flext --mode cli system health # Explicit CLI mode

# Interactive Mode (Development)
./flext --mode interactive       # Explicit interactive REPL mode
```

### Configuration

**Enterprise Configuration** (config.YAML):

```yaml
app:
  mode: "auto" # auto, server, cli, interactive
  environment: "production"
  debug: false

server:
  host: "0.0.0.0"
  port: 8081 # FLEXT Service standard (NOT 8080)
  timeout: 30s

database:
  url: "postgresql://localhost:5433/flext" # Port 5433 (not default 5432)
  pool_size: 20

redis:
  url: "redis://localhost:6380" # Port 6380 (not default 6379)
  pool_size: 10

flexcore:
  url: "http://localhost:8080" # FlexCore coordination
  timeout: 30s

python:
  meltano_project_root: "./meltano_project"
  virtual_env: "./venv"
  timeout: "300s"
```

### Environment Variables

| Variable             | Description                                  | Default                           |
| -------------------- | -------------------------------------------- | --------------------------------- |
| `FLEXT_MODE`         | Operation mode (server/cli/interactive/auto) | auto                              |
| `FLEXT_SERVER_PORT`  | Server port (CRITICAL: use 8081)             | 8081                              |
| `FLEXT_DATABASE_URL` | PostgreSQL connection                        | postgresql://localhost:5433/flext |
| `FLEXT_REDIS_URL`    | Redis connection                             | redis://localhost:6380            |
| `FLEXT_FLEXCORE_URL` | FlexCore service URL                         | <http://localhost:8080>           |

## Development Commands

### Essential Workflow

```bash
# Enterprise validation (MANDATORY before commits)
make validate              # Complete validation pipeline
make build                 # Build optimized Go binary
make run                   # Start FLEXT Service with full configuration
make test                  # Comprehensive test suite

# Quality gates (ZERO TOLERANCE)
make lint                  # golangci-lint with comprehensive rules
make vet                   # Go vet static analysis
make security              # gosec security scanning
make format                # gofmt + goimports
```

### Service Operations

```bash
# Production service management
go run main.go --mode server --config config.yaml    # Server startup
go run main.go --mode cli pipeline list              # CLI operations
go run main.go --mode interactive                    # Interactive REPL

# Health monitoring and integration validation
curl http://localhost:8081/health                     # Basic health check
curl http://localhost:8081/health?detail=true        # Detailed health status
curl http://localhost:8081/api/v1/flexcore/health    # FlexCore integration status
curl http://localhost:8081/metrics                   # Prometheus metrics
```

### API Endpoints (Development)

```bash
# Core service endpoints
GET  /health                              # Service health check
GET  /metrics                             # Prometheus metrics
GET  /api/v1/status                       # Service status

# Plugin management
GET    /api/v1/plugins                    # List available plugins
POST   /api/v1/plugins/{id}/execute       # Execute specific plugin

# Unified Meltano/Singer/DBT integration
GET    /api/v1/meltano/projects           # Meltano projects
POST   /api/v1/meltano/run                # Execute Meltano pipeline
GET    /api/v1/singer/taps                # Singer taps
POST   /api/v1/singer/extract             # Singer extraction
GET    /api/v1/dbt/models                 # DBT models
POST   /api/v1/dbt/run                    # DBT transformations

# FlexCore integration
GET    /api/v1/flexcore/health            # FlexCore service health
POST   /api/v1/flexcore/plugins/execute   # Execute FlexCore plugins
```

## Docker & Production Deployment

### Development Environment

```bash
# Complete development stack
docker-compose up -d                      # Full stack with dependencies

# Service access points
# FLEXT Service: http://localhost:8081    (PRIMARY SERVICE)
# FlexCore API:  http://localhost:8080    (Runtime coordination)
# PostgreSQL:    localhost:5433           (Database)
# Redis:         localhost:6380           (Coordination and caching)
```

### Production Dockerfile

```dockerfile
# Multi-stage production build
FROM golang:1.24-alpine AS builder
WORKDIR /app
COPY . .
RUN go mod download
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o flext cmd/flext/main.go

FROM python:3.13-slim AS runtime
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /app/flext .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8081
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

CMD ["./flext", "--mode", "server"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flext-service
  labels:
    app: flext-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flext-service
  template:
    metadata:
      labels:
        app: flext-service
    spec:
      containers:
        - name: flext-service
          image: flext/service:2.0.0
          ports:
            - containerPort: 8081
              name: http
          env:
            - name: FLEXT_MODE
              value: "server"
            - name: FLEXT_SERVER_PORT
              value: "8081"
            - name: FLEXT_DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: flext-secrets
                  key: database-url
            - name: FLEXT_FLEXCORE_URL
              value: "http://flexcore-service:8080"
          livenessProbe:
            httpGet:
              path: /health
              port: 8081
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8081
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
```

## Quality Standards

### **Enterprise Quality Gates**

- **Test Coverage**: Minimum 80% with regression prevention
- **Performance**: Sub-200ms API response times
- **Security**: Zero vulnerabilities (gosec + dependency audit)
- **Code Quality**: Zero warnings (golangci-lint comprehensive rules)
- **Architecture**: Clean Architecture + DDD + Railway-oriented programming

### **Production Readiness**

- **High Availability**: Multi-node Kubernetes deployment with auto-failover
- **Health Monitoring**: Comprehensive health checks with dependency validation
- **Performance**: Validated for 1M+ records/hour data processing
- **Monitoring**: Real-time performance metrics with Prometheus/Grafana
- **Zero-Downtime**: Rolling updates with health validation

## Integration with FLEXT Ecosystem

### **Service Coordination**

```bash
# FLEXT Service (8081) ↔ FlexCore (8080) Integration
curl -X POST http://localhost:8081/api/v1/flexcore/plugins/execute \
  -H "Content-Type: application/json" \
  -d '{"plugin": "meltano", "command": "--version"}'

# Python Bridge Integration
curl -X POST http://localhost:8081/api/v1/meltano/run \
  -H "Content-Type: application/json" \
  -d '{"pipeline": "extract-load", "target": "postgres"}'
```

### **Ecosystem Position**

- **Foundation**: Built on flext-core patterns (FlextCore.Result, DI Container)
- **Coordination**: Primary service orchestrating all 32 ecosystem projects
- **Integration**: Python bridge for Singer taps/targets, Meltano, and DBT
- **Monitoring**: Integrated with flext-observability for comprehensive metrics

## Troubleshooting

### Common Production Issues

**Port Configuration:**

- ❌ **Wrong Port**: Using 8080 instead of 8081 (conflicts with FlexCore)
- ✅ **Correct Port**: FLEXT Service uses 8081, FlexCore uses 8080

**Service Communication:**

- ❌ **Connection Failed**: Check FlexCore availability at localhost:8080
- ✅ **Health Validation**: Both services should return healthy status

**Multi-Modal Issues:**

- ❌ **Mode Detection**: Set explicit mode if auto-detection fails
- ✅ **Environment**: Check TTY, container, and argument detection

### Diagnostic Commands

```bash
# System diagnostics
./flext --mode cli system diagnose       # Complete system health check
./flext --mode cli system doctor         # Configuration validation
curl http://localhost:8081/health?detail=true    # Detailed health status

# Performance profiling
go tool pprof http://localhost:8081/debug/pprof/profile  # CPU profiling
go tool pprof http://localhost:8081/debug/pprof/heap     # Memory profiling

# Integration debugging
curl http://localhost:8081/api/v1/flexcore/health        # FlexCore status
redis-cli -h localhost -p 6380 INFO                     # Redis status
psql -h localhost -p 5433 -U flext -d flext            # PostgreSQL status
```

## Contributing

### Architecture Standards

- **Clean Architecture**: Maintain strict layer separation
- **Railway-Oriented Programming**: Use ServiceInitializationResult pattern
- **Domain-Driven Design**: Follow bounded context patterns
- **Go Best Practices**: Follow Go conventions and idioms

### Development Workflow

```bash
# Setup and validation
cd cmd/flext
go build -o flext main.go
make validate                    # MANDATORY before commits
./flext --mode server --config config.yaml
```

## License

MIT License - See project root for license details.

## Links

- **[FLEXT Hub](../../docs/README.md)**: Complete ecosystem navigation
- **[FlexCore](../../flexcore/)**: Go runtime service (port 8080)
- **[FLEXT Core](../../flext-core/)**: Foundation library with FlextCore.Result patterns
- **[Complete Documentation](../../docs/README.md)**: Architecture and integration guides

---

_Enterprise data integration engine - Core service of the FLEXT ecosystem_
