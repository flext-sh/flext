"""Type definitions and enums for the enterprise plugin system."""

from __future__ import annotations

import traceback
from datetime import UTC, datetime
from enum import Enum
from typing import Any, TypedDict

from pydantic import BaseModel, Field


class PluginType(Enum):
    """Plugin type classification for enterprise plugin system.

    Defines the functional categories of plugins available in the system,
    enabling proper routing, validation, and lifecycle management.
    """

    # Data processing plugins
    EXTRACTOR = "extractor"
    LOADER = "loader"
    TRANSFORMER = "transformer"
    VALIDATOR = "validator"

    # Pipeline and orchestration plugins
    ORCHESTRATOR = "orchestrator"
    SCHEDULER = "scheduler"
    TRIGGER = "trigger"

    # Monitoring and observability plugins
    MONITOR = "monitor"
    ALERTER = "alerter"
    LOGGER = "logger"
    TRACER = "tracer"

    # Integration and connectivity plugins
    CONNECTOR = "connector"
    ADAPTER = "adapter"
    BRIDGE = "bridge"

    # Security and compliance plugins
    AUTHENTICATOR = "authenticator"
    AUTHORIZER = "authorizer"
    ENCRYPTOR = "encryptor"
    AUDITOR = "auditor"

    # Utility and extension plugins
    UTILITY = "utility"
    EXTENSION = "extension"
    FILTER = "filter"
    PROCESSOR = "processor"


class PluginCapability(Enum):
    """Plugin capability enumeration for functional classification."""

    # Data processing capabilities
    DATA_EXTRACTION = "data_extraction"
    DATA_LOADING = "data_loading"
    DATA_TRANSFORMATION = "data_transformation"
    DATA_VALIDATION = "data_validation"

    # Schema and metadata capabilities
    SCHEMA_INFERENCE = "schema_inference"
    SCHEMA_VALIDATION = "schema_validation"
    METADATA_EXTRACTION = "metadata_extraction"

    # Synchronization capabilities
    INCREMENTAL_SYNC = "incremental_sync"
    FULL_SYNC = "full_sync"
    REAL_TIME_SYNC = "real_time_sync"

    # Pipeline capabilities
    PIPELINE_ORCHESTRATION = "pipeline_orchestration"
    TASK_SCHEDULING = "task_scheduling"
    DEPENDENCY_MANAGEMENT = "dependency_management"

    # Monitoring capabilities
    HEALTH_MONITORING = "health_monitoring"
    PERFORMANCE_MONITORING = "performance_monitoring"
    ERROR_REPORTING = "error_reporting"


class PluginLifecycle(Enum):
    """Plugin lifecycle states for state management and monitoring."""

    UNREGISTERED = "unregistered"
    REGISTERED = "registered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ERROR = "error"
    UNLOADING = "unloading"
    UNLOADED = "unloaded"


class PluginStatus(Enum):
    r"""PluginStatus - Framework Component.

    Implementa componente central do framework com funcionalidades específicas.
    Segue padrões arquiteturais estabelecidos.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    Sem métodos públicos.

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = PluginStatus()\n    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """Plugin operational status for health monitoring."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class PluginExecutionResult(BaseModel):
    """Result container for plugin execution with comprehensive metadata."""

    model_config = {"frozen": True}

    # Execution outcome
    success: bool = Field(description="Whether the plugin execution succeeded")
    result: Any = Field(default=None, description="The plugin execution result data")
    error: str | None = Field(
        default=None,
        description="Error message if execution failed",
    )

    # Execution metadata
    plugin_id: str = Field(description="Unique identifier of the executed plugin")
    execution_id: str = Field(description="Unique identifier for this execution")
    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    end_time: datetime | None = Field(
        default=None,
        description="Execution completion time",
    )
    duration_ms: int | None = Field(
        default=None,
        description="Execution duration in milliseconds",
    )

    # Context and tracing
    execution_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution context metadata",
    )
    trace_id: str | None = Field(default=None, description="Distributed tracing ID")
    span_id: str | None = Field(default=None, description="Distributed tracing span ID")

    # Resource usage
    memory_usage_mb: float | None = Field(
        default=None,
        description="Peak memory usage in MB",
    )
    cpu_time_ms: float | None = Field(
        default=None,
        description="CPU time consumed in milliseconds",
    )

    def mark_completed(self, result: Any = None, error: str | None = None) -> None:
        """Mark execution as completed with result or error."""
        if not self.model_config.get("frozen"):
            self.end_time = datetime.now(UTC)
            if self.start_time:
                duration = (self.end_time - self.start_time).total_seconds() * 1000
                self.duration_ms = int(duration)

            if error:
                self.success = False
                self.error = error
            else:
                self.success = True
                self.result = result


