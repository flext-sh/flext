"""Plugin manager for orchestrating plugin lifecycle and operations.

Copyright (c) 2025 FLX Team. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from flx_plugin.core.discovery import DiscoveredPlugin, PluginDiscovery
from flx_plugin.core.loader import LoadedPlugin, PluginLoader
from flx_plugin.core.types import (
    PluginError,
    PluginExecutionError,
    PluginExecutionResult,
    PluginStatus,
    PluginType,
)
from flx_plugin.core.validators import PluginValidator

logger = logging.getLogger(__name__)


class PluginManager:
    """Central plugin management system.

    Orchestrates the complete plugin lifecycle including:
    - Discovery and registration
    - Loading and initialization
    - Execution and monitoring
    - Unloading and cleanup
    """

    def __init__(
        self,
        plugin_directories: Optional[List[Path]] = None,
        entry_point_groups: Optional[List[str]] = None,
        security_enabled: bool = True,
        auto_discover: bool = True,
    ) -> None:
        """Initialize plugin manager.

        Args:
        ----
            plugin_directories: Directories to scan for plugins
            entry_point_groups: Entry point groups to scan
            security_enabled: Whether to enforce security validation
            auto_discover: Whether to automatically discover plugins on init

        """
        self.discovery = PluginDiscovery(plugin_directories, entry_point_groups)
        self.loader = PluginLoader(
            validator=PluginValidator(),
            security_enabled=security_enabled,
        )
        self.auto_discover = auto_discover
        self._discovered_plugins: Dict[str, DiscoveredPlugin] = {}
        self._execution_tasks: Dict[str, asyncio.Task] = {}

    async def initialize(self) -> None:
        """Initialize the plugin manager."""
        if self.auto_discover:
            await self.discover_plugins()

    async def discover_plugins(self) -> Dict[str, DiscoveredPlugin]:
        """Discover all available plugins.

        Returns
        -------
            Dictionary mapping plugin IDs to discovered plugins

        """
        self._discovered_plugins = await self.discovery.discover_all()
        logger.info(f"Discovered {len(self._discovered_plugins)} plugins")
        return self._discovered_plugins

    async def load_plugin(
        self,
        plugin_id: str,
        config: Optional[dict[str, Any]] = None,
        initialize: bool = True,
    ) -> LoadedPlugin:
        """Load a plugin by ID.

        Args:
        ----
            plugin_id: Plugin ID to load
            config: Plugin configuration
            initialize: Whether to initialize after loading

        Returns:
        -------
            Loaded plugin instance

        Raises:
        ------
            PluginError: If plugin not found or loading fails

        """
        if plugin_id not in self._discovered_plugins:
            # Try to discover plugins if not already done
            if not self._discovered_plugins:
                await self.discover_plugins()

            if plugin_id not in self._discovered_plugins:
                raise PluginError(
                    f"Plugin not found: {plugin_id}",
                    plugin_id=plugin_id,
                    error_code="NOT_FOUND",
                )

        discovered = self._discovered_plugins[plugin_id]
        return await self.loader.load_plugin(discovered, config, initialize)

    async def unload_plugin(self, plugin_id: str) -> None:
        """Unload a plugin.

        Args:
        ----
            plugin_id: Plugin ID to unload

        """
        # Cancel any running executions
        if plugin_id in self._execution_tasks:
            task = self._execution_tasks[plugin_id]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            del self._execution_tasks[plugin_id]

        # Unload the plugin
        await self.loader.unload_plugin(plugin_id)

    async def reload_plugin(
        self,
        plugin_id: str,
        config: Optional[dict[str, Any]] = None,
    ) -> LoadedPlugin:
        """Reload a plugin with new configuration.

        Args:
        ----
            plugin_id: Plugin ID to reload
            config: New configuration

        Returns:
        -------
            Reloaded plugin instance

        """
        if plugin_id not in self._discovered_plugins:
            raise PluginError(
                f"Plugin not found: {plugin_id}",
                plugin_id=plugin_id,
                error_code="NOT_FOUND",
            )

        discovered = self._discovered_plugins[plugin_id]
        return await self.loader.reload_plugin(plugin_id, discovered, config)

    async def execute_plugin(
        self,
        plugin_id: str,
        input_data: Any = None,
        context: Optional[dict[str, Any]] = None,
    ) -> PluginExecutionResult:
        """Execute a plugin.

        Args:
        ----
            plugin_id: Plugin ID to execute
            input_data: Input data for plugin
            context: Execution context

        Returns:
        -------
            Plugin execution result

        Raises:
        ------
            PluginExecutionError: If execution fails

        """
        # Get loaded plugin
        loaded = self.loader.get_loaded_plugin(plugin_id)
        if not loaded:
            # Try to load the plugin
            loaded = await self.load_plugin(plugin_id)

        # Create execution ID
        import uuid

        execution_id = str(uuid.uuid4())

        # Create execution context
        exec_context = {
            "execution_id": execution_id,
            "plugin_id": plugin_id,
            **(context or {}),
        }

        # Create execution result
        result = PluginExecutionResult(
            success=False,
            plugin_id=plugin_id,
            execution_id=execution_id,
            execution_context=exec_context,
        )

        try:
            # Execute plugin
            plugin_result = await loaded.instance.execute(input_data, exec_context)

            # Update result
            result.success = True
            result.result = plugin_result

        except Exception as e:
            # Update result with error
            result.success = False
            result.error = str(e)

            raise PluginExecutionError(
                f"Plugin execution failed: {plugin_id}",
                plugin_id=plugin_id,
                execution_id=execution_id,
                cause=e,
            )

        finally:
            # Mark execution completed
            result.mark_completed(
                result.result if result.success else None,
                result.error if not result.success else None,
            )

        return result

    async def execute_plugin_async(
        self,
        plugin_id: str,
        input_data: Any = None,
        context: Optional[dict[str, Any]] = None,
    ) -> asyncio.Task:
        """Execute a plugin asynchronously.

        Args:
        ----
            plugin_id: Plugin ID to execute
            input_data: Input data for plugin
            context: Execution context

        Returns:
        -------
            Asyncio task for the execution

        """
        # Cancel any existing execution
        if plugin_id in self._execution_tasks:
            existing_task = self._execution_tasks[plugin_id]
            if not existing_task.done():
                existing_task.cancel()

        # Create new execution task
        task = asyncio.create_task(self.execute_plugin(plugin_id, input_data, context))
        self._execution_tasks[plugin_id] = task

        return task

    async def get_plugin_status(self, plugin_id: str) -> PluginStatus:
        """Get plugin operational status.

        Args:
        ----
            plugin_id: Plugin ID

        Returns:
        -------
            Plugin status

        """
        loaded = self.loader.get_loaded_plugin(plugin_id)
        if not loaded:
            return PluginStatus.UNKNOWN

        return loaded.instance.status

    async def get_plugin_health(self, plugin_id: str) -> dict[str, Any]:
        """Get plugin health information.

        Args:
        ----
            plugin_id: Plugin ID

        Returns:
        -------
            Health check results

        """
        loaded = self.loader.get_loaded_plugin(plugin_id)
        if not loaded:
            return {
                "status": "unknown",
                "error": "Plugin not loaded",
            }

        try:
            return await loaded.instance.health_check()
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def list_plugins(
        self,
        plugin_type: Optional[PluginType] = None,
        status: Optional[PluginStatus] = None,
    ) -> List[dict[str, Any]]:
        """List available plugins with optional filtering.

        Args:
        ----
            plugin_type: Filter by plugin type
            status: Filter by operational status

        Returns:
        -------
            List of plugin information dictionaries

        """
        plugins = []

        for plugin_id, discovered in self._discovered_plugins.items():
            # Apply type filter
            if plugin_type and discovered.metadata.plugin_type != plugin_type:
                continue

            # Get loaded status
            loaded = self.loader.get_loaded_plugin(plugin_id)
            current_status = loaded.instance.status if loaded else PluginStatus.UNKNOWN

            # Apply status filter
            if status and current_status != status:
                continue

            # Build plugin info
            plugin_info = {
                "id": plugin_id,
                "name": discovered.metadata.name,
                "version": discovered.metadata.version,
                "type": discovered.metadata.plugin_type.value,
                "status": current_status.value,
                "loaded": loaded is not None,
                "initialized": loaded.is_initialized if loaded else False,
                "source": discovered.source,
                "capabilities": discovered.metadata.capabilities,
            }

            plugins.append(plugin_info)

        return plugins

    def get_discovered_plugin(self, plugin_id: str) -> Optional[DiscoveredPlugin]:
        """Get discovered plugin information.

        Args:
        ----
            plugin_id: Plugin ID

        Returns:
        -------
            Discovered plugin or None

        """
        return self._discovered_plugins.get(plugin_id)

    def get_loaded_plugin(self, plugin_id: str) -> Optional[LoadedPlugin]:
        """Get loaded plugin instance.

        Args:
        ----
            plugin_id: Plugin ID

        Returns:
        -------
            Loaded plugin or None

        """
        return self.loader.get_loaded_plugin(plugin_id)

    def is_plugin_loaded(self, plugin_id: str) -> bool:
        """Check if a plugin is loaded.

        Args:
        ----
            plugin_id: Plugin ID

        Returns:
        -------
            True if plugin is loaded

        """
        return self.loader.is_loaded(plugin_id)

    async def shutdown(self) -> None:
        """Shutdown the plugin manager and cleanup resources."""
        # Cancel all running executions
        for task in self._execution_tasks.values():
            if not task.done():
                task.cancel()

        # Wait for all tasks to complete
        if self._execution_tasks:
            await asyncio.gather(
                *self._execution_tasks.values(),
                return_exceptions=True,
            )

        # Unload all plugins
        loaded_plugins = list(self.loader.get_all_loaded_plugins().keys())
        for plugin_id in loaded_plugins:
            try:
                await self.unload_plugin(plugin_id)
            except Exception as e:
                logger.error(f"Error unloading plugin {plugin_id}: {e}")

        logger.info("Plugin manager shutdown complete")
