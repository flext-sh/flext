# Constants & Semantic Patterns

**Version**: 1.0.0 | **Status**: Active | **Python**: 3.13+

## Overview

Hierarchical, organized approach to managing constants across the FLEXT ecosystem. Ensures single source of truth, semantic organization, and extensible structure for all constant values.

## Core Principles

### Single Source of Truth

Each constant defined exactly once.

### Hierarchical Organization

Clear semantic grouping by purpose.

### Extensible Architecture

Projects extend base constants without duplication.

### Type Safety

All constants are strongly typed.

## Foundation Constants

```python
from typing import ClassVar, Final, Literal
from enum import StrEnum, IntEnum

class FlextConstants:
    """Foundation semantic constants for FLEXT ecosystem."""

    class Core:
        """Core system constants."""

        # Identity
        NAME: Final[str] = "FLEXT"
        VERSION: Final[str] = "1.0.0"
        ECOSYSTEM_SIZE: Final[int] = 33

        # Architecture
        ARCHITECTURE: Final[str] = "clean_architecture"
        PATTERN: Final[str] = "domain_driven_design"
        PRINCIPLES: Final[tuple[str, ...]] = ("SOLID", "DRY", "KISS", "YAGNI")

        # Environment
        PYTHON_VERSION: Final[str] = "3.13+"
        GO_VERSION: Final[str] = "1.24+"
        ENCODING: Final[str] = "utf-8"
        TIMEZONE: Final[str] = "UTC"

    class Errors:
        """Standard error codes and messages."""

        # Error Code Ranges
        BUSINESS_ERROR_RANGE: Final[tuple[int, int]] = (1000, 1999)
        TECHNICAL_ERROR_RANGE: Final[tuple[int, int]] = (2000, 2999)
        VALIDATION_ERROR_RANGE: Final[tuple[int, int]] = (3000, 3999)
        SECURITY_ERROR_RANGE: Final[tuple[int, int]] = (4000, 4999)

        # Common Error Codes
        GENERIC_ERROR: Final[str] = "FLEXT_0001"
        VALIDATION_ERROR: Final[str] = "FLEXT_3001"
        BUSINESS_RULE_VIOLATION: Final[str] = "FLEXT_1001"
        AUTHORIZATION_DENIED: Final[str] = "FLEXT_4001"
        AUTHENTICATION_FAILED: Final[str] = "FLEXT_4002"
        RESOURCE_NOT_FOUND: Final[str] = "FLEXT_1004"
        DUPLICATE_RESOURCE: Final[str] = "FLEXT_1005"
        CONNECTION_ERROR: Final[str] = "FLEXT_2001"
        TIMEOUT_ERROR: Final[str] = "FLEXT_2002"
        CONFIGURATION_ERROR: Final[str] = "FLEXT_2003"

        # Error Messages
        MESSAGES: ClassVar[dict[str, str]] = {
            GENERIC_ERROR: "An error occurred",
            VALIDATION_ERROR: "Validation failed",
            BUSINESS_RULE_VIOLATION: "Business rule violation",
            AUTHORIZATION_DENIED: "Authorization denied",
            AUTHENTICATION_FAILED: "Authentication failed",
            RESOURCE_NOT_FOUND: "Resource not found",
            DUPLICATE_RESOURCE: "Resource already exists",
            CONNECTION_ERROR: "Connection failed",
            TIMEOUT_ERROR: "Operation timed out",
            CONFIGURATION_ERROR: "Configuration error"
        }

    class Messages:
        """User-facing messages."""

        # Success Messages
        SUCCESS_GENERIC: Final[str] = "Operation completed successfully"
        SUCCESS_CREATED: Final[str] = "Resource created successfully"
        SUCCESS_UPDATED: Final[str] = "Resource updated successfully"
        SUCCESS_DELETED: Final[str] = "Resource deleted successfully"

        # Info Messages
        INFO_PROCESSING: Final[str] = "Processing request..."
        INFO_LOADING: Final[str] = "Loading data..."
        INFO_VALIDATING: Final[str] = "Validating input..."

        # Warning Messages
        WARN_DEPRECATED: Final[str] = "This feature is deprecated"
        WARN_SLOW_OPERATION: Final[str] = "This operation may take time"

        # Error Messages
        ERROR_INVALID_INPUT: Final[str] = "Invalid input provided"
        ERROR_UNAUTHORIZED: Final[str] = "You are not authorized to perform this action"
        ERROR_NOT_FOUND: Final[str] = "The requested resource was not found"
        ERROR_INTERNAL: Final[str] = "An internal error occurred. Please try again later"

    class Status:
        """Standard status values."""

        # Lifecycle Status
        ACTIVE: Final[str] = "active"
        INACTIVE: Final[str] = "inactive"
        PENDING: Final[str] = "pending"
        PROCESSING: Final[str] = "processing"
        COMPLETED: Final[str] = "completed"
        FAILED: Final[str] = "failed"
        CANCELLED: Final[str] = "cancelled"
        ARCHIVED: Final[str] = "archived"

        # Health Status
        HEALTHY: Final[str] = "healthy"
        DEGRADED: Final[str] = "degraded"
        UNHEALTHY: Final[str] = "unhealthy"

        # Connection Status
        CONNECTED: Final[str] = "connected"
        DISCONNECTED: Final[str] = "disconnected"
        CONNECTING: Final[str] = "connecting"

    class Patterns:
        """Validation regex patterns."""

        # Identifiers
        UUID_PATTERN: Final[str] = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        SLUG_PATTERN: Final[str] = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"

        # Authentication
        EMAIL_PATTERN: Final[str] = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        USERNAME_PATTERN: Final[str] = r"^[a-zA-Z0-9_-]{3,32}$"
        PASSWORD_PATTERN: Final[str] = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

        # Network
        IPV4_PATTERN: Final[str] = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        HOSTNAME_PATTERN: Final[str] = r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"

        # Versioning
        SEMVER_PATTERN: Final[str] = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"

    class Defaults:
        """Default operational values."""

        # Timeouts (seconds)
        TIMEOUT: Final[int] = 30
        CONNECTION_TIMEOUT: Final[int] = 10
        READ_TIMEOUT: Final[int] = 30
        WRITE_TIMEOUT: Final[int] = 30

        # Retries
        MAX_RETRIES: Final[int] = 3
        RETRY_DELAY: Final[float] = 1.0
        RETRY_BACKOFF: Final[float] = 2.0

        # Pagination
        PAGE_SIZE: Final[int] = 100
        MAX_PAGE_SIZE: Final[int] = 1000
        DEFAULT_PAGE: Final[int] = 1

        # Caching
        CACHE_TTL: Final[int] = 3600  # 1 hour
        CACHE_MAX_SIZE: Final[int] = 1000

        # Database
        DB_POOL_SIZE: Final[int] = 10
        DB_POOL_TIMEOUT: Final[int] = 30

        # API
        API_VERSION: Final[str] = "v1"
        API_PREFIX: Final[str] = "/api"
        API_RATE_LIMIT: Final[int] = 100

    class Limits:
        """System limits and constraints."""

        # String Limits
        MIN_STRING_LENGTH: Final[int] = 1
        MAX_STRING_LENGTH: Final[int] = 255
        MAX_TEXT_LENGTH: Final[int] = 65535

        # Numeric Limits
        MIN_PORT: Final[int] = 1
        MAX_PORT: Final[int] = 65535

        # Collection Limits
        MAX_ARRAY_SIZE: Final[int] = 10000
        MAX_BATCH_SIZE: Final[int] = 1000

        # File Limits
        MAX_FILE_SIZE: Final[int] = 104857600  # 100MB
        MAX_UPLOAD_SIZE: Final[int] = 52428800  # 50MB

        # Request Limits
        MAX_REQUEST_SIZE: Final[int] = 10485760  # 10MB
        MAX_URL_LENGTH: Final[int] = 2048

        # Resource Limits
        MAX_CONNECTIONS: Final[int] = 1000
        MAX_THREADS: Final[int] = 100

    class Performance:
        """Performance tuning constants."""

        # Thresholds
        SLOW_QUERY_THRESHOLD: Final[float] = 1.0  # seconds
        SLOW_REQUEST_THRESHOLD: Final[float] = 2.0  # seconds
        HIGH_MEMORY_THRESHOLD: Final[float] = 0.8  # 80%
        HIGH_CPU_THRESHOLD: Final[float] = 0.8  # 80%

        # Monitoring
        METRICS_INTERVAL: Final[int] = 60  # seconds
        HEALTH_CHECK_INTERVAL: Final[int] = 30  # seconds
```

