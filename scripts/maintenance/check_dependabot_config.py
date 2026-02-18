#!/usr/bin/env python3
# Owner-Skill: .claude/skills/workspace-maintenance/SKILL.md
"""Validate that every FLEXT submodule has a standardized dependabot.yml.

Checks for:
- Presence of .github/dependabot.yml in each project
- Required YAML structure (version: 2, updates list)
- Each update entry has package-ecosystem, directory, schedule with interval
- Standardized labels for pip ecosystem
- Schedule timezone set to America/Sao_Paulo
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _discover import discover_all_paths  # noqa: E402

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REPORT_PATH = (
    REPO_ROOT
    / ".sisyphus"
    / "reports"
    / "workspace-maintenance--json--dependabot-violations.json"
)

EXPECTED_VERSION = 2
EXPECTED_TIMEZONE = "America/Sao_Paulo"
EXPECTED_PIP_LABELS = ["dependencies", "python"]
REQUIRED_UPDATE_FIELDS = ("package-ecosystem", "directory", "schedule")
REQUIRED_SCHEDULE_FIELDS = ("interval",)


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
        description="Validate dependabot.yml standardization across all FLEXT submodules.",
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
        "--strict",
        action="store_true",
        help="Treat warnings as errors (non-zero exit on any violation)",
    )
    return parser.parse_args()


def discover_all_projects(root: Path) -> list[Path]:
    return discover_all_paths(root)


def check_dependabot_exists(project_path: Path) -> list[Violation]:
    """Check that .github/dependabot.yml exists."""
    name = project_path.name
    yml_path = project_path / ".github" / "dependabot.yml"
    yaml_path = project_path / ".github" / "dependabot.yaml"

    if not yml_path.exists() and not yaml_path.exists():
        return [
            Violation(
                project=name,
                check="dependabot-exists",
                message="missing .github/dependabot.yml",
                severity="error",
            )
        ]
    return []


def check_dependabot_structure(project_path: Path) -> list[Violation]:
    """Validate dependabot.yml content structure."""
    if yaml is None:
        return [
            Violation(
                project=project_path.name,
                check="dependabot-parse",
                message="PyYAML not installed -- cannot validate YAML content",
                severity="warning",
            )
        ]

    name = project_path.name
    violations: list[Violation] = []

    yml_path = project_path / ".github" / "dependabot.yml"
    yaml_path = project_path / ".github" / "dependabot.yaml"
    config_path = yml_path if yml_path.exists() else yaml_path

    if not config_path.exists():
        return []  # Already caught by check_dependabot_exists

    try:
        content = config_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
    except (OSError, UnicodeDecodeError) as exc:
        violations.append(
            Violation(
                project=name,
                check="dependabot-parse",
                message=f"cannot read dependabot config: {exc}",
                severity="error",
            )
        )
        return violations
    except yaml.YAMLError as exc:
        violations.append(
            Violation(
                project=name,
                check="dependabot-parse",
                message=f"invalid YAML in dependabot config: {exc}",
                severity="error",
            )
        )
        return violations

    if not isinstance(data, dict):
        violations.append(
            Violation(
                project=name,
                check="dependabot-structure",
                message="dependabot config root must be a mapping",
                severity="error",
            )
        )
        return violations

    # Check version
    version = data.get("version")
    if version != EXPECTED_VERSION:
        violations.append(
            Violation(
                project=name,
                check="dependabot-version",
                message=f"expected version: {EXPECTED_VERSION}, got: {version}",
                severity="error",
            )
        )

    # Check updates list
    updates = data.get("updates")
    if not isinstance(updates, list) or len(updates) == 0:
        violations.append(
            Violation(
                project=name,
                check="dependabot-updates",
                message="updates must be a non-empty list",
                severity="error",
            )
        )
        return violations

    for idx, entry in enumerate(updates):
        if not isinstance(entry, dict):
            violations.append(
                Violation(
                    project=name,
                    check="dependabot-entry",
                    message=f"updates[{idx}] must be a mapping",
                    severity="error",
                )
            )
            continue

        # Required fields
        for req_field in REQUIRED_UPDATE_FIELDS:
            if req_field not in entry:
                violations.append(
                    Violation(
                        project=name,
                        check="dependabot-entry",
                        message=f"updates[{idx}] missing required field: {req_field}",
                        severity="error",
                    )
                )

        # Schedule fields
        schedule = entry.get("schedule")
        if isinstance(schedule, dict):
            for sched_field in REQUIRED_SCHEDULE_FIELDS:
                if sched_field not in schedule:
                    violations.append(
                        Violation(
                            project=name,
                            check="dependabot-schedule",
                            message=f"updates[{idx}].schedule missing: {sched_field}",
                            severity="error",
                        )
                    )
            # Timezone check
            tz = schedule.get("timezone")
            if tz and tz != EXPECTED_TIMEZONE:
                violations.append(
                    Violation(
                        project=name,
                        check="dependabot-timezone",
                        message=f"updates[{idx}].schedule.timezone: expected {EXPECTED_TIMEZONE}, got {tz}",
                    )
                )

        # Labels check for pip ecosystem
        ecosystem = entry.get("package-ecosystem", "")
        if ecosystem == "pip":
            labels = entry.get("labels", [])
            if sorted(labels) != sorted(EXPECTED_PIP_LABELS):
                violations.append(
                    Violation(
                        project=name,
                        check="dependabot-labels",
                        message=f"updates[{idx}] pip labels: expected {EXPECTED_PIP_LABELS}, got {labels}",
                    )
                )

    return violations


def validate_project(project_path: Path) -> ProjectInfo:
    """Run all dependabot checks for a project."""
    info = ProjectInfo(path=str(project_path), name=project_path.name)
    info.violations.extend(check_dependabot_exists(project_path))
    info.violations.extend(check_dependabot_structure(project_path))
    return info


def write_report(infos: list[ProjectInfo]) -> None:
    """Write JSON report to .sisyphus/reports/."""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "tool": "check_dependabot_config",
        "version": "1.0.0",
        "projects_scanned": len(infos),
        "total_violations": sum(len(p.violations) for p in infos),
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
    }

    REPORT_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def print_summary(infos: list[ProjectInfo]) -> None:
    """Print ANSI colored summary."""
    total_violations = sum(len(p.violations) for p in infos)

    print(f"\n{Ansi.BOLD}Dependabot Config Report{Ansi.RESET}")
    print(f"{'=' * 60}")
    print(f"Projects scanned: {len(infos)}")
    print(f"Total violations: {total_violations}")
    print()

    for info in infos:
        if not info.violations:
            continue
        print(f"{Ansi.CYAN}{info.name}{Ansi.RESET}")
        for v in info.violations:
            color = Ansi.RED if v.severity == "error" else Ansi.YELLOW
            print(f"  {color}[{v.severity}]{Ansi.RESET} {v.check}: {v.message}")

    if total_violations == 0:
        print(f"\n{Ansi.GREEN}All dependabot configs are standardized.{Ansi.RESET}")
    else:
        errors = sum(1 for p in infos for v in p.violations if v.severity == "error")
        warnings = total_violations - errors
        print(
            f"\n{Ansi.RED}{errors} error(s){Ansi.RESET}, {Ansi.YELLOW}{warnings} warning(s){Ansi.RESET}"
        )


def main() -> int:
    """Orchestrate dependabot config validation."""
    args = parse_args()
    root = Path(args.root).resolve()

    projects = discover_all_projects(root)
    if not projects:
        print(
            f"{Ansi.RED}No flext-* projects found under {root}{Ansi.RESET}",
            file=sys.stderr,
        )
        return 1

    infos: list[ProjectInfo] = []
    for project_path in projects:
        infos.append(validate_project(project_path))

    if args.json_output:
        write_report(infos)
        total = sum(len(p.violations) for p in infos)
        data = {
            "projects_scanned": len(infos),
            "total_violations": total,
            "report_path": str(REPORT_PATH),
        }
        print(json.dumps(data, indent=2))
    else:
        print_summary(infos)

    write_report(infos)

    total_violations = sum(len(p.violations) for p in infos)
    if args.strict:
        return 1 if total_violations > 0 else 0

    # By default, only fail on errors (not warnings)
    errors = sum(1 for p in infos for v in p.violations if v.severity == "error")
    return 1 if errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
