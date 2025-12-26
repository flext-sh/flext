#!/usr/bin/env python3
"""FLEXT Cursor Rules Auto-Update Script.

Automatically updates Cursor rules based on CLAUDE.md changes.
Maintains synchronization between documentation and automation.

Usage:
    python3 scripts/update_cursor_rules.py [--force] [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


# FLEXT result pattern
class Result[T]:
    """A result type that can contain either a value or an error."""

    def __init__(self, value: T | None = None, error: str | None = None) -> None:
        """Initialize a Result with either a value or an error."""
        self.value = value
        self.error = error

    @property
    def is_success(self) -> bool:
        """Return True if the result contains a value (no error)."""
        return self.error is None

    @property
    def is_failure(self) -> bool:
        """Return True if the result contains an error."""
        return self.error is not None

    @classmethod
    def ok(cls, value: T) -> Result[T]:
        """Create a successful result with the given value."""
        return cls(value=value)

    @classmethod
    def err(cls, error: str) -> Result[T]:
        """Create a failed result with the given error message."""
        return cls(error=error)


class CursorRulesUpdater:
    """Automatically updates Cursor rules from CLAUDE.md."""

    def __init__(self, project_root: Path) -> None:
        """Initialize the Cursor rules updater with project root."""
        self.project_root = project_root
        self.claude_md = project_root / "CLAUDE.md"
        self.cursorrules = project_root / ".cursorrules"
        self.config_file = project_root / ".cursor" / "config.json"

    def get_claude_md_hash(self) -> str:
        """Get hash of CLAUDE.md for change detection."""
        if not self.claude_md.exists():
            return ""

        content = self.claude_md.read_text(encoding="utf-8")
        return hashlib.sha256(content.encode()).hexdigest()

    def load_current_config(self) -> dict[str, Any]:
        """Load current Cursor configuration."""
        if not self.config_file.exists():
            return {}

        try:
            return json.loads(self.config_file.read_text())
        except Exception:
            return {}

    def save_config(self, config: dict[str, Any]) -> Result[bool]:
        """Save updated configuration."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(json.dumps(config, indent=2))
            return Result.ok(True)
        except Exception as e:
            return Result.err(f"Failed to save config: {e}")

    def parse_claude_md_rules(self) -> dict[str, Any]:
        """Parse CLAUDE.md and extract automation rules."""
        if not self.claude_md.exists():
            return {}

        content = self.claude_md.read_text(encoding="utf-8")

        return {
            "import_order": self._extract_import_order_rules(),
            "type_system": self._extract_type_system_rules(),
            "architecture": self._extract_architecture_rules(),
            "quality_gates": self._extract_quality_gates(),
            "patterns": self._extract_patterns(),
            "skills": self._extract_skills(content),
        }

    def _extract_import_order_rules(self) -> dict[str, Any]:
        """Extract import order rules."""
        return {
            "enforce_order": True,
            "docstring_first": True,
            "future_imports_second": True,
            "standard_library_third": True,
            "third_party_fourth": True,
            "local_imports_last": True,
        }

    def _extract_type_system_rules(self) -> dict[str, Any]:
        """Extract type system rules."""
        return {
            "forbid_type_checking": True,
            "forbid_type_ignore": True,
            "forbid_cast": True,
            "forbid_any": True,
            "require_union_syntax": True,
            "require_concrete_types": True,
        }

    def _extract_architecture_rules(self) -> dict[str, Any]:
        """Extract architecture rules."""
        return {
            "tier_0": ["constants.py", "typings.py", "protocols.py"],
            "tier_1": ["models.py", "utilities.py"],
            "tier_2": ["servers/*.py"],
            "tier_3": ["services/*.py", "api.py"],
            "forbidden_cross_imports": True,
        }

    def _extract_quality_gates(self) -> dict[str, Any]:
        """Extract quality gates."""
        return {
            "import_order_check": True,
            "architecture_compliance": True,
            "type_safety": True,
            "test_coverage": True,
            "documentation_required": True,
        }

    def _extract_patterns(self) -> dict[str, Any]:
        """Extract FLEXT patterns."""
        return {
            "railway_oriented": True,
            "result_types": True,
            "namespace_aliases": True,
            "structural_typing": True,
        }

    def _extract_skills(self, content: str) -> dict[str, str]:
        """Extract available skills."""
        # Extract skills from the quick reference table
        skills = {}

        # Look for skill references in the content
        skill_patterns = [
            r"skill\s+`([^`]+)`",
            r"`([^`]+)`\s+skill",
        ]

        for pattern in skill_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                skills[match] = f"FLEXT skill: {match}"

        return skills

    def generate_cursor_config(self, rules: dict[str, Any]) -> dict[str, Any]:
        """Generate Cursor configuration from parsed rules."""
        current_config = self.load_current_config()

        # Update FLEXT section
        flext_config = current_config.get("flext", {})

        flext_config.update({
            "automation": {
                "enabled": True,
                "auto_validate": True,
                "auto_fix": False,
                "rules": rules,
                "last_updated": self.get_claude_md_hash(),
            },
            "commands": {
                "/flext-validate": {
                    "description": "Run FLEXT quality validations",
                    "command": "python3 cursor-agent-automation.py validate",
                },
                "/flext-fix": {
                    "description": "Auto-fix FLEXT violations",
                    "command": "python3 cursor-agent-automation.py fix",
                },
                "/flext-skills": {
                    "description": "Show available FLEXT skills",
                    "command": "python3 cursor-agent-automation.py skills",
                },
                "/flext-dev": {
                    "description": "FLEXT development helper",
                    "command": "make help",
                },
            },
        })

        # Add skills as individual commands
        for skill_name, skill_desc in rules.get("skills", {}).items():
            flext_config["commands"][f"/{skill_name}"] = {
                "description": skill_desc,
                "command": f"python3 cursor-agent-automation.py validate --skill {skill_name}",
            }

        current_config["flext"] = flext_config

        return current_config

    def update_cursor_rules_file(self, rules: dict[str, Any]) -> Result[bool]:
        """Update the .cursorrules file with new rules."""
        try:
            current_content = ""
            if self.cursorrules.exists():
                current_content = self.cursorrules.read_text()

            # Generate updated content
            updated_content = self._generate_cursorrules_content(rules)

            if updated_content != current_content:
                self.cursorrules.write_text(updated_content)
                return Result.ok(True)
            return Result.ok(True)  # No changes needed

        except Exception as e:
            return Result.err(f"Failed to update .cursorrules: {e}")

    def _generate_cursorrules_content(self, rules: dict[str, Any]) -> str:
        """Generate .cursorrules content from parsed rules."""
        lines = [
            "# FLEXT Ecosystem Cursor Rules",
            "# Auto-generated from CLAUDE.md",
            f"# Generated: {self.get_claude_md_hash()[:8]}",
            "# DO NOT EDIT - Regenerate with: python3 scripts/update_cursor_rules.py",
            "",
            "## FLEXT Ecosystem Standards",
            "",
            "You are an AI assistant working on the FLEXT Enterprise Data Integration Platform.",
            "Follow all global rules plus these FLEXT-specific standards.",
            "",
        ]

        # Add architecture rules
        if "architecture" in rules:
            rules["architecture"]
            lines.extend([
                "### Architecture Layering (ZERO TOLERANCE)",
                "",
                "```",
                "Tier 0 - Foundation (ZERO internal dependencies):",
                "  ├── constants.py    # Only StrEnum, Final, Literal",
                "  ├── typings.py      # Type aliases, TypeVars",
                "  └── protocols.py    # Interface definitions (Protocol classes)",
                "",
                "Tier 1 - Domain Foundation:",
                "  ├── models.py       # Pydantic models → Tier 0 only",
                "  └── utilities.py    # Helper functions → Tier 0, models",
                "",
                "Tier 2 - Infrastructure:",
                "  └── servers/*.py    # Server implementations → Tier 0, Tier 1 only",
                "",
                "Tier 3 - Application (Top Layer):",
                "  ├── services/*.py   # Business logic → All lower tiers",
                "  └── api.py          # Facade/API → All lower tiers",
                "```",
                "",
                "**RULE**: Lower tiers NEVER import from higher tiers.",
                "",
            ])

        # Add type system rules
        if "type_system" in rules:
            rules["type_system"]
            lines.extend([
                "### FLEXT Type System",
                "",
                "**Type Safety (Zero Tolerance)**:",
                "- No `TYPE_CHECKING` blocks - fix architecture",
                "- No `# type: ignore` - fix types properly",
                "- No `cast()` - use Models/Protocols/TypeGuards",
                "- No `Any` - concrete types everywhere",
                "",
                "**Modern Python Syntax**:",
                "```python",
                "# CORRECT",
                "status: str | None = None",
                "items: list[str] = []",
                "config: dict[str, int] = {}",
                "",
                "# WRONG",
                "status: Optional[str] = None",
                "items: List[str] = []",
                "config: Dict[str, int] = {}",
                "```",
                "",
            ])

        # Add quality gates
        if "quality_gates" in rules:
            lines.extend([
                "### Quality Gates (Mandatory)",
                "",
                "- Import order validation",
                "- Architecture compliance",
                "- Type safety enforcement",
                "- Railway-oriented programming",
                "- Namespace alias usage",
                "",
            ])

        # Add automation note
        lines.extend([
            "### Automation",
            "",
            "This file is automatically updated when CLAUDE.md changes.",
            "Use `/flext-validate` to run validations, `/flext-fix` to auto-fix issues.",
            "",
            "---",
        ])

        return "\n".join(lines)

    def needs_update(self) -> bool:
        """Check if update is needed."""
        current_config = self.load_current_config()
        current_hash = (
            current_config.get("flext", {})
            .get("automation", {})
            .get("last_updated", "")
        )
        new_hash = self.get_claude_md_hash()

        return current_hash != new_hash

    def update(
        self,
        *,
        force: bool = False,
        dry_run: bool = False,
    ) -> Result[dict[str, Any]]:
        """Update Cursor configuration from CLAUDE.md."""
        try:
            if not force and not self.needs_update():
                return Result.ok({"status": "no_update_needed"})

            # Parse CLAUDE.md rules
            rules = self.parse_claude_md_rules()

            # Generate new configuration
            new_config = self.generate_cursor_config(rules)

            if dry_run:
                return Result.ok({
                    "status": "dry_run",
                    "rules": rules,
                    "config": new_config,
                })

            # Save configuration
            config_result = self.save_config(new_config)
            if config_result.is_failure:
                return config_result

            # Update .cursorrules file
            rules_result = self.update_cursor_rules_file(rules)
            if rules_result.is_failure:
                return rules_result

            return Result.ok({
                "status": "updated",
                "rules": rules,
                "config": new_config,
            })

        except Exception as e:
            return Result.err(f"Update failed: {e}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update FLEXT Cursor Rules")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update even if no changes detected",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory",
    )

    args = parser.parse_args()

    updater = CursorRulesUpdater(args.project_root)
    result = updater.update(force=args.force, dry_run=args.dry_run)

    if result.is_success:
        data = result.value

        if data["status"] == "no_update_needed":
            print("✅ No updates needed - CLAUDE.md unchanged")
            return 0

        if data["status"] == "dry_run":
            print("🔍 Dry run - would update:")
            print(f"  • Rules: {len(data['rules'])} sections")
            print(f"  • Skills: {len(data['rules'].get('skills', {}))} skills")
            print(
                f"  • Commands: {len(data['config'].get('flext', {}).get('commands', {}))} commands",
            )
            return 0

        if data["status"] == "updated":
            print("✅ Cursor rules updated successfully!")
            print(f"  • Rules: {len(data['rules'])} sections")
            print(f"  • Skills: {len(data['rules'].get('skills', {}))} skills")
            print(
                f"  • Commands: {len(data['config'].get('flext', {}).get('commands', {}))} commands",
            )
            return 0

    else:
        print(f"❌ Update failed: {result.error}")
        return 1
    return None


if __name__ == "__main__":
    import sys

    sys.exit(main())
