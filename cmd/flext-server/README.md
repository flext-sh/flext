# FLEXT Server

High-performance HTTP API server for FLEXT data integration platform.

## Overview

The FLEXT Server provides RESTful API endpoints for managing data pipelines, plugins, and system operations. Built with Go for maximum performance and scalability.

## Features

- **RESTful API**: Complete HTTP API for all FLEXT operations
- **Pipeline Management**: Create, configure, and execute data pipelines
- **Plugin System**: Dynamic plugin loading and management
- **Meltano Integration**: Native Meltano project support
- **DBT Integration**: Data build tool integration
- **Health Monitoring**: Comprehensive health checks and metrics
- **Graceful Shutdown**: Clean shutdown with request completion
- **Structured Logging**: JSON-formatted logs with request tracing

## Installation

### From Binary

```bash
# Download latest release
curl -LO https://github.com/flext-sh/flext/releases/latest/download/flext-server
chmod +x flext-server
sudo mv flext-server /usr/local/bin/
```

### From Source

```bash
cd /home/marlonsc/flext/cmd/flext-server
go build -o flext-server main.go
```

## Usage

### Basic Startup

```bash
# Start server with default configuration
flext-server

# Use custom configuration
flext-server --config /path/to/config.yaml

# Override port
flext-server --port 9090
```

### Configuration Options

```bash
# Command line flags
flext-server --help

Options:
  --config string   Path to configuration file
  --port int        Server port (overrides config)
```

## API Endpoints

### Health and System

```http
GET /health              # Health check
GET /metrics             # Prometheus metrics
GET /api/v1/system/stats # System statistics
```

### Pipeline Operations

```http
GET    /api/v1/pipelines           # List pipelines
POST   /api/v1/pipelines           # Create pipeline
GET    /api/v1/pipelines/{id}      # Get pipeline
PUT    /api/v1/pipelines/{id}      # Update pipeline
DELETE /api/v1/pipelines/{id}      # Delete pipeline
POST   /api/v1/pipelines/{id}/run  # Execute pipeline
```

### Plugin Operations

```http
GET    /api/v1/plugins             # List plugins
POST   /api/v1/plugins             # Install plugin
GET    /api/v1/plugins/{name}      # Get plugin info
DELETE /api/v1/plugins/{name}      # Uninstall plugin
```

### Meltano Operations

```http
GET    /api/v1/meltano/projects    # List Meltano projects
POST   /api/v1/meltano/projects    # Create project
POST   /api/v1/meltano/run         # Run Meltano command
```

### DBT Operations

```http
GET    /api/v1/dbt/projects        # List DBT projects
POST   /api/v1/dbt/run             # Run DBT command
GET    /api/v1/dbt/docs            # Generate docs
```

## Configuration

### Configuration File

```yaml
# server-config.yaml
server:
  host: "0.0.0.0"
  port: 8080
  read_timeout: 30s
  write_timeout: 30s
  shutdown_timeout: 10s

database:
  url: "postgresql://localhost/flext"
  pool_size: 20
  max_idle_conns: 10

logging:
  level: "info"
  format: "json"
  structured: true

security:
  cors_enabled: true
  cors_origins: ["*"]
  rate_limit: 100
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLEXT_SERVER_HOST` | Server bind address | 0.0.0.0 |
| `FLEXT_SERVER_PORT` | Server port | 8080 |
| `FLEXT_DATABASE_URL` | Database connection URL | - |
| `FLEXT_LOG_LEVEL` | Logging level | info |
| `FLEXT_CONFIG_PATH` | Configuration file path | - |

## Architecture

### Clean Architecture

The server follows Clean Architecture principles:

```
cmd/flext-server/               # Main application
├── main.go                     # Application bootstrap
internal/
├── bounded_contexts/           # Domain boundaries
│   ├── pipeline/              # Pipeline domain
│   └── plugin/                # Plugin domain
├── infrastructure/            # Infrastructure layer
│   ├── server/               # HTTP server
│   ├── container/            # Dependency injection
│   └── logging/              # Structured logging
└── shared_kernel/            # Shared domain concepts
```

### Dependency Injection

The server uses a dependency injection container for:

- Repository implementations
- Use case orchestration
- Handler registration
- Configuration management

### Request Flow

1. **HTTP Request** → Router
2. **Router** → Handler
3. **Handler** → Use Case
4. **Use Case** → Repository
5. **Repository** → Database
6. **Response** ← Handler

## Development

### Building

```bash
# Build for current platform
go build -o flext-server main.go

# Build for multiple platforms
make build-server

# Build with optimizations
go build -ldflags="-s -w" -o flext-server main.go
```

### Testing

```bash
# Run all tests
go test ./...

# Run with coverage
go test -cover ./...

# Integration tests
go test -tags=integration ./...
```

### Hot Reload (Development)

```bash
# Install air for hot reload
go install github.com/cosmtrek/air@latest

# Start with hot reload
air -c .air.toml
```

## Deployment

### Docker

```dockerfile
FROM golang:1.24-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o flext-server cmd/flext-server/main.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/flext-server .
CMD ["./flext-server"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flext-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flext-server
  template:
    metadata:
      labels:
        app: flext-server
    spec:
      containers:
      - name: flext-server
        image: flext/server:latest
        ports:
        - containerPort: 8080
        env:
        - name: FLEXT_DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: flext-secrets
              key: database-url
```

## Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8080/health

# Detailed health check
curl http://localhost:8080/health?detail=true
```

### Metrics

The server exposes Prometheus metrics at `/metrics`:

- HTTP request duration
- Request count by endpoint
- Active connections
- Database connection pool stats
- Pipeline execution metrics

### Logging

Structured JSON logs include:

- Request ID for tracing
- User context
- Performance metrics
- Error details with stack traces

## Troubleshooting

### Common Issues

1. **Port Already in Use**: Change port with `--port` flag
2. **Database Connection Failed**: Check `DATABASE_URL` and network connectivity
3. **High Memory Usage**: Adjust connection pool settings
4. **Slow Responses**: Enable debug logging to identify bottlenecks

### Debug Mode

```bash
# Enable debug logging
FLEXT_LOG_LEVEL=debug flext-server

# Profile memory usage
go tool pprof http://localhost:8080/debug/pprof/heap

# Profile CPU usage
go tool pprof http://localhost:8080/debug/pprof/profile
```

## Security

- Input validation on all endpoints
- SQL injection prevention
- Rate limiting
- CORS configuration
- Request timeout enforcement
- Graceful error handling

## Performance

- Connection pooling
- Request batching
- Async pipeline execution
- Efficient JSON serialization
- Memory optimization

## License

MIT License - see [LICENSE](../../LICENSE) for details.

## Related

- [FLEXT CLI](../flext-cli/) - Command-line interface
- [FLEXT Demo](../flext-demo/) - Demo application
- [FLEXT Core](../../flext-core/) - Core framework library