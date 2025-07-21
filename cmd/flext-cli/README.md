# FLEXT CLI

Command-line interface for FLEXT data integration platform.

## Overview

The FLEXT CLI provides command-line access to all FLEXT platform functionality including pipeline management, plugin operations, and system administration.

## Features

- **Pipeline Management**: Create, configure, and execute data pipelines
- **Plugin Operations**: Install, configure, and manage data connectors
- **System Administration**: Monitor system health and configuration
- **Interactive Mode**: Interactive command-line interface for exploration
- **Configuration Management**: Manage environment and connection settings

## Installation

### From Binary

```bash
# Download latest release
curl -LO https://github.com/flext-sh/flext/releases/latest/download/flext-cli
chmod +x flext-cli
sudo mv flext-cli /usr/local/bin/
```

### From Source

```bash
cd /home/marlonsc/flext/cmd/flext-cli
go build -o flext-cli main.go
```

## Usage

### Basic Commands

```bash
# Show help
flext-cli --help

# Enable verbose logging
flext-cli --verbose

# Use custom configuration
flext-cli --config /path/to/config.yaml
```

### Pipeline Operations

```bash
# List all pipelines
flext-cli pipeline list

# Create new pipeline
flext-cli pipeline create --name "data-sync" --extractor tap-postgres --loader target-snowflake

# Run pipeline
flext-cli pipeline run --id pipeline-uuid

# Show pipeline status
flext-cli pipeline status --id pipeline-uuid
```

### Plugin Management

```bash
# List available plugins
flext-cli plugin list

# Install plugin
flext-cli plugin install tap-postgres

# Configure plugin
flext-cli plugin configure tap-postgres --config config.json
```

### System Operations

```bash
# Check system health
flext-cli system health

# Show system statistics
flext-cli system stats

# View logs
flext-cli system logs --follow
```

## Configuration

The CLI supports configuration via:

1. **Configuration File**: `--config` flag or `FLEXT_CONFIG_PATH` environment variable
2. **Environment Variables**: All settings can be overridden with `FLEXT_` prefixed variables
3. **Command Line Flags**: Runtime overrides for common settings

### Configuration File Example

```yaml
# flext-config.yaml
server:
  host: localhost
  port: 8080
  timeout: 30s

logging:
  level: info
  format: json

database:
  url: postgresql://localhost/flext
  pool_size: 20
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLEXT_CONFIG_PATH` | Path to configuration file | - |
| `FLEXT_SERVER_HOST` | FLEXT server hostname | localhost |
| `FLEXT_SERVER_PORT` | FLEXT server port | 8080 |
| `FLEXT_LOG_LEVEL` | Logging level (debug, info, warn, error) | info |
| `FLEXT_DATABASE_URL` | Database connection URL | - |

## Architecture

The CLI is built using:

- **Go 1.24+**: Modern Go with generics and enhanced error handling
- **Clean Architecture**: Separation of concerns with clear boundaries
- **Cobra CLI Framework**: Powerful command-line interface framework
- **Structured Logging**: JSON-formatted logs with contextual information
- **Graceful Shutdown**: Proper cleanup on interruption

## Development

### Building

```bash
# Build for current platform
go build -o flext-cli main.go

# Build for multiple platforms
make build-cli
```

### Testing

```bash
# Run all tests
go test ./...

# Run with coverage
go test -cover ./...
```

### Contributing

1. Follow Go conventions and best practices
2. Add tests for new functionality
3. Update documentation for new commands
4. Ensure all quality gates pass

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure FLEXT server is running and accessible
2. **Authentication Failed**: Check credentials and server configuration
3. **Command Not Found**: Verify CLI is installed and in PATH

### Debug Mode

```bash
# Enable debug logging
flext-cli --verbose command

# Show detailed error information
FLEXT_LOG_LEVEL=debug flext-cli command
```

## License

MIT License - see [LICENSE](../../LICENSE) for details.

## Related

- [FLEXT Server](../flext-server/) - Main API server
- [FLEXT Demo](../flext-demo/) - Demo application
- [FLEXT Core](../../flext-core/) - Core framework library