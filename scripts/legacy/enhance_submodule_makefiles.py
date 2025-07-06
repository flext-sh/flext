#!/usr/bin/env python3
"""
FLEXT Submodule Makefile Enhancement Tool
========================================

Enhances existing submodule Makefiles by adding workspace coordination
capabilities while preserving project-specific functionality.

This script DOES NOT replace existing Makefiles - it enhances them by:
1. Adding include for common workspace functions
2. Adding workspace-coordination targets
3. Preserving all existing project-specific targets
4. Ensuring backward compatibility

Author: FLEXT Automation
"""

import argparse
import shutil
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


class MakefileEnhancer:
    """Enhances existing Makefiles without replacing them."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.common_include = workspace_root / "templates" / "common_flext.mk"
        self.enhanced_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def scan_projects(self) -> list[Path]:
        """Scan for projects with existing Makefiles."""
        projects = []

        # Active projects
        active_projects = [
            "flext-core",
            "flext-auth",
            "flext-api",
            "flext-grpc",
            "flext-web",
            "flext-cli",
            "flext-plugin",
            "flext-observability",
            "flext-meltano",
            "flext-ldap",
            "flext-db-oracle",
            "flext-quality",
            "flext-tap-ldap",
            "flext-tap-oracle-oic",
            "flext-tap-oracle-wms",
            "flext-target-ldap",
            "flext-target-oracle",
            "flext-target-oracle-oic",
            "flext-dbt-ldap",
            "flext-oracle-oic-ext",
            "client-a-oud-mig",
            "client-b-poc-oic-wms",
            "client-b-meltano-native",
            "flext-meltano-bridge",
            "python-meltano-gopy",
            "flexcore",
        ]

        for project_name in active_projects:
            project_path = self.workspace_root / project_name
            makefile_path = project_path / "Makefile"

            if project_path.exists() and makefile_path.exists():
                projects.append(project_path)

        return projects

    def check_if_already_enhanced(self, makefile_path: Path) -> bool:
        """Check if Makefile already includes common_flext.mk."""
        if not makefile_path.exists():
            return False

        content = makefile_path.read_text()
        return "common_flext.mk" in content or "FLEXT WORKSPACE COORDINATION" in content

    def get_project_type(self, project_path: Path) -> str:
        """Determine project type based on name and structure."""
        project_name = project_path.name.lower()

        if project_name == "flexcore":
            return "go_project"
        if project_name == "python-meltano-gopy":
            return "gopy_project"
        if project_name.startswith(("flext-tap-", "flext-target-")):
            return "singer_project"
        if project_name.startswith("flext-"):
            return "flext_core"
        if project_name.startswith(("client-b-", "client-a-")):
            return "client_project"
        return "generic_python"

    def create_enhancement(self, project_path: Path, project_type: str) -> str:
        """Create enhancement content based on project type."""
        project_name = project_path.name

        # Common header for all enhancements
        enhancement = (
            """
# =============================================================================
# FLEXT WORKSPACE COORDINATION - AUTO-ENHANCED
# Added by enhance_submodule_makefiles.py
# =============================================================================

# Include workspace coordination functions (if available)
-include $(shell git rev-parse --show-toplevel 2>/dev/null || echo "..")/templates/common_flext.mk

# Enhanced help that shows both project-specific and workspace targets
enhanced-help: ## Show enhanced help with workspace coordination
ifeq ($(WORKSPACE_AVAILABLE),true)
	$(call workspace-help-header)
else
	$(call standalone-help-header)
