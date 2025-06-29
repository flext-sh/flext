"""Plugin context and dependency management for enterprise plugin system.

Copyright (c) 2025 FLX Team. All rights reserved.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, TypeVar

from pydantic import BaseModel, Field

from flx_plugin.core.types import PluginExecutionContext, PluginType

T = TypeVar("T")


class PluginDependency(BaseModel):
    """Plugin dependency specification with version constraints.

    Defines dependencies between plugins including version requirements,
    optional dependencies, and compatibility constraints for proper
    plugin ecosystem management.
    """

    model_config = {"frozen": True}

    # Dependency identification
    plugin_id: str = Field(description="ID of the required plugin")
    plugin_type: PluginType | None = Field(
        default=None,
        description="Expected plugin type",
    )

    # Version constraints
    min_version: str | None = Field(
        default=None,
        description="Minimum required version",
    )
    max_version: str | None = Field(
        default=None,
        description="Maximum compatible version",
    )
    exact_version: str | None = Field(
        default=None,
        description="Exact version requirement",
    )

    # Dependency characteristics
    optional: bool = Field(default=False, description="Whether dependency is optional")
    development_only: bool = Field(
        default=False,
        description="Development/testing dependency",
    )

    # Compatibility information
    compatible_versions: list[str] = Field(
        default_factory=list,
        description="List of known compatible versions",
    )
    incompatible_versions: list[str] = Field(
        default_factory=list,
        description="List of known incompatible versions",
    )

    def is_version_compatible(self, version: str) -> bool:
        """Check if given version satisfies dependency constraints.

        Args:
        ----
            version: Version string to check

        Returns:
        -------
            True if version satisfies all constraints

        """
        # Check exact version requirement
        if self.exact_version and version != self.exact_version:
            return False

        # Check incompatible versions
        if version in self.incompatible_versions:
            return False

        # Check compatible versions if specified
        if self.compatible_versions and version not in self.compatible_versions:
            return False

        # Check min/max version constraints
        # Note: In production, this would use proper semantic version comparison
        if self.min_version and self._compare_versions(version, self.min_version) < 0:
            return False

        return not (
            self.max_version and self._compare_versions(version, self.max_version) > 0
        )

    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings (simplified implementation).

        Args:
        ----
            version1: First version string
            version2: Second version string

        Returns:
        -------
            -1 if version1 < version2, 0 if equal, 1 if version1 > version2

        """
        # Simplified version comparison - in production use packaging.version
        parts1 = [int(x) for x in version1.split(".")]
        parts2 = [int(x) for x in version2.split(".")]

        # Pad shorter version with zeros
        max_len = max(len(parts1), len(parts2))
        parts1.extend([0] * (max_len - len(parts1)))
        parts2.extend([0] * (max_len - len(parts2)))

        for p1, p2 in zip(parts1, parts2, strict=False):
            if p1 < p2:
                return -1
            if p1 > p2:
                return 1
        return 0


