"""Hot reload orchestration for enterprise plugin system.

Copyright (c) 2025 FLX Team. All rights reserved.
"""

from __future__ import annotations

import importlib
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field

from flx_plugin.core.manager import PluginManager
from flx_plugin.hot_reload.rollback import RollbackManager
from flx_plugin.hot_reload.state_manager import StateManager
from flx_plugin.hot_reload.watcher import PluginWatcher, WatchEvent, WatchEventType

logger = logging.getLogger(__name__)


class ReloadEvent(BaseModel):
    """Plugin reload event information."""

    event_type: str = Field(description="Type of reload event")
    plugin_id: str = Field(description="Plugin identifier")
    plugin_path: Path = Field(description="Plugin file path")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    success: bool = Field(default=False, description="Whether reload succeeded")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    duration_ms: Optional[float] = Field(default=None, description="Reload duration")

    class Config:
        arbitrary_types_allowed = True


class ReloadStrategy(BaseModel):
    """Configuration for reload strategy."""

    preserve_state: bool = Field(
        default=True, description="Whether to preserve plugin state"
    )
    create_rollback: bool = Field(
        default=True, description="Whether to create rollback point"
    )
    reload_dependencies: bool = Field(
        default=False, description="Whether to reload dependent plugins"
    )
    max_retries: int = Field(default=3, description="Maximum reload retry attempts")
    retry_delay_ms: int = Field(
        default=1000, description="Delay between retry attempts"
    )


