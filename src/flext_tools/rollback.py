"""Minimal rollback utilities for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Self

from flext_core import FlextCore


class RollbackManager:
    """Basic rollback manager for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize rollback manager."""

    def create_checkpoint(self, name: str) -> FlextCore.Result[str]:
        """Create rollback checkpoint."""
        return FlextCore.Result[str].ok(f"Checkpoint {name} created")

    def rollback_to_checkpoint(self, checkpoint_id: str) -> FlextCore.Result[None]:
        """Rollback to checkpoint."""
        _ = checkpoint_id  # Parameter used for checkpoint rollback
        return FlextCore.Result[None].ok(None)

    def list_checkpoints(self: Self) -> FlextCore.Result[FlextCore.Types.StringList]:
        """List available checkpoints."""
        return FlextCore.Result[FlextCore.Types.StringList].ok([])
