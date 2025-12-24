#!/usr/bin/env python3
"""Script to update all FLEXT project Makefiles with comprehensive clean targets.

This script finds all main project Makefiles and ensures they have comprehensive
clean targets that remove build artifacts, cache files, and project-specific cruft.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from pathlib import Path

# List of main project directories (not subdirectories)
MAIN_PROJECTS = [
    "flext-core",
    "flext-cli",
    "flext-api",
    "flext-auth",
    "flext-ldap",
    "flext-ldif",
    "flext-meltano",
    "flext-db-oracle",
    "flext-dbt-ldap",
    "flext-dbt-ldif",
    "flext-dbt-oracle",
    "flext-dbt-oracle-wms",
    "flext-grpc",
    "flext-observability",
    "flext-oracle-oic",
    "flext-oracle-wms",
    "flext-plugin",
    "flext-quality",
    "flext-tap-ldap",
    "flext-tap-ldif",
    "flext-tap-oracle",
    "flext-tap-oracle-oic",
    "flext-tap-oracle-wms",
    "flext-target-ldap",
    "flext-target-ldif",
    "flext-target-oracle",
    "flext-target-oracle-oic",
    "flext-target-oracle-wms",
    "flext-web",
    "client-a-oud-mig",
    "client-b-meltano-native",
]

# Comprehensive clean target template
CLEAN_TARGET_TEMPLATE = '''.PHONY: clean
clean: ## Clean build artifacts and cruft
	@echo "🧹 Cleaning $(PROJECT_NAME) - removing build artifacts, cache files, and cruft..."

	# Build artifacts
	rm -rf build/ dist/ *.egg-info/

	# Test artifacts
	rm -rf .pytest_cache/ htmlcov/ .coverage .coverage.* coverage.xml

	# Python cache directories
	rm -rf .mypy_cache/ .pyrefly_cache/ .ruff_cache/

	# Python bytecode
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

	# Temporary files
	find . -type f -name "*.tmp" -delete 2>/dev/null || true
	find . -type f -name "*.temp" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true

	# Log files
	find . -type f -name "*.log" -delete 2>/dev/null || true

	# Editor files
	find . -type f -name ".vscode/settings.json" -delete 2>/dev/null || true
	find . -type f -name ".idea/" -type d -exec rm -rf {} + 2>/dev/null || true

	@echo "✅ $(PROJECT_NAME) cleanup complete"'''

# Project-specific additions
PROJECT_SPECIFIC_CLEANUP = {
    "flext-ldif": """
	# LDIF-specific files
	rm -rf *.ldif output.ldif test.ldif input.ldif

	# Data directories
	rm -rf data/input/ data/output/ data/test/""",
    "flext-meltano": """
	# Meltano-specific files
	rm -rf .meltano/ catalog-*.json state.json state-*.json
	rm -rf .meltano-tmp/ meltano-*.log

	# Data pipeline files
	rm -rf extract/ load/ transform/ output/ analyze/ orchestrate/
	rm -rf notebook/ data/""",
    "flext-api": """
	# API-specific files
	rm -rf openapi.json docs/openapi.json
	rm -rf .fastapi/ .uvicorn/

	# Data directories
	rm -rf data/ output/ temp/""",
    "flext-auth": """
	# Auth-specific files
	rm -rf auth_tokens.json auth_sessions.db user_sessions.db

	# Data directories
	rm -rf data/ output/ temp/ fixtures/""",
    "flext-db-oracle": """
	# Database-specific files
	rm -rf *.db *.sqlite *.sqlite3
	rm -rf data/ output/ temp/""",
    "flext-grpc": """
	# gRPC-specific files
	rm -rf *.pb2.py *.pb2.pyi
	rm -rf data/ output/ temp/""",
    "client-a-oud-mig": """
	# Migration-specific files
	rm -rf *.ldif output.ldif test.ldif input.ldif
	rm -rf data/input/ data/output/ data/test/
	rm -rf migration.log migration-*.log""",
    "client-b-meltano-native": """
	# Meltano-specific files
	rm -rf .meltano/ catalog-*.json state.json state-*.json
	rm -rf .meltano-tmp/ meltano-*.log

	# Data pipeline files
	rm -rf extract/ load/ transform/ output/ analyze/ orchestrate/
	rm -rf notebook/ data/""",
}


def update_makefile(makefile_path: Path, project_name: str) -> bool | None:
    """Update a Makefile with comprehensive clean target."""
    print(f"🔄 Updating {makefile_path}")

    try:
        content = makefile_path.read_text(encoding="utf-8")

        # Extract project name from Makefile if not provided
        if not project_name:
            # Try to extract from PROJECT_NAME variable
            project_match = re.search(r"PROJECT_NAME\s*:=\s*([^\n]+)", content)
            if project_match:
                project_name = project_match.group(1).strip()

        # Find the current clean target
        clean_pattern = (
            r"(\.PHONY: clean\nclean:.*?## .*?\n)(.*?)(?=\n\n\.PHONY:|\n# |$))"
        )
        clean_match = re.search(clean_pattern, content, re.DOTALL)

        if clean_match:
            # Replace existing clean target
            before_clean = clean_match.group(1)
            after_clean = PROJECT_SPECIFIC_CLEANUP.get(project_name, "")

            new_clean_target = before_clean + CLEAN_TARGET_TEMPLATE

            if after_clean:
                new_clean_target = new_clean_target.replace(
                    '@echo "✅ $(PROJECT_NAME) cleanup complete"',
                    after_clean + '\n\n\t@echo "✅ $(PROJECT_NAME) cleanup complete"',
                )

            new_content = content.replace(clean_match.group(0), new_clean_target)
            makefile_path.write_text(new_content, encoding="utf-8")
            print(f"✅ Updated {makefile_path}")
            return True
        print(f"⚠️  No clean target found in {makefile_path}")
        return False

    except Exception as e:
        print(f"❌ Error updating {makefile_path}: {e}")
        return False


def main() -> None:
    """Main function to update all Makefiles."""
    print("🚀 Starting comprehensive Makefile cleanup...")
    print("=" * 60)

    updated_count = 0
    for project in MAIN_PROJECTS:
        makefile_path = Path(f"..{project}/Makefile")
        if makefile_path.exists():
            if update_makefile(makefile_path, project):
                updated_count += 1
        else:
            print(f"⚠️  No Makefile found for {project}")

    print("=" * 60)
    print(f"✅ Updated {updated_count} Makefiles with comprehensive clean targets")
    print("🧹 All projects now have standardized cruft removal")


if __name__ == "__main__":
    main()