## Enum-Based Constants

```python
class FlextStatus(StrEnum):
    """Enumeration for status values."""

    # Lifecycle
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

    @classmethod
    def is_terminal(cls, status: 'FlextStatus') -> bool:
        """Check if status is terminal (no further changes expected)."""
        return status in {cls.COMPLETED, cls.FAILED, cls.CANCELLED, cls.ARCHIVED}

    @classmethod
    def is_active(cls, status: 'FlextStatus') -> bool:
        """Check if status represents active processing."""
        return status in {cls.ACTIVE, cls.PROCESSING}

class FlextLogLevel(StrEnum):
    """Enumeration for log levels."""

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"
    AUDIT = "AUDIT"

    @classmethod
    def to_numeric(cls, level: 'FlextLogLevel') -> int:
        """Convert log level to numeric value for comparison."""
        mapping = {
            cls.TRACE: 5,
            cls.DEBUG: 10,
            cls.INFO: 20,
            cls.WARN: 30,
            cls.ERROR: 40,
            cls.FATAL: 50,
            cls.AUDIT: 100
        }
        return mapping.get(level, 0)

class FlextEnvironment(StrEnum):
    """Enumeration for deployment environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

    @classmethod
    def is_production(cls, env: 'FlextEnvironment') -> bool:
        """Check if environment is production."""
        return env == cls.PRODUCTION

    @classmethod
    def allows_debug(cls, env: 'FlextEnvironment') -> bool:
        """Check if environment allows debug features."""
        return env in {cls.DEVELOPMENT, cls.TESTING}
```

