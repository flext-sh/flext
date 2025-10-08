#!/usr/bin/env python3
"""Script to add clean targets to Makefiles that don't have them.

This script finds Makefiles without clean targets and adds a comprehensive
clean target that removes build artifacts, cache files, and cruft.
"""

from pathlib import Path

# Projects that need clean targets added
PROJECTS_NEEDING_CLEAN = [
    "flext-dbt-ldif",
    "flext-dbt-oracle",
    "flext-dbt-oracle-wms",
    "flext-oracle-oic",
    "flext-oracle-wms",
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
    "client-a-oud-mig",
    "client-b-meltano-native",
]

# Basic clean target template for projects without specific requirements
BASIC_CLEAN_TARGET = """# =============================================================================
# MAINTENANCE
# =============================================================================

.PHONY: clean
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

	@echo "✅ $(PROJECT_NAME) cleanup complete"

.PHONY: clean-all
clean-all: clean ## Deep clean including venv
	rm -rf .venv/

.PHONY: reset
reset: clean-all setup ## Reset project

# =============================================================================
# DIAGNOSTICS
# =============================================================================

"""

# Project-specific clean additions for projects that need them
PROJECT_SPECIFIC_ADDITIONS = {
    "flext-dbt-ldif": """
	# DBT-specific files
	rm -rf target/ dbt_packages/ logs/""",
    "flext-dbt-oracle": """
	# DBT-specific files
	rm -rf target/ dbt_packages/ logs/""",
    "flext-dbt-oracle-wms": """
	# DBT-specific files
	rm -rf target/ dbt_packages/ logs/""",
    "flext-oracle-oic": """
	# Oracle-specific files
	rm -rf *.json oracle-*.log
	rm -rf data/ output/ temp/""",
    "flext-oracle-wms": """
	# Oracle-specific files
	rm -rf *.json oracle-*.log
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


def add_clean_target(makefile_path: Path, project_name: str) -> bool | None:
    """Add a clean target to a Makefile that doesn't have one."""
    print(f"🔄 Adding clean target to {makefile_path}")

    try:
        content = makefile_path.read_text(encoding="utf-8")

        # Find where to insert the clean target (before DIAGNOSTICS or end)
        diagnostics_pos = content.find(
            "# =============================================================================\n# DIAGNOSTICS"
        )
        if diagnostics_pos == -1:
            # Try to find end of file
            diagnostics_pos = len(content)

        # Insert the clean target before diagnostics
        clean_section = BASIC_CLEAN_TARGET
        after_clean = PROJECT_SPECIFIC_ADDITIONS.get(project_name, "")

        if after_clean:
            clean_section = clean_section.replace(
                '@echo "✅ $(PROJECT_NAME) cleanup complete"',
                after_clean + '\n\n\t@echo "✅ $(PROJECT_NAME) cleanup complete"',
            )

        new_content = (
            content[:diagnostics_pos] + clean_section + content[diagnostics_pos:]
        )
        makefile_path.write_text(new_content, encoding="utf-8")
        print(f"✅ Added clean target to {makefile_path}")
        return True

    except Exception as e:
        print(f"❌ Error adding clean target to {makefile_path}: {e}")
        return False


def main() -> None:
    """Main function to add clean targets to Makefiles that don't have them."""
    print("🚀 Adding clean targets to Makefiles that don't have them...")
    print("=" * 60)

    added_count = 0
    for project in PROJECTS_NEEDING_CLEAN:
        makefile_path = Path(f"..{project}/Makefile")
        if makefile_path.exists():
            # Check if it already has a clean target
            content = makefile_path.read_text(encoding="utf-8")
            if ".PHONY: clean" not in content and add_clean_target(
                makefile_path, project
            ):
                added_count += 1
        else:
            print(f"⚠️  No Makefile found for {project}")

    print("=" * 60)
    print(f"✅ Added {added_count} clean targets to Makefiles")
    print("🧹 All FLEXT projects now have standardized cruft removal")


if __name__ == "__main__":
    main()
