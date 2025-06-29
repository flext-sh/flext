"""Rollback management for plugin hot reload functionality.

Copyright (c) 2025 FLX Team. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from flx_plugin.core.base import Plugin
from flx_plugin.hot_reload.state_manager import StateManager

logger = logging.getLogger(__name__)


class RollbackPoint(BaseModel):
    """Represents a rollback point in plugin history."""

    rollback_id: str = Field(description="Unique rollback point identifier")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When rollback point was created",
    )
    description: str = Field(description="Rollback point description")
    plugin_id: str = Field(description="Plugin identifier")
    plugin_version: str = Field(description="Plugin version at rollback point")
    state_snapshot_id: str = Field(description="Associated state snapshot ID")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class RollbackHistory(BaseModel):
    """Rollback history for a plugin."""

    plugin_id: str = Field(description="Plugin identifier")
    rollback_points: List[RollbackPoint] = Field(
        default_factory=list, description="List of rollback points"
    )
    max_history_size: int = Field(
        default=10, description="Maximum number of rollback points to keep"
    )

    def add_rollback_point(self, point: RollbackPoint) -> None:
        """Add a rollback point to history.

        Args:
        ----
            point: Rollback point to add

        """
        self.rollback_points.append(point)

        # Trim history if needed
        if len(self.rollback_points) > self.max_history_size:
            # Remove oldest points
            self.rollback_points = self.rollback_points[-self.max_history_size :]

    def get_latest_point(self) -> Optional[RollbackPoint]:
        """Get the most recent rollback point.

        Returns
        -------
            Latest rollback point or None

        """
        if not self.rollback_points:
            return None
        return self.rollback_points[-1]

    def get_point_by_id(self, rollback_id: str) -> Optional[RollbackPoint]:
        """Get rollback point by ID.

        Args:
        ----
            rollback_id: Rollback point identifier

        Returns:
        -------
            Rollback point or None

        """
        for point in self.rollback_points:
            if point.rollback_id == rollback_id:
                return point
        return None


class RollbackManager:
    """Manages rollback operations for plugin hot reload.

    Provides rollback capabilities to recover from failed
    reload operations or unwanted plugin updates.
    """

    def __init__(
        self,
        state_manager: StateManager,
        backup_directory: Optional[Path] = None,
    ) -> None:
        """Initialize rollback manager.

        Args:
        ----
            state_manager: State manager for snapshots
            backup_directory: Directory for plugin backups

        """
        self.state_manager = state_manager
        self.backup_directory = backup_directory or Path.cwd() / ".plugin_backups"

        if not self.backup_directory.exists():
            self.backup_directory.mkdir(parents=True, exist_ok=True)

        self._histories: Dict[str, RollbackHistory] = {}
        self._plugin_backups: Dict[str, Dict[str, Path]] = {}

    async def create_rollback_point(
        self,
        plugin: Plugin,
        description: str,
        backup_code: bool = True,
    ) -> str:
        """Create a rollback point for a plugin.

        Args:
        ----
            plugin: Plugin instance
            description: Rollback point description
            backup_code: Whether to backup plugin code

        Returns:
        -------
            Rollback point ID

        """
        import uuid

        plugin_id = plugin.metadata.id
        rollback_id = str(uuid.uuid4())

        # Create state snapshot
        snapshot_id = await self.state_manager.create_snapshot(
            description=f"Rollback point: {description}",
            plugin_ids=[plugin_id],
        )

        # Backup plugin code if requested
        if backup_code:
            backup_path = await self._backup_plugin_code(plugin, rollback_id)
            if plugin_id not in self._plugin_backups:
                self._plugin_backups[plugin_id] = {}
            self._plugin_backups[plugin_id][rollback_id] = backup_path

        # Create rollback point
        point = RollbackPoint(
            rollback_id=rollback_id,
            description=description,
            plugin_id=plugin_id,
            plugin_version=plugin.metadata.version,
            state_snapshot_id=snapshot_id,
            metadata={
                "code_backed_up": backup_code,
            },
        )

        # Add to history
        if plugin_id not in self._histories:
            self._histories[plugin_id] = RollbackHistory(plugin_id=plugin_id)

        self._histories[plugin_id].add_rollback_point(point)

        logger.info(
            f"Created rollback point for plugin {plugin_id}",
            rollback_id=rollback_id,
            description=description,
        )

        return rollback_id

    async def rollback_plugin(
        self,
        plugin_id: str,
        rollback_id: Optional[str] = None,
        restore_code: bool = True,
    ) -> Dict[str, Any]:
        """Rollback a plugin to a previous state.

        Args:
        ----
            plugin_id: Plugin identifier
            rollback_id: Specific rollback point (latest if None)
            restore_code: Whether to restore plugin code

        Returns:
        -------
            Rollback result information

        """
        # Get rollback history
        history = self._histories.get(plugin_id)
        if not history:
            raise ValueError(f"No rollback history for plugin {plugin_id}")

        # Get rollback point
        if rollback_id:
            point = history.get_point_by_id(rollback_id)
        else:
            point = history.get_latest_point()

        if not point:
            raise ValueError(f"Rollback point not found: {rollback_id}")

        result = {
            "rollback_id": point.rollback_id,
            "plugin_id": plugin_id,
            "from_version": "unknown",
            "to_version": point.plugin_version,
            "state_restored": False,
            "code_restored": False,
            "errors": [],
        }

        # Restore state
        try:
            restore_results = await self.state_manager.restore_snapshot(
                point.state_snapshot_id
            )
            result["state_restored"] = restore_results.get(plugin_id, False)
        except Exception as e:
            logger.error(
                f"Error restoring state for plugin {plugin_id}: {e}",
                exc_info=True,
            )
            result["errors"].append(f"State restoration failed: {str(e)}")

        # Restore code if requested
        if restore_code and point.metadata.get("code_backed_up"):
            try:
                await self._restore_plugin_code(plugin_id, point.rollback_id)
                result["code_restored"] = True
            except Exception as e:
                logger.error(
                    f"Error restoring code for plugin {plugin_id}: {e}",
                    exc_info=True,
                )
                result["errors"].append(f"Code restoration failed: {str(e)}")

        logger.info(
            f"Rolled back plugin {plugin_id}",
            rollback_id=point.rollback_id,
            state_restored=result["state_restored"],
            code_restored=result["code_restored"],
        )

        return result

    async def _backup_plugin_code(
        self,
        plugin: Plugin,
        rollback_id: str,
    ) -> Path:
        """Backup plugin code.

        Args:
        ----
            plugin: Plugin instance
            rollback_id: Rollback point identifier

        Returns:
        -------
            Path to backup

        """
        import inspect
        import shutil

        plugin_module = inspect.getmodule(plugin.__class__)
        if not plugin_module or not hasattr(plugin_module, "__file__"):
            raise ValueError("Cannot determine plugin module file")

        source_file = Path(plugin_module.__file__)
        if not source_file.exists():
            raise ValueError(f"Plugin source file not found: {source_file}")

        # Create backup directory
        plugin_backup_dir = self.backup_directory / plugin.metadata.id
        plugin_backup_dir.mkdir(exist_ok=True)

        # Backup file
        backup_file = plugin_backup_dir / f"{rollback_id}_{source_file.name}"
        shutil.copy2(source_file, backup_file)

        logger.debug(
            "Backed up plugin code",
            plugin_id=plugin.metadata.id,
            source=str(source_file),
            backup=str(backup_file),
        )

        return backup_file

    async def _restore_plugin_code(
        self,
        plugin_id: str,
        rollback_id: str,
    ) -> None:
        """Restore plugin code from backup.

        Args:
        ----
            plugin_id: Plugin identifier
            rollback_id: Rollback point identifier

        """
        import shutil

        # Get backup path
        if (
            plugin_id not in self._plugin_backups
            or rollback_id not in self._plugin_backups[plugin_id]
        ):
            raise ValueError(f"No code backup found for rollback {rollback_id}")

        backup_file = self._plugin_backups[plugin_id][rollback_id]
        if not backup_file.exists():
            raise ValueError(f"Backup file not found: {backup_file}")

        # Determine target path
        # This is simplified - in reality would need to track original location
        target_file = backup_file.parent.parent / backup_file.name.split("_", 1)[1]

        # Restore file
        shutil.copy2(backup_file, target_file)

        logger.debug(
            "Restored plugin code",
            plugin_id=plugin_id,
            backup=str(backup_file),
            target=str(target_file),
        )

    def get_rollback_history(
        self,
        plugin_id: str,
    ) -> Optional[RollbackHistory]:
        """Get rollback history for a plugin.

        Args:
        ----
            plugin_id: Plugin identifier

        Returns:
        -------
            Rollback history or None

        """
        return self._histories.get(plugin_id)

    def list_rollback_points(
        self,
        plugin_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List available rollback points.

        Args:
        ----
            plugin_id: Filter by plugin ID (all if None)

        Returns:
        -------
            List of rollback point summaries

        """
        points = []

        for pid, history in self._histories.items():
            if plugin_id and pid != plugin_id:
                continue

            for point in history.rollback_points:
                points.append(
                    {
                        "rollback_id": point.rollback_id,
                        "plugin_id": point.plugin_id,
                        "created_at": point.created_at,
                        "description": point.description,
                        "version": point.plugin_version,
                        "has_code_backup": point.metadata.get("code_backed_up", False),
                    }
                )

        return points

    def cleanup_old_backups(
        self,
        days_to_keep: int = 30,
    ) -> int:
        """Clean up old backup files.

        Args:
        ----
            days_to_keep: Number of days to keep backups

        Returns:
        -------
            Number of files deleted

        """
        import time

        deleted_count = 0
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)

        for backup_file in self.backup_directory.rglob("*"):
            if backup_file.is_file():
                if backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    deleted_count += 1

        logger.info(
            f"Cleaned up {deleted_count} old backup files",
            days_to_keep=days_to_keep,
        )

        return deleted_count
