"""CLI facade for flext-workspace — thin orchestrator over flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import cli

if TYPE_CHECKING:
    from . import t


class FlextRootCli:
    """Workspace root CLI facade — composes flext-cli."""

    @staticmethod
    def main() -> None:
        """Entry point for flext CLI."""
        _ = cli.execute()


def main() -> None:
    """Module-level CLI entry point."""
    FlextRootCli.main()


if __name__ == "__main__":
    main()


__all__: t.VariadicTuple[str] = ("FlextRootCli", "main")
