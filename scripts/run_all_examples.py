#!/usr/bin/env python3
"""Run all project examples in a consistent, safe way.

Features:
- Discovers all project `examples/` directories in the monorepo
- Runs only numerically prefixed examples: `NN_*.py`
- Skips heavy/docker examples by default (configurable via flags)
- Sets `PYTHONPATH=src` and runs from the project root
- Continues on error by default and prints a concise summary

Usage:
    python scripts/run_all_examples.py [--project SUBSTR] [--timeout 20] [--include-docker]

Notes:
- Per-project "run all" scripts that already exist (e.g., client-a-oud-mig/examples/run_all_examples.py)
  are preserved and can still be used directly. This script is an orchestrator across the repo.

"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def find_example_dirs(root: Path) -> list[Path]:
    """Return all `examples` dirs directly under project roots (not under tests)."""
    results: list[Path] = []
    for p in root.glob("*/examples"):
        if not p.is_dir():
            continue
        # Skip test example folders
        if any(parent.name == "tests" for parent in p.parents):
            continue
        results.append(p)
    return sorted(results)


def list_example_files(examples_dir: Path, *, include_docker: bool) -> list[Path]:
    """List numerically prefixed example files to run, filtering heavy ones by default."""
    files: list[Path] = []
    for f in examples_dir.glob("[0-9][0-9]_*.py"):
        name = f.name.lower()
        if not include_docker and ("docker" in name or "run_with_docker" in name):
            continue
        files.append(f)
    return sorted(files)


@dataclass
class RunResult:
    """Run result."""

    project: str
    example: str
    returncode: int


def run_example(project_root: Path, example_file: Path, timeout: int) -> RunResult:
    """Run example."""
    env = os.environ.copy()
    # Prefer project-local src so examples can import their package
    env["PYTHONPATH"] = "src"
    proc = subprocess.run(
        [sys.executable, str(example_file.name)],
        cwd=str(project_root / "examples"),
        env=env,
        shell=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    project = project_root.name
    # Stream concise output to console
    status = "OK" if proc.returncode == 0 else f"FAIL({proc.returncode})"
    print(f"[{project}] {example_file.name}: {status}")
    if proc.returncode != 0:
        # Show short stderr tail for debugging
        err_tail = (proc.stderr or "").splitlines()[-5:]
        for line in err_tail:
            print(f"  ! {line}")
    return RunResult(
        project=project,
        example=example_file.name,
        returncode=proc.returncode,
    )


def main(argv: Iterable[str] | None = None) -> int:
    """Main function."""
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--project",
        dest="project_filter",
        help="Filter by project name substring",
        default=None,
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Per-example timeout in seconds (default: 20)",
    )
    ap.add_argument(
        "--include-docker",
        action="store_true",
        help="Include docker/integration-heavy examples",
    )
    ap.add_argument("--dry-run", action="store_true", help="Only print what would run")
    args = ap.parse_args(list(argv) if argv is not None else None)

    example_dirs = find_example_dirs(REPO_ROOT)
    if args.project_filter:
        example_dirs = [
            d
            for d in example_dirs
            if args.project_filter.lower() in str(d.parent.name).lower()
        ]

    if not example_dirs:
        print("No examples/ directories found")
        return 0

    print(f"Discovered {len(example_dirs)} examples/ directories")

    all_results: list[RunResult] = []
    for examples_dir in example_dirs:
        project_root = examples_dir.parent
        # Skip directories that have no numeric examples
        files = list_example_files(examples_dir, include_docker=args.include_docker)
        if not files:
            continue

        print(f"\n== {project_root.name} ({len(files)} examples) ==")
        if args.dry_run:
            for f in files:
                print(f"DRY-RUN: would run {project_root.name}/examples/{f.name}")
            continue

        for f in files:
            try:
                res = run_example(project_root, f, timeout=args.timeout)
                all_results.append(res)
            except subprocess.TimeoutExpired:
                print(f"[{project_root.name}] {f.name}: TIMEOUT({args.timeout}s)")
                all_results.append(RunResult(project_root.name, f.name, returncode=124))
            except Exception as e:
                print(f"[{project_root.name}] {f.name}: ERROR({e})")
                all_results.append(RunResult(project_root.name, f.name, returncode=1))

    # Summary
    ran = len(all_results)
    failed = sum(1 for r in all_results if r.returncode != 0)
    print("\nSummary:")
    print(f"  Ran: {ran}")
    print(f"  Failed: {failed}")
    if failed:
        print("  Failures:")
        for r in all_results:
            if r.returncode != 0:
                print(f"    - [{r.project}] {r.example} -> {r.returncode}")

    # Non-zero if any failures
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
