# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
"""Artifact naming helpers for the <skill>--<kind>--<slug>.<ext> contract."""

import re
from pathlib import Path

ARTIFACT_PATTERN = re.compile(r"^[a-z][-a-z0-9]*--[a-z]+--[a-z][-a-z0-9]*\.[a-z]+$")
SISYPHUS_ROOT = Path(".sisyphus")
ARTIFACT_DIRS = ("reports", "baselines", "evidence")


def artifact_name(skill: str, kind: str, slug: str) -> str:
    return f"{skill}--{kind}--{slug}.{kind}"


def artifact_path(directory: str, skill: str, kind: str, slug: str) -> Path:
    return SISYPHUS_ROOT / directory / artifact_name(skill, kind, slug)


def validate_artifact_name(filename: str) -> bool:
    return bool(ARTIFACT_PATTERN.match(filename))


def extract_skill_from_artifact(filename: str) -> str | None:
    parts = filename.split("--")
    return parts[0] if len(parts) >= 3 else None
