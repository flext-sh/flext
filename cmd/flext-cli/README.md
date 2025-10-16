# flext-cli

**Type**: Go Service | **Status**: Active Development | **Dependencies**: Go 1.24+

Command-line interface service for FLEXT data integration platform.

> ⚠️ Development Status: Basic CLI bootstrap working; shared_kernel package conflicts; pipeline commands not implemented yet.

## Quick Start

```bash
# Build CLI
cd ..cmd/flext-cli
go build -o flext-cli main.go

# Test basic functionality
./flext-cli --help

# Development setup
make build
```

## Current Reality

**What Actually Works:**

- Basic CLI application bootstrap with context support
- Simple logging with INFO/ERROR levels
- Command-line argument parsing with flag package
- Graceful shutdown handling

**What Needs Work:**

- shared_kernel package conflicts (TODOs in main.go)
- Pipeline management commands not implemented
- Plugin operations not available
- System REDACTED_LDAP_BIND_PASSWORDistration features missing
- Interactive mode not implemented

## Architecture Role in FLEXT Ecosystem

### **Go Service Component**

FLEXT CLI provides command-line access to ecosystem services:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM (32 Projects)                 │
├─────────────────────────────────────────────────────────────────┤
│ Services: FlexCore(Go) | FLEXT Service(Go/Python) | [FLEXT-CLI] │
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

1. **CLI Interface**: Command-line access to FLEXT platform
2. **Service Coordination**: Interface with Go and Python services
3. **Development Tools**: Developer utilities and REDACTED_LDAP_BIND_PASSWORDistration

## Key Features

### **Current Implementation**

```go
// main.go - Current working implementation
func main() {
    // Parse command line flags
    flag.Parse()

    // Basic logging (temporary implementation)
    appConfig.Logger = &basicLogger{}

    // Create CLI with enhanced error handling
    cliApp := cli.NewCLI()

    // Run with graceful shutdown
    if err := cliApp.Run(ctx, os.Args); err != nil {
        // Error handling
    }
}
```

### **Package Dependencies**

- `github.com/flext-sh/flext/pkg/interfaces/cli`
- Basic flag parsing and context support
- Commented out logging and shared_kernel (conflicts)

## Installation & Usage

### Build from Source

```bash
# Clone and build
cd ..cmd/flext-cli
go build -o flext-cli main.go

# Run basic CLI
./flext-cli --help
```

### Current Usage

```bash
# Basic execution (what actually works)
./flext-cli

# With arguments (parsed but limited functionality)
./flext-cli --verbose
```

## Development Commands

### Build Operations

```bash
# Build CLI binary
go build -o flext-cli main.go

# Build with Makefile
make build

# Cross-platform builds (if configured)
make build-cli
```

### Testing

```bash
# Run Go tests
go test ./...

# Test with coverage
go test -cover ./...
```

## Configuration

### Current Configuration

```go
// Basic app configuration (from main.go)
var appConfig struct {
    Logger interface {
        Info(msg string, fields ...interface{})
        Error(msg string, fields ...interface{})
    }
}
```

### Environment Variables

```bash
# Basic environment support
export FLEXT_LOG_LEVEL="debug"  # May be supported by CLI framework
```

## Quality Standards

### **Current Code Quality**

- **Go 1.24+**: Modern Go with generics support
- **Context Support**: Proper context handling for cancellation
- **Error Handling**: Basic error handling with os.Exit(1)
- **Logging**: Temporary basic logging implementation

## Integration with FLEXT Ecosystem

### **Service Integration**

```bash
# CLI interfaces with ecosystem services
# (Implementation pending - currently basic bootstrap)
```

### **Package Structure**

- **pkg/interfaces/cli**: CLI framework interfaces
- **pkg/logging**: Logging package (conflicts, commented out)
- **pkg/utils/shared_kernel**: Shared utilities (conflicts)

## Current Status

**Version**: 0.9.0 (Development - Basic Bootstrap)

**Completed**:

- ✅ Go CLI application bootstrap
- ✅ Basic command-line argument parsing
- ✅ Context support for graceful shutdown
- ✅ Simple logging implementation

**Critical Issues**:

- ❌ shared_kernel package conflicts (TODOs in code)
- ❌ Pipeline commands not implemented
- ❌ Plugin management missing
- ❌ System REDACTED_LDAP_BIND_PASSWORDistration features absent

**Planned**:

- 📋 Resolve shared_kernel package conflicts
- 📋 Implement pipeline management commands
- 📋 Add plugin operations
- 📋 Build system REDACTED_LDAP_BIND_PASSWORDistration features

## Contributing

### Development Standards

- **Go Best Practices**: Follow Go conventions
- **Error Handling**: Use proper Go error handling patterns
- **Testing**: Add tests for new functionality
- **CLI Framework**: Use established CLI patterns

### Development Workflow

```bash
# Setup and build
cd cmd/flext-cli
go build -o flext-cli main.go
./flext-cli
```

## License

MIT License - See [LICENSE](../../LICENSE) file for details.

## Links

- **[FlexCore](../../flexcore/)**: Go runtime service
- **[FLEXT Service](../flext/)**: Main Go/Python service
- **[FLEXT Core](../../flext-core/)**: Foundation library

---
