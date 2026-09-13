"""CLI facade for flext-workspace — thin orchestrator over flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys

from flext_cli import cli as flext_cli


class FlextRootCli:
    """Workspace root CLI facade — composes flext-cli."""

    @staticmethod
    def main(args: list[str] | None = None) -> int:
        """Main entry point for flext CLI."""
        return flext_cli.main(args)


def main() -> None:
    """Module-level CLI entry point."""
    sys.exit(FlextRootCli.main())


__all__: tuple[str, ...] = ("FlextRootCli", "main")