class PluginContext(BaseModel):
    """Comprehensive execution context for plugin operations.

    Provides all necessary context information for plugin execution
    including user information, session data, resource limits,
    and dependency injection containers.
    """

    model_config = {"frozen": True}

    # Execution identification
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plugin_id: str = Field(description="ID of the executing plugin")

    # User and session context
    user_id: str | None = Field(
        default=None,
        description="ID of the user executing the plugin",
    )
    session_id: str | None = Field(default=None, description="Session identifier")
    tenant_id: str | None = Field(default=None, description="Multi-tenant context")

    # Request context
    request_id: str | None = Field(default=None, description="Request identifier")
    trace_id: str | None = Field(default=None, description="Distributed tracing ID")
    span_id: str | None = Field(default=None, description="Distributed tracing span ID")

    # Environment context
    environment: str = Field(default="development", description="Execution environment")
    pipeline_id: str | None = Field(default=None, description="Pipeline context")
    pipeline_run_id: str | None = Field(
        default=None,
        description="Pipeline run identifier",
    )

    # Temporal context
    execution_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    timeout_seconds: int | None = Field(default=None, description="Execution timeout")

    # Resource limits
    max_memory_mb: int | None = Field(default=None, description="Maximum memory limit")
    max_cpu_percent: int | None = Field(default=None, description="Maximum CPU usage")
    max_execution_time_seconds: int | None = Field(
        default=None,
        description="Maximum execution time",
    )

    # Plugin configuration
    plugin_config: dict[str, Any] = Field(
        default_factory=dict,
        description="Plugin configuration",
    )
    environment_config: dict[str, Any] = Field(
        default_factory=dict,
        description="Environment configuration",
    )

    # Security context
    permissions: list[str] = Field(
        default_factory=list,
        description="Granted permissions",
    )
    security_level: str = Field(
        default="standard",
        description="Security sandbox level",
    )
    allowed_operations: list[str] = Field(
        default_factory=list,
        description="Allowed operations",
    )

    # Dependency injection
    services: dict[str, Any] = Field(
        default_factory=dict,
        description="Injected services",
    )
    dependencies: dict[str, Any] = Field(
        default_factory=dict,
        description="Plugin dependencies",
    )

    # Metadata and logging
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )
    tags: list[str] = Field(default_factory=list, description="Context tags")

    def get_service(
        self, service_name: str, service_type: type[T] | None = None
    ) -> T | None:
        """Get injected service by name with optional type checking.

        Args:
        ----
            service_name: Name of the service to retrieve
            service_type: Expected service type for validation

        Returns:
        -------
            Service instance or None if not found

        Raises:
        ------
            TypeError: If service exists but doesn't match expected type

        """
        service = self.services.get(service_name)

        if service is None:
            return None

        if service_type and not isinstance(service, service_type):
            msg = f"Service '{service_name}' is type {type(service).__name__}, expected {service_type.__name__}"
            raise TypeError(
                msg,
            )

        return service

    def get_dependency(
        self, dependency_name: str, dependency_type: type[T] | None = None
    ) -> T | None:
        """Get plugin dependency by name with optional type checking.

        Args:
        ----
            dependency_name: Name of the dependency to retrieve
            dependency_type: Expected dependency type for validation

        Returns:
        -------
            Dependency instance or None if not found

        Raises:
        ------
            TypeError: If dependency exists but doesn't match expected type

        """
        dependency = self.dependencies.get(dependency_name)

        if dependency is None:
            return None

        if dependency_type and not isinstance(dependency, dependency_type):
            msg = (
                f"Dependency '{dependency_name}' is type {type(dependency).__name__}, "
                f"expected {dependency_type.__name__}"
            )
            raise TypeError(
                msg,
            )

        return dependency

    def has_permission(self, permission: str) -> bool:
        """Check if context has specific permission.

        Args:
        ----
            permission: Permission string to check

        Returns:
        -------
            True if permission is granted

        """
        return permission in self.permissions

    def can_perform_operation(self, operation: str) -> bool:
        """Check if operation is allowed in current context.

        Args:
        ----
            operation: Operation string to check

        Returns:
        -------
            True if operation is allowed

        """
        return operation in self.allowed_operations

    def add_metadata(self, key: str, value: Any) -> PluginContext:
        """Add metadata to context (returns new context due to frozen model).

        Args:
        ----
            key: Metadata key
            value: Metadata value

        Returns:
        -------
            New context with added metadata

        """
        new_metadata = self.metadata.copy()
        new_metadata[key] = value

        return self.model_copy(update={"metadata": new_metadata})

    def with_timeout(self, timeout_seconds: int) -> PluginContext:
        """Create new context with specified timeout.

        Args:
        ----
            timeout_seconds: Timeout in seconds

        Returns:
        -------
            New context with specified timeout

        """
        return self.model_copy(update={"timeout_seconds": timeout_seconds})

    def with_resource_limits(
        self,
        max_memory_mb: int | None = None,
        max_cpu_percent: int | None = None,
        max_execution_time_seconds: int | None = None,
    ) -> PluginContext:
        """Create new context with resource limits.

        Args:
        ----
            max_memory_mb: Maximum memory limit in MB
            max_cpu_percent: Maximum CPU usage percentage
            max_execution_time_seconds: Maximum execution time

        Returns:
        -------
            New context with resource limits

        """
        updates = {}
        if max_memory_mb is not None:
            updates["max_memory_mb"] = max_memory_mb
        if max_cpu_percent is not None:
            updates["max_cpu_percent"] = max_cpu_percent
        if max_execution_time_seconds is not None:
            updates["max_execution_time_seconds"] = max_execution_time_seconds

        return self.model_copy(update=updates)

    def to_execution_context(self) -> PluginExecutionContext:
        """Convert to plugin execution context dictionary.

        Returns
        -------
            Dictionary representation for execution context

        """
        return PluginExecutionContext(
            execution_id=self.execution_id,
            plugin_id=self.plugin_id,
            user_id=self.user_id or "",
            session_id=self.session_id or "",
            trace_id=self.trace_id or "",
            environment=self.environment,
            request_metadata=self.metadata,
            resource_limits={
                "max_memory_mb": self.max_memory_mb,
                "max_cpu_percent": self.max_cpu_percent,
                "max_execution_time_seconds": self.max_execution_time_seconds,
            },
        )


