"""FLEXT Workspace CLI - Unified Class Pattern Implementation.

Enterprise-grade workspace management CLI using FLEXT unified class pattern
with complete delegation to flext-cli. Eliminates loose helper functions and
Click direct usage, organizing all functionality into nested classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Self

from flext_cli import FlextCli
from flext_core import FlextLogger, FlextResult, FlextService, FlextUtilities
from flext_quality.tools import Colors, print_colored

from flext.services import create_services
from flext.workspace_service import create_workspace_service


class FlextWorkspaceCli(FlextService[str]):
    """Unified workspace CLI service with nested command handlers.

    Implements FLEXT unified class pattern with all workspace management
    functionality organized into nested classes. Eliminates loose helper
    functions and provides enterprise-grade workspace coordination.
    """

    def __init__(self, **_data: object) -> None:
        """Initialize workspace CLI with flext-cli integration."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._cli_api = FlextCli()

        # Workspace configuration
        self._workspace_root = Path(__file__).parent.parent.parent.parent
        self._venv_path = self._workspace_root / ".venv"
        self._python_bin = self._venv_path / "bin" / "python"

        # Module registry
        self._modules = {
            "flext-core": self._workspace_root / "flext-core",
            "flext-api": self._workspace_root / "flext-api",
            "flext-cli": self._workspace_root / "flext-cli",
            "flext-web": self._workspace_root / "flext-web",
            "flext-grpc": self._workspace_root / "flext-grpc",
            "flext-ldap": self._workspace_root / "flext-ldap",
            "flext-ldif": self._workspace_root / "flext-ldif",
            "flext-plugin": self._workspace_root / "flext-plugin",
            "flext-auth": self._workspace_root / "flext-auth",
            "flext-observability": self._workspace_root / "flext-observability",
            "flext-meltano": self._workspace_root / "flext-meltano",
            "flext-quality": self._workspace_root / "flext-quality",
        }

    @property
    def workspace_root(self) -> Path:
        """Get the workspace root directory."""
        return self._workspace_root

    @property
    def modules(self) -> dict[str, Path]:
        """Get the registered modules."""
        return self._modules

    @property
    def python_bin(self) -> Path:
        """Get the Python binary path."""
        return self._python_bin

    @property
    def logger(self) -> FlextLogger:
        """Get the logger instance."""
        return self._logger

    class _WorkspaceService:
        """Nested workspace service for command execution."""

        def __init__(self, cli_service: FlextWorkspaceCli) -> None:
            super().__init__()
            self._cli_service = cli_service

        def run_command(
            self,
            command: list[str],
            cwd: Path | None = None,
            *,
            check: bool = True,
        ) -> FlextResult[Any]:
            """Execute command with comprehensive error handling."""
            if cwd is None:
                cwd = self._cli_service.workspace_root

            print_colored(f"Running: {' '.join(command)} in {cwd}")

            try:
                result = FlextUtilities.run_external_command(
                    command,
                    cwd=cwd,
                    check=False,
                    text=True,
                )

                if result.is_failure:
                    error_msg = result.error
                    if check:
                        print_colored(f"❌ Command failed: {error_msg}")
                        return FlextResult[Any].fail(f"Command failed: {error_msg}")
                    # Non-critical failure - return wrapped process result
                    return FlextResult[Any].fail(error_msg)

                # Success case - return wrapped process result
                wrapper = result.unwrap()
                if check and wrapper.returncode != 0:
                    error = f"Command failed with return code {wrapper.returncode}: {wrapper.stderr}"
                    print_colored(f"❌ {error}")
                    return FlextResult[Any].fail(error)

                return FlextResult[Any].ok(wrapper)

            except Exception as e:
                error = f"Command execution failed: {e}"
                print_colored(f"❌ {error}")
                return FlextResult[Any].fail(error)

        def run_make_target(
            self, target: str, module: str | None = None, *, check: bool = True
        ) -> FlextResult[Any]:
            """Execute Make target with proper scoping."""
            cwd = (
                self._cli_service.modules.get(module, self._cli_service.workspace_root)
                if module
                else self._cli_service.workspace_root
            )

            return self.run_command(["make", target], cwd=cwd, check=check)

        def get_module_status(self, module: str) -> FlextResult[dict[str, object]]:
            """Get comprehensive status information for a module."""
            try:
                module_path = self._cli_service.modules.get(module)
                if not module_path:
                    return FlextResult[dict[str, object]].fail(
                        f"Module '{module}' not found in registry"
                    )

                if not module_path.exists():
                    not_found_status: dict[str, object] = {
                        "exists": False,
                        "name": module,
                        "path": str(module_path),
                    }
                    return FlextResult[dict[str, object]].ok(not_found_status)

                # Check for key files
                has_pyproject = (module_path / "pyproject.toml").exists()
                has_makefile = (module_path / "Makefile").exists()
                has_src = (module_path / "src").exists()
                has_tests = (module_path / "tests").exists()

                module_status: dict[str, object] = {
                    "exists": True,
                    "name": module,
                    "path": str(module_path),
                    "has_pyproject": has_pyproject,
                    "has_makefile": has_makefile,
                    "has_src": has_src,
                    "has_tests": has_tests,
                }

                return FlextResult[dict[str, object]].ok(module_status)

            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Failed to get module status for '{module}': {e}"
                )

        def list_modules(self: Self) -> FlextResult[list[dict[str, object]]]:
            """List all workspace modules with status information."""
            try:
                modules: list[dict[str, object]] = []
                for module in self._cli_service.modules:
                    result = self.get_module_status(module)
                    if result.is_failure:
                        return FlextResult[list[dict[str, object]]].fail(
                            result.error or "Unknown error"
                        )
                    modules.append(result.unwrap())
                return FlextResult[list[dict[str, object]]].ok(modules)
            except Exception as e:
                error = f"Failed to list modules: {e}"
                return FlextResult[list[dict[str, object]]].fail(error)

    class _StatusCommands:
        """Nested status command handlers."""

        def __init__(self, cli_service: FlextWorkspaceCli) -> None:
            super().__init__()
            self._cli_service = cli_service
            self._workspace_service = cli_service._WorkspaceService(cli_service)
            self._actual_workspace_service = create_workspace_service()
            self._modules_result: FlextResult[list[dict[str, object]]] | None = None
            self.modules: list[dict[str, object]] | None = None

        def display_status(self: Self) -> FlextResult[dict[str, object]]:
            """Display comprehensive workspace status."""
            print_colored("🏢 FLEXT Workspace Status")
            print_colored("=" * 50)

            self._modules_result = (
                self._actual_workspace_service.discover_workspace_projects()
            )
            if self._modules_result.is_failure:
                return FlextResult[dict[str, object]].fail("Failed to load modules")

            self.modules = self._modules_result.unwrap()

            # Display module status in organized format
            for module_info in self.modules:
                # module_info is a dict with project information
                name = module_info.get("name", "")
                # Project exists if it has a name and repository_path
                if module_info.get("name") and module_info.get("repository_path"):
                    print_colored(f"✅ {name}: Found")

                    # Show available features based on dict keys
                    features: list[str] = []
                    if module_info.get("is_test_project"):
                        features.append("Tests")
                    if module_info.get("test_framework"):
                        features.append(
                            f"Framework: {module_info.get('test_framework')}"
                        )
                    project_type = module_info.get("project_type", "application")
                    if project_type != "application":
                        features.append(f"Type: {project_type}")

                    if features:
                        print_colored(
                            f"   Features: {', '.join(features)}", Colors.BLUE
                        )
                else:
                    print_colored(f"❌ {name}: Missing")

            status_data: dict[str, object] = {
                "total_modules": len(self.modules),
                "modules": list(self.modules),  # Convert to list for type compatibility
            }

            available_count = len([
                m for m in self.modules if m.get("name") and m.get("repository_path")
            ])
            print_colored(
                f"\n📊 Summary: {available_count}/{status_data['total_modules']} modules available"
            )

            return FlextResult[dict[str, object]].ok(status_data)

    class _TestCommands:
        """Nested test command handlers."""

        def __init__(self, cli_service: FlextWorkspaceCli) -> None:
            super().__init__()
            self._cli_service = cli_service
            self._workspace_service = cli_service._WorkspaceService(cli_service)

        def run_tests(
            self,
            module: str | None = None,
            *,
            integration: bool = False,
            coverage: bool = False,
        ) -> FlextResult[dict[str, object]]:
            """Execute comprehensive test suites."""
            # Use parameters to avoid unused warnings
            _ = integration
            _ = coverage
            if module:
                print_colored(f"🧪 Running tests for {module}")
                result = self._workspace_service.run_make_target("test")
                if result.is_failure:
                    return FlextResult[dict[str, object]].fail(
                        f"Tests failed for {module}: {result.error}"
                    )

                # Check if the process completed successfully
                completed_process = result.unwrap()
                if completed_process.returncode == 0:
                    print_colored(f"✅ {module} tests passed")
                    return FlextResult[dict[str, object]].ok({"status": "passed"})
                return FlextResult[dict[str, object]].fail(f"Tests failed for {module}")

            print_colored("🧪 Running all workspace tests")

            results: dict[str, object] = {}
            for module_name in self._cli_service.modules:
                print_colored(f"Testing {module_name}...")
                result = self._workspace_service.run_make_target("test")

                if result.is_success:
                    completed_process = result.unwrap()
                    if completed_process.returncode == 0:
                        print_colored(f"✅ {module_name} tests passed")
                        results[module_name] = "passed"
                    else:
                        print_colored(f"❌ {module_name} tests failed")
                        results[module_name] = "failed"
                else:
                    print_colored(f"❌ {module_name} tests failed")
                    results[module_name] = "failed"

            return FlextResult[dict[str, object]].ok({
                "status": "completed",
                "results": results,
            })

    class _QualityCommands:
        """Nested quality command handlers."""

        def __init__(self, cli_service: FlextWorkspaceCli) -> None:
            super().__init__()
            self._cli_service = cli_service
            self._workspace_service = cli_service._WorkspaceService(cli_service)

        def run_quality_check(
            self,
            module: str | None = None,
            *,
            integration: bool = False,
            coverage: bool = False,
        ) -> FlextResult[dict[str, object]]:
            """Execute comprehensive quality analysis."""
            # Use parameters to avoid unused warnings
            _ = integration
            _ = coverage
            if module:
                print_colored(f"🔍 Running quality checks for {module}")
                result = self._workspace_service.run_make_target("check")
                if result.is_failure:
                    return FlextResult[dict[str, object]].fail(
                        f"Quality checks failed for {module}"
                    )

                # Check if the process completed successfully
                completed_process = result.unwrap()
                if completed_process.returncode == 0:
                    print_colored(f"✅ {module} quality checks passed")
                    return FlextResult[dict[str, object]].ok({"status": "passed"})
                return FlextResult[dict[str, object]].fail(
                    f"Quality checks failed for {module}"
                )

            print_colored("🔍 Running workspace quality checks")
            result = self._workspace_service.run_make_target("check-all")
            if result.is_failure:
                return FlextResult[dict[str, object]].fail(
                    "Workspace quality checks failed"
                )

            print_colored("✅ Workspace quality checks passed")
            return FlextResult[dict[str, object]].ok({"status": "passed"})

    class _BuildCommands:
        """Nested build command handlers."""

        def __init__(self, cli_service: FlextWorkspaceCli) -> None:
            super().__init__()
            self._cli_service = cli_service
            self._workspace_service = cli_service._WorkspaceService(cli_service)

        def run_build(
            self,
            module: str | None = None,
            *,
            integration: bool = False,
            coverage: bool = False,
        ) -> FlextResult[dict[str, object]]:
            """Execute comprehensive build process."""
            # Use parameters to avoid unused warnings
            _ = integration
            _ = coverage
            if module:
                print_colored(f"🔨 Building {module}")
                result = self._workspace_service.run_make_target("build")
                if result.is_failure:
                    return FlextResult[dict[str, object]].fail(
                        f"Build failed for {module}"
                    )

                print_colored(f"✅ {module} build completed")
                return FlextResult[dict[str, object]].ok({"status": "completed"})
            print_colored("🔨 Building entire workspace")
            result = self._workspace_service.run_make_target("build-all")
            if result.is_failure:
                return FlextResult[dict[str, object]].fail("Build failed")

            print_colored("✅ Workspace build completed")
            return FlextResult[dict[str, object]].ok({"status": "completed"})

    class _DockerCommands:
        """Nested Docker command handlers using python-on-whales."""

        def __init__(self, cli_service: FlextWorkspaceCli) -> None:
            super().__init__()
            self._cli_service = cli_service
            self._workspace_service = cli_service._WorkspaceService(cli_service)
            # Lazy import for optional docker-compose support
            self._docker_compose = None

        def _get_docker_compose(self) -> Any:
            """Lazy-load docker-compose from python-on-whales."""
            if self._docker_compose is None:
                try:
                    from python_on_whales import docker_compose

                    self._docker_compose = docker_compose
                except ImportError:
                    msg = (
                        "python-on-whales is required for docker-compose operations. "
                        "Install with: poetry add python-on-whales"
                    )
                    raise ImportError(msg)
            return self._docker_compose

        def start_containers(
            self,
            _services: list[str] | None = None,
            *,
            _integration: bool = False,
            _coverage: bool = False,
        ) -> FlextResult[dict[str, object]]:
            """Start Docker containers for development environment using python-on-whales."""
            print_colored("🐳 Starting Docker containers")
            try:
                docker_compose = self._get_docker_compose()
                docker_compose.up(detach=True)
                print_colored("✅ Containers started successfully")
                return FlextResult[dict[str, object]].ok({"status": "started"})
            except ImportError as e:
                return FlextResult[dict[str, object]].fail(f"Docker error: {e}")
            except Exception as e:
                error_msg = str(e).lower()
                if "not found" in error_msg or "no such file" in error_msg:
                    return FlextResult[dict[str, object]].fail(
                        "docker-compose not found. Ensure Docker is installed."
                    )
                return FlextResult[dict[str, object]].fail(
                    f"Failed to start containers: {e}"
                )

        def stop_containers(
            self,
            *,
            _integration: bool = False,
            _coverage: bool = False,
        ) -> FlextResult[dict[str, object]]:
            """Stop and remove Docker containers using python-on-whales."""
            print_colored("🐳 Stopping Docker containers")
            try:
                docker_compose = self._get_docker_compose()
                docker_compose.down()
                print_colored("✅ Containers stopped successfully")
                return FlextResult[dict[str, object]].ok({"status": "stopped"})
            except ImportError as e:
                return FlextResult[dict[str, object]].fail(f"Docker error: {e}")
            except Exception as e:
                error_msg = str(e).lower()
                if "not found" in error_msg or "no such file" in error_msg:
                    return FlextResult[dict[str, object]].fail(
                        "docker-compose not found. Ensure Docker is installed."
                    )
                return FlextResult[dict[str, object]].fail(
                    f"Failed to stop containers: {e}"
                )

        def view_logs(
            self,
            service: str | None = None,
            *,
            follow: bool = False,
        ) -> FlextResult[dict[str, object]]:
            """View and monitor Docker container logs using python-on-whales."""
            try:
                docker_compose = self._get_docker_compose()

                # Fetch logs via docker-compose
                if service:
                    # Get logs for specific service
                    docker_compose.logs(services=[service], follow=follow)
                else:
                    # Get logs for all services
                    docker_compose.logs(follow=follow)

                return FlextResult[dict[str, object]].ok({
                    "status": "completed",
                    "service": service or "all",
                })
            except ImportError as e:
                return FlextResult[dict[str, object]].fail(f"Docker error: {e}")
            except Exception as e:
                error_msg = str(e).lower()
                if "not found" in error_msg or "no such file" in error_msg:
                    return FlextResult[dict[str, object]].fail(
                        "docker-compose not found. Ensure Docker is installed."
                    )
                return FlextResult[dict[str, object]].fail(f"Failed to view logs: {e}")

    class _SetupCommands:
        """Nested setup and maintenance command handlers."""

        def __init__(self, cli_service: FlextWorkspaceCli) -> None:
            super().__init__()
            self._cli_service = cli_service
            self._workspace_service = cli_service._WorkspaceService(cli_service)

        def setup_workspace(self: Self) -> FlextResult[dict[str, object]]:
            """Initialize comprehensive workspace environment."""
            print_colored("🚀 Setting up FLEXT workspace")

            setup_steps = [
                ("Installing dependencies"),
                ("Syncing dependencies", "sync-deps"),
                (
                    "Setting up pre-commit hooks",
                    lambda: self._workspace_service.run_command([
                        "pre-commit",
                        "install",
                    ]),
                ),
                ("Finalizing setup", "dev-setup"),
            ]

            completed_steps: list[object] = []
            for step_name, action in setup_steps:
                print_colored(f"⏳ {step_name}...")

                try:
                    if callable(action):
                        result = action()
                    else:
                        result = self._workspace_service.run_make_target(str(action))

                    # Result is already a FlextResult from run_make_target

                    # Type narrowing for PyRight
                    if isinstance(result, FlextResult) and result.is_failure:
                        return FlextResult[dict[str, object]].fail(
                            f"Setup failed at step: {step_name}"
                        )

                    completed_steps.append(step_name)
                    print_colored(f"✅ {step_name} completed")

                except Exception as e:
                    return FlextResult[dict[str, object]].fail(f"Setup failed: {e}")

            print_colored("✅ Workspace setup complete!")
            return FlextResult[dict[str, object]].ok({"status": "started"})

        def clean_workspace(
            self, *, confirmed: bool = False
        ) -> FlextResult[dict[str, str]]:
            """Remove workspace artifacts and temporary files."""
            if not confirmed:
                print_colored("⚠️  This will remove all build artifacts and caches.")
                print_colored("Use confirmed=True parameter to proceed with cleanup.")
                return FlextResult[dict[str, str]].ok({
                    "status": "confirmation_required"
                })

            print_colored("🧹 Cleaning workspace")

            result = self._workspace_service.run_make_target("clean-workspace")
            if result.is_failure:
                return FlextResult[dict[str, str]].fail("Workspace clean failed")

            print_colored("✅ Workspace cleaned successfully")
            return FlextResult[dict[str, str]].ok({"status": "cleaned"})

        def run_integration_test(
            self, env: str = "development"
        ) -> FlextResult[dict[str, str]]:
            """Execute comprehensive integration tests."""
            print_colored(f"🧪 Running integration tests in {env} environment")

            # Start required containers via docker handler
            print_colored("Starting test containers...")
            docker_handler = self._cli_service.create_docker_handler()
            container_result = docker_handler.start_containers()

            if container_result.is_failure:
                return FlextResult[dict[str, str]].fail(
                    f"Failed to start test containers: {container_result.error}"
                )

            try:
                # Run integration tests
                test_result = self._workspace_service.run_command([
                    str(self._cli_service.python_bin),
                    "-m",
                    "pytest",
                    "tests/integration",
                    "-v",
                    "--tb=short",
                ])

                if test_result.is_failure:
                    return FlextResult[dict[str, str]].fail("Integration tests failed")

                # Check if tests passed via return code
                test_wrapper = test_result.unwrap()
                if test_wrapper.returncode != 0:
                    return FlextResult[dict[str, str]].fail("Integration tests failed")

                print_colored("✅ Integration tests passed!")
                return FlextResult[dict[str, str]].ok({"status": "tests_passed"})

            finally:
                # Clean up containers
                print_colored("Cleaning up test containers...")
                cleanup_result = docker_handler.stop_containers()
                if cleanup_result.is_failure:
                    self._cli_service.logger.warning(
                        f"Failed to clean up test containers: {cleanup_result.error}"
                    )

    def execute(self, _request: str = "") -> FlextResult[str]:
        """Execute workspace CLI service - required by FlextService abstract method."""
        try:
            # Default execution returns workspace CLI system info
            info = {
                "service": self.__class__.__name__,
                "domain": "workspace_cli",
                "status": "ready",
                "workspace": str(self._workspace_root),
            }
            return FlextResult[str].ok(f"FlextWorkspaceCli ready: {info}")
        except Exception as e:
            return FlextResult[str].fail(f"Workspace CLI service execution failed: {e}")

    def create_status_handler(self: Self) -> _StatusCommands:
        """Create status command handler."""
        return self._StatusCommands(self)

    def create_test_handler(self: Self) -> _TestCommands:
        """Create test command handler."""
        return self._TestCommands(self)

    def create_quality_handler(self: Self) -> _QualityCommands:
        """Create quality command handler."""
        return self._QualityCommands(self)

    def create_build_handler(self: Self) -> _BuildCommands:
        """Create build command handler."""
        return self._BuildCommands(self)

    def create_docker_handler(self: Self) -> _DockerCommands:
        """Create Docker command handler."""
        return self._DockerCommands(self)

    def create_setup_handler(self: Self) -> _SetupCommands:
        """Create setup command handler."""
        return self._SetupCommands(self)


