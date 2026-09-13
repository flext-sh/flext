"""Workspace CLI entry point.

This module provides the entry point for the flext-workspace command.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import cli


class FlextRootWorkspace:
    """Workspace orchestration command entry point."""

    @staticmethod
    def main() -> None:
        """Entry point for flext-workspace."""
        _ = cli.execute()


if __name__ == "__main__":
    FlextRootWorkspace.main()

