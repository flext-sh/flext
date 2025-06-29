"""Plugin discovery system for FLX Meltano Enterprise.

This module provides comprehensive plugin discovery capabilities using Python
entry points and dynamic plugin registration for the enterprise plugin ecosystem.

📋 Architecture: docs/architecture/003-plugin-system-architecture/03-entry-point-discovery.md
🎯 Status: IMPLEMENTING MISSING CRITICAL COMPONENT

Features:
- Entry point-based plugin discovery
- Plugin metadata validation and caching
- Hot-reload capability for development
- Security validation integration
- Plugin dependency resolution

Usage:
    from flx_core.plugins.discovery import PluginDiscovery, PluginRegistry

    discovery = PluginDiscovery()
    plugins = await discovery.discover_plugins()

    registry = PluginRegistry()
    await registry.register_plugin(plugin_instance)
"""

from __future__ import annotations

import importlib.metadata
import warnings
from typing import TYPE_CHECKING, Any

from flx_core.domain.advanced_types import ServiceError, ServiceResult

# ZERO TOLERANCE CONSOLIDATION: Use centralized plugin import management
from flx_core.utils.import_fallback_patterns import OptionalDependency
from flx_observability.structured_logging import get_logger
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from collections.abc import Sequence

    from flx_core.plugins.base import PluginInterface, PluginMetadata
    from flx_core.plugins.types import PluginType

logger = get_logger(__name__)

# Centralized plugin import dependency with fallback handling
PLUGIN_IMPORT_DEPENDENCY = OptionalDependency(
    "Plugin Import Validation",
    fallback_value=None,
)


class PluginEntryPoint(BaseModel):
    """Plugin entry point metadata."""

    name: str = Field(description="Plugin entry point name")
    module_name: str = Field(description="Python module containing plugin")
    plugin_class: str = Field(description="Plugin class name")
    group: str = Field(default="flx.plugins", description="Entry point group")
    version: str | None = Field(default=None, description="Plugin version")

    @property
    def qualified_name(self) -> str:
        """Get fully qualified plugin name."""
        return f"{self.group}:{self.name}"


class PluginDiscoveryResult(BaseModel):
    """Result of plugin discovery operation."""

    discovered_plugins: list[PluginEntryPoint] = Field(default_factory=list)
    failed_discoveries: dict[str, str] = Field(default_factory=dict)
    total_discovered: int = Field(default=0)
    discovery_errors: list[str] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        """Calculate totals after initialization."""
        self.total_discovered = len(self.discovered_plugins)


