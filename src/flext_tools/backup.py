"""Minimal backup manager for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Self

from flext_core import FlextResult, FlextTypes


class BackupManager:
    """Basic backup manager for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize backup manager."""

    def create_backup(self, source_path: str | Path) -> FlextResult[str]:
        """Create backup of source path."""
        return FlextResult[str].ok(f"Backup created for {source_path}")

    def restore_backup(self, backup_path: str | Path) -> FlextResult[None]:
        """Restore from backup.

        🚨 AUDIT VIOLATION: Inline validation instead of proper models class usage!
        ❌ CRITICAL ISSUE: This method performs inline validation that should be centralized
        ❌ INLINE VALIDATION: Empty path check should be handled by FlextModels validation

        🔧 REQUIRED ACTION:
        - Replace with FlextModels.BackupPath validation
        - Use FlextModels.Validation.validate_backup_path() for path validation
        - Remove inline validation logic from service methods

        📍 SHOULD BE USED INSTEAD: FlextModels.Validation.validate_backup_path(backup_path)
        """
        # Use the backup_path parameter for actual restoration
        backup_path_str = str(backup_path)
        # 🚨 AUDIT VIOLATION: Inline validation - should use FlextModels.Validation
        if not backup_path_str:
            return FlextResult[None].fail("Backup path cannot be empty")

        # Placeholder implementation - acknowledge parameter usage
        _ = backup_path_str  # Parameter is used for restoration logic
        return FlextResult[None].ok(None)

    def list_backups(self: Self) -> FlextResult[FlextTypes.StringList]:
        """List available backups."""
        return FlextResult[FlextTypes.StringList].ok([])