def create_workspace_cli() -> FlextWorkspaceCli:
    """Factory function to create workspace CLI instance."""
    return FlextWorkspaceCli()


def main() -> None:
    """Main entry point using unified workspace CLI class."""
    workspace_cli = create_workspace_cli()

    print_colored("🚀 FLEXT Workspace CLI (Unified Class Pattern)")

    # Demo: Display workspace status
    status_handler = workspace_cli.create_status_handler()
    status_result = status_handler.display_status()

    if status_result.is_success:
        print_colored("✅ Workspace status displayed successfully")
    else:
        print_colored(f"❌ Status display failed: {status_result.error}")


# ============================================================================
# LEGACY FUNCTION ALIASES FOR BACKWARD COMPATIBILITY
# ============================================================================


def cli() -> None:
    """Legacy CLI entry point - use FlextWorkspaceCli instead."""
    main()


def status() -> None:
    """Legacy status function - use FlextWorkspaceCli._StatusCommands.display_status instead."""
    workspace_cli = create_workspace_cli()
    status_handler = workspace_cli.create_status_handler()
    status_handler.display_status()


def run_tests(
    module: str | None = None, *, coverage: bool = False, integration: bool = False
) -> None:
    """Execute tests using unified service - ELIMINATES duplication with cli.py."""
    services = create_services()
    test_service = services.create_test_services()

    result = test_service.execute_unified_test(
        module=module, coverage=coverage, integration=integration
    )

    if result.is_success:
        test_result_data = result.unwrap()
        if isinstance(test_result_data, dict) and not test_result_data.get(
            "success", True
        ):
            returncode = test_result_data.get("returncode", 1)
            print_colored(f"❌ Tests failed with return code {returncode}")
            sys.exit(1)
        else:
            print_colored("✅ Tests completed successfully")
    else:
        print_colored(f"❌ Test execution failed: {result.error}")
        sys.exit(1)


