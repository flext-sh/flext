"""Plugin loader with security validation and dependency resolution.

Copyright (c) 2025 FLX Team. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from flx_plugin.core.base import Plugin, PluginMetadata
from flx_plugin.core.discovery import DiscoveredPlugin
from flx_plugin.core.types import (
    PluginDependencyError,
    PluginError,
    PluginLifecycle,
    PluginLoadError,
    PluginSecurityError,
    PluginStatus,
    PluginValidationError,
)
from flx_plugin.core.validators import PluginValidator

logger = logging.getLogger(__name__)


class LoadedPlugin:
    """Container for loaded plugin instance and metadata."""

    def __init__(
        self,
        plugin_id: str,
        instance: Plugin,
        metadata: PluginMetadata,
        config: dict[str, Any],
    ) -> None:
        """Initialize loaded plugin container.

        Args:
        ----
            plugin_id: Unique plugin identifier
            instance: Plugin instance
            metadata: Plugin metadata
            config: Plugin configuration

        """
        self.plugin_id = plugin_id
        self.instance = instance
        self.metadata = metadata
        self.config = config
        self.is_initialized = False

    async def initialize(self) -> None:
        """Initialize the plugin instance."""
        if not self.is_initialized:
            await self.instance.initialize()
            self.instance._initialized = True
            self.instance._update_lifecycle_state(PluginLifecycle.INITIALIZED)
            self.instance._update_status(PluginStatus.HEALTHY)
            self.is_initialized = True

    async def cleanup(self) -> None:
        """Cleanup the plugin instance."""
        if self.is_initialized:
            await self.instance.cleanup()
            self.instance._initialized = False
            self.instance._update_lifecycle_state(PluginLifecycle.UNLOADED)
            self.instance._update_status(PluginStatus.UNKNOWN)
            self.is_initialized = False


class PluginLoader:
    """Plugin loader with security validation and dependency resolution.

    Handles the complete plugin loading lifecycle including:
    - Security validation
    - Dependency resolution
    - Configuration validation
    - Instance creation and initialization
    """

    def __init__(
        self,
        validator: PluginValidator | None = None,
        security_enabled: bool = True,
        max_load_time: float = 30.0,
    ) -> None:
        """Initialize plugin loader.

        Args:
        ----
            validator: Plugin validator instance
            security_enabled: Whether to enforce security validation
            max_load_time: Maximum time allowed for plugin loading

        """
        self.validator = validator or PluginValidator()
        self.security_enabled = security_enabled
        self.max_load_time = max_load_time
        self._loaded_plugins: dict[str, LoadedPlugin] = {}
        self._loading_plugins: set[str] = set()

    async def load_plugin(
        self,
        discovered_plugin: DiscoveredPlugin,
        config: dict[str, Any] | None = None,
        initialize: bool = True,
    ) -> LoadedPlugin:
        """Load a discovered plugin.

        Args:
        ----
            discovered_plugin: Discovered plugin to load
            config: Plugin configuration
            initialize: Whether to initialize after loading

        Returns:
        -------
            Loaded plugin instance

        Raises:
        ------
            PluginLoadError: If loading fails
            PluginSecurityError: If security validation fails
            PluginDependencyError: If dependencies cannot be resolved

        """
        plugin_id = discovered_plugin.metadata.id

        # Check if already loading
        if plugin_id in self._loading_plugins:
            raise PluginLoadError(
                f"Plugin is already being loaded: {plugin_id}",
                plugin_id=plugin_id,
            )

        # Check if already loaded
        if plugin_id in self._loaded_plugins:
            logger.info(f"Plugin already loaded: {plugin_id}")
            return self._loaded_plugins[plugin_id]

        self._loading_plugins.add(plugin_id)

        try:
            # Load with timeout
            loaded = await asyncio.wait_for(
                self._load_plugin_internal(discovered_plugin, config, initialize),
                timeout=self.max_load_time,
            )

            self._loaded_plugins[plugin_id] = loaded
            logger.info(f"Successfully loaded plugin: {plugin_id}")
            return loaded

        except asyncio.TimeoutError:
            raise PluginLoadError(
                f"Plugin loading timed out after {self.max_load_time}s",
                plugin_id=plugin_id,
            )

        finally:
            self._loading_plugins.discard(plugin_id)

    async def _load_plugin_internal(
        self,
        discovered_plugin: DiscoveredPlugin,
        config: dict[str, Any] | None,
        initialize: bool,
    ) -> LoadedPlugin:
        """Internal plugin loading logic."""
        plugin_class = discovered_plugin.plugin_class
        metadata = discovered_plugin.metadata
        plugin_id = metadata.id

        # Merge default config with provided config
        final_config = {**metadata.default_configuration}
        if config:
            final_config.update(config)

        # Validate security if enabled
        if self.security_enabled:
            security_violations = await self.validator.validate_security(metadata)
            if security_violations:
                raise PluginSecurityError(
                    f"Plugin failed security validation: {plugin_id}",
                    plugin_id=plugin_id,
                    security_violations=security_violations,
                )

        # Validate dependencies
        missing_deps = await self._check_dependencies(metadata)
        if missing_deps:
            raise PluginDependencyError(
                f"Plugin has missing dependencies: {plugin_id}",
                plugin_id=plugin_id,
                missing_dependencies=missing_deps,
            )

        # Create plugin instance
        try:
            instance = plugin_class(config=final_config)
        except Exception as e:
            raise PluginLoadError(
                f"Failed to create plugin instance: {plugin_id}",
                plugin_id=plugin_id,
                cause=e,
            )

        # Update lifecycle state
        instance._update_lifecycle_state(PluginLifecycle.LOADED)

        # Validate configuration
        config_errors = await instance.validate_configuration(final_config)
        if config_errors:
            raise PluginValidationError(
                f"Plugin configuration validation failed: {plugin_id}",
                plugin_id=plugin_id,
                validation_failures=config_errors,
            )

        # Create loaded plugin container
        loaded = LoadedPlugin(
            plugin_id=plugin_id,
            instance=instance,
            metadata=metadata,
            config=final_config,
        )

        # Initialize if requested
        if initialize:
            try:
                await loaded.initialize()
            except Exception as e:
                raise PluginLoadError(
                    f"Plugin initialization failed: {plugin_id}",
                    plugin_id=plugin_id,
                    cause=e,
                )

        return loaded

    async def _check_dependencies(self, metadata: PluginMetadata) -> list[str]:
        """Check plugin dependencies.

        Args:
        ----
            metadata: Plugin metadata

        Returns:
        -------
            List of missing dependencies

        """
        missing_deps = []

        # Check Python package dependencies
        if metadata.dependencies:
            import importlib.util

            for dep in metadata.dependencies:
                # Extract package name from requirement string
                package_name = dep.split("==")[0].split(">=")[0].split("<=")[0].strip()

                spec = importlib.util.find_spec(package_name)
                if spec is None:
                    missing_deps.append(dep)

        # Check Meltano plugin dependencies
        if metadata.meltano_dependencies:
            # Check if required plugins are loaded
            for dep_id in metadata.meltano_dependencies:
                if dep_id not in self._loaded_plugins:
                    missing_deps.append(f"meltano:{dep_id}")

        return missing_deps

    async def unload_plugin(self, plugin_id: str) -> None:
        """Unload a plugin.

        Args:
        ----
            plugin_id: Plugin ID to unload

        Raises:
        ------
            PluginError: If plugin is not loaded

        """
        if plugin_id not in self._loaded_plugins:
            raise PluginError(
                f"Plugin not loaded: {plugin_id}",
                plugin_id=plugin_id,
                error_code="NOT_LOADED",
            )

        loaded = self._loaded_plugins[plugin_id]

        # Update lifecycle state
        loaded.instance._update_lifecycle_state(PluginLifecycle.UNLOADING)

        # Cleanup if initialized
        if loaded.is_initialized:
            try:
                await loaded.cleanup()
            except Exception as e:
                logger.error(f"Error during plugin cleanup: {plugin_id}", exc_info=e)

        # Remove from loaded plugins
        del self._loaded_plugins[plugin_id]
        logger.info(f"Unloaded plugin: {plugin_id}")

    async def reload_plugin(
        self,
        plugin_id: str,
        discovered_plugin: DiscoveredPlugin,
        config: dict[str, Any] | None = None,
    ) -> LoadedPlugin:
        """Reload a plugin.

        Args:
        ----
            plugin_id: Plugin ID to reload
            discovered_plugin: Updated discovered plugin
            config: New configuration

        Returns:
        -------
            Reloaded plugin instance

        """
        # Unload if already loaded
        if plugin_id in self._loaded_plugins:
            await self.unload_plugin(plugin_id)

        # Load with new configuration
        return await self.load_plugin(discovered_plugin, config)

    def get_loaded_plugin(self, plugin_id: str) -> LoadedPlugin | None:
        """Get a loaded plugin by ID.

        Args:
        ----
            plugin_id: Plugin ID

        Returns:
        -------
            Loaded plugin or None if not loaded

        """
        return self._loaded_plugins.get(plugin_id)

    def get_all_loaded_plugins(self) -> dict[str, LoadedPlugin]:
        """Get all loaded plugins.

        Returns
        -------
            Dictionary of loaded plugins

        """
        return self._loaded_plugins.copy()

    def is_loaded(self, plugin_id: str) -> bool:
        """Check if a plugin is loaded.

        Args:
        ----
            plugin_id: Plugin ID

        Returns:
        -------
            True if plugin is loaded

        """
        return plugin_id in self._loaded_plugins
