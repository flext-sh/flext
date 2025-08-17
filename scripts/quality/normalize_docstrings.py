#!/usr/bin/env python3
"""Normalize docstrings across the monorepo to Google style and PEP257."""

from __future__ import annotations

import argparse
import io
import runpy
import shutil
import sys
from collections.abc import Iterable
from contextlib import redirect_stderr, redirect_stdout, suppress
from importlib import import_module
from pathlib import Path

# Import ruff dynamically (call via import_module to allow runtime fallback)
_ruff_mod = import_module("ruff.__main__")
ruff_main = getattr(_ruff_mod, "main", None)

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
    """Iterate over Python files in the given root directory.

    Args:
      root (Path): Root directory to search for Python files.

    Raises:
      None.

    """
    for path in root.rglob("*.py"):
        parts = set(path.parts)
        if parts & IGNORED_DIRS:
            continue
        yield path


class _Completed:
    def __init__(self, returncode: int, stdout: str, stderr: str) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def run_pyment_on_file(path: Path) -> _Completed:
    """Run pyment on a single Python file.

    Args:
      path (Path): Path to the Python file to process.

    Raises:
      None.

    """
    # Execute pyment as a Python module to avoid subprocess
    if shutil.which("pyment") is None:
        return _Completed(127, "", "pyment not found in PATH")

    argv = ["pyment", "-w", "-o", "google", str(path)]
    stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
    # Temporarily set sys.argv and run module
    old_argv = sys.argv
    try:
        sys.argv = argv.copy()  # emulate CLI argv
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            try:
                runpy.run_module("pyment", run_name="__main__")
                return _Completed(0, stdout_buf.getvalue(), stderr_buf.getvalue())
            except SystemExit as e:  # pyment may call sys.exit
                code = e.code if isinstance(e.code, int) else 1
                return _Completed(code, stdout_buf.getvalue(), stderr_buf.getvalue())
    finally:
        sys.argv = old_argv


def has_command(cmd: str) -> bool:
    """Check if a command is available in the system.

    Args:
      cmd (str): Command name to check.

    Raises:
      None.

    """
    return shutil.which(cmd) is not None


def main(argv: list[str]) -> int:
    """Main function to normalize docstrings in Python files.

    Args:
      argv (List[str]): Command line arguments.

    Raises:
      None.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-ruff",
        action="store_true",
        help="Skip running Ruff docstring fixes",
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
        # Run Ruff in-process
    with suppress(SystemExit):
        if callable(ruff_main):
            ruff_main(["--select", "D", "--fix", str(REPO_ROOT)])
        else:
            print("ruff not available in-process; skip in-process fix")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