def check() -> None:
    """Execute quality checks using unified service - ELIMINATES duplication."""
    services = create_services()
    test_service = services.create_test_services()

    result = test_service.execute_quality_check(fix=False)

    if result.is_success:
        check_result_data = result.unwrap()
        if isinstance(check_result_data, dict) and check_result_data.get(
            "overall_success", False
        ):
            print_colored("✅ Quality checks passed")
        else:
            print_colored("❌ Quality checks failed")
            sys.exit(1)
    else:
        print_colored(f"❌ Quality check failed: {result.error}")
        sys.exit(1)


def build() -> None:
    """Execute build using unified service - ELIMINATES duplication."""
    services = create_services()
    test_service = services.create_test_services()

    result = test_service.execute_build_check()

    if result.is_success:
        build_result_data = result.unwrap()
        if isinstance(build_result_data, dict) and build_result_data.get(
            "success", False
        ):
            print_colored("✅ Build completed successfully")
        else:
            returncode = (
                build_result_data.get("returncode", 1)
                if isinstance(build_result_data, dict)
                else 1
            )
            print_colored(f"❌ Build failed with return code {returncode}")
            sys.exit(1)
    else:
        print_colored(f"❌ Build execution failed: {result.error}")
        sys.exit(1)


def docker() -> None:
    """Legacy docker function - use FlextWorkspaceCli._DockerCommands instead."""
    print_colored("Use FlextWorkspaceCli Docker handlers for container management")


