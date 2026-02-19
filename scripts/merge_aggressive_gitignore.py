#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-maintenance/SKILL.md
"""Merge aggressive whitelist rules with existing .gitignore files.

Preserves existing project-specific rules while adding whitelist protection.

Copyright (c) 2025 Flext Telecom. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

from pathlib import Path

FLEXT_ROOT = Path(__file__).resolve().parents[1]

# Core whitelist rules to add
WHITELIST_HEADER = """# ============================================================================
# AGGRESSIVE WHITELIST - Block everything by default, explicitly allow needed files
# ============================================================================
"""

WHITELIST_BLOCK = """
# Block everything at root level
/*
/*/
"""

WHITELIST_ALLOW = """
# ============================================================================
# ALLOWED: Core Directories
# ============================================================================
!src/
!tests/
!docs/
!examples/
!scripts/
!ansible/
!docker/
!dbt/
!.github/
!.vscode/

# ============================================================================
# ALLOWED: Root-Level Configuration Files
# ============================================================================
!pyproject.toml
!poetry.lock
!Makefile
!README.md
!CLAUDE.md
!LICENSE
!.python-version
!.tool-versions
!.gitignore
!.gitattributes
!.pre-commit-config.yaml

# Environment templates (NOT .env - keep secrets out!)
!.env.example
!.env.test
!.env.template
!.env.*.example

# Docker files
!Dockerfile
!Dockerfile.*
!docker-compose.yml
!docker-compose.*.yml
!.dockerignore

# ============================================================================
# ALLOWED: Contents Inside Whitelisted Directories
# ============================================================================
!src/**
!tests/**
!docs/**
!examples/**
!scripts/**
!ansible/**
!docker/**
!dbt/**
!.github/**
!.vscode/**
"""

SECURITY_BLOCKS = """
# ============================================================================
# SECURITY: Explicit Blocks (NEVER commit these)
# ============================================================================
.env
.internal.invalid
.env.production
.env.development
**/.env
*.key
*.pem
*.p12
*.pfx
credentials.json
secrets.yaml
secrets.yml
"""


def merge_gitignore(project_dir: Path) -> bool:
    """Merge aggressive whitelist with existing .gitignore.

    Args:
        project_dir: Project directory path

    Returns:
        True if successful, False otherwise

    """
    gitignore_file = project_dir / ".gitignore"

    # Read existing .gitignore
    existing_content = ""
    existing_rules = []
    has_whitelist = False

    if gitignore_file.exists():
        existing_content = gitignore_file.read_text()
        existing_rules = [
            line.strip() for line in existing_content.split("\n") if line.strip()
        ]

        # Check if already has whitelist rules
        if "/*" in existing_content and "/!src/" in existing_content.replace(" ", ""):
            has_whitelist = True
            print("   ℹ️  Already has whitelist rules")

    # Extract project-specific rules (not common patterns)
    common_patterns = {
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".hypothesis",
        ".coverage",
        "htmlcov",
        "dist",
        "build",
        "*.egg-info",
        ".venv",
        "venv",
        "env",
        ".DS_Store",
        "*.swp",
        ".idea",
        "*.log",
        ".env",
    }

    project_specific = []
    for rule in existing_rules:
        if not rule.startswith("#"):
            # Keep if not a common pattern
            rule_clean = rule.lstrip("!").strip("/")
            if rule_clean not in common_patterns and not any(
                p in rule for p in [".pyc", "__pycache__", ".cache", ".egg"]
            ):
                project_specific.append(rule)

    # Build merged content
    merged_lines = []

    # 1-4. Add core rules
    merged_lines.extend((
        WHITELIST_HEADER,
        WHITELIST_BLOCK,
        WHITELIST_ALLOW,
        SECURITY_BLOCKS,
    ))

    # 5. Add project-specific rules if any
    if project_specific:
        merged_lines.extend((
            "\n# ============================================================================",
            f"# PROJECT-SPECIFIC RULES: {project_dir.name}",
            "# ============================================================================\n",
        ))
        merged_lines.extend(project_specific)

    # 6-7. Add common patterns and safety rules
    merged_lines.extend((
        "\n# ============================================================================",
        "# COMMON PATTERNS: Artifacts inside allowed directories",
        "# ============================================================================",
        "**/__pycache__/",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        ".pytest_cache/",
        ".mypy_cache/",
        ".ruff_cache/",
        ".hypothesis/",
        ".coverage",
        "htmlcov/",
        "dist/",
        "build/",
        "*.egg-info/",
        "\n# ============================================================================",
        "# SAFETY: Keep .gitkeep files",
        "# ============================================================================",
        "!**/.gitkeep",
    ))

    merged_content = "\n".join(merged_lines)

    # Backup existing if it has content
    if existing_content and not has_whitelist:
        backup_file = project_dir / ".gitignore.backup"
        backup_file.write_text(existing_content)
        print("   📦 Backed up existing .gitignore")

    # Write merged content
    gitignore_file.write_text(merged_content)

    if has_whitelist:
        print("   🔄 Updated whitelist rules")
    else:
        print("   ✅ Merged aggressive whitelist with existing rules")

    return True


def main() -> None:
    """Merge .gitignore for all FLEXT projects."""
    print("=" * 80)
    print("🔒 Merging Aggressive Whitelist into Existing .gitignore Files")
    print("=" * 80)
    print("\nStrategy:")
    print("  • Preserve existing project-specific rules")
    print("  • Add aggressive whitelist (block all, allow specific)")
    print("  • Backup existing files as .gitignore.backup")
    print("  • Merge intelligently without duplication")
    print("\n" + "=" * 80 + "\n")

    # Find all projects with pyproject.toml
    projects = []
    for project_dir in sorted(FLEXT_ROOT.iterdir()):
        if not project_dir.is_dir():
            continue

        pyproject_file = project_dir / "pyproject.toml"
        if not pyproject_file.exists():
            continue

        projects.append(project_dir)

    print(f"Found {len(projects)} FLEXT projects\n")

    success_count = 0
    for project_dir in projects:
        print(f"🔧 {project_dir.name}")
        if merge_gitignore(project_dir):
            success_count += 1

    print("\n" + "=" * 80)
    print(
        f"✅ Merged aggressive .gitignore in {success_count}/{len(projects)} projects",
    )
    print("=" * 80)
    print("\n📋 Next Steps:")
    print("  1. Review changes: cd <project> && git diff .gitignore")
    print("  2. Test: git status (check what's now ignored)")
    print("  3. If needed: git add -f <file> to force-add blocked files")
    print("  4. Restore backup if issues: mv .gitignore.backup .gitignore")


if __name__ == "__main__":
    main()
