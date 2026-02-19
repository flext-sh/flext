# FLEXT Control Panel


<!-- TOC START -->
- [Quick Start](#quick-start)
- [Current Reality](#current-reality)
- [Architecture Role in FLEXT Ecosystem](#architecture-role-in-flext-ecosystem)
  - [**Service Launcher Component**](#service-launcher-component)
  - [**Core Responsibilities**](#core-responsibilities)
- [Key Features](#key-features)
  - [**Current Implementation**](#current-implementation)
  - [**Package Dependencies**](#package-dependencies)
- [Installation & Usage](#installation-usage)
  - [Build and Run](#build-and-run)
  - [Configuration](#configuration)
- [Development Commands](#development-commands)
  - [Build Operations](#build-operations)
  - [Testing](#testing)
- [Quality Standards](#quality-standards)
  - [**Current Code Quality**](#current-code-quality)
  - [**Development Standards**](#development-standards)
- [Integration with FLEXT Ecosystem](#integration-with-flext-ecosystem)
  - [**Service Framework Integration**](#service-framework-integration)
  - [**Package Structure**](#package-structure)
- [Current Status](#current-status)
- [Future Architecture](#future-architecture)
  - [**Planned Control Panel Features**](#planned-control-panel-features)
- [Contributing](#contributing)
  - [Development Workflow](#development-workflow)
  - [Architecture Guidelines](#architecture-guidelines)
- [License](#license)
- [Links](#links)
<!-- TOC END -->

**Reviewed**: 2026-02-17 | **Scope**: Documentation alignment and link consistency


**FLEXT Control Panel** service launcher using the common flextservice framework. This service provides a standardized launch mechanism for control panel functionality within the FLEXT ecosystem.

**Reviewed**: 2026-02-17 | **Version**: 0.10.0-dev

Part of the [FLEXT](https://github.com/flext-sh/flext) ecosystem.

> **⚠️ Current Status**: Basic service launcher implemented, full control panel features in development

## Quick Start

```bash
# Build Control Panel
cd ..cmd/flext-control-panel
go build -o flext-control-panel main.go

# Run service (default port 8081)
./flext-control-panel
```

## Current Reality

**What Actually Works:**

- ✅ **Service Launcher**: Basic service launcher using pkg/flextservice
- ✅ **Port Configuration**: Configured for port 8081 (control panel standard)
- ✅ **Service Registration**: Proper service information registration
- ✅ **Common Framework**: Uses shared flextservice.LaunchService pattern

**What Needs Work:**

- ❌ **Control Panel Features**: Full management interface not implemented
- ❌ **FlexCore Integration**: gRPC communication with FlexCore not implemented
- ❌ **Web Dashboard**: Management interface missing
- ❌ **API Endpoints**: Control panel specific APIs not implemented

## Architecture Role in FLEXT Ecosystem

### **Service Launcher Component**

FLEXT Control Panel provides centralized management interface for ecosystem services:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM (32 Projects)                 │
├─────────────────────────────────────────────────────────────────┤
│ Services: FLEXT Service:8081 | FlexCore:8080 | [CONTROL-PANEL]  │
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

1. **Service Management**: Centralized control for FLEXT ecosystem services
2. **Monitoring Interface**: Dashboard for service health and metrics
3. **Configuration Management**: Centralized configuration coordination

## Key Features

### **Current Implementation**

```go
// main.go - Current working implementation
func main() {
    // Service configuration
    serviceInfo := flextservice.ServiceInfo{
        Name:        "flext-control-panel",
        DefaultPort: 8081,
        Description: "FLEXT Control Panel",
    }

    // Launch using common framework
    flextservice.LaunchService(serviceInfo)
}
```

### **Package Dependencies**

- `github.com/flext-sh/flext/pkg/flextservice` - Common service framework
- Standard Go libraries for service operation
- Port 8081 configuration (control panel standard)

## Installation & Usage

### Build and Run

```bash
# Build control panel
cd ..cmd/flext-control-panel
go build -o flext-control-panel main.go

# Run service
./flext-control-panel

# Service will start on port 8081
# Health check: curl http://localhost:8081/health (when implemented)
```

### Configuration

Currently uses the flextservice framework configuration:

```go
// Service configuration
serviceInfo := flextservice.ServiceInfo{
    Name:        "flext-control-panel",    // Service name
    DefaultPort: 8081,                     // Control panel port
    Description: "FLEXT Control Panel",    // Service description
}
```

## Development Commands

### Build Operations

```bash
# Build control panel binary
go build -o flext-control-panel main.go

# Cross-platform builds
GOOS=linux GOARCH=amd64 go build -o flext-control-panel-linux main.go
GOOS=darwin GOARCH=amd64 go build -o flext-control-panel-darwin main.go
```

### Testing

```bash
# Run Go tests
go test ./...

# Test with coverage
go test -cover ./...

# Run service locally for testing
./flext-control-panel
```

## Quality Standards

### **Current Code Quality**

- **Go 1.24+**: Modern Go with proper package structure
- **Service Framework**: Uses established flextservice patterns
- **Configuration**: Proper service configuration via ServiceInfo
- **Simplicity**: Clean, minimal launcher implementation

### **Development Standards**

- **Go Best Practices**: Follow Go conventions and idioms
- **Common Framework**: Use flextservice for consistency
- **Error Handling**: Proper Go error handling patterns
- **Testing**: Add tests for new functionality

## Integration with FLEXT Ecosystem

### **Service Framework Integration**

```bash
# Control panel integrates with ecosystem via flextservice
# (Implementation details in pkg/flextservice)
```

### **Package Structure**

- **main.go**: Service launcher using flextservice framework
- **pkg/flextservice**: Common service framework (shared)
- Port 8081: Control panel standard port (distinct from FLEXT Service)

## Current Status

**Version**: 0.9.0 (Development - Service Launcher)

**Completed**:

- ✅ Go service launcher implementation
- ✅ flextservice framework integration
- ✅ Port 8081 configuration
- ✅ Service information registration

**Critical Gaps**:

- ❌ Control panel management features missing
- ❌ Web dashboard interface not implemented
- ❌ API endpoints for service management missing
- ❌ FlexCore gRPC integration not implemented

**Planned Development**:

- 📋 Implement control panel management APIs
- 📋 Add web dashboard interface
- 📋 Create FlexCore integration via gRPC
- 📋 Add service monitoring and health checks

## Future Architecture

### **Planned Control Panel Features**

**Service Management:**

- FlexCore instance management (start/stop/configure)
- Service health monitoring and metrics
- Configuration management and distribution
- Multi-instance coordination

**Web Interface:**

- Management dashboard
- Service status visualization
- Configuration interface
- Monitoring and alerting

**API Integration:**

- RESTful management APIs
- gRPC communication with FlexCore
- Service discovery and registration
- Health check and monitoring endpoints

## Contributing

### Development Workflow

```bash
# Setup and build
cd cmd/flext-control-panel
go build -o flext-control-panel main.go
./flext-control-panel

# Development cycle
# 1. Implement new features
# 2. Test locally
# 3. Add tests
# 4. Build and validate
```

### Architecture Guidelines

- **Service Framework**: Use flextservice patterns for consistency
- **Go Standards**: Follow Go best practices and conventions
- **Error Handling**: Implement proper error handling
- **Testing**: Add comprehensive tests for new features

## License

MIT License - See [LICENSE](../../LICENSE) file for details.

## Links

- **[FLEXT Hub](../../docs/index.md)**: Complete ecosystem navigation
- **[FLEXT Service](../flext/)**: Main data integration service
- **[FlexCore](../../flexcore/)**: Go runtime service
- **[FLEXT Core](https://github.com/organization/flext/tree/main/flext-core/)**: Foundation library

---
