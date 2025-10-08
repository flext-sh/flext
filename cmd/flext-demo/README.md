# FLEXT Demo Server

**Type**: Go Service | **Status**: Active Development | **Dependencies**: Go 1.24+, pkg/controlpanel

FLEXT Demo Server is a simple HTTP server demonstration showcasing basic FLEXT controlpanel integration patterns. It provides a basic server implementation using FLEXT's controlpanel configuration and monitoring components.

> **⚠️ Current Reality**: Simple HTTP server with controlpanel integration, not the elaborate demo system described in previous versions

## Quick Start

```bash
# Build demo server
cd ..cmd/flext-demo
go build -o flext-demo main.go

# Run server (default port 8080)
./flext-demo
```

## Current Reality

**What Actually Works:**

- ✅ **HTTP Server**: Basic HTTP server using controlpanel/monitoring/server
- ✅ **Configuration**: Demo-specific configuration extending base config
- ✅ **Logging**: Structured logging with flext logging package
- ✅ **Graceful Shutdown**: Signal handling with context timeout
- ✅ **Command Line Flags**: Port, host, node-id, cluster, environment flags
- ✅ **Health Routes**: Basic routes via server.SetupBasicRoutes()

**What Needs Work:**

- ❌ **Demo Scenarios**: No actual demo scenarios implemented
- ❌ **Educational Content**: No interactive demos or examples
- ❌ **Data Generators**: No sample data generation
- ❌ **Pipeline Examples**: No data pipeline demonstrations

## Architecture Role in FLEXT Ecosystem

### **Demo Service Component**

FLEXT Demo provides a simple demonstration of controlpanel integration:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM (32 Projects)                 │
├─────────────────────────────────────────────────────────────────┤
│ Services: FLEXT Service:8081 | FlexCore:8080 | [FLEXT-DEMO]     │
├─────────────────────────────────────────────────────────────────┤
│ Applications: API | Auth | Web | CLI | Quality | Observability  │
├─────────────────────────────────────────────────────────────────┤
│ Infrastructure: Oracle | LDAP | LDIF | gRPC | Plugin | WMS      │
├─────────────────────────────────────────────────────────────────┤
│ Singer Ecosystem: Taps(5) | Targets(5) | DBT(4) | Extensions(1) │
├─────────────────────────────────────────────────────────────────┤
│ Foundation: FLEXT-CORE (FlextResult | DI | Domain Patterns)     │
└─────────────────────────────────────────────────────────────────┘
```

### **Core Responsibilities**

1. **Demo Server**: Simple HTTP server for demonstrating basic patterns
2. **Configuration Demo**: Shows controlpanel configuration usage
3. **Monitoring Demo**: Demonstrates server setup and monitoring

## Key Features

### **Current Implementation**

```go
// main.go - Current working implementation
type DemoServer struct {
    nodeID      string
    clusterName string
    startTime   time.Time
    logger      logging.Logger
    config      *DemoConfig
    server      *server.Server
    httpServer  *http.Server
}

// Demo configuration extends base config
type DemoConfig struct {
    *config.Config
    NodeID      string
    ClusterName string
}
```

### **Package Dependencies**

- `github.com/flext-sh/flext/pkg/controlpanel/configuration/config`
- `github.com/flext-sh/flext/pkg/controlpanel/monitoring/server`
- `github.com/flext-sh/flext/pkg/logging`
- Standard Go libraries (context, flag, http, etc.)

## Installation & Usage

### Build and Run

```bash
# Build demo server
cd ..cmd/flext-demo
go build -o flext-demo main.go

# Run with default settings
./flext-demo

# Run with custom configuration
./flext-demo --port 9090 --host localhost --node-id demo-002 --cluster my-cluster --env production
```

### Command Line Options

```bash
./flext-demo [options]

Options:
  --port         Server port (default: 8080)
  --host         Server host (default: 0.0.0.0)
  --node-id      Node ID (default: demo-001)
  --cluster      Cluster name (default: flext-demo)
```

### Configuration

**Demo Configuration Structure:**

```go
// DemoConfig extends base config
baseCfg := &config.Config{}
baseCfg.Server.Host = host
baseCfg.Server.Port = port
baseCfg.Server.Environment = env
baseCfg.Server.Debug = (env != "production")
baseCfg.FlexCore.URL = "http://localhost:8080"

