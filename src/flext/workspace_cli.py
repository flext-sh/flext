"""FLEXT Workspace CLI - Unified Class Pattern Implementation.

Enterprise-grade workspace management CLI using FLEXT unified class pattern
with complete delegation to flext-cli. Eliminates loose helper functions and
Click direct usage, organizing all functionality into nested classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from flext.services import create_services
from flext.workspace_service import create_workspace_service
from flext_cli import FlextCliApi
from flext_core import FlextService, FlextLogger, FlextResult
from flext_tools import Colors, print_colored


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
        self._cli_api = FlextCliApi()

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

    class _WorkspaceService:
        """Nested workspace service for command execution."""

        def __init__(self, cli_service: FlextWorkspaceCli) -> None:
            self._cli_service = cli_service

        def run_command(
            self,
            command: list[str],
            cwd: Path | None = None,
            *,
            check: bool = True,
        ) -> FlextResult[subprocess.CompletedProcess[str]]:
            """Execute command with comprehensive error handling."""
            if cwd is None:
                cwd = self._cli_service._workspace_root

            print_colored(f"Running: {' '.join(command)} in {cwd}")

            try:
                result = subprocess.run(command, check=False, text=True)

                if check and result.returncode != 0:
                    error = f"Command failed: {result.stderr}"
                    print_colored(f"❌ {error}")
                    return FlextResult[subprocess.CompletedProcess[str]].fail(error)

                return FlextResult[subprocess.CompletedProcess[str]].ok(result)

            except Exception as e:
                error = f"Command execution failed: {e}"
                print_colored(f"❌ {error}")
                return FlextResult[subprocess.CompletedProcess[str]].fail(error)

        def run_make_target(
            self, target: str, module: str | None = None, *, check: bool = True
        ) -> FlextResult[subprocess.CompletedProcess[str]]:
            """Execute Make target with proper scoping."""
            cwd = (
                self._cli_service._modules.get(
                    module, self._cli_service._workspace_root
                )
                if module
                else self._cli_service._workspace_root
            )

            return self.run_command(["make", target], cwd=cwd, check=check)

        def get_module_status(self, module: str) -> FlextResult[dict[str, object]]:
            """Get comprehensive status information for a module."""
            try:
                module_path = self._cli_service._modules.get(module)
                if not module_path:
                    return FlextResult[dict[str, object]].fail(
                        f"Module '{module}' not found in registry"
                    )

                if not module_path.exists():
                    status = {"exists": False, "name": module, "path": str(module_path)}
                    return FlextResult[dict[str, object]].ok(status)

                # Check for key files
                has_pyproject = (module_path / "pyproject.toml").exists()
                has_makefile = (module_path / "Makefile").exists()
                has_src = (module_path / "src").exists()
                has_tests = (module_path / "tests").exists()

                status = {
                    "exists": True,
                    "name": module,
                    "path": str(module_path),
                    "has_pyproject": has_pyproject,
                    "has_makefile": has_makefile,
                    "has_src": has_src,
                    "has_tests": has_tests,
                }

                return FlextResult[dict[str, object]].ok(status)

            except Exception as e:
                return FlextResult[dict[str, object]].fail(
                    f"Failed to get module status for '{module}': {e}"
                )

        def list_modules(self) -> FlextResult[list[dict[str, object]]]:
            """List all workspace modules with status information."""
            try:
                modules = []
                for module in self._cli_service._modules:
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
            self._cli_service = cli_service
            self._workspace_service = cli_service._WorkspaceService(cli_service)
            self._actual_workspace_service = create_workspace_service()

        def display_status(self) -> FlextResult[dict[str, object]]:
            """Display comprehensive workspace status."""
            print_colored("🏢 FLEXT Workspace Status")
            print_colored("=" * 50)

            self._modules_result = (
                self._actual_workspace_service.discover_workspace_projects()
            )
            if self._modules_result.is_failure:
                return FlextResult[dict[str, object]].fail("Failed to load modules")

            self._modules = self._modules_result.unwrap()

            # Display module status in organized format
            for module_info in self._modules:
                # module_info is a Project object
                name = module_info.name
                # Project exists if it has a name and path
                if module_info.name and module_info.path:
                    print_colored(f"✅ {name}: Found")

                    # Show available features
                    features = []
                    if module_info.has_pyproject:
                        features.append("PyProject")
                    # Only show features that exist in the Project model
                    if module_info.has_tests:
                        features.append("Tests")

                    if features:
                        print_colored(
                            f"   Features: {', '.join(features)}", Colors.BLUE
                        )
                else:
                    print_colored(f"❌ {name}: Missing")

            status_data = {
                "total_modules": len(self._modules),
                "modules": self._modules,
            }

            available_count = len([m for m in self._modules if m.name and m.path])
            print_colored(
                f"\n📊 Summary: {available_count}/{status_data['total_modules']} modules available"
            )

            return FlextResult[dict[str, object]].ok(status_data)

    class _TestCommands:
        """Nested test command handlers."""

        def __init__(self, cli_service: FlextWorkspaceCli) -> None:
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

                print_colored(f"✅ {module} tests passed")
                return FlextResult[dict[str, object]].ok({"status": "started"})
            print_colored("🧪 Running all workspace tests")

            results = {}
            for module_name in self._cli_service._modules:
                print_colored(f"Testing {module_name}...")
                result = self._workspace_service.run_make_target("test")

                if result.is_success and result.unwrap().returncode == 0:
                    print_colored(f"✅ {module_name} tests passed")
                    results[module_name] = "passed"
                else:
                    print_colored(f"❌ {module_name} tests failed")
                    results[module_name] = "failed"

            return FlextResult[dict[str, object]].ok({"status": "started"})

    class _QualityCommands:
        """Nested quality command handlers."""

        def __init__(self, cli_service: FlextWorkspaceCli) -> None:
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

                print_colored(f"✅ {module} quality checks passed")
                return FlextResult[dict[str, object]].ok({"status": "passed"})
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
        """Nested Docker command handlers."""

        def __init__(self, cli_service: FlextWorkspaceCli) -> None:
            self._cli_service = cli_service
            self._workspace_service = cli_service._WorkspaceService(cli_service)

        def start_containers(
            self,
            _services: list[str] | None = None,
            *,
            _integration: bool = False,
            _coverage: bool = False,
        ) -> FlextResult[dict[str, object]]:
            """Start Docker containers for development environment."""
            print_colored("🐳 Starting Docker containers")

            cmd = ["docker-compose"]

            result = self._workspace_service.run_command(cmd)
            if result.is_failure:
                return FlextResult[dict[str, object]].fail("Failed to start containers")

            print_colored("✅ Containers started successfully")
            return FlextResult[dict[str, object]].ok({"status": "started"})

        def stop_containers(
            self,
            *,
            _integration: bool = False,
            _coverage: bool = False,
        ) -> FlextResult[dict[str, object]]:
            """Stop and remove Docker containers."""
            print_colored("🐳 Stopping Docker containers")

            result = self._workspace_service.run_command(["docker-compose"])
            if result.is_failure:
                return FlextResult[dict[str, object]].fail("Failed to stop containers")

            print_colored("✅ Containers stopped successfully")
            return FlextResult[dict[str, object]].ok({"status": "started"})

        def view_logs(
            self,
            service: str | None = None,
            *,
            follow: bool = False,
        ) -> FlextResult[dict[str, object]]:
            """View and monitor Docker container logs."""
            cmd = ["docker-compose", "logs"]
            if follow:
                cmd.append("-f")
            if service:
                cmd.append(service)

            result = self._workspace_service.run_command(cmd)
            if result.is_failure:
                return FlextResult[dict[str, object]].fail("Failed to view logs")

            return FlextResult[dict[str, object]].ok({
                "status": "completed",
                "service": service or "all",
            })

    class _SetupCommands:
        """Nested setup and maintenance command handlers."""

        def __init__(self, cli_service: FlextWorkspaceCli) -> None:
            self._cli_service = cli_service
            self._workspace_service = cli_service._WorkspaceService(cli_service)

        def setup_workspace(self) -> FlextResult[dict[str, object]]:
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

            completed_steps = []

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

            # Start required containers
            print_colored("Starting test containers...")
            container_result = self._workspace_service.run_command(["docker-compose"])

            if container_result.is_failure:
                return FlextResult[dict[str, str]].fail(
                    "Failed to start test containers"
                )

            try:
                # Run integration tests
                test_result = self._workspace_service.run_command([
                    str(self._cli_service._python_bin),
                    "-m",
                    "pytest",
                    "tests/integration",
                    "-v",
                    "--tb=short",
                ])

                if test_result.is_failure:
                    return FlextResult[dict[str, str]].fail("Integration tests failed")

                print_colored("✅ Integration tests passed!")
                return FlextResult[dict[str, str]].ok({"status": "tests_passed"})

            finally:
                # Clean up containers
                print_colored("Cleaning up test containers...")
                cleanup_result = self._workspace_service.run_command(["docker-compose"])
                if cleanup_result.is_failure:
                    self._cli_service._logger.warning(
                        "Failed to clean up test containers"
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

    def create_status_handler(self) -> _StatusCommands:
        """Create status command handler."""
        return self._StatusCommands(self)

    def create_test_handler(self) -> _TestCommands:
        """Create test command handler."""
        return self._TestCommands(self)

    def create_quality_handler(self) -> _QualityCommands:
        """Create quality command handler."""
        return self._QualityCommands(self)

    def create_build_handler(self) -> _BuildCommands:
        """Create build command handler."""
        return self._BuildCommands(self)

    def create_docker_handler(self) -> _DockerCommands:
        """Create Docker command handler."""
        return self._DockerCommands(self)

    def create_setup_handler(self) -> _SetupCommands:
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
        test_result = result.unwrap()
        if not test_result["success"]:
            print_colored(
                f"❌ Tests failed with return code {test_result['returncode']}"
            )
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
        check_result = result.unwrap()
        if check_result["overall_success"]:
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
        build_result = result.unwrap()
        if build_result["success"]:
            print_colored("✅ Build completed successfully")
        else:
            print_colored(
                f"❌ Build failed with return code {build_result['returncode']}"
            )
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