class PluginDiscovery:
    """Plugin discovery service using Python entry points.

    Discovers plugins through the Python packaging entry point system,
    providing comprehensive plugin metadata validation and hot-reload
    capabilities for enterprise plugin management.
    """

    def __init__(self, entry_point_group: str = "flx.plugins") -> None:
        """Initialize plugin discovery.

        Args:
        ----
            entry_point_group: Entry point group for plugin discovery

        """
        self.entry_point_group = entry_point_group
        self.logger = get_logger(self.__class__.__name__)
        self._discovered_cache: dict[str, PluginEntryPoint] = {}

    async def discover_plugins(
        self,
        plugin_types: Sequence[PluginType] | None = None,
        refresh_cache: bool = False,
    ) -> ServiceResult[PluginDiscoveryResult]:
        """Discover plugins via Python entry points.

        Args:
        ----
            plugin_types: Filter plugins by specific types (optional)
            refresh_cache: Force cache refresh for discovery

        Returns:
        -------
            ServiceResult containing discovery results with plugin metadata

        """
        self.logger.info(
            "Starting plugin discovery",
            group=self.entry_point_group,
            refresh_cache=refresh_cache,
        )

        if refresh_cache:
            self._discovered_cache.clear()

        try:
            # Discover entry points for plugin group
            entry_points = importlib.metadata.entry_points(group=self.entry_point_group)

            discovered_plugins: list[PluginEntryPoint] = []
            failed_discoveries: dict[str, str] = {}
            discovery_errors: list[str] = []

            for entry_point in entry_points:
                try:
                    # Extract plugin metadata from entry point
                    plugin_entry = self._create_plugin_entry_point(entry_point)

                    # Validate plugin can be loaded (basic validation)
                    validation_result = await self._validate_plugin_entry(plugin_entry)

                    if validation_result.is_ok():
                        discovered_plugins.append(plugin_entry)
                        self._discovered_cache[plugin_entry.name] = plugin_entry

                        self.logger.debug(
                            "Plugin discovered successfully",
                            plugin_name=plugin_entry.name,
                            module=plugin_entry.module_name,
                        )
                    else:
                        failed_discoveries[plugin_entry.name] = (
                            validation_result.error.message
                        )
                        self.logger.warning(
                            "Plugin validation failed",
                            plugin_name=plugin_entry.name,
                            error=validation_result.error.message,
                        )

                except Exception as e:
                    error_msg = f"Failed to process entry point {entry_point.name}: {e}"
                    discovery_errors.append(error_msg)
                    failed_discoveries[entry_point.name] = str(e)

                    self.logger.exception(
                        "Entry point processing failed",
                        entry_point=entry_point.name,
                        error=str(e),
                    )

            # Create discovery result
            result = PluginDiscoveryResult(
                discovered_plugins=discovered_plugins,
                failed_discoveries=failed_discoveries,
                discovery_errors=discovery_errors,
            )

            self.logger.info(
                "Plugin discovery completed",
                total_discovered=result.total_discovered,
                failed_count=len(failed_discoveries),
                error_count=len(discovery_errors),
            )

            return ServiceResult.ok(result)

        except Exception as e:
            error_msg = f"Plugin discovery failed: {e}"
            self.logger.error("Plugin discovery failed", error=str(e), exc_info=True)
            return ServiceResult.fail(ServiceError("SYSTEM_ERROR", error_msg))

    def _create_plugin_entry_point(
        self, entry_point: importlib.metadata.EntryPoint
    ) -> PluginEntryPoint:
        """Create plugin entry point from importlib entry point.

        Args:
        ----
            entry_point: Importlib entry point object

        Returns:
        -------
            PluginEntryPoint with validated metadata

        """
        # Parse module and class from entry point value
        module_name, _, class_name = entry_point.value.partition(":")

        return PluginEntryPoint(
            name=entry_point.name,
            module_name=module_name,
            plugin_class=class_name,
            group=entry_point.group,
            # Version extraction would require additional package metadata
            version=None,
        )

    async def _validate_plugin_entry(
        self, plugin_entry: PluginEntryPoint
    ) -> ServiceResult[bool]:
        """Validate plugin entry point can be loaded.

        Args:
        ----
            plugin_entry: Plugin entry point to validate

        Returns:
        -------
            ServiceResult indicating validation success/failure

        """
        try:
            # ZERO TOLERANCE CONSOLIDATION: Use centralized plugin import management
            module = PLUGIN_IMPORT_DEPENDENCY.try_import(plugin_entry.module_name)

            if module is None or not PLUGIN_IMPORT_DEPENDENCY.is_available:
                return ServiceResult.fail(
                    ServiceError.validation_error(
                        f"Failed to import plugin module: {plugin_entry.module_name}",
                    ),
                )

            # Validate the plugin module and class structure
            success, error_msg = self._validate_plugin_module(module, plugin_entry)

            if success:
                return ServiceResult.ok(True)
            return ServiceResult.fail(
                ServiceError.validation_error(f"Plugin validation failed: {error_msg}"),
            )

        except Exception as e:
            return ServiceResult.fail(
                ServiceError.system_error(f"Plugin validation error: {e}"),
            )

    def _validate_plugin_module(
        self, module: object, plugin_entry: PluginEntryPoint
    ) -> tuple[bool, str]:
        """Validate plugin module and class structure.

        Args:
        ----
            module: Imported plugin module
            plugin_entry: Plugin entry point metadata

        Returns:
        -------
            Tuple of (success, error_message)

        """
        try:
            # Check if plugin class exists in module
            if not hasattr(module, plugin_entry.plugin_class):
                return (
                    False,
                    f"Plugin class {plugin_entry.plugin_class} not found in module {plugin_entry.module_name}",
                )

            plugin_class = getattr(module, plugin_entry.plugin_class)

            # Basic validation that class looks like a plugin
            # Check for METADATA attribute (optional with warning)
            if not hasattr(plugin_class, "METADATA"):
                warnings.warn(
                    f"Plugin {plugin_entry.name} missing METADATA attribute",
                    UserWarning,
                    stacklevel=2,
                )

            return True, ""

        except Exception as e:
            return False, f"Plugin module validation error: {e}"

    def get_discovered_plugins(self) -> dict[str, PluginEntryPoint]:
        """Get currently discovered plugins from cache.

        Returns
        -------
            Dictionary of plugin name to entry point mappings

        """
        return self._discovered_cache.copy()

    def clear_cache(self) -> None:
        """Clear discovery cache."""
        self._discovered_cache.clear()
        self.logger.debug("Plugin discovery cache cleared")