class PluginContextBuilder:
    """Builder pattern for creating plugin contexts with fluent interface.

    Provides a convenient way to construct plugin contexts with
    method chaining for better readability and maintainability.
    """

    def __init__(self, plugin_id: str) -> None:
        """Initialize builder with required plugin ID.

        Args:
        ----
            plugin_id: ID of the plugin for which context is being built

        """
        self._plugin_id = plugin_id
        self._data: dict[str, Any] = {"plugin_id": plugin_id}

    def with_user(self, user_id: str) -> PluginContextBuilder:
        """Set user context."""
        self._data["user_id"] = user_id
        return self

    def with_session(self, session_id: str) -> PluginContextBuilder:
        """Set session context."""
        self._data["session_id"] = session_id
        return self

    def with_request(
        self, request_id: str, trace_id: str | None = None
    ) -> PluginContextBuilder:
        """Set request context."""
        self._data["request_id"] = request_id
        if trace_id:
            self._data["trace_id"] = trace_id
        return self

    def with_environment(self, environment: str) -> PluginContextBuilder:
        """Set execution environment."""
        self._data["environment"] = environment
        return self

    def with_pipeline(
        self, pipeline_id: str, pipeline_run_id: str | None = None
    ) -> PluginContextBuilder:
        """Set pipeline context."""
        self._data["pipeline_id"] = pipeline_id
        if pipeline_run_id:
            self._data["pipeline_run_id"] = pipeline_run_id
        return self

    def with_config(self, config: dict[str, Any]) -> PluginContextBuilder:
        """Set plugin configuration."""
        self._data["plugin_config"] = config
        return self

    def with_permissions(self, permissions: list[str]) -> PluginContextBuilder:
        """Set security permissions."""
        self._data["permissions"] = permissions
        return self

    def with_services(self, services: dict[str, Any]) -> PluginContextBuilder:
        """Set injected services."""
        self._data["services"] = services
        return self

    def with_dependencies(self, dependencies: dict[str, Any]) -> PluginContextBuilder:
        """Set plugin dependencies."""
        self._data["dependencies"] = dependencies
        return self

    def with_resource_limits(
        self,
        max_memory_mb: int | None = None,
        max_cpu_percent: int | None = None,
        max_execution_time_seconds: int | None = None,
    ) -> PluginContextBuilder:
        """Set resource limits."""
        if max_memory_mb is not None:
            self._data["max_memory_mb"] = max_memory_mb
        if max_cpu_percent is not None:
            self._data["max_cpu_percent"] = max_cpu_percent
        if max_execution_time_seconds is not None:
            self._data["max_execution_time_seconds"] = max_execution_time_seconds
        return self

    def with_metadata(self, metadata: dict[str, Any]) -> PluginContextBuilder:
        """Set context metadata."""
        self._data["metadata"] = metadata
        return self

    def build(self) -> PluginContext:
        """Build the plugin context.

        Returns
        -------
            Configured plugin context

        """
        return PluginContext(**self._data)
