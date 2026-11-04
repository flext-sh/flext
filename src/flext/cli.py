"""Command-line interface facade for the FLEXT workspace.

Dispatches command-line invocations to the centralized execution engine in
``flext-cli``, providing a unified console entry point across workspace services.

See Also:
    - ADR-017: Parametrized rule surfaces and single modernize CLI.
    - ADR-028: Facade boundary orchestrators declarative enforcement.
    - :mod:`flext_cli`: Core CLI implementation and command registry.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import cli


class FlextRootCli:
    """Workspace root command-line interface orchestrator.

    Exposes top-level command execution capabilities, delegating parsed options
    and arguments to the underlying ``flext_cli`` runtime.

    See Also:
        - :mod:`flext_cli.cli`: Upstream CLI controller.

    """

    @staticmethod
    def main() -> None:
        """Execute the root CLI application with command-line arguments.

        Invokes the global CLI runner to parse arguments, dispatch subcommands,
        and manage process exit status.
        """
        _ = cli.execute()


def main() -> None:
    """Run the workspace command-line application.

    Acts as the standard console script entry point defined in ``pyproject.toml``.
    """
    FlextRootCli.main()


if __name__ == "__main__":
    main()


__all__: tuple[str, ...] = ("FlextRootCli", "main")
