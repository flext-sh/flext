# FLEXT Logging System - Architecture and Implementation

## Executive Summary

The FLEXT logging system has been refactored following KISS, SOLID, and DRY principles, using hexagonal architecture with ports and adapters. The previous complex system was removed for being overly complex and reimplementing entire project architecture within the logging module.

## Related Documentation

- [Infrastructure Architecture](../architecture/infrastructure-architecture.md) - Overall infrastructure design
- [Ports Modernization](../architecture/ports-modernization.md) - Port implementation patterns
- [Development Standards](./development-standards.md) - Code quality standards

## Architecture Overview

### Hexagonal Architecture Implementation

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Core                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Business Logic                           │  │
│  │                     │                                 │  │
│  │                     ▼                                 │  │
│  │        flext.get_logger(__name__)                       │  │
│  │        flext.get_async_logger(__name__)                 │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Output Ports                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │    flext.ports.outbound.logging                         │  │
│  │                                                       │  │
│  │    LoggingPort (Protocol)                             │  │
│  │    AsyncLoggingPort (Protocol)                        │  │
│  │    LogLevel (IntEnum)                                 │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Adapters                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │    flext.adapters.outbound.logging                      │  │
│  │                                                       │  │
│  │    StandardLoggingImpl                                │  │
│  │    AsyncStandardLoggingImpl                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                External Dependencies                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Python Standard Logging                       │  │
│  │         (logging.getLogger)                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Output Ports (`flext.ports.outbound.logging`)

**LogLevel (IntEnum)**

```python
class LogLevel(IntEnum):
    TRACE = 5      # Custom level below DEBUG
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
```

**LoggingPort (Protocol)**

```python
@runtime_checkable
class LoggingPort(Protocol):
    def trace(self, message: str, *args: Any, **kwargs: Any) -> None: ...
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None: ...
    def info(self, message: str, *args: Any, **kwargs: Any) -> None: ...
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None: ...
    def error(self, message: str, *args: Any, **kwargs: Any) -> None: ...
    def critical(self, message: str, *args: Any, **kwargs: Any) -> None: ...
    def set_level(self, level: LogLevel) -> None: ...
```

**AsyncLoggingPort (Protocol)**

```python
@runtime_checkable
class AsyncLoggingPort(Protocol):
    async def trace(self, message: str, *args: Any, **kwargs: Any) -> None: ...
    async def debug(self, message: str, *args: Any, **kwargs: Any) -> None: ...
    async def info(self, message: str, *args: Any, **kwargs: Any) -> None: ...
    async def warning(self, message: str, *args: Any, **kwargs: Any) -> None: ...
    async def error(self, message: str, *args: Any, **kwargs: Any) -> None: ...
    async def critical(self, message: str, *args: Any, **kwargs: Any) -> None: ...
    def set_level(self, level: LogLevel) -> None: ...
```

### 2. Adapters (`flext.adapters.outbound.logging`)

**StandardLoggingImpl**

- Concrete implementation using Python's `logging.getLogger()`
- Automatically registers custom TRACE level
- Synchronous methods following PEP8 conventions

**AsyncStandardLoggingImpl**

- Asynchronous version of standard implementation
- Uses `asyncio.get_event_loop().run_in_executor()` for non-blocking operations
- Maintains full compatibility with synchronous interface

## Usage Examples

### Basic Usage

```python
import flext

# Get synchronous logger
logger = flext.get_logger(__name__)
logger.info("Application started")
logger.trace("Detailed debugging information")

# Get asynchronous logger
async_logger = flext.get_async_logger(__name__)
await async_logger.info("Async operation completed")
await async_logger.error("Async error occurred")
```

### Custom Log Levels

```python
import flext

# Logger with TRACE level (shows all messages)
logger = flext.get_logger(__name__, flext.LogLevel.TRACE)

# Logger with WARNING level (only WARNING, ERROR, CRITICAL)
prod_logger = flext.get_logger("production", flext.LogLevel.WARNING)
```

### All Available Levels

```python
logger.trace("Very detailed debug info")      # Custom level below DEBUG
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical system error")
```

## Design Principles Applied

### KISS Principles

- **Simple Interface**: Standard PEP8 logger methods (`debug`, `info`, etc.)
- **Single Responsibility**: Only handles logging, nothing else
- **No Over-Engineering**: Uses Python's standard logging library

### SOLID Principles

**Single Responsibility**

- Ports define contracts (interfaces)
- Adapters implement concrete functionality
- Clear separation of concerns

**Open/Closed**

- Easy to add new logging implementations
- Port interfaces are stable, adapters are extensible

**Liskov Substitution**

- Any implementation of LoggingPort works interchangeably
- Protocol-based design ensures compatibility

**Interface Segregation**

- Separate sync and async interfaces
- No forced dependencies on unused methods

**Dependency Inversion**

- Application depends on LoggingPort interface
- Concrete implementations depend on abstractions

### DRY Principles

- No code duplication between sync/async versions
- Reusable LogLevel enum
- Single source of truth for logging contracts

## Migration Strategy

### Before (Complex/Over-engineered)