cfg := &DemoConfig{
    Config:      baseCfg,
    NodeID:      nodeID,
    ClusterName: cluster,
}
```

## Development Commands

### Build Operations

```bash
# Build demo server
go build -o flext-demo main.go

# Cross-platform builds
GOOS=linux GOARCH=amd64 go build -o flext-demo-linux main.go
GOOS=darwin GOARCH=amd64 go build -o flext-demo-darwin main.go
```

### Testing

```bash
# Run Go tests
go test ./...

# Test with coverage
go test -cover ./...

# Run server for testing
./flext-demo --port 8082
```

### Server Operations

```bash
# Start demo server
./flext-demo --port 8080

# Test server health (when routes are implemented)
# curl http://localhost:8080/health

# View server logs
# Server logs to stdout with structured JSON logging
```

## Quality Standards

### **Current Code Quality**

- **Go 1.24+**: Modern Go with proper error handling
- **Structured Logging**: Uses FLEXT logging package with structured output
- **Configuration**: Proper configuration management with DemoConfig
- **Graceful Shutdown**: Context-based shutdown with 10-second timeout
- **Signal Handling**: Proper SIGINT/SIGTERM handling

### **Development Standards**

- **Go Best Practices**: Follow Go conventions and idioms
- **Error Handling**: Proper error handling with context
- **Logging**: Structured logging with consistent field names
- **Configuration**: Extend base configuration patterns

## Integration with FLEXT Ecosystem

### **Controlpanel Integration**

```bash
# Demo server uses controlpanel components:
# - pkg/controlpanel/configuration/config (configuration management)
# - pkg/controlpanel/monitoring/server (HTTP server setup)
# - pkg/logging (structured logging)
```

### **Package Structure**

- **main.go**: Demo server implementation
- **DemoServer**: Server struct with controlpanel integration
- **DemoConfig**: Configuration extending base config
- Uses controlpanel monitoring server for HTTP handling

## Current Status

**Version**: 0.9.0 (Development - Basic HTTP Server)

**Completed**:

- ✅ Basic HTTP server implementation
- ✅ Controlpanel configuration integration
- ✅ Structured logging setup
- ✅ Command line argument parsing
- ✅ Graceful shutdown handling

**Critical Gaps**:

- ❌ No actual demo scenarios implemented
- ❌ No educational content or examples
- ❌ No data pipeline demonstrations
- ❌ No interactive features

**Future Development**:

- 📋 Add actual demo scenarios and examples
- 📋 Implement educational content and tutorials
- 📋 Create data pipeline demonstrations
- 📋 Add interactive demo features

## Future Architecture

### **Planned Demo Features**

**Educational Demos:**

- Basic data integration examples
- Configuration pattern demonstrations
- Error handling and logging examples
- Service integration patterns

**Interactive Examples:**

- Command-line driven demos
- Step-by-step tutorials
- Best practice examples
- Architecture pattern demonstrations

**Code Examples:**

- Clean Architecture implementations
- Domain-Driven Design patterns
- Error handling strategies
- Testing approaches

## Contributing

### Development Workflow

```bash
# Setup and build
cd cmd/flext-demo
go build -o flext-demo main.go
./flext-demo

# Development cycle
# 1. Add demo features
# 2. Test locally
# 3. Add tests
# 4. Build and validate
```

### Architecture Guidelines

- **Controlpanel Integration**: Use controlpanel components for consistency
- **Go Standards**: Follow Go best practices and conventions
- **Configuration**: Extend base configuration patterns
- **Logging**: Use structured logging with proper field names

## Troubleshooting

### Common Issues

**Server Won't Start:**

- Check port availability: `netstat -tulpn | grep 8080`
- Verify Go build completed successfully
- Check for proper flag parsing

**Configuration Issues:**

- Verify flag syntax: `--port 8080` not `-port 8080`
- Check environment setting: development vs production
- Ensure FlexCore URL is accessible if needed

### Diagnostic Commands

```bash
# Test server startup
./flext-demo --env development --port 8082

# Check process
ps aux | grep flext-demo

# Test with different configurations
./flext-demo --help
```

## License

MIT License - See [LICENSE](../../LICENSE) file for details.

## Links

- **[FLEXT Hub](../../docs/NAVIGATION.md)**: Complete ecosystem navigation
- **[FLEXT Service](../flext/)**: Main data integration service
- **[FlexCore](../../flexcore/)**: Go runtime service
- **[FLEXT Core](../../flext-core/)**: Foundation library

---
