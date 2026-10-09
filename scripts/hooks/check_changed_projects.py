"""Scope workspace-wide pre-commit checks to the FLEXT projects that changed.

Pre-commit passes the staged file paths as positional arguments. This helper
selects affected project names from the typed workspace composition and runs
``flext_infra check run --gates <gate> --projects ...``
only for those projects. When no staged file belongs to a FLEXT project the
hook exits successfully without doing any work.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path

from flext_cli import cli
from flext_infra import u


class FlextRootCheckChangedProjects:
    """Pre-commit hook to scope checks to changed FLEXT projects."""

    REPOSITORY_ROOT: Path = Path(__file__).resolve().parents[2]
    MIN_POSITIONAL_ARGS: int = 2

    @classmethod
    def main(cls, what: str, files: list[str]) -> int:
        """Run the requested gate only for projects touched by the staged files.

        Returns:
            The resulting ``int``.

        """
        declared = u.Infra.git_declared_submodule_paths(cls.REPOSITORY_ROOT)
        if declared.failure:
            return cli.finalize_result(declared)
        changed = tuple(cls._relative_to_workspace(raw) for raw in files)
        projects = {
            project.as_posix()
            for project in declared.value
            if any(path.is_relative_to(project) for path in changed)
        }
        if not projects:
            return 0

        outcome = u.Cli.run_raw(
            [
                sys.executable,
                "-m",
                "flext_infra",
                "check",
                "run",
                "--repository-root",
                str(cls.REPOSITORY_ROOT),
                "--gates",
                what,
                *(
                    item
                    for project in sorted(projects)
                    for item in ("--projects", project)
                ),
            ],
            cwd=cls.REPOSITORY_ROOT,
            capture=False,
        )
        if outcome.failure:
            return cli.finalize_result(outcome)
        return outcome.value.outcome.raw_return_code

    @classmethod
    def _relative_to_workspace(cls, raw: str) -> Path:
        path = Path(raw)
        if not path.is_absolute():
            path = cls.REPOSITORY_ROOT / path
        return path.relative_to(cls.REPOSITORY_ROOT)

    @classmethod
    def cli_entry(cls, argv: list[str] | None = None) -> int:
        """CLI entry point.

        Returns:
            The resulting ``int``.

        Raises:
            SystemExit: If usage.

        """
        args = list(sys.argv[1:] if argv is None else argv)
        if len(args) < cls.MIN_POSITIONAL_ARGS:
            msg = "usage: check_changed_projects.py <boundary|loc-cap> [file ...]"
            raise SystemExit(msg)
        result = cls.main(args[0], args[1:])
        cli.exit(result)
        return result  # unreachable, but satisfies type checker


if __name__ == "__main__":
    raise SystemExit(FlextRootCheckChangedProjects.cli_entry())
