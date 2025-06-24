#!/usr/bin/env python3
"""Configuration Generation Module

Unified configuration generation for all project types in the workspace.
Based on multiple generate_config.py scripts found across projects.
"""

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from rich.console import Console

from .base import CustomFixModule, Issue


class ConfigGenerationModule(CustomFixModule):
    """Module for unified configuration generation across projects."""

    name = "config_generation"
    description = "Unified configuration generation for all project types"

    # Project type configuration templates
    CONFIG_TEMPLATES = {
        "oracle_oic": {
            "oauth_config": {
                "base_url": "OIC_IDCS_CLIENT_AUD",
                "oauth_client_id": "OIC_IDCS_CLIENT_ID",
                "oauth_client_secret": "OIC_IDCS_CLIENT_SECRET",
                "oauth_token_url": lambda env: f"{env.get('OIC_IDCS_URL')}/oauth2/v1/token",
                "oauth_scope": "OIC_IDCS_CLIENT_AUD",
            },
            "adapter_config": {
                "adapter_name": lambda project: f"{project.replace('_', '-')}",
                "adapter_type": "http",
                "instance_id": "OIC_INSTANCE_ID",
                "region": "OIC_REGION",
                "environment": ("OIC_ENVIRONMENT", "test"),
            },
            "http_config": {
                "timeout": ("HTTP_TIMEOUT", 120),
                "verify_ssl": ("HTTP_VERIFY_SSL", True),
                "max_retries": ("HTTP_MAX_RETRIES", 1),
                "retry_delay": ("HTTP_RETRY_DELAY", 2),
                "user_agent": ("HTTP_USER_AGENT", "FLX-OIC-HTTP-Client/1.0"),
            },
            "performance_config": {
                "buffer_size_bytes": ("HTTP_BUFFER_SIZE_BYTES", 8192),
                "keepalive_timeout_seconds": ("HTTP_KEEPALIVE_TIMEOUT_SECONDS", 30.0),
                "connection_pool_size": ("HTTP_CONNECTION_POOL_SIZE", 10),
            },
        },
        "oracle_wms": {
            "database_config": {
                "host": "ORACLE_HOST",
                "port": ("ORACLE_PORT", 1521),
                "service_name": "ORACLE_SERVICE_NAME",
                "username": "ORACLE_USERNAME",
                "password": "ORACLE_PASSWORD",
                "schema": "ORACLE_SCHEMA",
            },
            "wms_config": {
                "environment": ("WMS_ENVIRONMENT", "test"),
                "api_version": ("WMS_API_VERSION", "v1"),
                "batch_size": ("WMS_BATCH_SIZE", 1000),
                "timeout": ("WMS_TIMEOUT", 300),
            },
            "connection_config": {
                "pool_size": ("DB_POOL_SIZE", 5),
                "max_overflow": ("DB_MAX_OVERFLOW", 10),
                "pool_timeout": ("DB_POOL_TIMEOUT", 30),
                "pool_recycle": ("DB_POOL_RECYCLE", 3600),
            },
        },
        "singer_tap": {
            "tap_config": {
                "tap_name": lambda project: project.replace("-", "_"),
                "start_date": ("TAP_START_DATE", "2024-01-01T00:00:00Z"),
                "batch_size": ("TAP_BATCH_SIZE", 1000),
                "request_timeout": ("TAP_REQUEST_TIMEOUT", 300),
            },
            "api_config": {
                "base_url": "API_BASE_URL",
                "api_key": "API_KEY",
                "api_version": ("API_VERSION", "v1"),
                "rate_limit": ("API_RATE_LIMIT", 100),
            },
            "stream_config": {
                "selected_streams": ("SELECTED_STREAMS", []),
                "stream_maps": ("STREAM_MAPS", {}),
                "metadata": ("METADATA", {}),
            },
        },
        "meltano": {
            "meltano_config": {
                "project_id": "MELTANO_PROJECT_ID",
                "environment": ("MELTANO_ENVIRONMENT", "development"),
                "state_backend": ("MELTANO_STATE_BACKEND", "systemdb"),
                "database_uri": "MELTANO_DATABASE_URI",
            },
            "logging_config": {
                "level": ("LOG_LEVEL", "INFO"),
                "json_format": ("LOG_JSON", False),
                "file": ("LOG_FILE", None),
            },
            "plugin_config": {
                "auto_install": ("MELTANO_AUTO_INSTALL", True),
                "discovery_url": ("MELTANO_DISCOVERY_URL", "https://hub.meltano.com"),
            },
        },
        "ldap": {
            "ldap_config": {
                "server_uri": "LDAP_SERVER_URI",
                "bind_dn": "LDAP_BIND_DN",
                "bind_password": "LDAP_BIND_PASSWORD",
                "base_dn": "LDAP_BASE_DN",
                "search_scope": ("LDAP_SEARCH_SCOPE", "SUBTREE"),
            },
            "connection_config": {
                "timeout": ("LDAP_TIMEOUT", 30),
                "use_ssl": ("LDAP_USE_SSL", True),
                "verify_cert": ("LDAP_VERIFY_CERT", True),
                "pool_size": ("LDAP_POOL_SIZE", 5),
            },
            "migration_config": {
                "batch_size": ("MIGRATION_BATCH_SIZE", 100),
                "dry_run": ("MIGRATION_DRY_RUN", True),
                "backup_enabled": ("MIGRATION_BACKUP", True),
            },
        },
    }

    # Environment file names to look for
    ENV_FILES = [".env", ".internal.invalid", ".env.development", ".env.production"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.generated_configs: dict[str, dict[str, Any]] = {}

    def detect_project_type(self, project_path: Path) -> str | None:
        """Detect project type based on structure and dependencies."""
        project_name = project_path.name.lower()

        # Check by project name patterns
        if "oracle-oic" in project_name or "oic" in project_name:
            return "oracle_oic"
        if "oracle-wms" in project_name or "wms" in project_name:
            return "oracle_wms"
        if project_name.startswith("tap-"):
            return "singer_tap"
        if "meltano" in project_name:
            return "meltano"
        if "ldap" in project_name or "oud" in project_name:
            return "ldap"

        # Check by dependencies in pyproject.toml
        pyproject_file = project_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                import tomllib

                with open(pyproject_file, "rb") as f:
                    config = tomllib.load(f)

                deps = config.get("tool", {}).get("poetry", {}).get("dependencies", {})

                if "singer-sdk" in deps:
                    return "singer_tap"
                if "meltano" in deps:
                    return "meltano"
                if "cx-oracle" in deps or "oracledb" in deps:
                    return "oracle_wms" if "wms" in project_name else "oracle_oic"
                if "python-ldap" in deps or "ldap3" in deps:
                    return "ldap"
            except Exception:
                pass

        return None

    def load_environment_variables(self, project_path: Path) -> dict[str, str]:
        """Load environment variables from .env files."""
        env_vars: dict = {}

        # Load from multiple possible .env files
        for env_file in self.ENV_FILES:
            env_path = project_path / env_file
            if env_path.exists():
                load_dotenv(env_path)
                if self.verbose:
                    self.console.print(
                        f"[green]Loaded environment from: {env_file}[/green]"
                    )

        # Get all environment variables
        env_vars.update(os.environ)

        return env_vars

    def resolve_config_value(
        self, template_value: Any, env_vars: dict[str, str], project_name: str
    ) -> Any:
        """Resolve a configuration value from template."""
        if callable(template_value):
            # Handle lambda functions
            if (
                hasattr(template_value, "__name__")
                and "project" in template_value.__code__.co_varnames
            ):
                return template_value(project_name)
            return template_value(env_vars)

        if isinstance(template_value, tuple):
            # Handle (env_var, default_value) tuples
            env_var, default = template_value
            value = env_vars.get(env_var, default)

            # Type conversion based on default value type
            if isinstance(default, bool):
                return str(value).lower() in ("true", "1", "yes", "on")
            if isinstance(default, int):
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return default
            elif isinstance(default, float):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default
            elif isinstance(default, list):
                if isinstance(value, str) and value:
                    return value.split(",")
                return default
                return value

        elif isinstance(template_value, str):
            # Handle direct environment variable names
            return env_vars.get(template_value)

            return template_value
        return None

    def generate_project_config(
        self, project_path: Path, project_type: str
    ) -> dict[str, Any]:
        """Generate configuration for a specific project."""
        if project_type not in self.CONFIG_TEMPLATES:
            if self.verbose:
                self.console.print(
                    f"[yellow]Unknown project type: {project_type}[/yellow]"
                )
            return {}

        project_name = project_path.name
        env_vars = self.load_environment_variables(project_path)
        template = self.CONFIG_TEMPLATES[project_type]

        config: dict = {}

        for section_name, section_template in template.items():
            config[section_name] = {}

            for key, value_template in section_template.items():
                resolved_value = self.resolve_config_value(
                    value_template, env_vars, project_name
                )
                config[section_name][key] = resolved_value

        # Add metadata
        config["metadata"] = {
            "generated_by": "PyAuto Config Generation Module",
            "project_name": project_name,
            "project_type": project_type,
            "generated_at": str(Path.cwd()),
            "version": "1.0.0",
        }

        return config

    def save_config_file(
        self, project_path: Path, config: dict[str, Any], format: str = "json"
    ) -> bool:
        """Save configuration to file."""
        try:
            if format == "json":
                config_file = project_path / "config.json"
                with open(config_file, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2, default=str)

            elif format == "yaml":
                import yaml

                config_file = project_path / "config.yaml"
                with open(config_file, "w", encoding="utf-8") as f:
                    yaml.dump(config, f, default_flow_style=False, indent=2)

                if self.verbose:
                    self.console.print(f"[red]Unsupported format: {format}[/red]")
                return False

            if self.verbose:
                self.console.print(
                    f"[green]Configuration saved to: {config_file}[/green]"
                )

            return True

        except Exception as e:
            if self.verbose:
                self.console.print(f"[red]Error saving config: {e}[/red]")
            return False

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze projects for configuration generation opportunities."""
        issues: list = []

        # Check if this is a project root with .env but no config
        if file_path.name == ".env":
            project_path = file_path.parent
            config_files = ["config.json", "config.yaml", "config.yml"]

            if not any((project_path / cf).exists() for cf in config_files):
                project_type = self.detect_project_type(project_path)
                if project_type:
                    issues.append(
                        Issue(
                            line=1,
                            column=1,
                            code="CONFIG001",
                            message=f"Project has .env but no config file (detected type: {project_type})",
                            suggestion="Generate configuration file from environment variables",
                        )
                    )

        # Check for old generate_config.py scripts
        elif file_path.name == "generate_config.py":
            issues.append(
                Issue(
                    line=1,
                    column=1,
                    code="CONFIG002",
                    message="Individual generate_config.py script found",
                    suggestion="Replace with unified configuration generation module",
                )
            )

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply configuration generation fixes."""
        # This module works at the project level, not individual files
        return content

    def generate_workspace_configs(self, workspace_path: Path = None) -> dict[str, Any]:
        """Generate configurations for all projects in workspace."""
        if workspace_path is None:
            workspace_path = Path.cwd()

        if self.verbose:
            self.console.print(
                f"[blue]Generating configurations in: {workspace_path}[/blue]"
            )

        # Find all projects with .env files
        projects_with_env: list = []
        for env_file in workspace_path.rglob(".env"):
            if not any(
                part.startswith(".") and part != ".env" for part in env_file.parts
            ):
                projects_with_env.append(env_file.parent)

        if self.verbose:
            self.console.print(
                f"[green]Found {
                    len(projects_with_env)
                } projects with .env files[/green]"
            )

        generation_results = {
            "total_projects": len(projects_with_env),
            "successful_generations": 0,
            "failed_generations": 0,
            "project_results": {},
        }

        for project_path in projects_with_env:
            project_name = project_path.name
            project_type = self.detect_project_type(project_path)

            if self.verbose:
                self.console.print(
                    f"[yellow]Processing {project_name} (type: {
                        project_type or 'unknown'
                    })[/yellow]"
                )

            if not project_type:
                generation_results["project_results"][project_name] = {
                    "success": False,
                    "error": "Could not detect project type",
                }
                generation_results["failed_generations"] += 1
                continue

            # Generate configuration
            try:
                config = self.generate_project_config(project_path, project_type)

                if not config:
                    generation_results["project_results"][project_name] = {
                        "success": False,
                        "error": "Failed to generate configuration",
                    }
                    generation_results["failed_generations"] += 1
                    continue

                # Save configuration
                if not self.dry_run:
                    success = self.save_config_file(project_path, config, format="json")
                    if success:
                        generation_results["successful_generations"] += 1
                        self.generated_configs[project_name] = config
                        generation_results["failed_generations"] += 1
                    if self.verbose:
                        self.console.print(
                            f"[cyan][DRY RUN] Would generate config for {project_name}[/cyan]"
                        )
                    generation_results["successful_generations"] += 1

                generation_results["project_results"][project_name] = {
                    "success": True,
                    "project_type": project_type,
                    "config_sections": list(config.keys()),
                }

            except Exception as e:
                generation_results["project_results"][project_name] = {
                    "success": False,
                    "error": str(e),
                }
                generation_results["failed_generations"] += 1
                if self.verbose:
                    self.console.print(
                        f"[red]Error generating config for {project_name}: {e}[/red]"
                    )

        # Show summary
        if self.verbose:
            self._show_generation_summary(generation_results)

        return generation_results

    def _show_generation_summary(self, results: dict[str, Any]) -> None:
        """Show configuration generation summary."""
        # Results table
        from rich.table import Table

        table = Table(title="Configuration Generation Results")
        table.add_column("Project", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Type", style="blue")
        table.add_column("Config Sections")

        for project_name, result in results["project_results"].items():
            status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
            project_type = result.get("project_type", "unknown")
            sections = (
                ", ".join(result.get("config_sections", []))
                if result["success"]
                else result.get("error", "")
            )

            table.add_row(project_name, status, project_type, sections)

        self.console.print(table)

        # Summary panel
        success_rate = (
            (results["successful_generations"] / results["total_projects"] * 100)
            if results["total_projects"] > 0
            else 0
        )

        from rich.panel import Panel

        panel_text = (
            f"📁 Projects Found: {results['total_projects']}\n"
            f"✅ Successful: {results['successful_generations']}\n"
            f"❌ Failed: {results['failed_generations']}\n"
            f"📊 Success Rate: {success_rate:.1f}%"
        )

        panel_style = (
            "green"
            if success_rate == 100
            else "yellow"
            if success_rate >= 80
            else "red"
        )
        self.console.print(
            Panel(panel_text, title="Generation Summary", border_style=panel_style)
        )

    def run_workspace_config_generation(self, workspace_path: Path = None) -> bool:
        """Run configuration generation across the entire workspace."""
        results = self.generate_workspace_configs(workspace_path)
        return results["failed_generations"] == 0
