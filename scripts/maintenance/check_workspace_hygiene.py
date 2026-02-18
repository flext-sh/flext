#!/usr/bin/env python3
# Owner-Skill: .claude/skills/workspace-maintenance/SKILL.md
"""Validate workspace cleanliness across all FLEXT submodules.

Checks for:
- Untracked build/cache cruft directories
- .gitignore coverage for essential patterns
- Required files presence (pyproject.toml, README.md, Makefile, src/)
- Submodule pointer alignment (dirty submodule detection)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _discover import discover_all_paths  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REPORT_PATH = (
    REPO_ROOT
    / ".sisyphus"
    / "reports"
    / "workspace-maintenance--json--hygiene-violations.json"
)

CRUFT_DIRS = (
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "__pycache__",
    "dist",
    "build",
    ".eggs",
)
CRUFT_FILES = (".coverage",)
CRUFT_GLOBS = ("*.egg-info",)

REQUIRED_GITIGNORE_PATTERNS = (
    "__pycache__/",
    ".mypy_cache/",
    "dist/",
    ".coverage",
    "*.egg-info",
)

REQUIRED_FILES = ("pyproject.toml", "README.md", "Makefile")
REQUIRED_DIRS = ("src",)


class Ansi:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


@dataclass(frozen=True)
class Violation:
    project: str
    check: str
    message: str
    severity: str = "warning"


@dataclass
class ProjectInfo:
    path: str
    name: str
    violations: list[Violation] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate workspace cleanliness across all FLEXT submodules.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Workspace root directory (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Remove detected cruft directories (destructive)",
    )
    return parser.parse_args()


def discover_all_projects(root: Path) -> list[Path]:
    return discover_all_paths(root)


def check_untracked_cruft(project_path: Path) -> list[Violation]:
    """Check for cache/build cruft directories that should not exist."""
    violations: list[Violation] = []
    name = project_path.name

    for cruft in CRUFT_DIRS:
        target = project_path / cruft
        if target.exists():
            violations.append(
                Violation(
                    project=name,
                    check="untracked-cruft",
                    message=f"found cruft directory: {cruft}/",
                )
            )

    for cruft in CRUFT_FILES:
        target = project_path / cruft
        if target.exists():
            violations.append(
                Violation(
                    project=name,
                    check="untracked-cruft",
                    message=f"found cruft file: {cruft}",
                )
            )

    for pattern in CRUFT_GLOBS:
        matches = list(project_path.glob(pattern))
        for match in matches:
            violations.append(
                Violation(
                    project=name,
                    check="untracked-cruft",
                    message=f"found cruft: {match.name}/",
                )
            )

    return violations


def check_gitignore_coverage(project_path: Path) -> list[Violation]:
    """Verify .gitignore exists and contains essential patterns."""
    violations: list[Violation] = []
    name = project_path.name
    gitignore = project_path / ".gitignore"

    if not gitignore.exists():
        violations.append(
            Violation(
                project=name,
                check="gitignore-coverage",
                message="missing .gitignore file",
                severity="error",
            )
        )
        return violations

    try:
        content = gitignore.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        violations.append(
            Violation(
                project=name,
                check="gitignore-coverage",
                message="cannot read .gitignore file",
                severity="error",
            )
        )
        return violations

    lines = {line.strip() for line in content.splitlines()}
    for pattern in REQUIRED_GITIGNORE_PATTERNS:
        if pattern not in lines:
            violations.append(
                Violation(
                    project=name,
                    check="gitignore-coverage",
                    message=f"missing pattern in .gitignore: {pattern}",
                )
            )

    return violations


def check_required_files(project_path: Path) -> list[Violation]:
    """Verify required project files and directories exist."""
    violations: list[Violation] = []
    name = project_path.name

    for filename in REQUIRED_FILES:
        if not (project_path / filename).exists():
            violations.append(
                Violation(
                    project=name,
                    check="required-files",
                    message=f"missing required file: {filename}",
                    severity="error" if filename == "pyproject.toml" else "warning",
                )
            )

    for dirname in REQUIRED_DIRS:
        if not (project_path / dirname).is_dir():
            violations.append(
                Violation(
                    project=name,
                    check="required-dirs",
                    message=f"missing required directory: {dirname}/",
                    severity="warning",
                )
            )

    return violations


def check_submodule_alignment(root: Path) -> list[Violation]:
    """Check for dirty submodule pointers (+ prefix in git submodule status)."""
    violations: list[Violation] = []

    try:
        result = subprocess.run(
            ["git", "submodule", "status"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        violations.append(
            Violation(
                project="<root>",
                check="submodule-alignment",
                message="failed to run git submodule status",
                severity="error",
            )
        )
        return violations

    if result.returncode != 0:
        return violations

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("+"):
            # Dirty submodule: +<sha> <path> (<branch>)
            parts = line[1:].split()
            submodule_path = parts[1] if len(parts) >= 2 else line
            violations.append(
                Violation(
                    project=submodule_path,
                    check="submodule-alignment",
                    message="submodule pointer is dirty (local changes not committed to parent)",
                )
            )
        elif line.startswith("-"):
            parts = line[1:].split()
            submodule_path = parts[1] if len(parts) >= 2 else line
            violations.append(
                Violation(
                    project=submodule_path,
                    check="submodule-alignment",
                    message="submodule is not initialized",
                    severity="error",
                )
            )

    return violations


def validate_project(project_path: Path) -> ProjectInfo:
    """Run all per-project checks."""
    info = ProjectInfo(path=str(project_path), name=project_path.name)
    info.violations.extend(check_untracked_cruft(project_path))
    info.violations.extend(check_gitignore_coverage(project_path))
    info.violations.extend(check_required_files(project_path))
    return info


def apply_fixes(infos: list[ProjectInfo]) -> int:
    """Remove detected cruft directories. Returns count of items removed."""
    removed = 0
    for info in infos:
        project_path = Path(info.path)
        for v in info.violations:
            if v.check != "untracked-cruft":
                continue
            # Extract the cruft name from the message
            for cruft in CRUFT_DIRS:
                target = project_path / cruft
                if target.exists():
                    shutil.rmtree(target, ignore_errors=True)
                    removed += 1
            for cruft in CRUFT_FILES:
                target = project_path / cruft
                if target.exists():
                    target.unlink(missing_ok=True)
                    removed += 1
    return removed


def write_report(
    infos: list[ProjectInfo], submodule_violations: list[Violation]
) -> None:
    """Write JSON report to .sisyphus/reports/."""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "tool": "check_workspace_hygiene",
        "version": "1.0.0",
        "projects_scanned": len(infos),
        "total_violations": sum(len(p.violations) for p in infos)
        + len(submodule_violations),
        "projects": [
            {
                "name": p.name,
                "path": p.path,
                "violations": [
                    {
                        "check": v.check,
                        "message": v.message,
                        "severity": v.severity,
                    }
                    for v in p.violations
                ],
            }
            for p in infos
        ],
        "submodule_violations": [
            {
                "project": v.project,
                "check": v.check,
                "message": v.message,
                "severity": v.severity,
            }
            for v in submodule_violations
        ],
    }

    REPORT_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def print_summary(
    infos: list[ProjectInfo], submodule_violations: list[Violation]
) -> None:
    """Print ANSI colored summary."""
    total_violations = sum(len(p.violations) for p in infos) + len(submodule_violations)

    print(f"\n{Ansi.BOLD}Workspace Hygiene Report{Ansi.RESET}")
    print(f"{'=' * 60}")
    print(f"Projects scanned: {len(infos)}")
    print(f"Total violations: {total_violations}")
    print()

    # Per-project violations
    for info in infos:
        if not info.violations:
            continue
        print(f"{Ansi.CYAN}{info.name}{Ansi.RESET}")
        for v in info.violations:
            color = Ansi.RED if v.severity == "error" else Ansi.YELLOW
            print(f"  {color}[{v.severity}]{Ansi.RESET} {v.check}: {v.message}")

    # Submodule violations
    if submodule_violations:
        print(f"\n{Ansi.CYAN}Submodule Alignment{Ansi.RESET}")
        for v in submodule_violations:
            color = Ansi.RED if v.severity == "error" else Ansi.YELLOW
            print(f"  {color}[{v.severity}]{Ansi.RESET} {v.project}: {v.message}")

    # Summary line
    if total_violations == 0:
        print(f"\n{Ansi.GREEN}All checks passed.{Ansi.RESET}")
    else:
        errors = sum(
            1 for p in infos for v in p.violations if v.severity == "error"
        ) + sum(1 for v in submodule_violations if v.severity == "error")
        warnings = total_violations - errors
        print(
            f"\n{Ansi.RED}{errors} error(s){Ansi.RESET}, {Ansi.YELLOW}{warnings} warning(s){Ansi.RESET}"
        )


def main() -> int:
    """Orchestrate workspace hygiene checks."""
    args = parse_args()
    root = Path(args.root).resolve()

    projects = discover_all_projects(root)
    if not projects:
        print(
            f"{Ansi.RED}No flext-* projects found under {root}{Ansi.RESET}",
            file=sys.stderr,
        )
        return 1

    # Per-project checks
    infos: list[ProjectInfo] = []
    for project_path in projects:
        infos.append(validate_project(project_path))

    # Root-level submodule check
    submodule_violations = check_submodule_alignment(root)

    # Apply fixes if requested
    if args.apply:
        removed = apply_fixes(infos)
        print(f"{Ansi.GREEN}Removed {removed} cruft item(s).{Ansi.RESET}")

    # Output
    if args.json_output:
        write_report(infos, submodule_violations)
        # Also print JSON to stdout
        total = sum(len(p.violations) for p in infos) + len(submodule_violations)
        data = {
            "projects_scanned": len(infos),
            "total_violations": total,
            "report_path": str(REPORT_PATH),
        }
        print(json.dumps(data, indent=2))
    else:
        print_summary(infos, submodule_violations)

    # Always write report
    write_report(infos, submodule_violations)

    total_violations = sum(len(p.violations) for p in infos) + len(submodule_violations)
    return 1 if total_violations > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
