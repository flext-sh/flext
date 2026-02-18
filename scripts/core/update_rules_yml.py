#!/usr/bin/env python3
"""Update all rules.yml files to convert ripgrep/regex rules to ast-grep.

Reads each rules.yml, converts ripgrep/regex entries to ast-grep type,
and writes back. Preserves all other fields (fix_auto, fix_instruction, etc).
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


SKILLS_DIR = Path(".claude/skills")

# Skills where Markdown/Dockerfile/gitignore rules can't use ast-grep
# These get converted to 'custom' type instead
CUSTOM_ONLY_RULES: set[str] = {
    # Markdown rules (ast-grep doesn't support Markdown)
    "readme-preamble",
    "readme-ecosystem-link",
    "readme-has-key-features",
    "readme-has-installation",
    "readme-has-usage",
    "readme-has-architecture",
    "readme-has-contributing",
    "readme-has-license",
    "docs-absolute-paths",
    "docs-no-todo-fixme",
    "no-trailing-whitespace-in-md",
    "docs-has-readme",
    # Pointer policy rules (.md files)
    "pointer-reference-claude",
    "pointer-no-duplication-policy",
    # Quality gates (target Makefile/pyproject.toml)
    "require-ruff-config",
    "require-test-target",
    # Gitignore patterns
    "gitignore-has-pycache-pattern",
    "gitignore-has-dist-pattern",
}

# Fix type conversions: regex fix → ast-grep fix
FIX_TYPE_CONVERSIONS: dict[str, dict[str, str]] = {
    "no-breakpoint": {
        "fix_type": "ast-grep",
        "fix_file": "rules/no-breakpoint-fix.yml",
    },
    "no-assert-false": {
        "fix_type": "ast-grep",
        "fix_file": "rules/no-assert-false-fix.yml",
    },
}


def update_rules_yml(skill_dir: Path) -> bool:
    rules_yml = skill_dir / "rules.yml"
    if not rules_yml.exists():
        return False

    with open(rules_yml) as f:
        data = yaml.safe_load(f)

    if not data or "rules" not in data:
        return False

    changed = False
    skill_name = skill_dir.name
    rules_subdir = skill_dir / "rules"

    for rule in data["rules"]:
        rule_id = rule.get("id", "")
        rule_type = rule.get("type", "")

        if rule_type not in ("ripgrep", "regex"):
            continue

        if rule_id in CUSTOM_ONLY_RULES:
            rule["type"] = "custom"
            if "pattern" in rule:
                del rule["pattern"]
            if "flags" in rule:
                del rule["flags"]
            changed = True
            continue

        rule_file = rules_subdir / f"{rule_id}.yml"
        if not rule_file.exists():
            print(
                f"  WARNING: {skill_name}/{rule_id} — ast-grep rule file not found: {rule_file}"
            )
            continue

        rule["type"] = "ast-grep"
        rule["file"] = f"rules/{rule_id}.yml"
        rule["count_by"] = "rule_id"

        if "pattern" in rule:
            del rule["pattern"]
        if "flags" in rule:
            del rule["flags"]

        if rule_id in FIX_TYPE_CONVERSIONS:
            conv = FIX_TYPE_CONVERSIONS[rule_id]
            rule["fix_type"] = conv["fix_type"]
            rule["fix_file"] = conv["fix_file"]
            if "fix_pattern" in rule:
                del rule["fix_pattern"]
            if "fix_replacement" in rule:
                del rule["fix_replacement"]
        elif rule.get("fix_type") == "regex":
            rule["fix_type"] = "ast-grep"
            if "fix_pattern" in rule:
                del rule["fix_pattern"]
            if "fix_replacement" in rule:
                del rule["fix_replacement"]

        changed = True

    if changed:
        with open(rules_yml, "w") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=120,
            )
    return changed


def main() -> None:
    updated = 0
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        if update_rules_yml(skill_dir):
            print(f"  Updated: {skill_dir.name}/rules.yml")
            updated += 1

    print(f"\nUpdated {updated} rules.yml files")


if __name__ == "__main__":
    main()