def docker_up(
    services: list[str] | None = None,
    *,
    _integration: bool = False,
    _coverage: bool = False,
) -> None:
    """Legacy docker up function - use FlextWorkspaceCli._DockerCommands.start_containers instead."""
    workspace_cli = create_workspace_cli()
    docker_handler = workspace_cli.create_docker_handler()
    result = docker_handler.start_containers(
        services, _integration=_integration, _coverage=_coverage
    )
    if result.is_failure:
        print_colored(f"❌ Failed to start containers: {result.error}")
        sys.exit(1)


def docker_logs(service: str | None = None, *, follow: bool = False) -> None:
    """Legacy docker logs function - use FlextWorkspaceCli._DockerCommands.view_logs instead."""
    workspace_cli = create_workspace_cli()
    docker_handler = workspace_cli.create_docker_handler()
    docker_handler.view_logs(service, follow=follow)


def integration() -> None:
    """Legacy integration function - use FlextWorkspaceCli._SetupCommands instead."""
    print_colored("Use FlextWorkspaceCli Setup handlers for integration tests")


def integration_test(env: str = "development") -> None:
    """Legacy integration test function - use FlextWorkspaceCli._SetupCommands.run_integration_test instead."""
    workspace_cli = create_workspace_cli()
    setup_handler = workspace_cli.create_setup_handler()
    result = setup_handler.run_integration_test(env)
    if result.is_failure:
        print_colored(f"❌ Integration tests failed: {result.error}")
        sys.exit(1)


def setup() -> None:
    """Legacy setup function - use FlextWorkspaceCli._SetupCommands.setup_workspace instead."""
    workspace_cli = create_workspace_cli()
    setup_handler = workspace_cli.create_setup_handler()
    result = setup_handler.setup_workspace()
    if result.is_failure:
        print_colored(f"❌ Setup failed: {result.error}")
        sys.exit(1)


def clean() -> None:
    """Legacy clean function - use FlextWorkspaceCli._SetupCommands.clean_workspace instead."""
    workspace_cli = create_workspace_cli()
    setup_handler = workspace_cli.create_setup_handler()
    # Interactive confirmation for legacy function
    try:
        response = input(
            "This will remove all build artifacts and caches. Continue? [y/N]: "
        )
        if response.lower() == "y":
            result = setup_handler.clean_workspace(confirmed=True)
            if result.is_failure:
                print_colored(f"❌ Cleanup failed: {result.error}")
                sys.exit(1)
        else:
            print_colored("Cleanup cancelled")
    except KeyboardInterrupt:
        print_colored("\nCleanup cancelled")


# Export unified CLI class and legacy compatibility functions
__all__ = ["FlextWorkspaceCli"]
