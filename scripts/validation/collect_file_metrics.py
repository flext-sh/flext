#!/usr/bin/env python3
"""Canonical 4-lint metrics collector for FLEXT validation pipeline.

Runs ruff, mypy, pyright, and pyrefly on individual files or project
directories and outputs per-file JSON metric records.

Usage:
    # Per-file metrics (for a single file):
    python scripts/validation/collect_file_metrics.py --file path/to/file.py --project-dir project/

    # Per-file metrics for multiple files:
    python scripts/validation/collect_file_metrics.py --files file1.py file2.py --project-dir project/

    # Per-file metrics for all .py in a project:
    python scripts/validation/collect_file_metrics.py --project-dir flext-core/

Output JSON (per file):
    {"file": "path/to/file.py", "tool": "ruff", "count": 3}
    {"file": "path/to/file.py", "tool": "mypy", "count": 1}
    {"file": "path/to/file.py", "tool": "pyright", "count": 0}
    {"file": "path/to/file.py", "tool": "pyrefly", "count": 2}
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

TOOLS = ("ruff", "mypy", "pyright", "pyrefly")

# Directories to skip when discovering .py files
SKIP_DIRS = frozenset({
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".tox",
    "dist",
    "build",
    ".eggs",
    "node_modules",
    ".nox",
})


def _run(
    cmd: list[str], cwd: str | None = None, timeout: int = 120
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess, capturing stdout+stderr."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=timeout,
    )


def _tool_available(name: str) -> bool:
    """Check if a tool binary is on PATH."""
    try:
        subprocess.run([name, "--version"], capture_output=True, timeout=10)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def count_ruff(filepath: str, _project_dir: str | None = None) -> int:
    """Count ruff diagnostics for a single file."""
    result = _run(["ruff", "check", filepath, "--output-format=json", "--quiet"])
    if result.returncode not in (0, 1):
        return -1  # tool error
    try:
        data = json.loads(result.stdout) if result.stdout.strip() else []
        return len(data)
    except json.JSONDecodeError:
        return -1


def count_mypy(filepath: str, project_dir: str | None = None) -> int:
    """Count mypy errors attributed to a specific file.

    mypy must run from the project directory for proper config resolution.
    We then filter output lines to only count errors for the target file.
    """
    abs_file = str(Path(filepath).resolve())
    cwd = project_dir or "."

    # Make filepath relative to project_dir for matching
    try:
        rel_path = str(Path(abs_file).relative_to(Path(cwd).resolve()))
    except ValueError:
        rel_path = filepath

    result = _run(
        [
            "mypy",
            rel_path,
            "--no-error-summary",
            "--show-error-codes",
            "--no-color-output",
        ],
        cwd=cwd,
        timeout=120,
    )
    if result.returncode not in (0, 1, 2):
        return -1

    count = 0
    for line in result.stdout.splitlines():
        # mypy output: file:line: severity: message [code]
        if line.startswith(rel_path + ":") and ": error:" in line:
            count += 1
    return count


def count_pyright(filepath: str, _project_dir: str | None = None) -> int:
    """Count pyright diagnostics for a single file using JSON output."""
    result = _run(["pyright", "--outputjson", filepath], timeout=120)
    try:
        data = json.loads(result.stdout) if result.stdout.strip() else {}
        diags = data.get("generalDiagnostics", [])
        # Count errors and warnings (not information)
        return sum(1 for d in diags if d.get("severity", "") in ("error", "warning"))
    except json.JSONDecodeError:
        return -1


def count_pyrefly(filepath: str, _project_dir: str | None = None) -> int:
    """Count pyrefly errors for a single file using JSON output."""
    result = _run(
        ["pyrefly", "check", "--output-format", "json", filepath], timeout=120
    )
    try:
        data = json.loads(result.stdout) if result.stdout.strip() else {}
        errors = data.get("errors", [])
        return len(errors)
    except json.JSONDecodeError:
        # Fallback: count error lines from stderr/stdout
        count = 0
        for line in (result.stdout + result.stderr).splitlines():
            if line.strip().startswith("ERROR "):
                count += 1
        return count


COLLECTORS = {
    "ruff": count_ruff,
    "mypy": count_mypy,
    "pyright": count_pyright,
    "pyrefly": count_pyrefly,
}


def discover_py_files(project_dir: str) -> list[str]:
    """Discover all .py files in a project directory, skipping build artifacts."""
    py_files: list[str] = []
    for root, dirs, files in os.walk(project_dir):
        # Prune unwanted directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    py_files.sort()
    return py_files


def collect_file_metrics(
    filepath: str,
    project_dir: str | None = None,
    tools: tuple[str, ...] = TOOLS,
    degraded: bool = False,
) -> list[dict]:
    """Collect metrics for a single file across all 4 tools.

    Returns a list of dicts: [{"file", "tool", "count"}, ...]
    count = -1 means tool error (skip), -2 means tool unavailable.
    """
    results = []
    for tool in tools:
        if not _tool_available(tool):
            if not degraded:
                print(
                    f"ERROR: {tool} not found on PATH. Use --degraded to skip.",
                    file=sys.stderr,
                )
                sys.exit(2)
            results.append({"file": filepath, "tool": tool, "count": -2})
            continue

        collector = COLLECTORS[tool]
        count = collector(filepath, project_dir)
        results.append({"file": filepath, "tool": tool, "count": count})
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect per-file lint metrics (ruff, mypy, pyright, pyrefly)"
    )
    parser.add_argument("--file", help="Single file to check")
    parser.add_argument("--files", nargs="+", help="Multiple files to check")
    parser.add_argument(
        "--project-dir", help="Project directory (for mypy config resolution)"
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Discover all .py files in --project-dir",
    )
    parser.add_argument(
        "--tools",
        nargs="+",
        choices=TOOLS,
        default=list(TOOLS),
        help="Which tools to run",
    )
    parser.add_argument(
        "--degraded",
        action="store_true",
        help="Skip unavailable tools instead of failing",
    )
    parser.add_argument(
        "--summary", action="store_true", help="Also output a per-project summary line"
    )
    args = parser.parse_args()

    files_to_check: list[str] = []
    if args.file:
        files_to_check.append(args.file)
    if args.files:
        files_to_check.extend(args.files)
    if args.discover and args.project_dir:
        files_to_check.extend(discover_py_files(args.project_dir))

    if not files_to_check:
        parser.error("Provide --file, --files, or --discover with --project-dir")

    project_dir = args.project_dir or "."
    tools = tuple(args.tools)

    all_results: list[dict] = []
    for fpath in files_to_check:
        metrics = collect_file_metrics(fpath, project_dir, tools, args.degraded)
        all_results.extend(metrics)
        for m in metrics:
            print(json.dumps(m))

    if args.summary:
        # Aggregate per-tool totals
        totals: dict[str, int] = {}
        for r in all_results:
            tool = r["tool"]
            count = r["count"]
            if count >= 0:
                totals[tool] = totals.get(tool, 0) + count
        summary = {
            "type": "project_summary",
            "project_dir": project_dir,
            "file_count": len(files_to_check),
            "totals": totals,
        }
        print(json.dumps(summary))


if __name__ == "__main__":
    main()