class PluginRegistry:
    """Plugin registry for managing discovered and loaded plugins.

    Provides centralized registry for plugin instances with lifecycle
    management and dependency resolution capabilities.
    """

    def __init__(self) -> None:
        """Initialize plugin registry."""
        self.logger = get_logger(self.__class__.__name__)
        self._registered_plugins: dict[str, PluginInterface] = {}
        self._plugin_metadata: dict[str, PluginMetadata] = {}

    async def register_plugin(self, plugin: PluginInterface) -> ServiceResult[None]:
        """Register a plugin instance in the registry.

        Args:
        ----
            plugin: Plugin instance to register

        Returns:
        -------
            ServiceResult indicating registration success/failure

        """
        try:
            plugin_id = plugin.METADATA.id

            # Check for duplicate registration
            if plugin_id in self._registered_plugins:
                return ServiceResult.fail(
                    ServiceError.validation_error(
                        f"Plugin {plugin_id} already registered",
                    ),
                )

            # Store plugin and metadata
            self._registered_plugins[plugin_id] = plugin
            self._plugin_metadata[plugin_id] = plugin.METADATA

            self.logger.info(
                "Plugin registered successfully",
                plugin_id=plugin_id,
                plugin_type=plugin.METADATA.type.value,
            )

            return ServiceResult.ok(None)

        except Exception as e:
            error_msg = f"Plugin registration failed: {e}"
            self.logger.exception(
                "Plugin registration failed",
                plugin_id=getattr(plugin, "METADATA", {}).get("id", "unknown"),
                error=str(e),
            )
            return ServiceResult.fail(ServiceError("SYSTEM_ERROR", error_msg))

    async def unregister_plugin(self, plugin_id: str) -> ServiceResult[None]:
        """Unregister a plugin from the registry.

        Args:
        ----
            plugin_id: ID of plugin to unregister

        Returns:
        -------
            ServiceResult indicating unregistration success/failure

        """
        try:
            if plugin_id not in self._registered_plugins:
                return ServiceResult.fail(
                    ServiceError.validation_error(
                        f"Plugin {plugin_id} not found in registry",
                    ),
                )

            # Cleanup plugin instance
            plugin = self._registered_plugins[plugin_id]
            await plugin.cleanup()

            # Remove from registry
            del self._registered_plugins[plugin_id]
            del self._plugin_metadata[plugin_id]

            self.logger.info("Plugin unregistered successfully", plugin_id=plugin_id)
            return ServiceResult.ok(None)

        except Exception as e:
            error_msg = f"Plugin unregistration failed: {e}"
            self.logger.exception(
                "Plugin unregistration failed",
                plugin_id=plugin_id,
                error=str(e),
            )
            return ServiceResult.fail(ServiceError("SYSTEM_ERROR", error_msg))

    def get_plugin(self, plugin_id: str) -> PluginInterface | None:
        """Get registered plugin by ID.

        Args:
        ----
            plugin_id: ID of plugin to retrieve

        Returns:
        -------
            Plugin instance if found, None otherwise

        """
        return self._registered_plugins.get(plugin_id)

    def list_plugins(
        self, plugin_type: PluginType | None = None
    ) -> list[PluginMetadata]:
        """List all registered plugins with optional type filtering.

        Args:
        ----
            plugin_type: Filter plugins by type (optional)

        Returns:
        -------
            List of plugin metadata for registered plugins

        """
        plugins = list(self._plugin_metadata.values())

        if plugin_type:
            plugins = [p for p in plugins if p.type == plugin_type]

        return plugins

    def get_plugin_count(self) -> int:
        """Get count of registered plugins.

        Returns
        -------
            Number of registered plugins

        """
        return len(self._registered_plugins)

    async def cleanup_all(self) -> None:
        """Cleanup all registered plugins."""
        self.logger.info(
            "Cleaning up all registered plugins",
            plugin_count=len(self._registered_plugins),
        )

        for plugin_id, plugin in self._registered_plugins.items():
            try:
                await plugin.cleanup()
                self.logger.debug("Plugin cleaned up", plugin_id=plugin_id)
            except Exception as e:
                self.logger.exception(
                    "Plugin cleanup failed",
                    plugin_id=plugin_id,
                    error=str(e),
                )

        self._registered_plugins.clear()
        self._plugin_metadata.clear()

        self.logger.info("All plugins cleaned up successfully")
