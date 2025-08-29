# Error & Observability Patterns

**Version**: 0.9.0 | **Status**: Active | **Python**: 3.13+ | **Go**: 1.24+

## Overview

Comprehensive error handling and observability architecture for the FLEXT ecosystem. Ensures consistent error classification, rich context preservation, and seamless monitoring integration.

## Core Principles

### Semantic Error Classification

Clear distinction between error types:

```
FlextExceptions.Error                  # Base for all errors
├── FlextBusinessError      # Business logic violations
│   ├── ValidationError     # Data validation failures
│   └── AuthorizationError  # Permission denied
└── FlextTechnicalError     # Infrastructure issues
    ├── ConnectionError     # Network/DB issues
    └── ConfigurationError  # Config problems
```

### Rich Context Preservation

Every error carries comprehensive context.

### Protocol-Based Observability

Separation of interface and implementation:

- **flext-core**: Defines observability protocols
- **flext-observability**: Provides production implementations
- **Projects**: Use protocols, get implementation via DI

### Cross-Language Compatibility

Seamless error propagation between Python and Go.

## Error Hierarchy

```python
from typing import Optional, Dict, ClassVar

from datetime import datetime
from enum import StrEnum
import uuid

class ErrorCode(StrEnum):
    """Standard error codes across FLEXT ecosystem."""
    # Business Errors (1xxx)
    VALIDATION_ERROR = "FLEXT_1001"
    BUSINESS_RULE_VIOLATION = "FLEXT_1002"
    AUTHORIZATION_DENIED = "FLEXT_1003"
    RESOURCE_NOT_FOUND = "FLEXT_1004"
    DUPLICATE_RESOURCE = "FLEXT_1005"

    # Technical Errors (2xxx)
    CONNECTION_ERROR = "FLEXT_2001"
    TIMEOUT_ERROR = "FLEXT_2002"
    CONFIGURATION_ERROR = "FLEXT_2003"
    SERIALIZATION_ERROR = "FLEXT_2004"
    EXTERNAL_SERVICE_ERROR = "FLEXT_2005"

class FlextExceptions.Error(Exception):
    """Universal base exception with full observability support."""

    __error_family__: ClassVar[str] = "FLEXT"
    __error_type__: ClassVar[str] = "GENERIC"

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, object]] = None,
        cause: Optional[Exception] = None,
        recoverable: Optional[bool] = None,
        alert_level: str = "error"
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self._generate_error_code()
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.context = context or {}
        self.cause = cause
        self.recoverable = recoverable if recoverable is not None else self._is_recoverable()
        self.alert_level = alert_level
        self.timestamp = datetime.utcnow()

        # Automatic observability integration
        self._log_error()
        self._emit_metrics()
        self._create_trace_span()

    def to_result(self) -> 'FlextResult[None]':
        """Convert exception to FlextResult for consistent handling."""
        from flext_core.result import FlextResult
        return FlextResult[None].fail(
            self.message,
            error_code=self.error_code,
            correlation_id=self.correlation_id,
            **self.context
        )

    def to_dict(self) -> Dict[str, object]:
        """Serialize exception for cross-service communication."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "correlation_id": self.correlation_id,
            "context": self.context,
            "recoverable": self.recoverable,
            "alert_level": self.alert_level,
            "timestamp": self.timestamp.isoformat()
        }

class FlextBusinessError(FlextExceptions.Error):
    """Business logic violations requiring user action."""
    __error_type__ = "BUSINESS"

    def _is_recoverable(self) -> bool:
        return False  # Business errors typically require user intervention

class FlextTechnicalError(FlextExceptions.Error):
    """Technical/infrastructure errors potentially recoverable."""
    __error_type__ = "TECHNICAL"

    def _is_recoverable(self) -> bool:
        return True  # Technical errors often recoverable with retry
```

## Domain-Specific Errors

### Data Domain Errors

