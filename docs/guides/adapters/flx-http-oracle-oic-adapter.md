# FLX HTTP Oracle OIC

Enhanced Oracle Integration Cloud HTTP client using FLX infrastructure with comprehensive API capabilities.

## Features

- **FLX Framework Integration**: Uses FLX infrastructure patterns for dependency injection and service architecture
- **JWT Authentication**: Automatic token management using FLX JWT service patterns
- **HTTP Client**: Robust HTTP client with retry logic, rate limiting, and error handling
- **Configuration Management**: Environment-based configuration with validation
- **CLI Interface**: Comprehensive command-line interface for all OIC operations
- **Type Safety**: Python 3.13+ with full type annotations and Pydantic models
- **Factory Pattern**: Proper dependency injection and service creation
- **Monitoring**: Real-time monitoring and health checks

## Installation

```bash
pip install -e .
```

## Configuration

Set the following environment variables or create a `.env` file:

```env
# IDCS Configuration
OIC_IDCS_URL=your-idcs-domain.oracle.com
OIC_IDCS_CLIENT_ID=your-client-id
OIC_IDCS_CLIENT_SECRET=your-client-secret
OIC_IDCS_CLIENT_AUD=https://your-idcs-aud.oracle.com

# OIC Instance Configuration
OIC_INSTANCE_ID=your-instance-id
OIC_REGION=us-ashburn-1
OIC_ENVIRONMENT=dev

# Optional Settings
OIC_TIMEOUT=60.0
OIC_MAX_RETRIES=3
OIC_API_VERSION=v1
OIC_VERIFY_SSL=true
```

## Usage

### Python API

```python
import asyncio
from flext_http_oracle_oic import OicConfig, flext_create_oic_context

async def main():
    # Load configuration
    config = OicConfig.from_env()

    # Use factory pattern with context manager
    async with flext_create_oic_context(config) as factory:
        service = factory.create_oic_service()

        # Health check
        is_healthy = await service.health_check()

        # List integrations
        integrations = await service.list_integrations()
        for integration in integrations:
            print(f"{integration.name}: {integration.status}")

        # List connections
        connections = await service.list_connections()
        for connection in connections:
            print(f"{connection.name}: {connection.type}")

asyncio.run(main())
```

### CLI Usage

```bash
# Configuration management
python -m flext_http_oracle_oic.cli config validate --test-connection
python -m flext_http_oracle_oic.cli config view

# Integration management
python -m flext_http_oracle_oic.cli integrations list --format table
python -m flext_http_oracle_oic.cli integrations get INTEGRATION_ID

# Connection management
python -m flext_http_oracle_oic.cli connections list --type REST
python -m flext_http_oracle_oic.cli connections test CONNECTION_ID

# Monitoring
python -m flext_http_oracle_oic.cli monitoring overview --hours 24
python -m flext_http_oracle_oic.cli monitoring health

# JWT management
python -m flext_http_oracle_oic.cli jwt status
python -m flext_http_oracle_oic.cli jwt token --show-token
```

## Architecture

This package follows FLX framework patterns:

- **Factory Pattern**: `OicFactory` manages dependency injection
- **Service Layer**: `OracleOicService` implements business logic
- **Infrastructure**: Uses FLX HTTP client and JWT service
- **Configuration**: Environment-based with validation
- **CLI**: Command-based interface with proper separation of concerns

## Components

### Core Services

- **OracleOicService**: Main service implementing FlxHttpService interface
- **FlxJwtService**: JWT authentication using FLX patterns
- **FlxHttpClient**: HTTP client with retry and rate limiting
- **OicFactory**: Dependency injection factory

### Models

- **OicConfig**: Configuration with validation
- **OicIntegration**: Integration entity model
- **OicConnection**: Connection entity model
- **OicMonitoringData**: Monitoring data model

### CLI Commands

- **config**: Configuration validation and testing
- **integrations**: Integration management
- **connections**: Connection management
- **monitoring**: Monitoring and health checks
- **jwt**: JWT token management

## Development

### Requirements

- Python 3.13+
- FLX framework
- Pydantic for data validation
- Click for CLI
- AsyncIO for async operations

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/flext_http_oracle_oic

# Type checking
mypy src/flext_http_oracle_oic/
```

### Building

```bash
# Install in development mode
pip install -e .

# Run linting
ruff check src/

# Format code
ruff format src/
```

## Examples

See the `examples/` directory for comprehensive usage examples:

- `basic_usage.py`: Basic service usage
- `cli_examples.sh`: CLI command examples
- `factory_patterns.py`: Factory pattern usage

## Error Handling

The package provides comprehensive error handling:

- **OicException**: Base exception for all OIC errors
- **OicConfigError**: Configuration-related errors
- **OicAuthError**: Authentication failures
- **OicApiError**: API communication errors
- **OicConnectionError**: Connection issues
- **OicTimeoutError**: Timeout handling
- **OicRateLimitError**: Rate limiting errors

## Logging

Uses structured logging with FLX patterns:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Enable debug mode
config = OicConfig.from_env()
factory = OicFactory(config, debug_mode=True)
```

## License

This flext_project follows the enterprise licensing patterns of the FLX framework.

## Contributing

1. Follow SOLID principles
2. Use strong typing (Python 3.13+)
3. Write comprehensive tests
4. Follow FLX framework patterns
5. Update documentation