class PluginError(Exception):
    r"""PluginError - Custom Exception.

    Implementa exceção customizada para casos específicos do domínio. Fornece informações detalhadas sobre erros.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    to_dict(): Método específico da classe

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = PluginError()\n    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """Base exception for plugin system errors."""

    def __init__(
        self,
        message: str,
        plugin_id: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize plugin error with comprehensive context.

        Args:
        ----
            message: Human-readable error message
            plugin_id: ID of the plugin that caused the error
            error_code: Machine-readable error classification
            details: Additional error context and metadata
            cause: Original exception that caused this error

        """
        super().__init__(message)
        self.message = message
        self.plugin_id = plugin_id
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.now(UTC)
        self.traceback = traceback.format_exc() if cause else None

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            "message": self.message,
            "plugin_id": self.plugin_id,
            "error_code": self.error_code,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "traceback": self.traceback,
            "cause": str(self.cause) if self.cause else None,
        }


class PluginValidationError(PluginError):
    r"""PluginValidationError - Custom Exception.

    Implementa exceção customizada para casos específicos do domínio. Fornece informações detalhadas sobre erros.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    Sem métodos públicos documentados.

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = PluginValidationError()\n    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """Exception raised when plugin validation fails."""

    def __init__(
        self,
        message: str,
        plugin_id: str,
        validation_failures: list[str],
        **kwargs: Any,
    ) -> None:
        """Initialize validation error with failure details.

        Args:
        ----
            message: Error message
            plugin_id: ID of the plugin that failed validation
            validation_failures: List of specific validation failures
            **kwargs: Additional error context

        """
        super().__init__(message, plugin_id, "VALIDATION_FAILED", **kwargs)
        self.validation_failures = validation_failures
        self.details["validation_failures"] = validation_failures


class PluginLoadError(PluginError):
    r"""PluginLoadError - Custom Exception.

    Implementa exceção customizada para casos específicos do domínio. Fornece informações detalhadas sobre erros.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    Sem métodos públicos documentados.

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = PluginLoadError()\n    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """Exception raised when plugin loading fails."""

    def __init__(self, message: str, plugin_id: str, **kwargs: Any) -> None:
        """Initialize plugin load error with failure details."""
        super().__init__(message, plugin_id, "LOAD_FAILED", **kwargs)


class PluginExecutionError(PluginError):
    r"""PluginExecutionError - Custom Exception.

    Implementa exceção customizada para casos específicos do domínio. Fornece informações detalhadas sobre erros.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    Sem métodos públicos documentados.

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = PluginExecutionError()\n    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """Exception raised when plugin execution fails."""

    def __init__(
        self,
        message: str,
        plugin_id: str,
        execution_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize plugin execution error with execution context."""
        super().__init__(message, plugin_id, "EXECUTION_FAILED", **kwargs)
        self.execution_id = execution_id
        if execution_id:
            self.details["execution_id"] = execution_id


class PluginDependencyError(PluginError):
    """Exception raised when plugin dependency resolution fails."""

    def __init__(
        self,
        message: str,
        plugin_id: str,
        missing_dependencies: list[str],
        **kwargs: Any,
    ) -> None:
        """Initialize plugin dependency error with missing dependencies."""
        super().__init__(message, plugin_id, "DEPENDENCY_FAILED", **kwargs)
        self.missing_dependencies = missing_dependencies
        self.details["missing_dependencies"] = missing_dependencies


class PluginSecurityError(PluginError):
    """Exception raised when plugin security validation fails."""

    def __init__(
        self,
        message: str,
        plugin_id: str,
        security_violations: list[str],
        **kwargs: Any,
    ) -> None:
        """Initialize plugin security error with violation details."""
        super().__init__(message, plugin_id, "SECURITY_VIOLATION", **kwargs)
        self.security_violations = security_violations
        self.details["security_violations"] = security_violations


# Type definitions for plugin configuration
class PluginConfigDict(TypedDict):
    """Plugin configuration dictionary for runtime settings."""

    enabled: bool
    priority: int
    settings: dict[str, Any]
    dependencies: list[str]
    security_level: str
    resource_limits: dict[str, Any]


# Type definitions for plugin metadata
class PluginMetadataDict(TypedDict):
    """Plugin metadata dictionary for identification and discovery."""

    id: str
    name: str
    version: str
    description: str
    author: str
    license: str
    plugin_type: str
    entry_point: str
    dependencies: list[str]
    capabilities: list[str]
    configuration_schema: dict[str, Any]


# Type definitions for plugin execution context
class PluginExecutionContext(TypedDict):
    """Plugin execution context dictionary for runtime tracking."""

    execution_id: str
    plugin_id: str
    user_id: str
    session_id: str
    trace_id: str
    environment: str
    request_metadata: dict[str, Any]
    resource_limits: dict[str, Any]
