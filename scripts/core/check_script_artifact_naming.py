#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
"""Validate script-generated artifact naming under .sisyphus/."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from artifact_naming import artifact_name, validate_artifact_name


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SISYPHUS_ROOT = REPO_ROOT / ".sisyphus"
REPORT_PATH = (
    SISYPHUS_ROOT / "reports" / "scripts-infra--json--artifact-naming-violations.json"
)
VALIDATED_TOP_DIRS = {"reports", "baselines"}
SKIPPED_TOP_DIRS = {"evidence", "plans", "drafts"}
SKIPPED_FILES = {".gitkeep"}


class Ansi:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    RESET = "\033[0m"


@dataclass(frozen=True)
class NamingViolation:
    path: str
    filename: str
    reason: str
    suggestion: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate .sisyphus artifact files follow "
            "<skill>--<kind>--<slug>.<ext> naming contract."
        ),
    )
    return parser.parse_args()


def should_validate(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.name in SKIPPED_FILES:
        return False

    try:
        relative = path.relative_to(SISYPHUS_ROOT)
    except ValueError:
        return False

    if not relative.parts:
        return False

    top_dir = relative.parts[0]
    if top_dir in SKIPPED_TOP_DIRS:
        return False
    return top_dir in VALIDATED_TOP_DIRS


def collect_artifacts() -> list[Path]:
    if not SISYPHUS_ROOT.exists():
        return []
    return sorted(path for path in SISYPHUS_ROOT.rglob("*") if should_validate(path))


def slugify(value: str) -> str:
    text = value.lower().replace("_", "-").replace(" ", "-")
    text = re.sub(r"[^a-z0-9-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "artifact"


def suggest_filename(filename: str) -> str:
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


def print_header() -> None:
    print(f"{Ansi.CYAN}Artifact Naming Validation{Ansi.RESET}")
    print(f"{Ansi.CYAN}{'PATH':<70} {'STATUS':<10} DETAILS{Ansi.RESET}")


def print_ok(path: Path) -> None:
    rel = path.relative_to(REPO_ROOT).as_posix()
    print(f"{rel:<70} {Ansi.GREEN}{'OK':<10}{Ansi.RESET} contract match")


def print_violation(violation: NamingViolation) -> None:
    details = (
        f"{violation.path:<70} {Ansi.RED}{'VIOLATION':<10}{Ansi.RESET} "
        + f"{violation.reason}; suggestion: {violation.suggestion}"
    )
    print(details)


def write_report(violations: list[NamingViolation]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
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
    _ = REPORT_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    _ = parse_args()

    artifacts = collect_artifacts()
    violations: list[NamingViolation] = []

    print_header()
    for artifact in artifacts:
        filename = artifact.name
        rel = artifact.relative_to(REPO_ROOT).as_posix()

        if validate_artifact_name(filename):
            print_ok(artifact)
            continue

        suggestion = suggest_filename(filename)
        violation = NamingViolation(
            path=rel,
            filename=filename,
            reason="filename does not match <skill>--<kind>--<slug>.<ext>",
            suggestion=suggestion,
        )
        violations.append(violation)
        print_violation(violation)

    write_report(violations)
    summary = (
        f"\n{Ansi.CYAN}Summary:{Ansi.RESET} total={len(artifacts)} "
        + f"{Ansi.GREEN}ok={len(artifacts) - len(violations)}{Ansi.RESET} "
        + f"{Ansi.RED}violations={len(violations)}{Ansi.RESET}"
    )
    print(summary)
    print(f"Violations report: {REPORT_PATH.relative_to(REPO_ROOT)}")

    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