```python
class FlextData:
    """Namespace for data-related errors."""

    class ConnectionError(FlextTechnicalError):
        """Database/service connection failures."""
        __error_type__ = "DATA_CONNECTION"

        def __init__(self, message: str, *, connection_type: str, host: Optional[str] = None, **kwargs):
            super().__init__(
                message,
                context={"connection_type": connection_type, "host": host},
                recoverable=True,
                alert_level="warning",
                **kwargs
            )

    class ValidationError(FlextBusinessError):
        """Data validation failures."""
        __error_type__ = "DATA_VALIDATION"

        def __init__(self, message: str, *, field_name: Optional[str] = None, field_value: object = None, **kwargs):
            super().__init__(
                message,
                context={"field_name": field_name, "field_value": str(field_value) if field_value else None},
                recoverable=False,
                alert_level="error",
                **kwargs
            )
```

### Authentication Domain Errors

```python
class FlextAuth:
    """Namespace for authentication errors."""

    class TokenExpiredError(FlextTechnicalError):
        """JWT or session token expiration."""
        __error_type__ = "AUTH_TOKEN_EXPIRED"

        def __init__(self, message: str = "Authentication token expired", *, token_type: str = "JWT", **kwargs):
            super().__init__(
                message,
                context={"token_type": token_type},
                recoverable=True,
                alert_level="info",
                **kwargs
            )

    class UnauthorizedError(FlextBusinessError):
        """Access denied for resource."""
        __error_type__ = "AUTH_UNAUTHORIZED"

        def __init__(self, message: str, *, resource: Optional[str] = None, action: Optional[str] = None, **kwargs):
            super().__init__(
                message,
                context={"resource": resource, "action": action},
                recoverable=False,
                alert_level="warning",
                **kwargs
            )
```

## Observability Protocols

```python
from typing import Protocol, runtime_checkable, Dict, Optional, ContextManager


@runtime_checkable
class FlextLoggerProtocol(Protocol):
    """Protocol for structured logging."""

    def trace(self, message: str, **context: object) -> None: ...
    def debug(self, message: str, **context: object) -> None: ...
    def info(self, message: str, **context: object) -> None: ...
    def warn(self, message: str, **context: object) -> None: ...
    def error(self, message: str, *, error_code: Optional[str] = None, **context: object) -> None: ...
    def audit(self, message: str, *, user_id: Optional[str] = None, action: Optional[str] = None, **context: object) -> None: ...

@runtime_checkable
class FlextTracerProtocol(Protocol):
    """Protocol for distributed tracing."""

    def start_span(self, operation_name: str, *, kind: str = "INTERNAL", attributes: Optional[Dict[str, object]] = None) -> ContextManager: ...
    def get_current_span(self) -> Optional[object]: ...
    def inject_context(self, carrier: Dict[str, object]) -> None: ...
    def extract_context(self, carrier: Dict[str, object]) -> Optional[object]: ...

@runtime_checkable
class FlextMetricsProtocol(Protocol):
    """Protocol for metrics collection."""

    def increment(self, metric_name: str, value: float = 1, tags: Optional[Dict[str, str]] = None) -> None: ...
    def gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None: ...
    def histogram(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None: ...
    def timer(self, metric_name: str, tags: Optional[Dict[str, str]] = None) -> ContextManager: ...

@runtime_checkable
class FlextObservabilityProtocol(Protocol):
    """Complete observability interface."""

    @property
    def log(self) -> FlextLoggerProtocol: ...

    @property
    def trace(self) -> FlextTracerProtocol: ...

    @property
    def metrics(self) -> FlextMetricsProtocol: ...
```

## Minimal Implementation (Development)

```python
import sys
from contextlib import contextmanager
from datetime import datetime

class FlextConsole:
    """Simple console logger for development."""

    def _format_message(self, level: str, message: str, **context: object) -> str:
        timestamp = datetime.utcnow().isoformat()
        context_str = " ".join(f"{k}={v}" for k, v in context.items())
        return f"[{timestamp}] {level}: {message} {context_str}".strip()

    def trace(self, message: str, **context: object) -> None:
        print(self._format_message("TRACE", message, **context))

    def debug(self, message: str, **context: object) -> None:
        print(self._format_message("DEBUG", message, **context))

    def info(self, message: str, **context: object) -> None:
        print(self._format_message("INFO", message, **context))

    def warn(self, message: str, **context: object) -> None:
        print(self._format_message("WARN", message, **context), file=sys.stderr)

    def error(self, message: str, **context: object) -> None:
        print(self._format_message("ERROR", message, **context), file=sys.stderr)

    def audit(self, message: str, **context: object) -> None:
        print(self._format_message("AUDIT", message, **context))

class FlextObservability:
    """Minimal observability for development."""

    def __init__(self):
        self._log = FlextConsole()
        # NoOp implementations for trace and metrics...

    @property
    def log(self) -> FlextLoggerProtocol:
        return self._log

# Factory functions
_observability_instance: Optional[FlextObservabilityProtocol] = None

def get_observability() -> FlextObservabilityProtocol:
    """Get observability instance (singleton)."""
    global _observability_instance
    if _observability_instance is None:
        _observability_instance = FlextObservability()
    return _observability_instance
```

