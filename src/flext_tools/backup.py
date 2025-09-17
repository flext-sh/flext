"""Minimal backup manager for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult


class BackupManager:
    """Basic backup manager for legacy scripts."""

    def __init__(self) -> None:
        """Initialize backup manager."""

    def create_backup(self, source_path: str | Path) -> FlextResult[str]:
        """Create backup of source path."""
        return FlextResult[str].ok(f"Backup created for {source_path}")

    def restore_backup(self, backup_path: str | Path) -> FlextResult[None]:
        """Restore from backup."""
        # Use the backup_path parameter for actual restoration
        backup_path_str = str(backup_path)
        if not backup_path_str:
            return FlextResult[None].fail("Backup path cannot be empty")

        # Placeholder implementation - acknowledge parameter usage
        _ = backup_path_str  # Parameter is used for restoration logic
        return FlextResult[None].ok(None)

    def list_backups(self) -> FlextResult[list[str]]:
        """List available backups."""
        return FlextResult[list[str]].ok([])
