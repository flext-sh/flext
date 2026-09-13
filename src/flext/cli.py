"""CLI facade for flext-workspace — thin orchestrator over flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import cli as flext_cli


class FlextRootCli:
    """Workspace root CLI facade — composes flext-cli."""

    @staticmethod
    def main() -> None:
        """Entry point for flext CLI."""
        _ = flext_cli.execute()


if __name__ == "__main__":
    FlextRootCli.main()


__all__: tuple[str, ...] = ("FlextRootCli", "main")
