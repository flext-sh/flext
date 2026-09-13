"""CLI facade for flext-workspace — declarative command entry point.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys

from flext_cli import cli
from flext_core import p, t


class FlextRootCli:
    """Thin declarative CLI router for flext-workspace."""

    def __init__(self) -> None:
        """Bind the singleton facade and register the declarative routes."""
        self._app = cli.create_app_with_common_params(
            name="flext", help_text="FLEXT workspace orchestration CLI"
        )
        self._register_commands()

    def run(self, args: t.StrSequence | None = None) -> p.Result[bool]:
        """Execute the CLI app through the public flext-cli facade."""
        result: p.Result[bool] = cli.execute_app(
            self._app, prog_name="flext", args=args
        )
        return result

    def _register_commands(self) -> None:
        """Register the configured routes."""


def main() -> int:
    """Run the CLI and return a process-compatible exit code."""
    result = FlextRootCli().run(sys.argv[1:])
    return cli.finalize_result(result)


if __name__ == "__main__":
    cli.exit(main())


__all__: tuple[str, ...] = ("FlextRootCli", "main")
