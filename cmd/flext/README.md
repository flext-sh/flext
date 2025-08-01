# FLEXT Service - Data Integration Engine

The FLEXT Service is the core data processing engine of the FLEXT platform, providing unified access to Singer taps/targets, Meltano orchestration, and DBT transformations through a high-performance Go service with Python integration.

## Overview

FLEXT Service bridges the gap between high-performance Go runtime and Python's rich data ecosystem:

- **Multi-Modal Operation**: Server, CLI, and interactive modes with automatic detection
- **Python Bridge**: Native integration with Meltano, Singer, and DBT ecosystems
- **Plugin Architecture**: Extensible plugin system for data processing capabilities
- **Production Ready**: Enterprise-grade service with comprehensive monitoring
- **FlexCore Integration**: Seamless communication with FlexCore runtime container

## Installation

### From Binary

```bash
# Download latest release
curl -LO https://github.com/flext-sh/flext/releases/latest/download/flext
chmod +x flext
sudo mv flext /usr/local/bin/
```

### From Source

```bash
cd /home/marlonsc/flext/cmd/flext
go build -o flext main.go
```

## Usage

### Automatic Mode Detection

The application automatically detects the appropriate mode based on environment and arguments:

```bash
# Starts in server mode if running in container or with --server
flext

# Starts in CLI mode if interactive terminal detected
flext pipeline list

# Force specific mode
flext --mode server
flext --mode cli
flext --mode interactive
```

### Server Mode

```bash
# Start as HTTP API server
flext --mode server

# Custom configuration
flext --mode server --config /etc/flext/config.yaml

# Override port
flext --mode server --port 9090
```

### CLI Mode

```bash
# Use as command-line tool
flext pipeline create --name "data-sync"
flext plugin install tap-postgres
flext system health
```

### Interactive Mode

```bash
# Start interactive session
flext --mode interactive

# Interactive shell with tab completion
flext> pipeline list
flext> help commands
flext> exit
```

## Configuration

### Configuration File

```yaml
# flext.yaml
app:
  mode: "auto"          # auto, server, cli, interactive
  environment: "production"
  debug: false

server:
  host: "0.0.0.0"
  port: 8080
  timeout: 30s

cli:
  output_format: "table"  # table, json, yaml
  color: true
  pager: true

logging:
  level: "info"
  format: "json"
  structured: true

database:
  url: "postgresql://localhost/flext"
  pool_size: 20
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLEXT_MODE` | Operating mode (server/cli/interactive/auto) | auto |
| `FLEXT_CONFIG_PATH` | Configuration file path | ./flext.YAML |
| `FLEXT_SERVER_PORT` | Server port (server mode) | 8080 |
| `FLEXT_DATABASE_URL` | Database connection URL | - |
| `FLEXT_LOG_LEVEL` | Logging level | info |
| `FLEXT_ENVIRONMENT` | Environment (development/staging/production) | development |

## Modes

### 1. Server Mode

Production HTTP API server:

- RESTful API endpoints
- Health monitoring
- Metrics collection
- Graceful shutdown
- Load balancer ready

**Entry Points:**

- Container environments
- `--mode server` flag
- `FLEXT_MODE=server` environment variable
- Port binding detection

### 2. CLI Mode

Command-line interface:

- Rich command set
- Tab completion
- Colored output
- Progress indicators
- Batch operations

**Entry Points:**

- Interactive terminal with arguments
- `--mode cli` flag
- CI/CD environments
- Script execution

### 3. Interactive Mode

Interactive shell:

- REPL interface
- Command history
- Auto-completion
- Help system
- Session persistence

**Entry Points:**

- Interactive terminal without arguments
- `--mode interactive` flag
- Development environments
- User exploration

### 4. Auto Mode (Default)

Intelligent mode detection:

```
Environment Check ? Mode Selection
??? Container/Docker ? Server Mode
??? CI/CD Pipeline ? CLI Mode
??? Interactive TTY + Args ? CLI Mode
??? Interactive TTY + No Args ? Interactive Mode
??? Fallback ? Server Mode
```

## Architecture

### Application Bootstrap

