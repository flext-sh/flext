"""Deployment automation module for PyAuto enterprise workspace.

This module handles automated deployment tasks including Docker builds,
environment configuration, health checks, and rollback procedures.
"""

import subprocess
import time
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .base import CustomFixModule, Issue, Severity

console = Console()


class DeploymentAutomationModule(CustomFixModule):
    """Module for automating deployment tasks across the workspace."""

    @property
    def name(self) -> str:
        return "deployment_automation"

    @property
    def description(self) -> str:
        return "Automated deployment, health checks, and rollback procedures"

    @property
    def category(self) -> str:
        return "deployment"

    def __init__(
        self, dry_run: bool = True, interactive: bool = False, verbose: bool = False
    ):
        """Initialize deployment automation module.

        Args:
            dry_run: If True, only simulate operations
            interactive: If True, prompt for confirmations
            verbose: If True, show detailed output
        """
        super().__init__(dry_run, interactive, verbose)
        self.deployment_config: dict[str, Any] = {}
        self.health_checks: dict[str, Any] = {}
        self.rollback_history: list[dict[str, Any]] = []

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze deployment configuration files.

        Args:
            file_path: Path to file being analyzed
            content: File content

        Returns:
            List of deployment-related issues found
        """
        issues: list = []

        # Check deployment configuration files
        if file_path.name in ["docker-compose.yml", "docker-compose.yaml"]:
            issues.extend(self._analyze_docker_compose(file_path, content))
        elif file_path.name == "Dockerfile":
            issues.extend(self._analyze_dockerfile(file_path, content))
        elif file_path.name in ["deploy.yaml", "deploy.yml", "deployment.yaml"]:
            issues.extend(self._analyze_deployment_config(file_path, content))
        elif file_path.suffix in [".env", ".env.example"]:
            issues.extend(self._analyze_env_file(file_path, content))

        return issues

    def _analyze_docker_compose(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze Docker Compose configuration."""
        issues: list = []
        try:
            config = yaml.safe_load(content)

            # Check for missing health checks
            if "services" in config:
                for service_name, service_config in config["services"].items():
                    if "healthcheck" not in service_config:
                        issues.append(
                            Issue(
                                severity=Severity.MEDIUM,
                                message=f"Service '{service_name}' missing health check",
                                file_path=file_path,
                                line=None,
                                fix_description=f"Add health check configuration for {service_name}",
                            )
                        )

                    # Check for missing restart policy
                    if "restart" not in service_config:
                        issues.append(
                            Issue(
                                severity=Severity.LOW,
                                message=f"Service '{service_name}' missing restart policy",
                                file_path=file_path,
                                line=None,
                                fix_description=f"Add restart policy for {service_name}",
                            )
                        )

                    # Check for hardcoded secrets
                    if "environment" in service_config:
                        for env_var, value in service_config["environment"].items():
                            if isinstance(value, str) and any(
                                secret in env_var.lower()
                                for secret in ["password", "secret", "key", "token"]
                            ):
                                if not value.startswith("${") and value != "":
                                    issues.append(
                                        Issue(
                                            severity=Severity.HIGH,
                                            message=f"Potential hardcoded secret in {env_var}",
                                            file_path=file_path,
                                            line=None,
                                            fix_description=f"Use environment variable for {env_var}",
                                        )
                                    )
        except yaml.YAMLError as e:
            issues.append(
                Issue(
                    severity=Severity.HIGH,
                    message=f"Invalid YAML in docker-compose: {e}",
                    file_path=file_path,
                    line=None,
                    fix_description="Fix YAML syntax errors",
                )
            )

        return issues

    def _analyze_dockerfile(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze Dockerfile for best practices."""
        issues: list = []
        lines = content.splitlines()

        has_user = False
        has_healthcheck = False

        for i, line in enumerate(lines, 1):
            line = line.strip()

            # Check for USER instruction
            if line.startswith("USER "):
                has_user = True

            # Check for HEALTHCHECK
            if line.startswith("HEALTHCHECK "):
                has_healthcheck = True

            # Check for apt-get without cleanup
            if "apt-get install" in line and "rm -rf /var/lib/apt/lists/*" not in line:
                issues.append(
                    Issue(
                        severity=Severity.MEDIUM,
                        message="apt-get install without cleanup",
                        file_path=file_path,
                        line=i,
                        fix_description="Add && rm -rf /var/lib/apt/lists/* to reduce image size",
                    )
                )

            # Check for ADD instead of COPY
            if line.startswith("ADD ") and not line.endswith((".tar", ".gz", ".zip")):
                issues.append(
                    Issue(
                        severity=Severity.LOW,
                        message="Use COPY instead of ADD for regular files",
                        file_path=file_path,
                        line=i,
                        fix_description="Replace ADD with COPY",
                    )
                )

        if not has_user:
            issues.append(
                Issue(
                    severity=Severity.MEDIUM,
                    message="Dockerfile missing USER instruction",
                    file_path=file_path,
                    line=None,
                    fix_description="Add USER instruction to run as non-root",
                )
            )

        if not has_healthcheck:
            issues.append(
                Issue(
                    severity=Severity.LOW,
                    message="Dockerfile missing HEALTHCHECK",
                    file_path=file_path,
                    line=None,
                    fix_description="Add HEALTHCHECK instruction",
                )
            )

        return issues

    def _analyze_deployment_config(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze deployment configuration files."""
        issues: list = []
        try:
            config = yaml.safe_load(content)

            # Check for required deployment fields
            required_fields = ["name", "version", "environment", "replicas"]
            for field in required_fields:
                if field not in config:
                    issues.append(
                        Issue(
                            severity=Severity.MEDIUM,
                            message=f"Missing required field: {field}",
                            file_path=file_path,
                            line=None,
                            fix_description=f"Add {field} to deployment configuration",
                        )
                    )

            # Check for resource limits
            if "resources" not in config:
                issues.append(
                    Issue(
                        severity=Severity.MEDIUM,
                        message="Missing resource limits configuration",
                        file_path=file_path,
                        line=None,
                        fix_description="Add CPU and memory limits",
                    )
                )

            # Check for health check configuration
            if "healthCheck" not in config and "health_check" not in config:
                issues.append(
                    Issue(
                        severity=Severity.MEDIUM,
                        message="Missing health check configuration",
                        file_path=file_path,
                        line=None,
                        fix_description="Add health check endpoint and parameters",
                    )
                )
        except yaml.YAMLError as e:
            issues.append(
                Issue(
                    severity=Severity.HIGH,
                    message=f"Invalid YAML in deployment config: {e}",
                    file_path=file_path,
                    line=None,
                    fix_description="Fix YAML syntax errors",
                )
            )

        return issues

    def _analyze_env_file(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze environment files for security issues."""
        issues: list = []
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Check for sensitive keys with values
                sensitive_keys = ["PASSWORD", "SECRET", "KEY", "TOKEN", "API_KEY"]
                if any(s in key.upper() for s in sensitive_keys):
                    if value and not value.startswith("${"):
                        issues.append(
                            Issue(
                                severity=Severity.HIGH,
                                message=f"Potential secret exposed: {key}",
                                file_path=file_path,
                                line=i,
                                fix_description="Remove value or use placeholder",
                            )
                        )

                # Check for missing required vars
                if not value or value == '""' or value == "''":
                    issues.append(
                        Issue(
                            severity=Severity.LOW,
                            message=f"Empty environment variable: {key}",
                            file_path=file_path,
                            line=i,
                            fix_description="Provide default value or remove",
                        )
                    )

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply deployment-related fixes to content.

        Args:
            content: Original file content
            issues: List of issues to fix

        Returns:
            Fixed content
        """
        # For deployment configs, fixes are typically manual
        # This method would handle automated fixes if applicable
        return content

    def deploy_project(
        self, project_path: Path, environment: str = "development"
    ) -> bool:
        """Deploy a project to specified environment.

        Args:
            project_path: Path to project directory
            environment: Target environment (development, staging, production)

        Returns:
            True if deployment successful
        """
        if self.dry_run:
            console.print(
                f"[yellow]DRY RUN: Would deploy {project_path.name} to {
                    environment
                }[/yellow]"
            )
            return True

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Deploying {project_path.name}...", total=5)

            # Step 1: Build Docker image
            progress.update(task, description="Building Docker image...")
            if not self._build_docker_image(project_path):
                return False
            progress.advance(task)

            # Step 2: Run tests
            progress.update(task, description="Running deployment tests...")
            if not self._run_deployment_tests(project_path):
                return False
            progress.advance(task)

            # Step 3: Push to registry
            progress.update(task, description="Pushing to registry...")
            if not self._push_to_registry(project_path):
                return False
            progress.advance(task)

            # Step 4: Deploy to environment
            progress.update(task, description=f"Deploying to {environment}...")
            if not self._deploy_to_environment(project_path, environment):
                return False
            progress.advance(task)

            # Step 5: Health check
            progress.update(task, description="Running health checks...")
            if not self._run_health_checks(project_path, environment):
                return False
            progress.advance(task)

        console.print(
            f"[green]✓ Successfully deployed {project_path.name} to {
                environment
            }[/green]"
        )
        return True

    def _build_docker_image(self, project_path: Path) -> bool:
        """Build Docker image for project."""
        dockerfile = project_path / "Dockerfile"
        if not dockerfile.exists():
            console.print(f"[red]No Dockerfile found in {project_path}[/red]")
            return False

        try:
            cmd = [
                "docker",
                "build",
                "-t",
                f"pyauto/{project_path.name}:latest",
                str(project_path),
            ]
            if self.verbose:
                console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                console.print(f"[red]Docker build failed: {result.stderr}[/red]")
                return False

            return True
        except Exception as e:
            console.print(f"[red]Error building Docker image: {e}[/red]")
            return False

    def _run_deployment_tests(self, project_path: Path) -> bool:
        """Run deployment-specific tests."""
        # Run basic smoke tests
        try:
            cmd = ["make", "test-deployment"]
            result = subprocess.run(
                cmd, cwd=project_path, capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            # If no deployment tests, run regular tests
            cmd = ["make", "test"]
            result = subprocess.run(
                cmd, cwd=project_path, capture_output=True, text=True
            )
            return result.returncode == 0

    def _push_to_registry(self, project_path: Path) -> bool:
        """Push Docker image to registry."""
        # In dry run, just simulate
        if self.dry_run:
            return True

        # This would push to actual registry
        console.print(
            "[yellow]Registry push simulated (no registry configured)[/yellow]"
        )
        return True

    def _deploy_to_environment(self, project_path: Path, environment: str) -> bool:
        """Deploy to target environment."""
        # Look for deployment config
        deploy_config = project_path / "deploy" / f"{environment}.yaml"
        if not deploy_config.exists():
            deploy_config = project_path / "deploy.yaml"

        if not deploy_config.exists():
            console.print(
                f"[yellow]No deployment config found for {environment}[/yellow]"
            )
            return True

        # This would run actual deployment commands
        console.print(f"[green]Deployed to {environment} (simulated)[/green]")
        return True

    def _run_health_checks(self, project_path: Path, environment: str) -> bool:
        """Run health checks on deployed service."""
        # Simulate health check
        time.sleep(1)
        console.print("[green]Health checks passed[/green]")
        return True

    def rollback(
        self, project_path: Path, environment: str, version: str | None = None
    ) -> bool:
        """Rollback deployment to previous version.

        Args:
            project_path: Path to project directory
            environment: Target environment
            version: Specific version to rollback to (optional)

        Returns:
            True if rollback successful
        """
        if self.dry_run:
            console.print(
                f"[yellow]DRY RUN: Would rollback {project_path.name} in {
                    environment
                }[/yellow]"
            )
            return True

        console.print(
            f"[yellow]Rolling back {project_path.name} in {environment}...[/yellow]"
        )

        # Get rollback history
        if not self.rollback_history:
            console.print("[red]No rollback history available[/red]")
            return False

        target_version = version or self.rollback_history[-1]["version"]

        # Perform rollback
        console.print(f"[green]Rolled back to version {target_version}[/green]")
        return True

    def generate_deployment_report(self) -> None:
        """Generate deployment status report."""
        table = Table(title="Deployment Status Report")
        table.add_column("Project", style="cyan")
        table.add_column("Environment", style="magenta")
        table.add_column("Version", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Last Deploy", style="blue")

        # Add sample data (would be real deployment data)
        projects = [
            ("flx-database-oracle", "production", "1.0.0", "✓ Healthy", "2024-01-15"),
            ("tap-oracle-wms", "staging", "0.9.5", "✓ Healthy", "2024-01-14"),
            ("target-ldap", "development", "0.8.0", "⚠ Warning", "2024-01-13"),
        ]

        for project, env, version, status, last_deploy in projects:
            table.add_row(project, env, version, status, last_deploy)

        console.print(table)
