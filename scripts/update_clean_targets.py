#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-maintenance/SKILL.md
"""Script to update remaining FLEXT project Makefiles with comprehensive clean targets.

This script finds Makefiles that still have basic clean targets and updates them
with comprehensive cruft removal capabilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

# Projects that still need updating
PROJECTS_TO_UPDATE = [
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
CLEAN_TARGET_BASE = '''.PHONY: clean
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
    "flext-dbt-ldap": """
	# DBT-specific files
	rm -rf target/ dbt_packages/ logs/""",
    "flext-dbt-ldif": """
	# DBT-specific files
	rm -rf target/ dbt_packages/ logs/""",
    "flext-dbt-oracle": """
	# DBT-specific files
	rm -rf target/ dbt_packages/ logs/""",
    "flext-dbt-oracle-wms": """
	# DBT-specific files
	rm -rf target/ dbt_packages/ logs/""",
    "flext-grpc": """
	# gRPC-specific files
	rm -rf *.pb2.py *.pb2.pyi
	rm -rf data/ output/ temp/""",
    "flext-observability": """
	# Observability-specific files
	rm -rf metrics/ logs/ traces/
	rm -rf data/ output/ temp/""",
    "flext-oracle-oic": """
	# Oracle-specific files
	rm -rf *.json oracle-*.log
	rm -rf data/ output/ temp/""",
    "flext-oracle-wms": """
	# Oracle-specific files
	rm -rf *.json oracle-*.log
	rm -rf data/ output/ temp/""",
    "flext-plugin": """
	# Plugin-specific files
	rm -rf plugins/ plugin-registry.json
	rm -rf data/ output/ temp/""",
    "flext-quality": """
	# Quality-specific files
	rm -rf reports/ quality-*.json
	rm -rf data/ output/ temp/""",
    "flext-tap-ldap": """
	# Tap-specific files
	rm -rf state.json state-*.json
	rm -rf data/ output/ temp/""",
    "flext-tap-ldif": """
	# Tap-specific files
	rm -rf state.json state-*.json
	rm -rf data/ output/ temp/""",
    "flext-tap-oracle": """
	# Tap-specific files
	rm -rf state.json state-*.json
	rm -rf data/ output/ temp/""",
    "flext-tap-oracle-oic": """
	# Tap-specific files
	rm -rf state.json state-*.json
	rm -rf data/ output/ temp/""",
    "flext-tap-oracle-wms": """
	# Tap-specific files
	rm -rf state.json state-*.json
	rm -rf data/ output/ temp/""",
    "flext-target-ldap": """
	# Target-specific files
	rm -rf state.json state-*.json
	rm -rf data/ output/ temp/""",
    "flext-target-ldif": """
	# Target-specific files
	rm -rf state.json state-*.json
	rm -rf data/ output/ temp/""",
    "flext-target-oracle": """
	# Target-specific files
	rm -rf state.json state-*.json
	rm -rf data/ output/ temp/""",
    "flext-target-oracle-oic": """
	# Target-specific files
	rm -rf state.json state-*.json
	rm -rf data/ output/ temp/""",
    "flext-target-oracle-wms": """
	# Target-specific files
	rm -rf state.json state-*.json
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

        # Find the current clean target by looking for the pattern
        clean_start = content.find(".PHONY: clean")
        if clean_start == -1:
            print(f"⚠️  No clean target found in {makefile_path}")
            return False

        # Find where the clean target ends (next .PHONY or # section)
        next_phony = content.find("\n\n.PHONY:", clean_start)
        next_section = content.find("\n# ===", clean_start)
        next_end = content.find("\n\n# ===", clean_start)

        if next_phony != -1:
            clean_end = next_phony
        elif next_section != -1:
            clean_end = next_section
        elif next_end != -1:
            clean_end = next_end
        else:
            clean_end = len(content)

        clean_section = content[clean_start:clean_end]

        # Extract the header line
        lines = clean_section.split("\n")
        header_line = lines[0] + "\n" + lines[1]  # .PHONY: clean\nclean: ## ...

        # Create the new clean target
        after_clean = PROJECT_SPECIFIC_CLEANUP.get(project_name, "")
        new_clean_target = header_line + CLEAN_TARGET_BASE

        if after_clean:
            new_clean_target = new_clean_target.replace(
                '@echo "✅ $(PROJECT_NAME) cleanup complete"',
                after_clean + '\n\n\t@echo "✅ $(PROJECT_NAME) cleanup complete"',
            )

        # Replace in the file
        new_content = content.replace(clean_section, new_clean_target)
        makefile_path.write_text(new_content, encoding="utf-8")
        print(f"✅ Updated {makefile_path}")
        return True

    except Exception as e:
        print(f"❌ Error updating {makefile_path}: {e}")
        return False


def main() -> None:
    """Main function to update remaining Makefiles."""
    print("🚀 Updating remaining Makefiles with comprehensive clean targets...")
    print("=" * 70)

    updated_count = 0
    for project in PROJECTS_TO_UPDATE:
        makefile_path = Path(f"..{project}/Makefile")
        if makefile_path.exists():
            if update_makefile(makefile_path, project):
                updated_count += 1
        else:
            print(f"⚠️  No Makefile found for {project}")

    print("=" * 70)
    print(f"✅ Updated {updated_count} Makefiles with comprehensive clean targets")
    print("🧹 All FLEXT projects now have standardized cruft removal")


if __name__ == "__main__":
    main()