## Usage Examples

### Basic Error Handling

```python
from flext_core.errors import FlextData, FlextAuth, FlextExceptions.Error
from flext_core.result import FlextResult

def connect_to_database(config: Dict[str, object]) -> FlextResult[Connection]:
    """Connect to database with proper error handling."""
    try:
        # Validate configuration
        if 'host' not in config:
            raise FlextData.ValidationError(
                "Missing required configuration",
                field_name="host"
            )

        # Attempt connection
        connection = create_connection(config)

        if not connection.is_alive():
            raise FlextData.ConnectionError(
                "Failed to establish database connection",
                connection_type="postgresql",
                host=config['host']
            )

        return FlextResult[None].ok(connection)

    except FlextExceptions.Error as e:
        # FlextExceptions.Errors already logged and tracked
        return e.to_result()
    except Exception as e:
        # Wrap unexpected errors
        error = FlextTechnicalError(
            f"Unexpected error during connection: {str(e)}",
            cause=e
        )
        return error.to_result()
```

### Observability Integration

```python
from flext_core.observability import FlextLogger, get_metrics, get_tracer

class UserService:
    """Service with integrated observability."""

    def __init__(self):
        self.logger = FlextLogger()
        self.metrics = get_metrics()
        self.tracer = get_tracer()

    async def create_user(self, user_data: Dict[str, object]) -> FlextResult[User]:
        """Create user with full observability."""

        with self.tracer.start_span("user.create") as span:
            span.set_attribute("user.email", user_data.get("email"))

            self.logger.info("Creating new user", email=user_data.get("email"))

            with self.metrics.timer("user.creation.duration"):
                try:
                    # Validate user data
                    if not self._validate_email(user_data.get("email")):
                        raise FlextData.ValidationError(
                            "Invalid email format",
                            field_name="email",
                            field_value=user_data.get("email")
                        )

                    # Create user
                    user = await self._create_user_record(user_data)

                    self.logger.info("User created successfully", user_id=user.id)
                    self.metrics.increment("users.created")

                    return FlextResult[None].ok(user)

                except FlextExceptions.Error as e:
                    span.set_attribute("error", True)
                    self.metrics.increment("users.creation.failed", tags={"error_type": e.__class__.__name__})
                    return e.to_result()
```

### Error Recovery Patterns

```python
class RetryStrategy:
    """Retry strategy for recoverable errors."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def execute_with_retry(
        self,
        operation: Callable[[], FlextResult[T]],
        recoverable_errors: tuple = (FlextTechnicalError,)
    ) -> FlextResult[T]:
        """Execute operation with exponential backoff retry."""

        for attempt in range(self.max_retries + 1):
            try:
                result = await operation()

                if result.is_success:
                    return result

                # Check if error is recoverable
                if hasattr(result, 'error') and isinstance(result.error, recoverable_errors):
                    if result.error.recoverable and attempt < self.max_retries:
                        delay = self.base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue

                return result

            except recoverable_errors as e:
                if e.recoverable and attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    raise

        return FlextResult[None].fail("Max retries exceeded")
```

## Quality Standards

- **Semantic Classification**: Use appropriate error types
- **Rich Context**: Include all relevant debugging information
- **Correlation IDs**: Always propagate correlation IDs
- **Recoverability**: Mark errors as recoverable when appropriate
- **Observability**: Ensure all errors are logged and tracked

## Related Patterns

- [Foundation](./foundation.md) - FlextResult integration
- [Type System](./types.md) - Error type definitions
- [Configuration](./config-cli.md) - Configuration errors

---

**Error & Observability Patterns** - Comprehensive error handling and observability architecture that ensures consistency across the FLEXT ecosystem.