endif
	@echo "$(BOLD)🏗️  """
            + project_name
            + """ - Project Commands$(NC)"
	@echo "$(CYAN)=====================================$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v 'workspace-\\|enhanced-' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\\n", $$1, $$2}'
ifeq ($(WORKSPACE_AVAILABLE),true)
	@echo ""
	@echo "$(BOLD)$(CYAN)🔗 Workspace Coordination Targets$(NC)"
	@echo "$(CYAN)  workspace-status          Show workspace coordination status$(NC)"
	@echo "$(CYAN)  workspace-install         Install with workspace coordination$(NC)"
	@echo "$(CYAN)  workspace-install-dev     Install dev dependencies with coordination$(NC)"
	@echo "$(CYAN)  workspace-test            Run tests with workspace coordination$(NC)"
	@echo "$(CYAN)  workspace-lint            Run linting with workspace coordination$(NC)"
	@echo "$(CYAN)  workspace-format          Format code with workspace coordination$(NC)"
	@echo "$(CYAN)  workspace-clean           Clean with workspace coordination$(NC)"
	@echo "$(CYAN)  workspace-quality         Run quality checks with coordination$(NC)"
	@echo "$(CYAN)  workspace-commit          Run commit pipeline with coordination$(NC)"
endif

# Enhanced install that uses workspace coordination when available
enhanced-install: ## Install with workspace coordination (fallback to local)
	$(call install-with-workspace,$$(MAKE) install-local)

enhanced-install-dev: ## Install dev dependencies with workspace coordination
	$(call install-dev-with-workspace,$$(MAKE) install-dev-local)

enhanced-test: ## Run tests with workspace coordination (fallback to local)
	$(call test-with-workspace,$$(MAKE) test-local)

enhanced-lint: ## Run linting with workspace coordination (fallback to local)
	$(call lint-with-workspace,$$(MAKE) lint-local)

enhanced-format: ## Format code with workspace coordination (fallback to local)
	$(call format-with-workspace,$$(MAKE) format-local)

enhanced-clean: ## Clean with workspace coordination (fallback to local)
	$(call clean-with-workspace,$$(MAKE) clean-local)

enhanced-quality: ## Run quality checks with workspace coordination
	$(call quality-check,ruff check .)

enhanced-commit: ## Run commit pipeline with workspace coordination
	$(call commit-pipeline,ruff check .,python -m pytest tests/ -v)

# Project validation
validate-project-deps: ## Validate project dependencies for reuse
	$(call validate-dependencies)
	$(call ensure-core-deps)

"""
        )

        # Add project-type specific enhancements
        if project_type == "singer_project":
            enhancement += """
# Singer-specific enhancements
singer-validate: ## Validate Singer tap/target configuration
	@echo "$(BLUE)🎵 [$(CURRENT_PROJECT)] Validating Singer configuration...$(NC)"
	@if [ -f "config.json.example" ]; then \\
		echo "$(GREEN)✓ Example config found$(NC)"; \\
	else \\
		echo "$(YELLOW)💡 Consider adding config.json.example$(NC)"; \\
	fi
	@if [ -f "catalog.json" ] || [ -f "src/$(CURRENT_PROJECT)/catalog.py" ]; then \\
		echo "$(GREEN)✓ Catalog management found$(NC)"; \\
	else \\
		echo "$(YELLOW)💡 Consider adding catalog management$(NC)"; \\
	fi

singer-test-connection: ## Test Singer connection (requires config.json)
	@if [ -f "config.json" ]; then \\
		echo "$(CYAN)🔗 Testing Singer connection...$(NC)"; \\
		poetry run tap-$(CURRENT_PROJECT) --config config.json --discover || \\
		poetry run target-$(CURRENT_PROJECT) --config config.json --test || \\
		echo "$(YELLOW)⚠ Connection test not available$(NC)"; \\
	else \\
		echo "$(YELLOW)⚠ config.json not found for connection test$(NC)"; \\
	fi
"""

        elif project_type == "flext_core":
            enhancement += """
# FLEXT Core project enhancements
core-validate-architecture: ## Validate clean architecture compliance
	@echo "$(BLUE)🏛️  [$(CURRENT_PROJECT)] Validating clean architecture...$(NC)"
	@if [ -d "src/$(CURRENT_PROJECT)/domain" ]; then \\
		echo "$(GREEN)✓ Domain layer found$(NC)"; \\
	fi
	@if [ -d "src/$(CURRENT_PROJECT)/application" ]; then \\
		echo "$(GREEN)✓ Application layer found$(NC)"; \\
	fi
	@if [ -d "src/$(CURRENT_PROJECT)/infrastructure" ]; then \\
		echo "$(GREEN)✓ Infrastructure layer found$(NC)"; \\
	fi

core-check-dependencies: ## Check if other projects should depend on this one
	@echo "$(BLUE)📋 [$(CURRENT_PROJECT)] Checking potential dependents...$(NC)"
	@case "$(CURRENT_PROJECT)" in \\
		flext-core) \\
			echo "$(CYAN)💡 Core project - should be used by Singer taps/targets$(NC)" ;; \\
		flext-db-oracle) \\
			echo "$(CYAN)💡 Oracle DB project - should be used by Oracle-related projects$(NC)" ;; \\
		flext-auth) \\
			echo "$(CYAN)💡 Auth project - should be used by API and web projects$(NC)" ;; \\
	esac
"""

        elif project_type == "client_project":
            enhancement += """
# Client project enhancements
client-status: ## Show client project status
	@echo "$(BLUE)🏢 [$(CURRENT_PROJECT)] Client Project Status$(NC)"
	@if [ -f "README.md" ]; then \\
		echo "$(GREEN)✓ Documentation found$(NC)"; \\
	fi
	@if [ -d "config" ] || [ -f "config.json" ]; then \\
		echo "$(GREEN)✓ Configuration found$(NC)"; \\
	fi
	@if [ -d "data" ] || [ -d "logs" ]; then \\
		echo "$(GREEN)✓ Data/logs directories found$(NC)"; \\
	fi

client-backup-config: ## Backup client configuration
	@echo "$(CYAN)💾 Backing up configuration...$(NC)"
	@mkdir -p backups
	@if [ -f "config.json" ]; then \\
		cp config.json backups/config_$(shell date +%Y%m%d_%H%M%S).json; \\
		echo "$(GREEN)✓ config.json backed up$(NC)"; \\
	fi
	@if [ -d "config" ]; then \\
		cp -r config backups/config_$(shell date +%Y%m%d_%H%M%S)/; \\
		echo "$(GREEN)✓ config directory backed up$(NC)"; \\
	fi
"""

        elif project_type == "go_project":
            enhancement += """
# Go project enhancements
go-workspace-build: ## Build Go project with workspace coordination
	@echo "$(BLUE)🐹 [$(CURRENT_PROJECT)] Building Go project...$(NC)"
	@go mod tidy
	@go build ./...

go-workspace-test: ## Test Go project with workspace coordination
	@echo "$(BLUE)🧪 [$(CURRENT_PROJECT)] Testing Go project...$(NC)"
	@go test ./... -v
"""

        return enhancement

    def enhance_makefile(self, project_path: Path) -> bool:
        """Enhance a single Makefile."""
        makefile_path = project_path / "Makefile"

        try:
            # Check if already enhanced
            if self.check_if_already_enhanced(makefile_path):
                console.print(
                    f"[yellow]⚠ {project_path.name} already enhanced, skipping[/yellow]"
                )
                self.skipped_count += 1
                return True

            # Backup original
            backup_path = makefile_path.with_suffix(".bak")
            shutil.copy2(makefile_path, backup_path)
            console.print(
                f"[blue]💾 Backed up {project_path.name}/Makefile to .bak[/blue]"
            )

            # Get project type and create enhancement
            project_type = self.get_project_type(project_path)
            enhancement = self.create_enhancement(project_path, project_type)

            # Read original content
            original_content = makefile_path.read_text()

            # Find a good place to insert enhancement (usually after help target)
            lines = original_content.split("\n")
            insert_index = len(lines)  # Default to end

            # Look for help target or default goal
            for i, line in enumerate(lines):
                if (
                    line.strip().startswith(".DEFAULT_GOAL")
                    or line.strip().startswith("help:")
                    or (line.strip().startswith(".PHONY:") and "help" in line)
                ):
                    # Find the end of the help target
                    j = i + 1
                    while j < len(lines) and (
                        lines[j].startswith("\t") or lines[j].strip() == ""
                    ):
                        j += 1
                    insert_index = j
                    break

            # Insert enhancement
            lines.insert(insert_index, enhancement)
            enhanced_content = "\n".join(lines)

            # Write enhanced content
            makefile_path.write_text(enhanced_content)

            console.print(f"[green]✅ Enhanced {project_path.name}/Makefile[/green]")
            self.enhanced_count += 1
            return True

        except Exception as e:
            console.print(f"[red]❌ Failed to enhance {project_path.name}: {e}[/red]")
            self.error_count += 1

            # Restore backup if it exists
            backup_path = makefile_path.with_suffix(".bak")
            if backup_path.exists():
                shutil.copy2(backup_path, makefile_path)
                console.print(
                    f"[yellow]🔄 Restored backup for {project_path.name}[/yellow]"
                )

            return False

    def enhance_all_projects(self) -> None:
        """Enhance all project Makefiles."""
        projects = self.scan_projects()

        console.print(
            Panel.fit(
                f"[bold cyan]🚀 FLEXT Makefile Enhancement[/bold cyan]\n"
                f"Found {len(projects)} projects with Makefiles\n"
                f"Common include: {self.common_include}"
            )
        )

        if not self.common_include.exists():
            console.print(
                "[red]❌ common_flext.mk not found! Please create it first.[/red]"
            )
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Enhancing Makefiles...", total=len(projects))

            for project_path in projects:
                progress.update(task, description=f"Enhancing {project_path.name}...")
                self.enhance_makefile(project_path)
                progress.advance(task)

        # Summary
        table = Table(title="Enhancement Summary")
        table.add_column("Status", style="cyan")
        table.add_column("Count", style="green")

        table.add_row("✅ Enhanced", str(self.enhanced_count))
        table.add_row("⚠ Skipped (already enhanced)", str(self.skipped_count))
        table.add_row("❌ Errors", str(self.error_count))
        table.add_row("📊 Total Projects", str(len(projects)))

        console.print(table)

    def revert_enhancements(self) -> None:
        """Revert all enhancements using backup files."""
        projects = self.scan_projects()
        reverted = 0

        console.print("[yellow]🔄 Reverting Makefile enhancements...[/yellow]")

        for project_path in projects:
            makefile_path = project_path / "Makefile"
            backup_path = makefile_path.with_suffix(".bak")

            if backup_path.exists():
                shutil.copy2(backup_path, makefile_path)
                backup_path.unlink()  # Remove backup
                console.print(
                    f"[green]✅ Reverted {project_path.name}/Makefile[/green]"
                )
                reverted += 1

        console.print(f"[green]🔄 Reverted {reverted} Makefiles[/green]")


def main() -> None:
    """Main function."""

    parser = argparse.ArgumentParser(description="Enhance FLEXT submodule Makefiles")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="FLEXT workspace root directory",
    )
    parser.add_argument(
        "--revert", action="store_true", help="Revert enhancements using backup files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be enhanced without making changes",
    )

    args = parser.parse_args()

    enhancer = MakefileEnhancer(args.workspace)

    if args.revert:
        enhancer.revert_enhancements()
    elif args.dry_run:
        projects = enhancer.scan_projects()
        console.print(f"[cyan]Would enhance {len(projects)} projects:[/cyan]")
        for project in projects:
            status = (
                "already enhanced"
                if enhancer.check_if_already_enhanced(project / "Makefile")
                else "would enhance"
            )
            console.print(f"  - {project.name}: {status}")
    else:
        enhancer.enhance_all_projects()


if __name__ == "__main__":
    main()
