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
            cwd=cls.REPOSITORY_ROOT,
        )
        if outcome.failure:
            return 1
        command: p.Cli.CommandOutput = outcome.value
        return command.exit_code

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
        return cli.exit(cls.main(args[0], args[1:]))


if __name__ == "__main__":
    raise SystemExit(FlextRootCheckChangedProjects.cli_entry())

