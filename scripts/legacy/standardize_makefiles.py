#!/usr/bin/env python3
"""
FLEXT Makefile Standardization Tool
==================================

Applies the standardized Makefile template to all submodules while preserving
project-specific customizations and ensuring proper dependency reuse.

Author: FLEXT Automation


import re
import shutil
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


class MakefileStandardizer:
    Standardizes Makefiles across FLEXT submodules."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.template_path = (
            workspace_root / "templates" / "makefile_submodule_template.mk"
        )
        self.projects_config = self._load_project_configurations()

    def _load_project_configurations(self) -> dict[str, dict[str, Any]]:
        """Load project-specific configurations for customization."""
        return {
            # Core Framework
            "flext-core": {
                "category": "core",
                "custom_targets": [
                    "validate-architecture",
                    "remove-legacy",
                    "strict-all",
                ],
                "dependencies": [],
            },
            "flext-auth": {
                "category": "core",
                "custom_targets": ["auth-test", "jwt-validate"],
                "dependencies": ["flext-core"],
            },
            "flext-api": {
                "category": "core",
                "custom_targets": ["api-start", "api-docs", "api-test"],
                "dependencies": ["flext-core", "flext-auth"],
            },
            # Singer ETL Plugins
            "flext-tap-ldap": {
                "category": "singer",
                "custom_targets": [
                    "tap-discover",
                    "tap-test",
                    "tap-run",
                    "tap-validate",
                ],
                "dependencies": ["flext-core", "flext-ldap"],
            },
            "flext-tap-oracle-oic": {
                "category": "singer",
                "custom_targets": ["tap-discover", "tap-test", "tap-run"],
                "dependencies": ["flext-core", "flext-db-oracle"],
            },
            "flext-tap-oracle-wms": {
                "category": "singer",
                "custom_targets": ["tap-discover", "tap-test", "tap-run"],
                "dependencies": ["flext-core", "flext-db-oracle"],
            },
            "flext-target-ldap": {
                "category": "singer",
                "custom_targets": ["target-test", "target-load"],
                "dependencies": ["flext-core", "flext-ldap"],
            },
            "flext-target-oracle": {
                "category": "singer",
                "custom_targets": ["target-test", "target-load"],
                "dependencies": ["flext-core", "flext-db-oracle"],
            },
            "flext-target-oracle-oic": {
                "category": "singer",
                "custom_targets": ["target-test", "target-load"],
                "dependencies": ["flext-core", "flext-db-oracle"],
            },
            # Extensions
            "flext-web": {
                "category": "web",
                "custom_targets": ["web-start", "web-build", "web-test"],
                "dependencies": ["flext-core", "flext-auth", "flext-api"],
            },
            "flext-cli": {
                "category": "cli",
                "custom_targets": ["cli-test", "cli-install", "cli-package"],
                "dependencies": ["flext-core"],
            },
            "flext-grpc": {
                "category": "service",
                "custom_targets": ["grpc-start", "grpc-test", "proto-gen"],
                "dependencies": ["flext-core"],
            },
            "flext-ldap": {
                "category": "infrastructure",
                "custom_targets": ["ldap-test", "ldap-connect", "schema-validate"],
                "dependencies": ["flext-core"],
            },
            "flext-db-oracle": {
                "category": "infrastructure",
                "custom_targets": ["db-test", "db-migrate", "db-seed"],
                "dependencies": ["flext-core"],
            },
            "flext-observability": {
                "category": "infrastructure",
                "custom_targets": ["metrics-test", "monitor-start"],
                "dependencies": ["flext-core"],
            },
            "flext-meltano": {
                "category": "platform",
                "custom_targets": ["meltano-run", "meltano-test"],
                "dependencies": ["flext-core"],
            },
            "flext-plugin": {
                "category": "platform",
                "custom_targets": ["plugin-test", "plugin-load"],
                "dependencies": ["flext-core"],
            },
            "flext-quality": {
                "category": "tooling",
                "custom_targets": ["quality-audit", "quality-report"],
                "dependencies": ["flext-core"],
            },
            # Enterprise Projects
            "client-a-oud-mig": {
                "category": "enterprise",
                "custom_targets": ["migration-test", "migration-run", "ansible-deploy"],
                "dependencies": ["flext-core", "flext-ldap", "flext-db-oracle"],
            },
            "client-b-poc-oic-wms": {
                "category": "enterprise",
                "custom_targets": ["integration-test", "oic-sync", "wms-sync"],
                "dependencies": ["flext-core", "flext-db-oracle"],
            },
            "client-b-meltano-native": {
                "category": "enterprise",
                "custom_targets": ["native-run", "extract-load"],
                "dependencies": ["flext-core", "flext-meltano"],
            },
            # Infrastructure
            "flexcore": {
                "category": "go_core",
                "custom_targets": ["go-build", "go-test", "docker-build"],
                "dependencies": [],
            },
        }

    def get_projects_to_standardize(self) -> list[str]:
        """Get list of projects that should be standardized."""
        projects = []
        for project_name in self.projects_config:
            project_path = self.workspace_root / project_name
            if project_path.exists() and project_path.is_dir():
                # Skip Go projects and some special cases
                if project_name == "flexcore":
                    continue
                projects.append(project_name)
        return projects

    def backup_existing_makefile(self, project_path: Path) -> None:
        """Backup existing Makefile before modification."""
        makefile_path = project_path / "Makefile"
        if makefile_path.exists():
            backup_path = project_path / "Makefile.backup"
            shutil.copy2(makefile_path, backup_path)
            console.print("  📁 Backed up existing Makefile to Makefile.backup")

    def extract_custom_targets(self, makefile_content: str) -> list[str]:
        """Extract custom targets from existing Makefile."""
        custom_targets = []
        lines = makefile_content.split("\n")

        for line in lines:
            # Look for target definitions
            if re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*:.*?##", line):
                target_name = line.split(":")[0].strip()
                # Skip common targets that are in the template
                common_targets = {
                    "help",
                    "install",
                    "install-dev",
                    "test",
                    "test-fast",
                    "lint",
                    "lint-fix",
                    "format",
                    "type-check",
                    "security",
                    "build",
                    "clean",
                    "clean-all",
                    "validate",
                    "quality-gate",
                }
                if target_name not in common_targets:
                    custom_targets.append(line.strip())

        return custom_targets

    def generate_custom_targets_section(
        self, project_name: str, custom_targets: list[str]
    ) -> str:
        """Generate custom targets section for the project."""
        if not custom_targets:
            return ""

        config = self.projects_config.get(project_name, {})
        category = config.get("category", "generic")

        section = f"""