class HotReloadManager:
    """Central hot reload management system.

    Orchestrates the complete hot reload process including:
    - File system monitoring
    - State preservation and restoration
    - Safe plugin reloading
    - Rollback on failure
    - Dependency management
    """

    def __init__(
        self,
        plugin_manager: PluginManager,
        watch_directories: List[Path],
        state_directory: Optional[Path] = None,
        backup_directory: Optional[Path] = None,
        strategy: Optional[ReloadStrategy] = None,
    ) -> None:
        """Initialize hot reload manager.

        Args:
        ----
            plugin_manager: Plugin manager instance
            watch_directories: Directories to watch for changes
            state_directory: Directory for state persistence
            backup_directory: Directory for plugin backups
            strategy: Reload strategy configuration

        """
        self.plugin_manager = plugin_manager
        self.watch_directories = watch_directories
        self.strategy = strategy or ReloadStrategy()

        # Initialize components
        self.state_manager = StateManager(state_directory)
        self.rollback_manager = RollbackManager(self.state_manager, backup_directory)
        self.watcher = PluginWatcher(
            watch_directories,
            patterns=["*.py"],
            ignore_patterns=["__pycache__", "*.pyc", ".git", "*_test.py"],
        )

        # Track reload state
        self._reloading: Set[str] = set()
        self._reload_history: List[ReloadEvent] = []
        self._plugin_paths: Dict[Path, str] = {}  # path -> plugin_id mapping

        # Setup watcher handler
        self.watcher.add_handler(self._handle_file_change)

    async def start(self) -> None:
        """Start hot reload monitoring."""
        logger.info("Starting hot reload manager")

        # Build initial plugin path mapping
        await self._build_plugin_path_mapping()

        # Start watching
        await self.watcher.start()

    async def stop(self) -> None:
        """Stop hot reload monitoring."""
        logger.info("Stopping hot reload manager")

        # Stop watching
        await self.watcher.stop()

    async def reload_plugin(
        self,
        plugin_id: str,
        force: bool = False,
    ) -> ReloadEvent:
        """Manually reload a plugin.

        Args:
        ----
            plugin_id: Plugin to reload
            force: Force reload even if already reloading

        Returns:
        -------
            Reload event with results

        """
        # Check if already reloading
        if plugin_id in self._reloading and not force:
            logger.warning(f"Plugin {plugin_id} already reloading")
            return ReloadEvent(
                event_type="manual_reload",
                plugin_id=plugin_id,
                plugin_path=Path("unknown"),
                success=False,
                error="Plugin already reloading",
            )

        # Find plugin path
        plugin_path = None
        for path, pid in self._plugin_paths.items():
            if pid == plugin_id:
                plugin_path = path
                break

        if not plugin_path:
            return ReloadEvent(
                event_type="manual_reload",
                plugin_id=plugin_id,
                plugin_path=Path("unknown"),
                success=False,
                error="Plugin path not found",
            )

        # Perform reload
        return await self._reload_plugin(plugin_id, plugin_path)

    async def _handle_file_change(self, event: WatchEvent) -> None:
        """Handle file system change event.

        Args:
        ----
            event: File system event

        """
        # Only handle modifications
        if event.event_type != WatchEventType.MODIFIED:
            return

        # Check if this is a plugin file
        plugin_id = self._plugin_paths.get(event.path)
        if not plugin_id:
            # Try to identify plugin from path
            plugin_id = await self._identify_plugin_from_path(event.path)
            if not plugin_id:
                return

        # Reload plugin
        logger.info(f"Detected change in plugin {plugin_id}")
        await self._reload_plugin(plugin_id, event.path)

    async def _reload_plugin(
        self,
        plugin_id: str,
        plugin_path: Path,
    ) -> ReloadEvent:
        """Perform plugin reload with all safety measures.

        Args:
        ----
            plugin_id: Plugin to reload
            plugin_path: Path to plugin file

        Returns:
        -------
            Reload event with results

        """
        import time

        start_time = time.time()

        event = ReloadEvent(
            event_type="hot_reload",
            plugin_id=plugin_id,
            plugin_path=plugin_path,
        )

        # Mark as reloading
        self._reloading.add(plugin_id)

        try:
            # Get current plugin
            current_plugin = self.plugin_manager.get_loaded_plugin(plugin_id)
            if not current_plugin:
                event.success = False
                event.error = "Plugin not currently loaded"
                return event

            logger.info(f"Starting hot reload for plugin {plugin_id}")

            # Step 1: Create rollback point if configured
            rollback_id = None
            if self.strategy.create_rollback:
                try:
                    rollback_id = await self.rollback_manager.create_rollback_point(
                        current_plugin.instance,
                        f"Before hot reload at {datetime.now(UTC)}",
                        backup_code=True,
                    )
                except Exception as e:
                    logger.error(f"Failed to create rollback point: {e}")
                    # Continue anyway

            # Step 2: Save state if configured
            if self.strategy.preserve_state:
                try:
                    await self.state_manager.save_plugin_state(
                        current_plugin.instance,
                        force=True,
                    )
                except Exception as e:
                    logger.error(f"Failed to save plugin state: {e}")
                    # Continue anyway

            # Step 3: Unload current plugin
            await self.plugin_manager.unload_plugin(plugin_id)

            # Step 4: Reload module
            module_name = self._get_module_name(plugin_path)
            if module_name in sys.modules:
                # Reload the module
                module = sys.modules[module_name]
                importlib.reload(module)
            else:
                # Import for first time
                importlib.import_module(module_name)

            # Step 5: Reload plugin
            # Find the entry point for this plugin
            discovered = self.plugin_manager.get_discovered_plugin(plugin_id)
            if not discovered:
                raise ValueError(f"Plugin {plugin_id} not in discovered plugins")

            # Load the new version
            loaded = await self.plugin_manager.load_plugin(
                plugin_id,
                config=current_plugin.config,
            )

            # Step 6: Restore state if configured
            if self.strategy.preserve_state:
                try:
                    await self.state_manager.restore_plugin_state(loaded.instance)
                except Exception as e:
                    logger.error(f"Failed to restore plugin state: {e}")
                    # Continue anyway

            # Step 7: Reload dependencies if configured
            if self.strategy.reload_dependencies:
                await self._reload_dependent_plugins(plugin_id)

            # Success!
            event.success = True
            logger.info(f"Successfully reloaded plugin {plugin_id}")

        except Exception as e:
            logger.error(
                f"Failed to reload plugin {plugin_id}: {e}",
                exc_info=True,
            )
            event.success = False
            event.error = str(e)

            # Attempt rollback if we have a rollback point
            if rollback_id and self.strategy.create_rollback:
                try:
                    logger.info(f"Attempting rollback for plugin {plugin_id}")
                    await self.rollback_manager.rollback_plugin(
                        plugin_id,
                        rollback_id,
                    )
                except Exception as rollback_error:
                    logger.error(
                        f"Rollback failed for plugin {plugin_id}: {rollback_error}",
                        exc_info=True,
                    )

        finally:
            # Remove from reloading set
            self._reloading.discard(plugin_id)

            # Calculate duration
            event.duration_ms = (time.time() - start_time) * 1000

            # Add to history
            self._reload_history.append(event)

        return event

    async def _build_plugin_path_mapping(self) -> None:
        """Build mapping of file paths to plugin IDs."""
        # Get all loaded plugins
        for (
            plugin_id,
            loaded,
        ) in self.plugin_manager.loader.get_loaded_plugins().items():
            try:
                import inspect

                module = inspect.getmodule(loaded.instance.__class__)
                if module and hasattr(module, "__file__"):
                    path = Path(module.__file__)
                    self._plugin_paths[path] = plugin_id

            except Exception as e:
                logger.error(f"Error mapping path for plugin {plugin_id}: {e}")

    async def _identify_plugin_from_path(self, path: Path) -> Optional[str]:
        """Try to identify plugin from file path.

        Args:
        ----
            path: File path

        Returns:
        -------
            Plugin ID or None

        """
        # This is a simplified implementation
        # In reality, would need more sophisticated plugin identification

        # Check if file contains a plugin class
        try:
            with open(path) as f:
                content = f.read()

            # Look for plugin class definition
            if "class" in content and (
                "Plugin" in content or "plugin" in content.lower()
            ):
                # Extract module name from path
                module_name = self._get_module_name(path)

                # Try to match with discovered plugins
                for (
                    plugin_id,
                    discovered,
                ) in self.plugin_manager._discovered_plugins.items():
                    if discovered.module_name == module_name:
                        self._plugin_paths[path] = plugin_id
                        return plugin_id

        except Exception as e:
            logger.error(f"Error identifying plugin from {path}: {e}")

        return None

    def _get_module_name(self, path: Path) -> str:
        """Get module name from file path.

        Args:
        ----
            path: File path

        Returns:
        -------
            Module name

        """
        # Find the module name relative to Python path
        # This is simplified - in reality would need proper module resolution

        # Remove .py extension
        if path.suffix == ".py":
            path = path.with_suffix("")

        # Convert path to module name
        parts = path.parts

        # Find where the module starts (look for __init__.py in parents)
        module_parts = []
        for i in range(len(parts)):
            parent = Path(*parts[: i + 1])
            if (parent / "__init__.py").exists():
                module_parts = parts[i:]
                break

        if not module_parts:
            module_parts = parts

        return ".".join(module_parts)

    async def _reload_dependent_plugins(self, plugin_id: str) -> None:
        """Reload plugins that depend on the given plugin.

        Args:
        ----
            plugin_id: Plugin that was reloaded

        """
        # This would need to track plugin dependencies
        # For now, just log
        logger.info(f"Would reload dependent plugins for {plugin_id}")

    def get_reload_history(
        self,
        plugin_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[ReloadEvent]:
        """Get reload history.

        Args:
        ----
            plugin_id: Filter by plugin ID
            limit: Maximum events to return

        Returns:
        -------
            List of reload events

        """
        events = self._reload_history

        if plugin_id:
            events = [e for e in events if e.plugin_id == plugin_id]

        return events[-limit:]

    def is_reloading(self, plugin_id: str) -> bool:
        """Check if plugin is currently reloading.

        Args:
        ----
            plugin_id: Plugin to check

        Returns:
        -------
            True if plugin is reloading

        """
        return plugin_id in self._reloading
