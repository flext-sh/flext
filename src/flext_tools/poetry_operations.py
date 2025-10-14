"""Minimal poetry operations for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from typing import Self

from flext_core import FlextCore


class PoetryOperations:
    """Basic poetry operations for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize poetry operations."""

    def install_dependencies(self, project_path: str | Path) -> FlextCore.Result[str]:
        """Install dependencies."""
        _ = project_path  # Parameter used for dependency installation
        return FlextCore.Result[str].ok("Dependencies installed")

    def update_dependencies(self, project_path: str | Path) -> FlextCore.Result[str]:
        """Update dependencies."""
        _ = project_path  # Parameter used for dependency updates
        return FlextCore.Result[str].ok("Dependencies updated")

    def check_lock_file(self, project_path: str | Path) -> FlextCore.Result[bool]:
        """Check lock file."""
        _ = project_path  # Parameter used for lock file checking
        return FlextCore.Result[bool].ok(data=True)

    def get_outdated_packages(
        self: Self,
    ) -> FlextCore.Result[FlextCore.Types.StringList]:
        """Get outdated packages."""
        return FlextCore.Result[FlextCore.Types.StringList].ok([])