# =============================================================================
# {category.upper()}-SPECIFIC TARGETS
# =============================================================================

"""

        for target in custom_targets:
            section += target + "\n"

        # Add category-specific targets based on configuration
        predefined_targets = config.get("custom_targets", [])
        if "tap-discover" in predefined_targets:
            section += """
.PHONY: tap-discover
tap-discover: ## Discover schema using Singer tap
    @echo -e "$(CYAN)Discovering schema...$(NC)"
    @if [ -f "config.json" ]
 then \
        $(PYTHON) -m tap_$(shell echo $(PROJECT_NAME) | sed 's/flext-tap-//') --config config.json --discover > catalog.json
  \
    else \:
        echo -e "$(YELLOW)⚠ config.json not found$(NC)"
  \
    fi

.PHONY: tap-test
tap-test: ## Test tap connection
    @echo -e "$(CYAN)Testing tap connection...$(NC)"
    @if [ -f "config.json" ]
 then \
        $(PYTHON) -m tap_$(shell echo $(PROJECT_NAME) | sed 's/flext-tap-//') --config config.json --test
  \
    else \:
        echo -e "$(YELLOW)⚠ config.json not found$(NC)"
  \
    fi

.PHONY: tap-run
tap-run: ## Run tap extraction
    @echo -e "$(CYAN)Running tap extraction...$(NC)"
    @if [ -f "config.json" ] && [ -f "catalog.json" ]
 then \
        $(PYTHON) -m tap_$(shell echo $(PROJECT_NAME) | sed 's/flext-tap-//') --config config.json --catalog catalog.json
  \
    else \:
        echo -e "$(YELLOW)⚠ config.json or catalog.json not found$(NC)"
  \
    fi
"""

        if "api-start" in predefined_targets:
            section += """
.PHONY: api-start
api-start: ## Start API server
    @echo -e "$(CYAN)Starting API server...$(NC)"
    @$(PYTHON) -m uvicorn src.flext_api.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: api-docs
api-docs: ## Generate API documentation
    @echo -e "$(CYAN)Generating API docs...$(NC)"
    @$(PYTHON) -c "import webbrowser
 webbrowser.open('http://localhost:8000/docs')"
