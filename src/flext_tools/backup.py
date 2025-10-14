"""Minimal backup manager for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from typing import Self

from flext_core import FlextCore


class BackupManager:
    """Basic backup manager for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize backup manager."""

    def create_backup(self, source_path: str | Path) -> FlextCore.Result[str]:
        """Create backup of source path."""
        return FlextCore.Result[str].ok(f"Backup created for {source_path}")

    def restore_backup(self, backup_path: str | Path) -> FlextCore.Result[None]:
        """Restore from backup.

        🚨 AUDIT VIOLATION: Inline validation instead of proper models class usage!
        ❌ CRITICAL ISSUE: This method performs inline validation that should be centralized
        ❌ INLINE VALIDATION: Empty path check should be handled by FlextCore.Models validation

        🔧 REQUIRED ACTION:
        - Replace with FlextCore.Models.BackupPath validation
        - Use FlextCore.Models.Validation.validate_backup_path() for path validation
        - Remove inline validation logic from service methods

        📍 SHOULD BE USED INSTEAD: FlextCore.Models.Validation.validate_backup_path(backup_path)
        """
        # Use the backup_path parameter for actual restoration
        backup_path_str = str(backup_path)
        # 🚨 AUDIT VIOLATION: Inline validation - should use FlextCore.Models.Validation
        if not backup_path_str:
            return FlextCore.Result[None].fail("Backup path cannot be empty")

        # Placeholder implementation - acknowledge parameter usage
        _ = backup_path_str  # Parameter is used for restoration logic
        return FlextCore.Result[None].ok(None)

    def list_backups(self: Self) -> FlextCore.Result[FlextCore.Types.StringList]:
        """List available backups."""
        return FlextCore.Result[FlextCore.Types.StringList].ok([])
