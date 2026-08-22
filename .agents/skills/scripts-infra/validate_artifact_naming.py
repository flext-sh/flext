#!/usr/bin/env python3
# Owner-Skill: .agents/skills/scripts-infra/SKILL.md
"""Validate script-generated artifact naming under .reports/."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import ClassVar

from flext_infra import c, m, t


class UsageError(Exception):
    """UsageError class."""


class InfraError(Exception):
    """InfraError class."""


class NamingViolation(m.BaseModel):
    """NamingViolation class."""

    model_config: ClassVar[t.ConfigDict] = m.ConfigDict(frozen=True)

    path: str = m.Field(description="Relative path to the artifact")
    filename: str = m.Field(description="Artifact filename")
    reason: str = m.Field(description="Reason for the violation")
    suggestion: str = m.Field(description="Suggested correct filename")


def eprint(message: str) -> None:
    """Eprint function."""
    print(message, file=sys.stderr)


def artifact_name(skill: str, kind: str, slug: str) -> str:
    """artifact_name function."""
    return f"{skill}--{kind}--{slug}.{kind}"


def validate_artifact_name(filename: str) -> bool:
    """validate_artifact_name function."""
    return bool(c.Infra.SKILL_REPORT_ARTIFACT_NAME_RE.match(filename))


def parse_args(argv: t.StrSequence) -> argparse.Namespace:
    """parse_args function."""
    parser = argparse.ArgumentParser(
        description=(
            "Validate .reports artifact files follow "
            "<skill>--<kind>--<slug>.<ext> naming contract."
        ),
    )
    _ = parser.add_argument(
        "--root",
        required=True,
        help="Repository root path used to resolve .reports artifacts",
    )
    _ = parser.add_argument(
        "--mode",
        choices=["baseline", "strict"],
        default="baseline",
        help="Validation mode (accepted for skill_validate contract)",
    )
    try:
        return parser.parse_args(argv)
    except SystemExit as exc:
        code = (
            exc.code if isinstance(exc.code, int) else int(c.Infra.ScriptExitCode.USAGE)
        )
        if code == 0:
            raise
        msg = "invalid CLI arguments"
        raise UsageError(msg) from exc


def should_validate(path: Path, reports_root: Path) -> bool:
    """should_validate function."""
    validate_path = (
        path.is_file() and path.name not in c.Infra.SKILL_REPORT_SKIPPED_FILES
    )
    try:
        relative = path.relative_to(reports_root)
    except ValueError:
        validate_path = False
    else:
        top_dir = relative.parts[0] if relative.parts else ""
        validate_path = validate_path and (
            len(relative.parts) == 1
            or (
                top_dir not in c.Infra.SKILL_REPORT_SKIPPED_TOP_DIRS
                and top_dir in c.Infra.SKILL_REPORT_VALIDATED_TOP_DIRS
            )
        )
    return validate_path


def collect_artifacts(reports_root: Path) -> t.SequenceOf[Path]:
    """collect_artifacts function."""
    if not reports_root.exists():
        return []
    return sorted(
        path for path in reports_root.rglob("*") if should_validate(path, reports_root)
    )


def slugify(value: str) -> str:
    """Slugify function."""
    text = value.lower().replace("_", "-").replace(" ", "-")
    text = c.Infra.SKILL_REPORT_ARTIFACT_SLUG_INVALID_RE.sub("-", text)
    text = c.Infra.SKILL_REPORT_ARTIFACT_MULTI_DASH_RE.sub("-", text).strip("-")
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
        if c.Infra.SKILL_REPORT_ARTIFACT_SKILL_RE.match(possible_skill):
            skill = possible_skill

    return artifact_name(skill, kind, stem)


def validate(
    *,
    repo_root: Path,
    reports_root: Path,
) -> t.SequenceOf[NamingViolation]:
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
            ),
        )

    if violations:
        eprint(f"Violations found: {len(violations)}")
        for item in violations:
            eprint(f"- {item.path}: {item.reason}; suggestion: {item.suggestion}")
    else:
        eprint("No violations found.")

    return violations


def write_report(report_path: Path, violations: t.SequenceOf[NamingViolation]) -> None:
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


def _run_validation(args: argparse.Namespace) -> tuple[int, int]:
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
    exit_code = (
        int(c.Infra.ScriptExitCode.PASS)
        if violation_count == 0
        else int(c.Infra.ScriptExitCode.FAIL)
    )
    return exit_code, violation_count


def run_main(argv: t.StrSequence) -> int:
    """run_main function."""
    violation_count = 0
    try:
        exit_code, violation_count = _run_validation(parse_args(argv))
    except UsageError as exc:
        eprint(f"ERROR: {exc}")
        exit_code = int(c.Infra.ScriptExitCode.USAGE)
    except InfraError as exc:
        eprint(f"ERROR: {exc}")
        exit_code = int(c.Infra.ScriptExitCode.INFRA)
    except Exception as exc:
        eprint(f"ERROR: unexpected infra failure: {exc}")
        exit_code = int(c.Infra.ScriptExitCode.INFRA)
    print(json.dumps({"violation_count": violation_count}, separators=(",", ":")))
    return exit_code


def main() -> None:
    """Main function."""
    raise SystemExit(run_main(sys.argv[1:]))


if __name__ == "__main__":
    main()
