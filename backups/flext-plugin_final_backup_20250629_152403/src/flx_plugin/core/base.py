"""Base plugin interface and metadata classes for the enterprise plugin system.

Copyright (c) 2025 FLX Team. All rights reserved.
"""

from __future__ import annotations

import abc
from datetime import UTC, datetime
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from flx_plugin.core.types import PluginLifecycle, PluginStatus, PluginType


class PluginMetadata(BaseModel):
    """Comprehensive metadata for enterprise plugins.

    Provides all necessary information for plugin discovery, validation,
    dependency resolution, and lifecycle management with type safety.
    """

    model_config = {"frozen": True}

    # Core identification
    id: str = Field(description="Unique plugin identifier")
    name: str = Field(description="Human-readable plugin name")
    version: str = Field(description="Semantic version string")
    description: str = Field(description="Plugin description and purpose")

    # Plugin classification
    plugin_type: PluginType = Field(description="Functional category of the plugin")
    capabilities: list[str] = Field(
        default_factory=list,
        description="List of plugin capabilities",
    )

    # Authorship and licensing
    author: str = Field(description="Plugin author or organization")
    license: str = Field(description="Plugin license identifier")
    homepage: str | None = Field(default=None, description="Plugin homepage URL")
    repository: str | None = Field(
        default=None,
        description="Source code repository URL",
    )

    # Technical specifications
    entry_point: str = Field(description="Python entry point for plugin class")
    python_version: str = Field(default=">=3.13", description="Required Python version")
    dependencies: list[str] = Field(
        default_factory=list,
        description="Required Python packages",
    )
    meltano_dependencies: list[str] = Field(
        default_factory=list,
        description="Required Meltano plugins",
    )

    # Configuration schema
    configuration_schema: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON schema for plugin configuration validation",
    )
    default_configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Default configuration values",
    )

    # Security and permissions
    required_permissions: list[str] = Field(
        default_factory=list,
        description="Required system permissions",
    )
    security_level: str = Field(
        default="standard",
        description="Security sandbox level",
    )
    trusted: bool = Field(
        default=False,
        description="Whether plugin is trusted by organization",
    )

    # Resource requirements
    min_memory_mb: int = Field(
        default=128,
        description="Minimum memory requirement in MB",
    )
    max_memory_mb: int | None = Field(
        default=None,
        description="Maximum memory limit in MB",
    )
    cpu_cores: int = Field(default=1, description="CPU cores requirement")
    disk_space_mb: int = Field(default=100, description="Disk space requirement in MB")

    # Metadata timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Plugin(abc.ABC):
    """Abstract base class for all FLX enterprise plugins.

    Defines the contract that all plugins must implement for proper
    integration with the enterprise plugin system, including lifecycle
    management, configuration, and execution patterns.
    """

    # Plugin metadata - must be defined by concrete implementations
    METADATA: ClassVar[PluginMetadata]

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize plugin with configuration.

        Args:
        ----
            config: Plugin-specific configuration dictionary

        """
        self._config = config or {}
        self._lifecycle_state = PluginLifecycle.UNREGISTERED
        self._status = PluginStatus.UNKNOWN
        self._initialized = False
        self._last_health_check = datetime.now(UTC)

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return self.METADATA

    @property
    def lifecycle_state(self) -> PluginLifecycle:
        """Get current lifecycle state."""
        return self._lifecycle_state

    @property
    def status(self) -> PluginStatus:
        """Get current operational status."""
        return self._status

    @property
    def config(self) -> dict[str, Any]:
        """Get plugin configuration."""
        return self._config.copy()

    @property
    def is_initialized(self) -> bool:
        """Check if plugin is initialized."""
        return self._initialized

    def _update_lifecycle_state(self, state: PluginLifecycle) -> None:
        """Update plugin lifecycle state."""
        self._lifecycle_state = state

    def _update_status(self, status: PluginStatus) -> None:
        """Update plugin operational status."""
        self._status = status
        self._last_health_check = datetime.now(UTC)

    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize plugin resources and connections.

        Called once during plugin loading to set up required resources,
        establish connections, and prepare the plugin for execution.

        Raises
        ------
            PluginError: When initialization fails

        """
        ...

    @abc.abstractmethod
    async def cleanup(self) -> None:
        """Clean up plugin resources and connections.

        Called during plugin unloading to properly release resources,
        close connections, and perform necessary cleanup operations.

        Raises
        ------
            PluginError: When cleanup fails

        """
        ...

    @abc.abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Perform plugin health check.

        Returns comprehensive health status including operational metrics,
        resource usage, and any detected issues or warnings.

        Returns
        -------
            Dictionary containing health status and metrics

        """
        ...

    @abc.abstractmethod
    async def execute(self, input_data: Any, context: dict[str, Any]) -> Any:
        """Execute plugin functionality.

        Main entry point for plugin execution with input data and context.
        Implementation varies by plugin type and specific functionality.

        Args:
        ----
            input_data: Input data for plugin processing
            context: Execution context and metadata

        Returns:
        -------
            Plugin execution result

        Raises:
        ------
            PluginExecutionError: When execution fails

        """
        ...

    async def validate_configuration(self, config: dict[str, Any]) -> list[str]:
        """Validate plugin configuration against schema.

        Args:
        ----
            config: Configuration dictionary to validate

        Returns:
        -------
            List of validation error messages (empty if valid)

        """
        # Basic validation - can be overridden by concrete implementations
        errors = []

        if not isinstance(config, dict):
            errors.append("Configuration must be a dictionary")
            return errors

        # Validate against configuration schema if available
        schema = self.metadata.configuration_schema
        if schema:
            try:
                import jsonschema

                jsonschema.validate(instance=config, schema=schema)
            except jsonschema.ValidationError as e:
                errors.append(f"Configuration validation failed: {e.message}")
            except jsonschema.SchemaError as e:
                errors.append(f"Invalid configuration schema: {e.message}")
            except ImportError:
                # If jsonschema not available, skip validation
                pass

        return errors

    async def get_capabilities(self) -> list[str]:
        """Get list of plugin capabilities.

        Returns
        -------
            List of capability strings

        """
        return self.metadata.capabilities

    async def get_resource_usage(self) -> dict[str, Any]:
        """Get current resource usage metrics.

        Returns
        -------
            Dictionary containing resource usage information

        """
        try:
            import psutil

            process = psutil.Process()
            MB_TO_BYTES = 1024 * 1024

            return {
                "memory_mb": process.memory_info().rss / MB_TO_BYTES,
                "cpu_percent": process.cpu_percent(),
                "open_files": len(process.open_files()),
                "threads": process.num_threads(),
                "status": process.status(),
            }
        except ImportError:
            # If psutil not available, return minimal info
            return {
                "memory_mb": 0,
                "cpu_percent": 0,
                "status": "unknown",
            }


class BaseExtractorPlugin(Plugin):
    """Base class for data extractor plugins.

    Specialized base class for plugins that extract data from various
    sources including databases, APIs, files, and streaming systems.
    """

    @abc.abstractmethod
    async def extract(self, source_config: dict[str, Any]) -> Any:
        """Extract data from configured source.

        Args:
        ----
            source_config: Source-specific configuration

        Returns:
        -------
            Extracted data in standardized format

        """
        ...

    async def execute(self, _input_data: Any, context: dict[str, Any]) -> Any:
        """Execute extraction functionality."""
        source_config = context.get("source_config", {})
        return await self.extract(source_config)


class BaseLoaderPlugin(Plugin):
    """Base class for data loader plugins.

    Specialized base class for plugins that load data into various
    destinations including databases, data warehouses, and file systems.
    """

    @abc.abstractmethod
    async def load(
        self, data: Any, destination_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Load data to configured destination.

        Args:
        ----
            data: Data to load
            destination_config: Destination-specific configuration

        Returns:
        -------
            Load operation results and metrics

        """
        ...

    async def execute(self, input_data: Any, context: dict[str, Any]) -> Any:
        """Execute loading functionality."""
        destination_config = context.get("destination_config", {})
        return await self.load(input_data, destination_config)


class BaseTransformerPlugin(Plugin):
    """Base class for data transformer plugins.

    Specialized base class for plugins that transform, validate,
    and enrich data during pipeline processing.
    """

    @abc.abstractmethod
    async def transform(self, data: Any, transform_config: dict[str, Any]) -> Any:
        """Transform data according to configuration.

        Args:
        ----
            data: Input data to transform
            transform_config: Transformation-specific configuration

        Returns:
        -------
            Transformed data

        """
        ...

    async def execute(self, input_data: Any, context: dict[str, Any]) -> Any:
        """Execute transformation functionality."""
        transform_config = context.get("transform_config", {})
        return await self.transform(input_data, transform_config)