```go
// main.go structure
func main() {
    // 1. Parse command line flags
    // 2. Load configuration
    // 3. Detect operating mode
    // 4. Initialize application
    // 5. Start appropriate mode
    // 6. Handle graceful shutdown
}
```

### Mode Implementations

```
cmd/flext/
??? main.go                    # Main entry point
??? modes/
?   ??? server.go             # Server mode implementation
?   ??? cli.go                # CLI mode implementation
?   ??? interactive.go        # Interactive mode implementation
?   ??? detector.go           # Mode detection logic
??? config/
?   ??? config.go             # Configuration management
?   ??? validation.go         # Configuration validation
??? bootstrap/
    ??? app.go                # Application bootstrap
    ??? shutdown.go           # Graceful shutdown
```

## Development

### Building

```bash
# Build for current platform
go build -o flext main.go

# Build optimized binary
go build -ldflags="-s -w" -o flext main.go

# Cross-compilation
GOOS=linux GOARCH=amd64 go build -o flext-linux main.go
GOOS=darwin GOARCH=amd64 go build -o flext-darwin main.go
GOOS=windows GOARCH=amd64 go build -o flext.exe main.go
```

### Testing

```bash
# Run all tests
go test ./...

# Test specific mode
go test -run TestServerMode

# Integration tests
go test -tags=integration ./...

# Benchmark tests
go test -bench=. ./...
```

### Debug Mode

```bash
# Enable debug logging
FLEXT_LOG_LEVEL=debug flext

# Profile application
go tool pprof flext profile.out

# Trace execution
FLEXT_TRACE=true flext
```

## Deployment

### Docker

```dockerfile
FROM golang:1.24-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -ldflags="-s -w" -o flext cmd/flext/main.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/flext .
EXPOSE 8080
CMD ["./flext"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flext
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flext
  template:
    metadata:
      labels:
        app: flext
    spec:
      containers:
      - name: flext
        image: flext/main:latest
        ports:
        - containerPort: 8080
        env:
        - name: FLEXT_MODE
          value: "server"
        - name: FLEXT_DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: flext-secrets
              key: database-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Systemd Service

```ini
[Unit]
Description=FLEXT Data Integration Platform
After=network.target

[Service]
Type=simple
User=flext
Group=flext
ExecStart=/usr/local/bin/flext --mode server --config /etc/flext/config.yaml
Restart=always
RestartSec=10
Environment=FLEXT_ENVIRONMENT=production

[Install]
WantedBy=multi-user.target
```

## Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8080/health

# Detailed health status
curl http://localhost:8080/health?detail=true
```

### Metrics

- Application metrics at `/metrics`
- Performance counters
- Resource usage
- Error rates
- Request latency

### Logging

Structured JSON logs with:

- Request tracing
- Performance metrics
- Error context
- User actions
- System events

## Production Considerations

### Performance

- Connection pooling
- Request optimization
- Memory management
- CPU utilization
- I/O efficiency

### Security

- Input validation
- Authentication
- Authorization
- Rate limiting
- Audit logging

### Reliability

- Health monitoring
- Graceful degradation
- Circuit breakers
- Retry mechanisms
- Failover support

### Scalability

- Horizontal scaling
- Load balancing
- Resource management
- Auto-scaling support
- Performance tuning

## Troubleshooting

### Common Issues

1. **Mode Detection Failed**: Set explicit mode with `--mode`
2. **Configuration Not Found**: Check `FLEXT_CONFIG_PATH`
3. **Port Already in Use**: Change port with `--port`
4. **Database Connection Failed**: Verify `DATABASE_URL`

### Diagnostic Commands

```bash
# Check configuration
flext config validate

# Test connectivity
flext system ping

# Show version and build info
flext version --detailed

# Generate diagnostic report
flext system diagnose
```

## License

MIT License - see [LICENSE](../../LICENSE) for details.

## Related

- [FLEXT CLI](../flext-cli/) - Dedicated CLI application
- [FLEXT Server](../flext-server/) - Dedicated server application
- [FLEXT Demo](../flext-demo/) - Demo application
- [FLEXT Core](../../flext-core/) - Core framework library
