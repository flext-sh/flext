"""Scope workspace-wide pre-commit checks to the FLEXT projects that changed.

Pre-commit passes the staged file paths as positional arguments. This helper
extracts the affected project names (top-level submodules that contain a
pyproject.toml) and runs ``flext_infra check --what <gate> --projects ...``
only for those projects. When no staged file belongs to a FLEXT project the
hook exits successfully without doing any work.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path

from flext_cli import cli, p


class FlextRootCheckChangedProjects:
<<<<<<< HEAD
    """FlextRoot check changed projects namespace."""

    REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
    MIN_POSITIONAL_ARGS = 2

    @staticmethod
    def _known_projects() -> frozenset[str]:
        """Return top-level directory names that look like FLEXT projects."""
        return frozenset(
            entry.name
            for entry in FlextRootCheckChangedProjects.REPOSITORY_ROOT.iterdir()
            if entry.is_dir() and (entry / "pyproject.toml").is_file()
        )

    @staticmethod
    def main(what: str, files: list[str]) -> int:
        """Run the requested gate only for projects touched by the staged files."""
        known = FlextRootCheckChangedProjects._known_projects()
        projects = {
            rel.parts[0]
            for raw in files
            if (rel := FlextRootCheckChangedProjects._relative_to_workspace(raw)).parts
            and rel.parts[0] in known
=======
    """Pre-commit hook to scope checks to changed FLEXT projects."""

    REPOSITORY_ROOT: Path = Path(__file__).resolve().parents[2]
    MIN_POSITIONAL_ARGS: int = 2

    @classmethod
    def _known_projects(cls) -> frozenset[str]:
        """Return top-level directory names that look like FLEXT projects."""
        return frozenset(
            entry.name
            for entry in cls.REPOSITORY_ROOT.iterdir()
            if entry.is_dir() and (entry / "pyproject.toml").is_file()
        )

    @classmethod
    def main(cls, what: str, files: list[str]) -> int:
        """Run the requested gate only for projects touched by the staged files."""
        known = cls._known_projects()
        projects = {
            rel.parts[0]
            for raw in files
            if (rel := cls._relative_to_workspace(raw)).parts and rel.parts[0] in known
>>>>>>> origin/0.12.0-dev
        }
        if not projects:
            return 0

        outcome = cli.run(
            [
                "uv",
                "run",
                "--all-packages",
                "python",
                "-m",
                "flext_infra",
                "check",
                "--what",
                what,
                "--projects",
                ",".join(sorted(projects)),
            ],
<<<<<<< HEAD
            cwd=FlextRootCheckChangedProjects.REPOSITORY_ROOT,
=======
            cwd=cls.REPOSITORY_ROOT,
>>>>>>> origin/0.12.0-dev
        )
        if outcome.failure:
            return 1
        command: p.Cli.CommandOutput = outcome.value
        return command.exit_code

<<<<<<< HEAD
    @staticmethod
    def _relative_to_workspace(raw: str) -> Path:
        path = Path(raw)
        if not path.is_absolute():
            path = FlextRootCheckChangedProjects.REPOSITORY_ROOT / path
        return path.relative_to(FlextRootCheckChangedProjects.REPOSITORY_ROOT)


if __name__ == "__main__":
    if len(sys.argv) < FlextRootCheckChangedProjects.MIN_POSITIONAL_ARGS:
        msg = "usage: check_changed_projects.py <boundary|loc-cap> [file ...]"
        raise SystemExit(msg)
    cli.exit(FlextRootCheckChangedProjects.main(sys.argv[1], sys.argv[2:]))
=======
    @classmethod
    def _relative_to_workspace(cls, raw: str) -> Path:
        path = Path(raw)
        if not path.is_absolute():
            path = cls.REPOSITORY_ROOT / path
        return path.relative_to(cls.REPOSITORY_ROOT)

    @classmethod
    def cli_entry(cls, argv: list[str] | None = None) -> int:
        """CLI entry point."""
        args = list(sys.argv[1:] if argv is None else argv)
        if len(args) < cls.MIN_POSITIONAL_ARGS:
            msg = "usage: check_changed_projects.py <boundary|loc-cap> [file ...]"
            raise SystemExit(msg)
        result = cls.main(args[0], args[1:])
        cli.exit(result)
        return result  # unreachable, but satisfies type checker


if __name__ == "__main__":
    raise SystemExit(FlextRootCheckChangedProjects.cli_entry())
>>>>>>> origin/0.12.0-dev
