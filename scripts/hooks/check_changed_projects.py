"""Scope workspace-wide pre-commit checks to the FLEXT projects that changed.

Pre-commit passes the staged file paths as positional arguments. This helper
extracts the affected project names (top-level submodules that contain a
pyproject.toml) and runs ``flext_infra check --what <gate> --projects ...``
only for those projects. When no staged file belongs to a FLEXT project the
hook exits successfully without doing any work.
"""

from __future__ import annotations

import sys
from pathlib import Path

from flext_cli import cli, p

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
MIN_POSITIONAL_ARGS = 2


def _known_projects() -> frozenset[str]:
    """Return top-level directory names that look like FLEXT projects."""
    return frozenset(
        entry.name
        for entry in WORKSPACE_ROOT.iterdir()
        if entry.is_dir() and (entry / "pyproject.toml").is_file()
    )


def main(what: str, files: list[str]) -> int:
    """Run the requested gate only for projects touched by the staged files."""
    known = _known_projects()
    projects = {
        rel.parts[0]
        for raw in files
        if (rel := _relative_to_workspace(raw)).parts and rel.parts[0] in known
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
        cwd=WORKSPACE_ROOT,
    )
    if outcome.failure:
        return 1
    command: p.Cli.CommandOutput = outcome.value
    return command.exit_code


def _relative_to_workspace(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = WORKSPACE_ROOT / path
    return path.relative_to(WORKSPACE_ROOT)


if __name__ == "__main__":
    if len(sys.argv) < MIN_POSITIONAL_ARGS:
        msg = "usage: check_changed_projects.py <boundary|loc-cap> [file ...]"
        raise SystemExit(msg)
    cli.exit(main(sys.argv[1], sys.argv[2:]))
