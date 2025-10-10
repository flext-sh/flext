#!/usr/bin/env python3
"""Create aggressive whitelist .gitignore for all FLEXT projects.

Only permits specific whitelisted files and directories.
Everything else is blocked by default.

Copyright (c) 2025 client-a Telecom. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

from pathlib import Path

FLEXT_ROOT = Path("/home/marlonsc/flext")

# Aggressive whitelist .gitignore template
GITIGNORE_TEMPLATE = r"""# AGGRESSIVE WHITELIST .gitignore
# Default: Block everything, then explicitly allow specific files/directories
# This ensures only intended files are committed to version control

# ============================================================================
# BLOCK EVERYTHING BY DEFAULT
# ============================================================================
/*
/*/

# ============================================================================
# WHITELIST: Allowed Directories
# ============================================================================

# Source code and documentation
!src/
!tests/
!docs/
!examples/
!scripts/

# Infrastructure and DevOps
!ansible/
!docker/
!dbt/
!.github/
!.vscode/

# ============================================================================
# WHITELIST: Allowed Root-Level Files
# ============================================================================

# Project configuration
!pyproject.toml
!poetry.lock
!Makefile
!README.md
!CLAUDE.md
!LICENSE
!.python-version
!.tool-versions

# Environment templates (NOT .env itself - secrets stay out!)
!.env.example
!.env.test
!.env.template
!.env.*.example

# Git configuration
!.gitignore
!.gitattributes
!.git-blame-ignore-revs

# Docker
!Dockerfile
!Dockerfile.*
!docker-compose.yml
!docker-compose.*.yml
!.dockerignore

# CI/CD
!.gitlab-ci.yml
!.pre-commit-config.yaml

# ============================================================================
# BLOCK: Secrets and Sensitive Files (EXPLICIT BLOCKS)
# ============================================================================

# Environment files with actual secrets
.env
.internal.invalid
.env.production
.env.development
**/.env

# Credentials and keys
*.key
*.pem
*.p12
*.pfx
credentials.json
secrets.yaml
secrets.yml

# ============================================================================
# BLOCK: Build Artifacts and Generated Files
# ============================================================================

# Python build artifacts
dist/
build/
*.egg-info/
**/__pycache__/
**/*.pyc
**/*.pyo
**/*.pyd
.Python

# Coverage reports
htmlcov/
.coverage
coverage.json
.coverage.*
*.cover
.hypothesis/

# Type checking and linting caches
.mypy_cache/
.pytype/
.ruff_cache/
.pytest_cache/
.benchmarks/

# Virtual environments
.venv/
venv/
env/
ENV/
**/.venv/
**/venv/

# ============================================================================
# BLOCK: IDE and Editor Files
# ============================================================================

# VS Code settings (allow .vscode/ directory but block workspace files)
.vscode/*.code-workspace
.vscode/internal.invalid.json

# JetBrains IDEs
.idea/
*.iml
*.ipr
*.iws

# Vim
*.swp
*.swo
*~
.*.sw?

# Emacs
*~
\#*\#
.\#*

# Sublime Text
*.sublime-project
*.sublime-workspace

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# ============================================================================
# BLOCK: Temporary and Log Files
# ============================================================================

*.log
*.tmp
*.temp
.tmp/
tmp/
temp/
logs/

# ============================================================================
# BLOCK: Generated Data Files (Project-Specific)
# ============================================================================

# LDIF generated files
migrated_*.ldif
data/output/
data/generated/

# Database files
*.db
*.sqlite
*.sqlite3

# ============================================================================
# ALLOW: Contents of Whitelisted Directories
# ============================================================================

# Allow everything inside whitelisted directories
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

# But still block caches and artifacts inside those directories
src/**/__pycache__/
tests/**/__pycache__/
examples/**/__pycache__/
scripts/**/__pycache__/

src/**/*.pyc
tests/**/*.pyc
examples/**/*.pyc
scripts/**/*.pyc

# ============================================================================
# PROJECT-SPECIFIC EXCEPTIONS
# ============================================================================

# Allow .gitkeep files to preserve empty directories
!**/.gitkeep

# Allow fixture data in tests
!tests/fixtures/**/*.ldif
!tests/fixtures/**/*.json
!tests/fixtures/**/*.yaml
!tests/fixtures/**/*.yml

# Allow sample/example data
!examples/data/**
!docs/examples/**

# ============================================================================
# FINAL SAFETY NET
# ============================================================================

# Ensure these are NEVER committed, even if explicitly added
.env
**/.env
*.key
*.pem
credentials.json
secrets.yaml
secrets.yml
"""


def create_gitignore_for_project(project_dir: Path) -> bool:
    """Create aggressive .gitignore for a project.

    Args:
        project_dir: Project directory path

    Returns:
        True if successful, False otherwise

    """
    gitignore_file = project_dir / ".gitignore"

    # Backup existing .gitignore if it exists
    if gitignore_file.exists():
        backup_file = project_dir / ".gitignore.backup"
        gitignore_file.rename(backup_file)
        print("   📦 Backed up existing .gitignore to .gitignore.backup")

    gitignore_file.write_text(GITIGNORE_TEMPLATE)
    print("   ✅ Created aggressive whitelist .gitignore")
    return True


def main() -> None:
    """Create .gitignore for all FLEXT projects."""
    print("=" * 80)
    print("🔒 Creating Aggressive Whitelist .gitignore for All FLEXT Projects")
    print("=" * 80)
    print("\nWhitelist Policy:")
    print("  ✅ ALLOW: src/, tests/, docs/, examples/, scripts/")
    print("  ✅ ALLOW: ansible/, docker/, dbt/, .github/, .vscode/")
    print("  ✅ ALLOW: pyproject.toml, poetry.lock, Makefile, README.md")
    print("  ✅ ALLOW: .env.example, .env.test (NOT .env)")
    print("  ❌ BLOCK: Everything else by default")
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
        if create_gitignore_for_project(project_dir):
            success_count += 1

    print("\n" + "=" * 80)
    print(
        f"✅ Created aggressive .gitignore in {success_count}/{len(projects)} projects"
    )
    print("=" * 80)
    print("\n⚠️  IMPORTANT NOTES:")
    print("  • Old .gitignore files backed up as .gitignore.backup")
    print("  • Review git status in each project before committing")
    print("  • Use 'git add -f' to force-add any needed files if blocked")
    print("  • .env files are EXPLICITLY blocked for security")


if __name__ == "__main__":
    main()
