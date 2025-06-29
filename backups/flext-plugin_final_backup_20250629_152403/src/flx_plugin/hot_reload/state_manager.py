"""Plugin state management for hot reload functionality.

Copyright (c) 2025 FLX Team. All rights reserved.
"""

from __future__ import annotations

import json
import logging
import pickle
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from flx_plugin.core.base import Plugin

logger = logging.getLogger(__name__)


class PluginState(BaseModel):
    """Represents the state of a plugin instance."""

    plugin_id: str = Field(description="Plugin identifier")
    plugin_version: str = Field(description="Plugin version")
    state_data: Dict[str, Any] = Field(
        default_factory=dict, description="Plugin state data"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="State metadata")
    saved_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="When state was saved"
    )

    class Config:
        arbitrary_types_allowed = True


class StateSnapshot(BaseModel):
    """Complete state snapshot for rollback."""

    snapshot_id: str = Field(description="Unique snapshot identifier")
    plugin_states: Dict[str, PluginState] = Field(
        default_factory=dict, description="States by plugin ID"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When snapshot was created",
    )
    description: str = Field(default="", description="Snapshot description")


class StateManager:
    """Manages plugin state for hot reload operations.

    Handles state extraction, preservation, and restoration
    during plugin reload operations.
    """

    def __init__(
        self,
        state_directory: Optional[Path] = None,
        enable_persistence: bool = True,
    ) -> None:
        """Initialize state manager.

        Args:
        ----
            state_directory: Directory for state persistence
            enable_persistence: Whether to persist state to disk

        """
        self.state_directory = state_directory or Path.cwd() / ".plugin_states"
        self.enable_persistence = enable_persistence

        if self.enable_persistence and not self.state_directory.exists():
            self.state_directory.mkdir(parents=True, exist_ok=True)

        self._plugin_states: Dict[str, PluginState] = {}
        self._snapshots: Dict[str, StateSnapshot] = {}

    async def save_plugin_state(
        self,
        plugin: Plugin,
        force: bool = False,
    ) -> PluginState:
        """Save plugin state.

        Args:
        ----
            plugin: Plugin instance
            force: Force save even if plugin doesn't support state

        Returns:
        -------
            Saved plugin state

        Raises:
        ------
            ValueError: If plugin doesn't support state and force=False

        """
        plugin_id = plugin.metadata.id

        # Check if plugin supports state preservation
        if not hasattr(plugin, "get_state") and not force:
            raise ValueError(f"Plugin {plugin_id} does not support state preservation")

        # Extract state
        state_data = {}
        if hasattr(plugin, "get_state"):
            try:
                state_data = await plugin.get_state()
            except Exception as e:
                logger.error(
                    f"Error extracting state from plugin {plugin_id}: {e}",
                    exc_info=True,
                )
                if not force:
                    raise

        # Create state object
        state = PluginState(
            plugin_id=plugin_id,
            plugin_version=plugin.metadata.version,
            state_data=state_data,
            metadata={
                "plugin_type": plugin.metadata.plugin_type.value,
                "capabilities": plugin.metadata.capabilities,
            },
        )

        # Store in memory
        self._plugin_states[plugin_id] = state

        # Persist if enabled
        if self.enable_persistence:
            await self._persist_state(plugin_id, state)

        logger.info(
            f"Saved state for plugin {plugin_id}",
            state_size=len(str(state_data)),
        )

        return state

    async def restore_plugin_state(
        self,
        plugin: Plugin,
        state: Optional[PluginState] = None,
    ) -> bool:
        """Restore plugin state.

        Args:
        ----
            plugin: Plugin instance
            state: State to restore (uses saved state if None)

        Returns:
        -------
            True if state was restored successfully

        """
        plugin_id = plugin.metadata.id

        # Get state to restore
        if state is None:
            state = self._plugin_states.get(plugin_id)
            if state is None and self.enable_persistence:
                state = await self._load_state(plugin_id)

        if state is None:
            logger.warning(f"No saved state found for plugin {plugin_id}")
            return False

        # Check if plugin supports state restoration
        if not hasattr(plugin, "set_state"):
            logger.warning(f"Plugin {plugin_id} does not support state restoration")
            return False

        # Restore state
        try:
            await plugin.set_state(state.state_data)
            logger.info(
                f"Restored state for plugin {plugin_id}",
                state_version=state.plugin_version,
            )
            return True

        except Exception as e:
            logger.error(
                f"Error restoring state for plugin {plugin_id}: {e}",
                exc_info=True,
            )
            return False

    async def create_snapshot(
        self,
        description: str = "",
        plugin_ids: Optional[List[str]] = None,
    ) -> str:
        """Create a state snapshot.

        Args:
        ----
            description: Snapshot description
            plugin_ids: Specific plugins to snapshot (all if None)

        Returns:
        -------
            Snapshot ID

        """
        import uuid

        snapshot_id = str(uuid.uuid4())

        # Determine which states to include
        states_to_snapshot = {}
        if plugin_ids:
            for plugin_id in plugin_ids:
                if plugin_id in self._plugin_states:
                    states_to_snapshot[plugin_id] = self._plugin_states[plugin_id]
        else:
            states_to_snapshot = self._plugin_states.copy()

        # Create snapshot
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            plugin_states=states_to_snapshot,
            description=description,
        )

        self._snapshots[snapshot_id] = snapshot

        # Persist if enabled
        if self.enable_persistence:
            await self._persist_snapshot(snapshot)

        logger.info(
            f"Created snapshot {snapshot_id}",
            plugin_count=len(states_to_snapshot),
            description=description,
        )

        return snapshot_id

    async def restore_snapshot(
        self,
        snapshot_id: str,
        plugins: Optional[Dict[str, Plugin]] = None,
    ) -> Dict[str, bool]:
        """Restore from snapshot.

        Args:
        ----
            snapshot_id: Snapshot to restore
            plugins: Plugin instances to restore to

        Returns:
        -------
            Dict of plugin_id -> success status

        """
        snapshot = self._snapshots.get(snapshot_id)
        if snapshot is None and self.enable_persistence:
            snapshot = await self._load_snapshot(snapshot_id)

        if snapshot is None:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        results = {}

        for plugin_id, state in snapshot.plugin_states.items():
            if plugins and plugin_id in plugins:
                plugin = plugins[plugin_id]
                success = await self.restore_plugin_state(plugin, state)
                results[plugin_id] = success
            else:
                # Just restore to memory
                self._plugin_states[plugin_id] = state
                results[plugin_id] = True

        logger.info(
            f"Restored snapshot {snapshot_id}",
            restored_count=sum(results.values()),
            total_count=len(results),
        )

        return results

    async def _persist_state(self, plugin_id: str, state: PluginState) -> None:
        """Persist state to disk.

        Args:
        ----
            plugin_id: Plugin identifier
            state: State to persist

        """
        state_file = self.state_directory / f"{plugin_id}.state.json"

        try:
            # Convert to JSON-serializable format
            state_dict = state.model_dump(mode="json")

            # Write to file
            with open(state_file, "w") as f:
                json.dump(state_dict, f, indent=2, default=str)

        except Exception as e:
            logger.error(
                f"Error persisting state for {plugin_id}: {e}",
                exc_info=True,
            )

    async def _load_state(self, plugin_id: str) -> Optional[PluginState]:
        """Load state from disk.

        Args:
        ----
            plugin_id: Plugin identifier

        Returns:
        -------
            Loaded state or None

        """
        state_file = self.state_directory / f"{plugin_id}.state.json"

        if not state_file.exists():
            return None

        try:
            with open(state_file) as f:
                state_dict = json.load(f)

            # Convert saved_at back to datetime
            if "saved_at" in state_dict:
                state_dict["saved_at"] = datetime.fromisoformat(
                    state_dict["saved_at"].replace("Z", "+00:00")
                )

            return PluginState(**state_dict)

        except Exception as e:
            logger.error(
                f"Error loading state for {plugin_id}: {e}",
                exc_info=True,
            )
            return None

    async def _persist_snapshot(self, snapshot: StateSnapshot) -> None:
        """Persist snapshot to disk.

        Args:
        ----
            snapshot: Snapshot to persist

        """
        snapshot_file = self.state_directory / f"snapshot_{snapshot.snapshot_id}.pkl"

        try:
            with open(snapshot_file, "wb") as f:
                pickle.dump(snapshot, f)

        except Exception as e:
            logger.error(
                f"Error persisting snapshot {snapshot.snapshot_id}: {e}",
                exc_info=True,
            )

    async def _load_snapshot(self, snapshot_id: str) -> Optional[StateSnapshot]:
        """Load snapshot from disk.

        Args:
        ----
            snapshot_id: Snapshot identifier

        Returns:
        -------
            Loaded snapshot or None

        """
        snapshot_file = self.state_directory / f"snapshot_{snapshot_id}.pkl"

        if not snapshot_file.exists():
            return None

        try:
            with open(snapshot_file, "rb") as f:
                return pickle.load(f)

        except Exception as e:
            logger.error(
                f"Error loading snapshot {snapshot_id}: {e}",
                exc_info=True,
            )
            return None

    def clear_state(self, plugin_id: str) -> None:
        """Clear saved state for a plugin.

        Args:
        ----
            plugin_id: Plugin identifier

        """
        if plugin_id in self._plugin_states:
            del self._plugin_states[plugin_id]

        if self.enable_persistence:
            state_file = self.state_directory / f"{plugin_id}.state.json"
            if state_file.exists():
                state_file.unlink()

        logger.info(f"Cleared state for plugin {plugin_id}")

    def get_plugin_state(self, plugin_id: str) -> Optional[PluginState]:
        """Get saved state for a plugin.

        Args:
        ----
            plugin_id: Plugin identifier

        Returns:
        -------
            Plugin state or None

        """
        return self._plugin_states.get(plugin_id)

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List available snapshots.

        Returns
        -------
            List of snapshot summaries

        """
        snapshots = []

        for snapshot in self._snapshots.values():
            snapshots.append(
                {
                    "snapshot_id": snapshot.snapshot_id,
                    "created_at": snapshot.created_at,
                    "description": snapshot.description,
                    "plugin_count": len(snapshot.plugin_states),
                }
            )

        return snapshots