"""

        return section

    def apply_template_to_project(self, project_name: str) -> bool:
        Apply standardized template to a specific project."""
        project_path = self.workspace_root / project_name
        makefile_path = project_path / "Makefile"

        if not self.template_path.exists():
            console.print(f"❌ Template not found: {self.template_path}")
            return False

        console.print(f"📝 Processing {project_name}...")

        # Backup existing Makefile
        self.backup_existing_makefile(project_path)

        # Extract custom targets from existing Makefile
        custom_targets = []
        if makefile_path.exists():
            existing_content = makefile_path.read_text()
            custom_targets = self.extract_custom_targets(existing_content)

        # Load template
        template_content = self.template_path.read_text()

        # Get project configuration
        config = self.projects_config.get(project_name, {})
        category = config.get("category", "generic")

        # Replace template variables
        customized_content = template_content.replace("{{PROJECT_NAME}}", project_name)
        customized_content = customized_content.replace(
            "{{PROJECT_CATEGORY}}", category
        )

        # Add custom targets section
        custom_section = self.generate_custom_targets_section(
            project_name, custom_targets
        )
        if custom_section:
            # Insert before the coordination exports section
            insertion_point = "# =============================================================================\n# COORDINATION EXPORTS"
            customized_content = customized_content.replace(
                insertion_point, custom_section + "\n" + insertion_point
            )

        # Write the new Makefile
        makefile_path.write_text(customized_content)

        console.print("  ✅ Applied standardized template")
        if custom_targets:
            console.print(f"  🔧 Preserved {len(custom_targets)} custom targets")

        return True

    def validate_dependencies(self, project_name: str) -> list[str]:
        """Validate that project has proper dependencies configured."""
        project_path = self.workspace_root / project_name
        pyproject_path = project_path / "pyproject.toml"

        if not pyproject_path.exists():
            return ["No pyproject.toml found"]

        config = self.projects_config.get(project_name, {})
        expected_deps = config.get("dependencies", [])

        pyproject_content = pyproject_path.read_text()

        return [
            f"Missing dependency: {dep}"
            for dep in expected_deps:
            if dep not in pyproject_content:
        ]

    def standardize_all_projects(self) -> tuple[list[str], list[str]]:
        """Standardize all eligible projects."""
        projects = self.get_projects_to_standardize()
        successful = []
        failed = []

        with Progress(:
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Standardizing Makefiles...", total=len(projects))

            for project in projects:
                progress.update(task, description=f"Processing {project}")

                try:
                    if self.apply_template_to_project(project):
                        successful.append(project)
                    else:
                        failed.append(project)
                except Exception as e:
                    console.print(f"❌ Error processing {project}: {e}")
                    failed.append(project)

                progress.advance(task)

        return successful, failed

    def generate_summary_report(self, successful: list[str], failed: list[str]) -> None:
        """Generate summary report of standardization process."""
        table = Table(title="FLEXT Makefile Standardization Report")
        table.add_column("Project", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Dependencies", style="yellow")
        table.add_column("Category", style="magenta")

        all_projects = successful + failed

        for project in all_projects:
            status = "✅ Success" if project in successful else "❌ Failed"
            config = self.projects_config.get(project, {})
            deps = ", ".join(config.get("dependencies", []))
            category = config.get("category", "unknown")

            table.add_row(project, status, deps, category)

        console.print("\n")
        console.print(table)

        # Dependency validation summary
        console.print("\n")
        dependency_panel = Panel(
            "📊 **Dependency Reuse Analysis**\n\n"
            "Projects should reuse FLEXT modules instead of reimplementing:\n"
            "• APIs/Web → flext-auth, flext-core\n"
            "• Singer plugins → flext-core\n"
            "• LDAP projects → flext-ldap\n"
            "• Oracle projects → flext-db-oracle\n\n"
            "Run `make validate-dependencies-all` to check compliance.",
            title="Dependency Guidelines",
            border_style="blue",
        )
        console.print(dependency_panel)


def main() -> None:
    """Main execution function."""
    workspace_root = Path(__file__).parent.parent

    console.print(
        Panel(
            "🔧 **FLEXT Makefile Standardization Tool**\n\n"
            "This tool applies the standardized Makefile template to all\n"
            "FLEXT submodules while preserving project-specific customizations.",
            title="FLEXT Automation",
            border_style="green",
        )
    )

    standardizer = MakefileStandardizer(workspace_root)

    console.print("\n🔍 **Analysis Phase**")
    projects = standardizer.get_projects_to_standardize()
    console.print(f"Found {len(projects)} projects to standardize:")

    for project in projects:
        config = standardizer.projects_config.get(project, {})
        category = config.get("category", "unknown")
        console.print(f"  • {project} ({category})")

    console.print("\n🚀 **Standardization Phase**")
    successful, failed = standardizer.standardize_all_projects()

    console.print("\n📊 **Results**")
    standardizer.generate_summary_report(successful, failed)

    if failed:
        console.print(f"\n❌ {len(failed)} projects failed standardization")
        return 1
    console.print(f"\n✅ All {len(successful)} projects standardized successfully")
    console.print("\n💡 **Next Steps:**")
    console.print("1. Review generated Makefiles")
    console.print("2. Test with: `make help` in each project")
    console.print("3. Run: `make validate-dependencies-all`")
    console.print(
        '4. Commit changes: `make auto-commit COMMIT_MSG="Standardize Makefiles"`'
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