## Project Extensions

### Example: Oracle WMS Constants

```python
class FlextOracleWmsConstants(FlextConstants):
    """Oracle WMS specific constants extending base."""

    class Api:
        """Oracle WMS API constants."""

        # Versions
        VERSIONS: Final[tuple[str, ...]] = ("v10", "v9", "v8")
        DEFAULT_VERSION: Final[str] = "v10"

        # Endpoints
        BASE_PATH: Final[str] = "/wms/lgfapi"
        AUTH_ENDPOINT: Final[str] = "/auth/login"
        ENTITIES_ENDPOINT: Final[str] = "/entity/{entity_name}"

    class Entities:
        """WMS entity constants."""

        # Core Entities
        CORE_ENTITIES: Final[tuple[str, ...]] = (
            "company", "facility", "location", "item", "user"
        )

        # Inventory Entities
        INVENTORY_ENTITIES: Final[tuple[str, ...]] = (
            "inventory", "allocation", "lock", "adjustment", "cycle_count"
        )

        # All Entities
        ALL_ENTITIES: Final[tuple[str, ...]] = (
            *CORE_ENTITIES,
            *INVENTORY_ENTITIES
        )
```

## Usage Examples

### Basic Constant Usage

```python
from flext_core.constants import FlextConstants, FlextStatus

# Access core constants
version = FlextConstants.Core.VERSION
timeout = FlextConstants.Defaults.TIMEOUT

# Use error codes
error_code = FlextConstants.Errors.VALIDATION_ERROR
error_message = FlextConstants.Errors.MESSAGES[error_code]

# Use status enums
status = FlextStatus.PROCESSING
if FlextStatus.is_active(status):
    print(f"Operation is active: {status}")

# Pattern validation
import re
email = "user@example.com"
if re.match(FlextConstants.Patterns.EMAIL_PATTERN, email):
    print("Valid email address")
```

### Configuration with Constants

```python
from flext_core.config import FlextSettings
from flext_core.constants import FlextConstants

class DatabaseConfig(FlextSettings):
    """Database configuration using semantic constants."""

    host: str = "localhost"
    port: int = 5432
    pool_size: int = FlextConstants.Defaults.DB_POOL_SIZE
    pool_timeout: int = FlextConstants.Defaults.DB_POOL_TIMEOUT
    max_connections: int = FlextConstants.Limits.MAX_CONNECTIONS

    class Config:
        env_prefix = "DB_"
```

### Validation with Patterns

```python
from flext_core.constants import FlextConstants
from flext_core.result import FlextResult
import re

class Validator:
    """Validator using semantic patterns."""

    @staticmethod
    def validate_email(email: str) -> FlextResult[str]:
        """Validate email format."""
        if not re.match(FlextConstants.Patterns.EMAIL_PATTERN, email):
            return FlextResult[None].fail(
                "Invalid email format",
                error_code=FlextConstants.Errors.VALIDATION_ERROR
            )
        return FlextResult[None].ok(email)

    @staticmethod
    def validate_port(port: int) -> FlextResult[int]:
        """Validate port number."""
        if not FlextConstants.Limits.MIN_PORT <= port <= FlextConstants.Limits.MAX_PORT:
            return FlextResult[None].fail(
                f"Port must be between {FlextConstants.Limits.MIN_PORT} and {FlextConstants.Limits.MAX_PORT}",
                error_code=FlextConstants.Errors.VALIDATION_ERROR
            )
        return FlextResult[None].ok(port)
```

### Performance Monitoring

```python
from flext_core.constants import FlextConstants
from flext_core.observability import get_metrics, get_logger
import time

class PerformanceMonitor:
    """Monitor system performance using constants."""

    def __init__(self):
        self.metrics = get_metrics()
        self.logger = get_logger()

    def check_query_performance(self, query_time: float, query: str) -> None:
        """Check if query is slow."""
        threshold = FlextConstants.Performance.SLOW_QUERY_THRESHOLD

        if query_time > threshold:
            self.logger.warn(
                "Slow query detected",
                query_time=query_time,
                threshold=threshold,
                query=query
            )

            self.metrics.increment(
                "database.slow_queries",
                tags={"threshold": str(threshold)}
            )
```

## Quality Standards

- **Immutability**: Use `Final` type hint for all constants
- **Type Safety**: Provide explicit type annotations
- **Naming Convention**: UPPER_CASE with underscores
- **Organization**: Group by semantic meaning
- **Documentation**: Include docstrings for complex constants

## Related Patterns

- [Foundation](./foundation.md) - Uses constants
- [Configuration](./config-cli.md) - Default values from constants
- [Error](./error-observability.md) - Error codes and messages

---

**Constants & Semantic Patterns** - A hierarchical, single-source-of-truth approach to managing constants that ensures consistency across the entire FLEXT ecosystem.
