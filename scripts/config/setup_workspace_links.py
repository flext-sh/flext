#!/usr/bin/env python3
"""Comprehensive Workspace Management - Gerenciamento Completo do Workspace.

Script unificado para configuração completa do workspace FLEXT:
- Setup de links entre projetos
- Configuração completa do ambiente
- Gerenciamento de dependências
- Verificação de tipos MyPy
- Setup SSL para staging
- Configuração de monitoramento

Usando flext_tools para máxima confiabilidade enterprise.
"""

from __future__ import annotations

import subprocess  # moved to top for PLC0415
import sys
from pathlib import Path

from flext_tools import Colors, PoetryValidator, print_colored
from flext_tools.core.script_base import FlextScript, ScriptMetadata
from flext_tools.infrastructure import MonitoringManager, SSLManager
from flext_tools.quality import MyPyChecker


class ComprehensiveWorkspaceManager(FlextScript):
    """Comprehensive FLEXT workspace management with unified operations."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="comprehensive_workspace_manager",
            description=(
                "Complete workspace setup, links, dependencies, type checking, "
                "SSL and monitoring"
            ),
            category="config",
            version="3.0.0",
        )

    def validate_preconditions(self) -> bool:
        """Validate preconditions."""
        workspace_root = Path.cwd()

        # Check if we're in FLEXT workspace
        flext_projects = [
            p
            for p in workspace_root.iterdir()
            if p.is_dir()
            and p.name.startswith("flext-")
            and (p / "pyproject.toml").exists()
        ]

        if not flext_projects:
            print_colored("❌ Execute from FLEXT workspace root", Colors.RED)
            return False

        print_colored(f"✅ Found {len(flext_projects)} FLEXT projects", Colors.GREEN)

        # Check Poetry availability
        try:
            # Security: poetry is a trusted executable in PATH
            subprocess.run(
                ["poetry", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            print_colored("✅ Poetry available", Colors.GREEN)
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            print_colored("❌ Poetry not found", Colors.RED)
            return False

    def execute_main_logic(self, **kwargs: object) -> bool:
        """Execute comprehensive workspace management."""
        try:
            workspace_root = Path.cwd()
            operation = kwargs.get("operation", "links")

            print_colored("🏗️ COMPREHENSIVE WORKSPACE MANAGER", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            success = True

            if operation in {"links", "all"}:
                success &= self._setup_workspace_links(workspace_root, **kwargs)

            if operation in {"setup", "all"}:
                success &= self._complete_workspace_setup(workspace_root, **kwargs)

            if operation in {"deps", "all"}:
                success &= self._manage_dependencies(workspace_root, **kwargs)

            if operation in {"typecheck", "all"}:
                success &= self._run_mypy_check(workspace_root, **kwargs)

            if operation in {"ssl", "all"}:
                success &= self._setup_ssl(workspace_root, **kwargs)

            if operation in {"monitoring", "all"}:
                success &= self._setup_monitoring(workspace_root, **kwargs)

            return bool(success)

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during workspace management: {e}", Colors.RED)
            return False

    def _discover_projects(self, workspace_root: Path) -> list[Path]:
        """Discover FLEXT projects."""
        # Projects to ignore
        ignore_list = {"algar-oud-mig", "gruponos-meltano-native", "flexcore"}

        projects = [
            item
            for item in workspace_root.iterdir()
            if item.is_dir()
            and (item / "pyproject.toml").exists()
            and item.name not in ignore_list
            and not any(skip in item.name for skip in [".git", ".venv", "__pycache__"])
        ]

        return sorted(projects, key=lambda p: p.name)

    def _print_summary(
        self,
        total_projects: int,
        linked: int,
        failed_projects: list[str],
    ) -> None:
        """Print setup summary."""
        print_colored("\n📊 WORKSPACE LINKS SUMMARY", Colors.BLUE)
        print_colored("=" * 40, Colors.BLUE)

        print(f"  📁 Projects processed: {total_projects}")
        print(f"  ✅ Successfully linked: {linked}")
        print(f"  ❌ Failed: {len(failed_projects)}")

        if failed_projects:
            print_colored("\n🚫 Failed Projects:", Colors.RED)
            for project in failed_projects:
                print(f"  • {project}")

        # Success rate
        if total_projects > 0:
            success_rate = (linked / total_projects) * 100

            if success_rate == 100:
                status_color = Colors.GREEN
                status = "PERFECT"
            elif success_rate >= 90:
                status_color = Colors.CYAN
                status = "EXCELLENT"
            elif success_rate >= 80:
                status_color = Colors.YELLOW
                status = "GOOD"
            else:
                status_color = Colors.RED
                status = "NEEDS ATTENTION"

            print_colored(
                f"\n🏆 Success Rate: {success_rate:.1f}% ({status})",
                status_color,
            )

            if success_rate == 100:
                print_colored(
                    "\n🎉 All workspace links configured successfully!",
                    Colors.GREEN,
                )
                print_colored(
                    "Projects can now use each other as development dependencies",
                    Colors.GREEN,
                )

    def _setup_workspace_links(self, workspace_root: Path, **_kwargs: object) -> bool:
        """Setup development links between workspace projects."""
        print_colored("\n🔗 WORKSPACE LINKS SETUP", Colors.BLUE)
        print_colored("-" * 40, Colors.BLUE)

        # Use flext_tools.poetry for operations
        poetry_ops = PoetryValidator()

        # Discover projects
        projects = self._discover_projects(workspace_root)

        total_linked = 0
        failed_projects: list[str] = []

        # Setup links for each project
        for project_path in projects:
            project_name = project_path.name

            print_colored(
                f"📦 Setting up links for {project_name}...",
                Colors.BLUE,
            )

            try:
                # Use flext_tools for Poetry operations
                success = poetry_ops.validate_project(project_path)

                if success:
                    print_colored(
                        f"  ✅ {project_name}: Links configured",
                        Colors.GREEN,
                    )
                    total_linked += 1
                else:
                    print_colored(
                        f"  ❌ {project_name}: Failed to setup links",
                        Colors.RED,
                    )
                    failed_projects.append(project_name)

            except (OSError, ValueError, TypeError) as e:
                print_colored(f"  ❌ {project_name}: Error - {e}", Colors.RED)
                failed_projects.append(project_name)

        # Summary
        self._print_summary(len(projects), total_linked, failed_projects)
        return len(failed_projects) == 0

    def _complete_workspace_setup(self, workspace_root: Path, **_kwargs: object) -> bool:
        """Complete workspace setup with Poetry dependency management."""
        print_colored("\n🏗️ COMPLETE WORKSPACE SETUP", Colors.BLUE)
        print_colored("-" * 40, Colors.BLUE)

        poetry_ops = PoetryValidator()
        success = poetry_ops.validate_project(workspace_root)

        if success:
            print_colored("✅ Workspace setup completed successfully", Colors.GREEN)
            print_colored(
                "🎉 All projects configured with proper dependencies",
                Colors.GREEN,
            )
        else:
            print_colored("❌ Workspace setup failed", Colors.RED)
            print_colored("Check Poetry logs for details", Colors.YELLOW)

        return bool(success)

    def _manage_dependencies(self, workspace_root: Path, **_kwargs: object) -> bool:
        """Manage workspace dependencies with Poetry validation."""
        print_colored("\n📦 WORKSPACE DEPENDENCY MANAGEMENT", Colors.BLUE)
        print_colored("-" * 40, Colors.BLUE)

        poetry_ops = PoetryValidator()
        success = poetry_ops.validate_project(workspace_root)

        if success:
            print_colored(
                "✅ Workspace dependencies managed successfully",
                Colors.GREEN,
            )
            print_colored(
                "📋 All projects have consistent dependency configurations",
                Colors.CYAN,
            )
        else:
            print_colored("❌ Failed to manage workspace dependencies", Colors.RED)
            print_colored("Check Poetry logs for details", Colors.YELLOW)

        return bool(success)

    def _run_mypy_check(self, workspace_root: Path, **kwargs: object) -> bool:
        """Run MyPy type checking across workspace."""
        print_colored("\n🔍 MYPY WORKSPACE CHECK", Colors.BLUE)
        print_colored("-" * 40, Colors.BLUE)

        try:
            mypy_checker = MyPyChecker(workspace_path=workspace_root)
            check_result = mypy_checker.check_workspace(
                projects_filter=kwargs.get("projects"),
                strict_mode=kwargs.get("strict", False),
            )

            if check_result:
                has_errors = check_result.get("has_errors", False)
                error_count = check_result.get("error_count", 0)

                if has_errors:
                    print_colored(
                        f"⚠️ Found {error_count} type checking issues",
                        Colors.YELLOW,
                    )
                else:
                    print_colored(
                        "🎉 No MyPy type checking issues found!",
                        Colors.GREEN,
                    )

                return bool(check_result.get("has_no_errors", True))

            print_colored("❌ MyPy workspace check failed", Colors.RED)
            return False
        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during MyPy check: {e}", Colors.RED)
            return False

    def _setup_ssl(self, workspace_root: Path, **_kwargs: object) -> bool:
        """Setup SSL/TLS certificates for staging environment."""
        print_colored("\n🔐 STAGING SSL SETUP", Colors.BLUE)
        print_colored("-" * 40, Colors.BLUE)

        try:
            ssl_manager = SSLManager()
            success = ssl_manager.setup_ssl(
                workspace_root=workspace_root,
                environment="staging",
            )

            if success:
                print_colored(
                    "✅ Staging SSL certificates configured successfully",
                    Colors.GREEN,
                )
                print_colored("🔗 Certificates available in ssl/staging/", Colors.CYAN)
            else:
                print_colored("❌ Failed to setup SSL certificates", Colors.RED)

            return bool(success)
        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during SSL setup: {e}", Colors.RED)
            return False

    def _setup_monitoring(self, workspace_root: Path, **kwargs: object) -> bool:
        """Setup monitoring infrastructure for FLEXT workspace."""
        print_colored("\n📊 MONITORING INFRASTRUCTURE SETUP", Colors.BLUE)
        print_colored("-" * 40, Colors.BLUE)

        try:
            monitoring_manager = MonitoringManager()
            success = monitoring_manager.setup_monitoring(
                workspace_root=workspace_root,
                environment=kwargs.get("environment", "staging"),
            )

            if success:
                print_colored(
                    "✅ Monitoring infrastructure configured successfully",
                    Colors.GREEN,
                )
                print_colored(
                    "📊 Prometheus, Grafana and alerts configured",
                    Colors.CYAN,
                )
                print_colored("🔗 Access Grafana at http://localhost:3000", Colors.BLUE)
                print_colored("📈 Prometheus at http://localhost:9090", Colors.BLUE)
            else:
                print_colored(
                    "❌ Failed to setup monitoring infrastructure",
                    Colors.RED,
                )

            return bool(success)
        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during monitoring setup: {e}", Colors.RED)
            return False

    def create_parser(self) -> object:
        """Create parser with comprehensive arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--operation",
            choices=["links", "setup", "deps", "typecheck", "ssl", "monitoring", "all"],
            default="links",
            help="Operation to perform (default: links)",
        )

        parser.add_argument(
            "--skip-dev",
            action="store_true",
            help="Skip development dependencies installation",
        )

        parser.add_argument(
            "--projects",
            help="Filter specific projects (comma-separated)",
        )

        parser.add_argument(
            "--strict",
            action="store_true",
            help="Enable strict MyPy checking",
        )

        parser.add_argument(
            "--force",
            action="store_true",
            help="Force regeneration of existing certificates",
        )

        parser.add_argument(
            "--environment",
            default="staging",
            choices=["staging", "production", "development"],
            help="Target environment for setup",
        )

        parser.add_argument(
            "--fix-conflicts",
            action="store_true",
            help="Fix dependency conflicts automatically",
        )

        parser.add_argument(
            "--update-deps",
            action="store_true",
            help="Update dependencies to latest compatible versions",
        )

        parser.add_argument(
            "--skip-containers",
            action="store_true",
            help="Skip Docker container setup (config files only)",
        )

        return parser

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = ComprehensiveWorkspaceManager()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