```python
# Old complex system
from flext.utils.logging import FlextLogger, FlextLogConfig
from flext.core.logging import FlextLogContext, FlextLogLevel

config = FlextLogConfig(...)
logger = FlextLogger.create_with_config(config)
context = FlextLogContext(...)
logger.log_with_context(FlextLogLevel.INFO, "message", context)
```

### After (KISS/Simple)

```python
# New simple system
import flext

logger = flext.get_logger(__name__)
logger.info("message")
```

## Production Configuration

### Structured Logging

```python
import flext

logger = flext.get_logger(__name__)

# Basic structured logging
logger.info(
    "User action completed",
    extra={
        "user_id": user.id,
        "action": "user_creation",
        "duration_ms": duration,
        "success": True
    }
)
```

### Performance Considerations

```python
# Use async logging for high-throughput scenarios
async_logger = flext.get_async_logger("high_volume_service")

# Non-blocking logging operations
await async_logger.info("Processing batch", extra={"batch_size": 1000})
```

### Error Logging with Context

```python
try:
    await process_user_data(user_data)
except Exception as e:
    logger.error(
        "User processing failed",
        extra={
            "user_id": user_data.get("id"),
            "error_type": type(e).__name__,
            "error_message": str(e)
        },
        exc_info=True
    )
```

## Testing Strategy

### Unit Testing

```python
def test_logging_levels():
    """Test all logging levels work correctly."""
    logger = flext.get_logger("test")

    # Test all levels
    logger.trace("trace message")
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
```

### Async Testing

```python
async def test_async_logging():
    """Test async logging functionality."""
    logger = flext.get_async_logger("test_async")

    await logger.info("async message")
    # Verify non-blocking behavior
```

### Integration Testing

```python
def test_logging_integration():
    """Test logging integration with application."""
    # Test that logging works in real application context
    pass
```

## File Structure

```
flext/
├── ports/outbound/logging.py          # Port interfaces
├── adapters/outbound/logging.py       # Concrete implementations
├── __init__.py                        # Public API
└── tests/
    └── test_logging_system.py         # Comprehensive tests
```

## Implementation Details

### Key Features

1. **TRACE Level**: Custom level (5) below DEBUG for very detailed debugging
2. **IntEnum Compatibility**: LogLevel uses IntEnum for Python logging compatibility
3. **Async Design**: Non-blocking async logging using executor threads
4. **Protocol-Based**: Uses `@runtime_checkable` protocols for duck typing
5. **Standard Library**: Built on Python's `logging` module for reliability

### Performance Optimizations

- Lazy logger creation
- Efficient level checking
- Non-blocking async operations
- Minimal overhead for disabled log levels

## Monitoring and Observability

### Log Aggregation

```python
# Configure for centralized logging
logger = flext.get_logger("service_name")
logger.info(
    "Service event",
    extra={
        "service": "user_service",
        "version": "1.0.0",
        "environment": "production",
        "trace_id": trace_id
    }
)
```

### Health Monitoring

```python
# Health check logging
async def health_check():
    logger = flext.get_async_logger("health")
    await logger.info("Health check passed", extra={"timestamp": datetime.utcnow()})
```

## Best Practices

### Do's ✅

- Use structured logging with `extra` parameter
- Include relevant context in log messages
- Use appropriate log levels
- Use async logging for high-throughput services
- Include error context and stack traces

### Don'ts ❌

- Don't log sensitive information (passwords, tokens)
- Don't use logging for application logic
- Don't log at inappropriate levels
- Don't create custom logging frameworks
- Don't reinvent Python's logging wheel

## Removed Components

The following over-engineered components were removed:

- `flext.utils.logging` (entire module)
- `flext.core.logging_simple`
- `flext.infra.logging` (old implementations)
- Complex domain-driven logging architecture
- Custom logging frameworks and abstractions

## Future Enhancements

### Planned Improvements

- Integration with distributed tracing
- Enhanced error correlation
- Performance metrics collection
- Log sampling for high-volume services

### Integration Points

- Prometheus metrics integration
- OpenTelemetry tracing
- Centralized log aggregation
- Error tracking services

## Conclusion

The new logging system successfully implements hexagonal architecture with KISS principles, providing a simple, powerful, and extensible logging solution that follows established Python conventions while maintaining clean architectural boundaries.

**Key Benefits**:

- ✅ **Simplified API**: Easy to use, follows Python standards
- ✅ **Architectural Compliance**: Proper hexagonal architecture
- ✅ **Performance**: Async support for high-throughput scenarios
- ✅ **Extensibility**: Easy to add new implementations
- ✅ **Testability**: Clean interfaces for testing

## See Also

- [Error Handling Strategy](./error-handling.md) - Error management patterns
- [Performance Monitoring](../guides/performance-monitoring.md) - Application monitoring
- [Testing Strategy](./testing-strategy.md) - Testing approaches
- [Production Deployment](../guides/deployment.md) - Production configuration

---

**Last Updated**: January 2025
**Status**: Production Ready
**Architecture**: Hexagonal (Ports & Adapters)
**Principles**: KISS, SOLID, DRY
