#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
"""Validate script-generated artifact naming under .reports/."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_USAGE = 2
EXIT_INFRA = 3

ARTIFACT_PATTERN = re.compile(r"^[a-z][-a-z0-9]*--[a-z]+--[a-z][-a-z0-9]*\.[a-z]+$")
VALIDATED_TOP_DIRS = {"."}
SKIPPED_TOP_DIRS = {"evidence", "plans", "drafts", "validation", "dependencies"}
SKIPPED_FILES = {".gitkeep"}


class UsageError(Exception):
    """UsageError class."""

    pass


class InfraError(Exception):
    """InfraError class."""

    pass


@dataclass(frozen=True)
class NamingViolation:
    """NamingViolation class."""

    path: str
    filename: str
    reason: str
    suggestion: str


def eprint(message: str) -> None:
    """Eprint function."""
    print(message, file=sys.stderr)


def artifact_name(skill: str, kind: str, slug: str) -> str:
    """artifact_name function."""
    return f"{skill}--{kind}--{slug}.{kind}"


def validate_artifact_name(filename: str) -> bool:
    """validate_artifact_name function."""
    return bool(ARTIFACT_PATTERN.match(filename))


def parse_args(argv: list[str]) -> argparse.Namespace:
    """parse_args function."""
    parser = argparse.ArgumentParser(
        description=(
            "Validate .reports artifact files follow "
            "<skill>--<kind>--<slug>.<ext> naming contract."
        ),
    )
    _ = parser.add_argument("--root", required=True, help="Workspace/project root")
    _ = parser.add_argument(
        "--mode",
        choices=["baseline", "strict"],
        default="baseline",
        help="Validation mode (accepted for skill_validate contract)",
    )
    try:
        return parser.parse_args(argv)
    except SystemExit as exc:
        code = int(exc.code) if isinstance(exc.code, int) else EXIT_USAGE
        if code == 0:
            raise
        msg = "invalid CLI arguments"
        raise UsageError(msg) from exc


def should_validate(path: Path, reports_root: Path) -> bool:
    """should_validate function."""
    if not path.is_file():
        return False
    if path.name in SKIPPED_FILES:
        return False

    try:
        relative = path.relative_to(reports_root)
    except ValueError:
        return False

    if not relative.parts:
        return False

    if len(relative.parts) == 1:
        return True
    top_dir = relative.parts[0]
    if top_dir in SKIPPED_TOP_DIRS:
        return False
    return top_dir in VALIDATED_TOP_DIRS


def collect_artifacts(reports_root: Path) -> list[Path]:
    """collect_artifacts function."""
    if not reports_root.exists():
        return []
    return sorted(
        path for path in reports_root.rglob("*") if should_validate(path, reports_root)
    )


def slugify(value: str) -> str:
    """Slugify function."""
    text = value.lower().replace("_", "-").replace(" ", "-")
    text = re.sub(r"[^a-z0-9-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "artifact"


def suggest_filename(filename: str) -> str:
    """suggest_filename function."""
    path = Path(filename)
    ext = path.suffix.lstrip(".").lower()
    stem = slugify(path.stem)
    kind = ext if ext.isalpha() else "json"

    parts = path.name.split("--")
    skill = "scripts-infra"
    if len(parts) >= 3:
        possible_skill = parts[0]
        if re.match(r"^[a-z][-a-z0-9]*$", possible_skill):
            skill = possible_skill

    return artifact_name(skill, kind, stem)


def validate(
    *,
    repo_root: Path,
    reports_root: Path,
) -> list[NamingViolation]:
    """Validate function."""
    artifacts = collect_artifacts(reports_root)
    violations: list[NamingViolation] = []

    eprint("Artifact Naming Validation")
    eprint(f"Scanned artifacts: {len(artifacts)}")

    for artifact in artifacts:
        filename = artifact.name
        rel = artifact.relative_to(repo_root).as_posix()

        if validate_artifact_name(filename):
            continue

        violations.append(
            NamingViolation(
                path=rel,
                filename=filename,
                reason="filename does not match <skill>--<kind>--<slug>.<ext>",
                suggestion=suggest_filename(filename),
            )
        )

    if violations:
        eprint(f"Violations found: {len(violations)}")
        for item in violations:
            eprint(f"- {item.path}: {item.reason}; suggestion: {item.suggestion}")
    else:
        eprint("No violations found.")

    return violations


def write_report(report_path: Path, violations: list[NamingViolation]) -> None:
    """write_report function."""
    payload = {
        "total_violations": len(violations),
        "violations": [
            {
                "filename": item.filename,
                "path": item.path,
                "reason": item.reason,
                "suggestion": item.suggestion,
            }
            for item in sorted(violations, key=lambda entry: entry.path)
        ],
    }

    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        _ = report_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        msg = f"cannot write report: {report_path}"
        raise InfraError(msg) from exc


def run_main(argv: list[str]) -> int:
    """run_main function."""
    violation_count = 0
    try:
        args = parse_args(argv)
        repo_root = Path(args.root).resolve()
        _mode = str(args.mode)

        if not repo_root.exists() or not repo_root.is_dir():
            msg = f"--root must point to an existing directory: {repo_root}"
            raise UsageError(msg)

        reports_root = repo_root / ".reports"
        report_path = repo_root / ".claude" / "skills" / "scripts-infra" / "report.json"

        violations = validate(repo_root=repo_root, reports_root=reports_root)
        violation_count = len(violations)
        write_report(report_path, violations)
        eprint(f"Violations report: {report_path}")
        return EXIT_PASS if violation_count == 0 else EXIT_FAIL
    except UsageError as exc:
        eprint(f"ERROR: {exc}")
        return EXIT_USAGE
    except InfraError as exc:
        eprint(f"ERROR: {exc}")
        return EXIT_INFRA
    except Exception as exc:
        eprint(f"ERROR: unexpected infra failure: {exc}")
        return EXIT_INFRA
    finally:
        print(json.dumps({"violation_count": violation_count}, separators=(",", ":")))


def main() -> None:
    """Main function."""
    raise SystemExit(run_main(sys.argv[1:]))


if __name__ == "__main__":
    main()
