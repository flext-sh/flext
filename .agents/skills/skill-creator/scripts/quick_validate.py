#!/usr/bin/env python3
"""AI Hub governance hook projection: quick_validate.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

# Copyright (c) 2025 FLEXT Team. All rights reserved.
import re
import sys
from pathlib import Path

"""Quick validation script for skills - minimal version."""


_HYPHEN_CASE_PATTERN = r"^[a-z0-9-]+$"


def _read_frontmatter(skill_md: Path) -> str | None:
    """Read and extract the YAML frontmatter block.

    Args:
        skill_md: Path to the SKILL.md file.

    Returns:
        The frontmatter block content, or None when missing or invalid.

    """
    if not skill_md.exists():
        return None
    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    return match.group(1)


def _validate_name(frontmatter: str) -> str | None:
    """Validate the skill name field.

    Args:
        frontmatter: Frontmatter block content.

    Returns:
        Error message when invalid, None when valid.

    """
    name_match = re.search(r"name:\s*(.+)", frontmatter)
    if not name_match:
        return None
    name = name_match.group(1).strip()
    if not re.match(_HYPHEN_CASE_PATTERN, name):
        return (
            f"Name '{name}' should be hyphen-case "
            "(lowercase letters, digits, and hyphens only)"
        )
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return (
            f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        )
    return None


def _validate_description(frontmatter: str) -> str | None:
    """Validate the skill description field.

    Args:
        frontmatter: Frontmatter block content.

    Returns:
        Error message when invalid, None when valid.

    """
    if "description:" not in frontmatter:
        return "Missing 'description' in frontmatter"
    desc_match = re.search(r"description:\s*(.+)", frontmatter)
    if desc_match:
        description = desc_match.group(1).strip()
        if "<" in description or ">" in description:
            return "Description cannot contain angle brackets (< or >)"
    return None


def validate_skill(skill_path: str) -> tuple[bool, str]:
    """Basic validation of a skill.

    Args:
        skill_path: Path to the skill directory.

    Returns:
        Tuple of validity flag and human-readable validation message.

    """
    frontmatter = _read_frontmatter(Path(skill_path) / "SKILL.md")
    if frontmatter is None:
        return False, "SKILL.md not found"
    if "name:" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    for validator in (_validate_name, _validate_description):
        error = validator(frontmatter)
        if error:
            return False, error
    return True, "Skill is valid!"


EXPECTED_ARG_COUNT = 2

if __name__ == "__main__":
    if len(sys.argv) != EXPECTED_ARG_COUNT:
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    sys.exit(0 if valid else 1)
