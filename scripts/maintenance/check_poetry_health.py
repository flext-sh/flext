#!/usr/bin/env python3
# Owner-Skill: .claude/skills/workspace-maintenance/SKILL.md
"""Validate poetry lock health and outdated dependencies across FLEXT submodules.

Checks for:
- pyproject.toml presence
- poetry.lock presence
- Lock file freshness (poetry check --lock)
- Outdated dependency count (poetry show --outdated)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _discover import discover_all_paths

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REPORT_PATH = (
    REPO_ROOT
    / ".sisyphus"
    / "reports"
    / "workspace-maintenance--json--poetry-health-violations.json"
)

MAX_OUTDATED_WARN = 10
LOCK_CHECK_TIMEOUT = 30
OUTDATED_CHECK_TIMEOUT = 60
UPDATE_LOCK_TIMEOUT = 120


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
    outdated_count: int = 0
    violations: list[Violation] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate poetry lock health across all FLEXT submodules.",
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
        help="Run poetry update --lock for projects with stale locks",
    )
    parser.add_argument(
        "--skip-outdated",
        action="store_true",
        help="Skip the outdated dependencies check (faster)",
    )
    return parser.parse_args()


def discover_all_projects(root: Path) -> list[Path]:
    return discover_all_paths(root)


def check_pyproject_exists(project_path: Path) -> list[Violation]:
    """Check that pyproject.toml exists."""
    name = project_path.name
    if not (project_path / "pyproject.toml").exists():
        return [
            Violation(
                project=name,
                check="pyproject-exists",
                message="missing pyproject.toml",
                severity="error",
            )
        ]
    return []


def check_poetry_lock_exists(project_path: Path) -> list[Violation]:
    """Check that poetry.lock exists."""
    name = project_path.name
    if not (project_path / "poetry.lock").exists():
        return [
            Violation(
                project=name,
                check="poetry-lock-exists",
                message="missing poetry.lock",
                severity="warning",
            )
        ]
    return []


def check_lock_freshness(project_path: Path) -> list[Violation]:
    """Run poetry check --lock to verify lock is in sync with pyproject.toml."""
    name = project_path.name

    if not (project_path / "poetry.lock").exists():
        return []  # Already caught by check_poetry_lock_exists

    try:
        result = subprocess.run(
            ["poetry", "check", "--lock", "--no-ansi"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False,
            timeout=LOCK_CHECK_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return [
            Violation(
                project=name,
                check="lock-freshness",
                message="poetry check --lock timed out",
                severity="warning",
            )
        ]
    except FileNotFoundError:
        return [
            Violation(
                project=name,
                check="lock-freshness",
                message="poetry command not found",
                severity="error",
            )
        ]

    if result.returncode != 0:
        stderr = result.stderr.strip()[:200] if result.stderr else ""
        stdout = result.stdout.strip()[:200] if result.stdout else ""
        detail = stderr or stdout or "lock file is out of sync"
        return [
            Violation(
                project=name,
                check="lock-freshness",
                message=f"stale lock: {detail}",
                severity="error",
            )
        ]

    return []


def check_outdated_count(project_path: Path) -> tuple[int, list[Violation]]:
    """Run poetry show --outdated to count outdated packages."""
    name = project_path.name

    if not (project_path / "poetry.lock").exists():
        return 0, []

    try:
        result = subprocess.run(
            ["poetry", "show", "--outdated", "--no-ansi"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False,
            timeout=OUTDATED_CHECK_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return 0, [
            Violation(
                project=name,
                check="outdated-count",
                message="poetry show --outdated timed out",
                severity="warning",
            )
        ]
    except FileNotFoundError:
        return 0, []  # Already caught in lock_freshness

    if result.returncode != 0:
        return 0, []

    lines = [
        line
        for line in result.stdout.splitlines()
        if line.strip() and not line.startswith("Warning")
    ]
    count = len(lines)
    violations: list[Violation] = []

    if count > MAX_OUTDATED_WARN:
        violations.append(
            Violation(
                project=name,
                check="outdated-count",
                message=f"{count} outdated packages (threshold: {MAX_OUTDATED_WARN})",
            )
        )

    return count, violations


def apply_lock_update(project_path: Path) -> bool:
    """Run poetry update --lock for a project. Returns True on success."""
    try:
        result = subprocess.run(
            ["poetry", "update", "--lock", "--no-ansi"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False,
            timeout=UPDATE_LOCK_TIMEOUT,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def validate_project(project_path: Path, skip_outdated: bool = False) -> ProjectInfo:
    """Run all poetry health checks for a project."""
    info = ProjectInfo(path=str(project_path), name=project_path.name)
    info.violations.extend(check_pyproject_exists(project_path))

    if info.violations:
        # No pyproject.toml, skip remaining checks
        return info

    info.violations.extend(check_poetry_lock_exists(project_path))
    info.violations.extend(check_lock_freshness(project_path))

    if not skip_outdated:
        count, outdated_violations = check_outdated_count(project_path)
        info.outdated_count = count
        info.violations.extend(outdated_violations)

    return info


def write_report(infos: list[ProjectInfo]) -> None:
    """Write JSON report to .sisyphus/reports/."""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "tool": "check_poetry_health",
        "version": "1.0.0",
        "projects_scanned": len(infos),
        "total_violations": sum(len(p.violations) for p in infos),
        "total_outdated": sum(p.outdated_count for p in infos),
        "projects": [
            {
                "name": p.name,
                "path": p.path,
                "outdated_count": p.outdated_count,
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
    }

    REPORT_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def print_summary(infos: list[ProjectInfo]) -> None:
    """Print ANSI colored summary."""
    total_violations = sum(len(p.violations) for p in infos)
    total_outdated = sum(p.outdated_count for p in infos)

    print(f"\n{Ansi.BOLD}Poetry Health Report{Ansi.RESET}")
    print(f"{'=' * 60}")
    print(f"Projects scanned: {len(infos)}")
    print(f"Total violations: {total_violations}")
    print(f"Total outdated packages: {total_outdated}")
    print()

    for info in infos:
        status_parts: list[str] = []
        if info.violations:
            status_parts.append(f"{len(info.violations)} violation(s)")
        if info.outdated_count > 0:
            status_parts.append(f"{info.outdated_count} outdated")

        if not status_parts:
            continue

        print(f"{Ansi.CYAN}{info.name}{Ansi.RESET} -- {', '.join(status_parts)}")
        for v in info.violations:
            color = Ansi.RED if v.severity == "error" else Ansi.YELLOW
            print(f"  {color}[{v.severity}]{Ansi.RESET} {v.check}: {v.message}")

    if total_violations == 0:
        print(f"\n{Ansi.GREEN}All poetry checks passed.{Ansi.RESET}")
    else:
        errors = sum(1 for p in infos for v in p.violations if v.severity == "error")
        warnings = total_violations - errors
        print(
            f"\n{Ansi.RED}{errors} error(s){Ansi.RESET}, {Ansi.YELLOW}{warnings} warning(s){Ansi.RESET}"
        )


def main() -> int:
    """Orchestrate poetry health checks."""
    args = parse_args()
    root = Path(args.root).resolve()

    projects = discover_all_projects(root)
    if not projects:
        print(
            f"{Ansi.RED}No flext-* projects found under {root}{Ansi.RESET}",
            file=sys.stderr,
        )
        return 1

    infos: list[ProjectInfo] = [
        validate_project(project_path, skip_outdated=args.skip_outdated)
        for project_path in projects
    ]

    # Apply lock updates if requested
    if args.apply:
        stale_projects = [
            info
            for info in infos
            if any(v.check == "lock-freshness" for v in info.violations)
        ]
        for info in stale_projects:
            print(f"{Ansi.CYAN}Updating lock: {info.name}{Ansi.RESET}")
            if apply_lock_update(Path(info.path)):
                print(f"  {Ansi.GREEN}OK{Ansi.RESET}")
            else:
                print(f"  {Ansi.RED}FAILED{Ansi.RESET}")

    if args.json_output:
        write_report(infos)
        total = sum(len(p.violations) for p in infos)
        data = {
            "projects_scanned": len(infos),
            "total_violations": total,
            "total_outdated": sum(p.outdated_count for p in infos),
            "report_path": str(REPORT_PATH),
        }
        print(json.dumps(data, indent=2))
    else:
        print_summary(infos)

    write_report(infos)

    # Fail only on errors
    errors = sum(1 for p in infos for v in p.violations if v.severity == "error")
    return 1 if errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
