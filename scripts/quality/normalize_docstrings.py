#!/usr/bin/env python3
"""Normalize docstrings across the monorepo to Google style and PEP257.

Process:
- Walk all tracked Python files under the workspace.
- Run Pyment per-file to convert docstrings to Google style.
- Ignore files that cause Pyment to crash; log them.
- Optionally, run Ruff to auto-fix docstring nitpicks (D rules).

Usage:
    python scripts/quality/normalize_docstrings.py [--no-ruff]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]

IGNORED_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    "build",
    "dist",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
}


def iter_python_files(root: Path) -> Iterable[Path]:
    """Args:
        root (Path):

    Raises:

    """
    for path in root.rglob("*.py"):
        parts = set(path.parts)
        if parts & IGNORED_DIRS:
            continue
        yield path


def run_pyment_on_file(path: Path) -> subprocess.CompletedProcess:
    """Args:
        path (Path):

    Raises:

    """
    # Pyment per-file; overwrite in-place to google style
    return subprocess.run(
        ["pyment", "-w", "-o", "google", str(path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def has_command(cmd: str) -> bool:
    """Args:
        cmd (str):

    Raises:

    """
    res = subprocess.run(
        [cmd, "--version"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return res.returncode == 0


def main(argv: list[str]) -> int:
    """Args:
        argv (List[str]):

    Raises:

    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-ruff", action="store_true", help="Skip running Ruff docstring fixes"
    )
    args = parser.parse_args(argv)

    py_files = list(iter_python_files(REPO_ROOT))
    print(f"Discovered {len(py_files)} Python files")

    failures: list[tuple[Path, str]] = []

    for idx, f in enumerate(py_files, 1):
        rel = f.relative_to(REPO_ROOT)
        proc = run_pyment_on_file(f)
        if proc.returncode != 0:
            failures.append((rel, proc.stderr.strip() or proc.stdout.strip()))
        if idx % 100 == 0:
            print(f"Processed {idx}/{len(py_files)} files...")

    print(f"Pyment completed with {len(failures)} failures")

    if failures:
        print("Failures (showing up to 50):")
        for rel, msg in failures[:50]:
            print(f" - {rel}: {msg.splitlines()[-1] if msg else 'unknown error'}")

    if not args.no_ruff and has_command("ruff"):
        print("Running Ruff docstring fixes (D rules)...")
        subprocess.run(
            [
                "ruff",
                "--select",
                "D",
                "--fix",
                str(REPO_ROOT),
            ],
            check=False,
        )

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
