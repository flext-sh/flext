"""Plugin discovery system using entry points and file system scanning.

Copyright (c) 2025 FLX Team. All rights reserved.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import inspect
import logging
import os
from pathlib import Path
from typing import Any

from flx_plugin.core.base import Plugin, PluginMetadata
from flx_plugin.core.types import PluginError, PluginType

logger = logging.getLogger(__name__)


class DiscoveredPlugin:
    """Container for discovered plugin information."""

    def __init__(
        self,
        metadata: PluginMetadata,
        plugin_class: type[Plugin],
        source: str,
        entry_point_name: str | None = None,
    ) -> None:
        """Initialize discovered plugin.

        Args:
        ----
            metadata: Plugin metadata
            plugin_class: Plugin class reference
            source: Discovery source (entry_point, file, package)
            entry_point_name: Entry point name if discovered via entry points

        """
        self.metadata = metadata
        self.plugin_class = plugin_class
        self.source = source
        self.entry_point_name = entry_point_name

    def __repr__(self) -> str:
        """String representation."""
        return f"DiscoveredPlugin({self.metadata.id}, source={self.source})"


class PluginDiscovery:
    """Plugin discovery system for finding and registering plugins.

    Discovers plugins through multiple mechanisms:
    - Python entry points (for installed packages)
    - File system scanning (for local plugins)
    - Direct registration (for programmatic use)
    """

    def __init__(
        self,
        plugin_directories: list[Path] | None = None,
        entry_point_groups: list[str] | None = None,
    ) -> None:
        """Initialize plugin discovery.

        Args:
        ----
            plugin_directories: Directories to scan for plugins
            entry_point_groups: Entry point groups to scan

        """
        self.plugin_directories = plugin_directories or []
        self.entry_point_groups = entry_point_groups or [
            "flx.plugins",
            "flx.extractors",
            "flx.loaders",
            "flx.transformers",
        ]
        self._discovered_plugins: dict[str, DiscoveredPlugin] = {}
        self._blacklisted_plugins: set[str] = set()

    def add_plugin_directory(self, directory: Path) -> None:
        """Add a directory to scan for plugins."""
        if directory not in self.plugin_directories:
            self.plugin_directories.append(directory)

    def blacklist_plugin(self, plugin_id: str) -> None:
        """Blacklist a plugin to prevent discovery."""
        self._blacklisted_plugins.add(plugin_id)

    def is_blacklisted(self, plugin_id: str) -> bool:
        """Check if a plugin is blacklisted."""
        return plugin_id in self._blacklisted_plugins

    async def discover_all(self) -> dict[str, DiscoveredPlugin]:
        """Discover all available plugins.

        Returns
        -------
            Dictionary mapping plugin IDs to discovered plugins

        """
        # Clear previous discoveries
        self._discovered_plugins.clear()

        # Discover from entry points
        await self._discover_entry_points()

        # Discover from file system
        await self._discover_file_system()

        # Filter out blacklisted plugins
        filtered = {
            plugin_id: plugin
            for plugin_id, plugin in self._discovered_plugins.items()
            if not self.is_blacklisted(plugin_id)
        }

        logger.info(f"Discovered {len(filtered)} plugins")
        return filtered

    async def discover_by_type(
        self, plugin_type: PluginType
    ) -> dict[str, DiscoveredPlugin]:
        """Discover plugins of a specific type.

        Args:
        ----
            plugin_type: Type of plugins to discover

        Returns:
        -------
            Dictionary mapping plugin IDs to discovered plugins

        """
        all_plugins = await self.discover_all()
        return {
            plugin_id: plugin
            for plugin_id, plugin in all_plugins.items()
            if plugin.metadata.plugin_type == plugin_type
        }

    async def _discover_entry_points(self) -> None:
        """Discover plugins from Python entry points."""
        for group in self.entry_point_groups:
            try:
                entry_points = importlib.metadata.entry_points(group=group)

                for ep in entry_points:
                    try:
                        plugin_class = ep.load()

                        if self._validate_plugin_class(plugin_class):
                            metadata = plugin_class.METADATA

                            if metadata.id not in self._discovered_plugins:
                                discovered = DiscoveredPlugin(
                                    metadata=metadata,
                                    plugin_class=plugin_class,
                                    source="entry_point",
                                    entry_point_name=ep.name,
                                )
                                self._discovered_plugins[metadata.id] = discovered
                                logger.debug(
                                    f"Discovered plugin via entry point: {metadata.id}"
                                )

                    except Exception as e:
                        logger.warning(f"Failed to load entry point {ep.name}: {e}")

            except Exception as e:
                logger.warning(f"Failed to scan entry point group {group}: {e}")

    async def _discover_file_system(self) -> None:
        """Discover plugins from file system."""
        for directory in self.plugin_directories:
            if not directory.exists():
                logger.warning(f"Plugin directory does not exist: {directory}")
                continue

            await self._scan_directory(directory)

    async def _scan_directory(self, directory: Path) -> None:
        """Scan a directory for plugins."""
        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                # Convert file path to module name
                relative_path = py_file.relative_to(directory.parent)
                module_name = str(relative_path).replace(os.sep, ".")[:-3]

                # Import module
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Find plugin classes in module
                    for _name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, Plugin)
                            and obj is not Plugin
                            and self._validate_plugin_class(obj)
                        ):
                            metadata = obj.METADATA

                            if metadata.id not in self._discovered_plugins:
                                discovered = DiscoveredPlugin(
                                    metadata=metadata,
                                    plugin_class=obj,
                                    source="file",
                                )
                                self._discovered_plugins[metadata.id] = discovered
                                logger.debug(
                                    f"Discovered plugin from file: {metadata.id}"
                                )

            except Exception as e:
                logger.warning(f"Failed to scan file {py_file}: {e}")

    def _validate_plugin_class(self, plugin_class: type[Any]) -> bool:
        """Validate that a class is a valid plugin.

        Args:
        ----
            plugin_class: Class to validate

        Returns:
        -------
            True if valid plugin class

        """
        try:
            # Check if it's a Plugin subclass
            if not issubclass(plugin_class, Plugin):
                return False

            # Check if it has metadata
            if not hasattr(plugin_class, "METADATA"):
                logger.warning(f"Plugin class {plugin_class.__name__} missing METADATA")
                return False

            # Check if metadata is valid
            metadata = plugin_class.METADATA
            if not isinstance(metadata, PluginMetadata):
                logger.warning(
                    f"Plugin class {plugin_class.__name__} has invalid METADATA"
                )
                return False

            # Check required methods
            required_methods = ["initialize", "cleanup", "health_check", "execute"]
            for method in required_methods:
                if not hasattr(plugin_class, method):
                    logger.warning(
                        f"Plugin class {plugin_class.__name__} missing method: {method}"
                    )
                    return False

            return True

        except Exception as e:
            logger.warning(f"Failed to validate plugin class {plugin_class}: {e}")
            return False

    def register_plugin(
        self,
        plugin_class: type[Plugin],
        override: bool = False,
    ) -> None:
        """Manually register a plugin.

        Args:
        ----
            plugin_class: Plugin class to register
            override: Whether to override existing plugin

        Raises:
        ------
            PluginError: If plugin is invalid or already registered

        """
        if not self._validate_plugin_class(plugin_class):
            raise PluginError(
                f"Invalid plugin class: {plugin_class.__name__}",
                error_code="INVALID_PLUGIN",
            )

        metadata = plugin_class.METADATA

        if metadata.id in self._discovered_plugins and not override:
            raise PluginError(
                f"Plugin already registered: {metadata.id}",
                plugin_id=metadata.id,
                error_code="DUPLICATE_PLUGIN",
            )

        discovered = DiscoveredPlugin(
            metadata=metadata,
            plugin_class=plugin_class,
            source="manual",
        )
        self._discovered_plugins[metadata.id] = discovered
        logger.info(f"Manually registered plugin: {metadata.id}")

    def get_discovered_plugin(self, plugin_id: str) -> DiscoveredPlugin | None:
        """Get a discovered plugin by ID.

        Args:
        ----
            plugin_id: Plugin ID

        Returns:
        -------
            Discovered plugin or None if not found

        """
        return self._discovered_plugins.get(plugin_id)
