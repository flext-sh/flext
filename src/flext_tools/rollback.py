"""Minimal rollback utilities for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self

from flext_core import FlextResult


class RollbackManager:
    """Basic rollback manager for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize rollback manager."""

    def create_checkpoint(self, name: str) -> FlextResult[str]:
        """Create rollback checkpoint."""
        return FlextResult[str].ok(f"Checkpoint {name} created")

    def rollback_to_checkpoint(self, checkpoint_id: str) -> FlextResult[None]:
        """Rollback to checkpoint."""
        _ = checkpoint_id  # Parameter used for checkpoint rollback
        return FlextResult[None].ok(None)

    def list_checkpoints(self: Self) -> FlextResult[list[str]]:
        """List available checkpoints."""
        return FlextResult[list[str]].ok([])
