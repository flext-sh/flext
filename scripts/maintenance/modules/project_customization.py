#!/usr/bin/env python3
"""Project Customization Module

Customizes pyproject.toml templates for specific project types.
Based on scripts/customize_project_template.py functionality.
"""

import tomllib
from pathlib import Path

from rich.console import Console

from .base import CustomFixModule, Issue


class ProjectCustomizationModule(CustomFixModule):
    """Module for customizing project templates based on project type."""

    name = "project_customization"
    description = "Customizes pyproject.toml templates for specific project types"

    # Project type configurations
    PROJECT_CONFIGURATIONS = {
        "singer_tap": {
            "dependencies": {
                "singer-sdk": "^0.40.0",
                "requests": "^2.32.3",
                "backoff": "^2.2.1",
            },
            "scripts_pattern": 'tap-{project_name} = "{module_name}.cli:main"',
            "description_template": "Singer tap for extracting data from {service_name}",
            "keywords": ["singer", "tap", "etl", "data-extraction"],
        },
        "api_integration": {
            "dependencies": {
                "httpx": "^0.28.1",
                "fastapi": "^0.115.6",
                "uvicorn": "^0.32.1",
            },
            "scripts_pattern": '{project_name}-api = "{module_name}.main:app"',
            "description_template": "API integration service for {service_name}",
            "keywords": ["api", "rest", "http", "integration"],
        },
        "database": {
            "dependencies": {
                "sqlalchemy": "^2.0.36",
                "alembic": "^1.14.0",
                "cx-oracle": "^8.3.0",
            },
            "scripts_pattern": '{project_name}-cli = "{module_name}.cli:main"',
            "description_template": "Database integration for {service_name}",
            "keywords": ["database", "sql", "oracle", "data"],
        },
        "ldap": {
            "dependencies": {
                "python-ldap": "^3.4.4",
                "ldap3": "^2.9.1",
            },
            "scripts_pattern": '{project_name}-ldap = "{module_name}.cli:main"',
            "description_template": "LDAP integration and migration tools",
            "keywords": ["ldap", "directory", "authentication", "migration"],
        },
        "meltano": {
            "dependencies": {
                "meltano": "^3.4.0",
                "grpcio": "^1.68.1",
                "grpcio-tools": "^1.68.1",
            },
            "scripts_pattern": '{project_name} = "{module_name}.__main__:main"',
            "description_template": "Meltano enterprise data integration platform",
            "keywords": ["meltano", "elt", "data-platform", "orchestration"],
        },
    }

    # Service name mappings for description generation
    SERVICE_MAPPINGS = {
        "oracle-oic": "Oracle Integration Cloud",
        "oracle-wms": "Oracle Warehouse Management System",
        "ldap": "LDAP Directory Services",
        "meltano": "Meltano Data Platform",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()

    def detect_project_type(
            self,
            project_name: str,
            project_path: Path) -> str:
        """Detect project type based on name and structure."""
        name_lower = project_name.lower()

        # Singer tap detection
        if name_lower.startswith("tap-") or "tap" in name_lower:
            return "singer_tap"

        # Database integration detection
        if "database" in name_lower or "oracle" in name_lower:
            return "database"

        # LDAP detection
        if "ldap" in name_lower:
            return "ldap"

        # Meltano detection
        if "meltano" in name_lower:
            return "meltano"

        # API integration detection (default for HTTP services)
        if "http" in name_lower or "api" in name_lower:
            return "api_integration"

        # Check for existing dependencies to detect type
        pyproject_file = project_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                with open(pyproject_file, "rb") as f:
                    config = tomllib.load(f)

                deps = config.get(
                    "tool",
                    {}).get(
                    "poetry",
                    {}).get(
                    "dependencies",
                    {})

                if "singer-sdk" in deps:
                    return "singer_tap"
                if "fastapi" in deps or "httpx" in deps:
                    return "api_integration"
                if "sqlalchemy" in deps or "cx-oracle" in deps:
                    return "database"
                if "python-ldap" in deps or "ldap3" in deps:
                    return "ldap"
                if "meltano" in deps:
                    return "meltano"
            except Exception:
                pass

        # Default to API integration
        return "api_integration"

    def generate_project_scripts(
        self, project_name: str, module_name: str, project_type: str
    ) -> dict[str, str]:
        """Generate CLI scripts configuration for the project."""
        config = self.PROJECT_CONFIGURATIONS.get(project_type, {})
        pattern = config.get(
            "scripts_pattern", '{project_name}-cli = "{module_name}.cli:main"'
        )

        script_name = pattern.format(
            project_name=project_name,
            module_name=module_name)
        script_parts = script_name.split(" = ")

        if len(script_parts) == 2:
            return {script_parts[0]: script_parts[1].strip('"')}

        return {}

    def generate_project_description(
            self,
            project_name: str,
            project_type: str) -> str:
        """Generate appropriate description for the project."""
        config = self.PROJECT_CONFIGURATIONS.get(project_type, {})
        template = config.get(
            "description_template", "Enterprise Python automation component"
        )

        # Extract service name from project name
        service_name = "Unknown Service"
        for key, value in self.SERVICE_MAPPINGS.items():
            if key in project_name.lower():
                service_name = value
                break

        return template.format(service_name=service_name)

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze pyproject.toml for customization opportunities."""
        issues: list = []

        if file_path.name == "pyproject.toml":
            try:
                with open(file_path, "rb") as f:
                    config = tomllib.load(f)

                project_path = file_path.parent
                project_name = project_path.name

                # Detect project type
                detected_type = self.detect_project_type(
                    project_name, project_path)

                # Check if project needs customization
                poetry_config = config.get("tool", {}).get("poetry", {})

                # Check dependencies
                dependencies = poetry_config.get("dependencies", {})
                expected_deps = self.PROJECT_CONFIGURATIONS[detected_type]["dependencies"]

                missing_deps: list = []
                for dep, _version in expected_deps.items():
                    if dep not in dependencies:
                        missing_deps.append(dep)

                if missing_deps:
                    issues.append(
                        Issue(
                            line=1,
                            column=1,
                            code="PROJ_CUSTOM001",
                            message=f"Missing {detected_type} dependencies: {
                                ', '.join(missing_deps)}",
                            suggestion=f"Add project-type specific dependencies for {detected_type}"))

                # Check scripts
                scripts = poetry_config.get("scripts", {})
                module_name = project_name.replace("-", "_")
                expected_scripts = self.generate_project_scripts(
                    project_name, module_name, detected_type)

                missing_scripts: list = []
                for script_name in expected_scripts:
                    if script_name not in scripts:
                        missing_scripts.append(script_name)

                if missing_scripts:
                    issues.append(
                        Issue(
                            line=1,
                            column=1,
                            code="PROJ_CUSTOM002",
                            message=f"Missing {detected_type} scripts: {
                                ', '.join(missing_scripts)}",
                            suggestion=f"Add project-type specific CLI scripts for {detected_type}"))

                # Check description
                description = poetry_config.get("description", "")
                if description == "Enterprise-grade Python automation component":
                    issues.append(
                        Issue(
                            line=1,
                            column=1,
                            code="PROJ_CUSTOM003",
                            message="Generic project description",
                            suggestion=f"Update description for {detected_type} project type"))

                # Check keywords
                keywords = poetry_config.get("keywords", [])
                expected_keywords = self.PROJECT_CONFIGURATIONS[detected_type]["keywords"]

                missing_keywords = [
                    kw for kw in expected_keywords if kw not in keywords]
                if missing_keywords:
                    issues.append(
                        Issue(
                            line=1,
                            column=1,
                            code="PROJ_CUSTOM004",
                            message=f"Missing {detected_type} keywords: {
                                ', '.join(missing_keywords)}",
                            suggestion=f"Add project-type specific keywords for {detected_type}"))

            except Exception as e:
                issues.append(Issue(
                    line=1,
                    column=1,
                    code="PROJ_CUSTOM_ERROR",
                    message=f"Failed to analyze project customization: {e}",
                    suggestion="Check pyproject.toml format and syntax"
                ))

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply customization fixes to pyproject.toml files."""
        # For this module, we handle fixes at the workspace level
        return content

    def customize_project(
        self,
        project_path: Path,
        project_name: str = None,
        module_name: str = None,
        project_type: str = None,
    ) -> bool:
        """Customize a specific project."""
        if project_name is None:
            project_name = project_path.name

        if module_name is None:
            module_name = project_name.replace("-", "_")

        if project_type is None:
            project_type = self.detect_project_type(project_name, project_path)

        if self.verbose:
            self.console.print(
                f"[blue]Customizing project: {project_name} "
                f"(type: {project_type}, module: {module_name})[/blue]"
            )

        pyproject_file = project_path / "pyproject.toml"
        if not pyproject_file.exists():
            if self.verbose:
                self.console.print(
                    f"[red]❌ pyproject.toml not found in {project_path}[/red]")
            return False

        try:
            with open(pyproject_file, "rb") as f:
                config = tomllib.load(f)
        except Exception as e:
            if self.verbose:
                self.console.print(
                    f"[red]❌ Failed to load pyproject.toml: {e}[/red]")
            return False

        # Get project-specific configuration
        project_config = self.PROJECT_CONFIGURATIONS.get(project_type, {})

        # Track changes
        changes_made: list = []

        # Update dependencies
        dependencies = (
            config.setdefault("tool", {})
            .setdefault("poetry", {})
            .setdefault("dependencies", {})
        )
        project_deps = project_config.get("dependencies", {})

        for dep_name, dep_version in project_deps.items():
            if dep_name not in dependencies:
                dependencies[dep_name] = dep_version
                changes_made.append(
                    f"Added dependency: {dep_name} = {dep_version}")

        # Update scripts
        scripts = config["tool"]["poetry"].setdefault("scripts", {})
        project_scripts = self.generate_project_scripts(
            project_name, module_name, project_type)

        for script_name, script_command in project_scripts.items():
            if script_name not in scripts:
                scripts[script_name] = script_command
                changes_made.append(
                    f"Added script: {script_name} = {script_command}")

        # Update description
        poetry_config = config["tool"]["poetry"]
        if (
            poetry_config.get("description")
            == "Enterprise-grade Python automation component"
        ):
            new_description = self.generate_project_description(
                project_name, project_type)
            poetry_config["description"] = new_description
            changes_made.append(f"Updated description: {new_description}")

        # Update keywords
        keywords = poetry_config.setdefault(
            "keywords", ["automation", "enterprise", "oracle", "integration"]
        )
        project_keywords = project_config.get("keywords", [])

        for keyword in project_keywords:
            if keyword not in keywords:
                keywords.append(keyword)
                changes_made.append(f"Added keyword: {keyword}")

        if not changes_made:
            if self.verbose:
                self.console.print(
                    f"[green]✅ Project {project_name} already customized[/green]")
            return True

        if self.dry_run:
            if self.verbose:
                self.console.print(
                    f"[cyan][DRY RUN] Would apply changes to {project_name}:[/cyan]")
                for change in changes_made:
                    self.console.print(f"[cyan]  - {change}[/cyan]")
            return True

        if self.interactive:
            self.console.print(
                f"[yellow]Proposed changes for {project_name}:[/yellow]")
            for change in changes_made:
                self.console.print(f"[yellow]  - {change}[/yellow]")

            confirm = self.console.input("Apply these changes? (y/N): ")
            if confirm.lower() != "y":
                self.console.print("[red]Customization cancelled[/red]")
                return False

        # Write updated configuration
        try:
            import tomli_w

            # Create backup
            backup_file = pyproject_file.with_suffix(".toml.backup")
            pyproject_file.rename(backup_file)

            # Write updated file
            with open(pyproject_file, "wb") as f:
                tomli_w.dump(config, f)

            if self.verbose:
                self.console.print(
                    f"[green]✅ Successfully customized {project_name}[/green]")
                self.console.print(
                    f"[yellow]📁 Backup saved: {backup_file}[/yellow]")
                for change in changes_made:
                    self.console.print(f"[green]  ✓ {change}[/green]")

            return True

        except Exception as e:
            if self.verbose:
                self.console.print(
                    f"[red]❌ Failed to write customized pyproject.toml: {e}[/red]")
            return False

    def customize_workspace(self, workspace_path: Path = None) -> bool:
        """Customize all projects in the workspace."""
        if workspace_path is None:
            workspace_path = Path.cwd()

        if self.verbose:
            self.console.print(
                f"[blue]Customizing projects in workspace: {workspace_path}[/blue]")

        # Find all projects
        projects: list = []
        for pyproject_file in workspace_path.rglob("pyproject.toml"):
            # Skip cache and venv directories
            if any(
                part.startswith(".")
                and part in {".venv", ".mypy_cache", ".pytest_cache"}
                for part in pyproject_file.parts
            ):
                continue
            projects.append(pyproject_file.parent)

        if self.verbose:
            self.console.print(
                f"[green]Found {
                    len(projects)} projects to customize[/green]")

        success_count = 0
        for project_path in projects:
            if self.customize_project(project_path):
                success_count += 1

        if self.verbose:
            action = "Would customize" if self.dry_run else "Customized"
            self.console.print(
                f"[bold green]{action} {success_count}/{len(projects)} projects[/bold green]")

        return success_count == len(projects)

    def run_workspace_customization(self, workspace_path: Path = None) -> bool:
        """Run customization across the entire workspace."""
        return self.customize_workspace(workspace_path)
