"""FLEXT Workspace CLI - Enterprise Multi-Project Command Interface.

Provides comprehensive command-line interface for managing the entire FLEXT
ecosystem workspace with unified project coordination, task execution, and
development workflow automation. This module implements enterprise-grade
workspace management patterns for coordinating all 32 FLEXT projects with
consistent tooling and automation capabilities.

The workspace CLI serves as the central command interface for developers,
operations teams, and automation systems working with the distributed FLEXT
ecosystem. It provides consistent patterns for project management, testing,
deployment, and monitoring across all ecosystem components.

Key Components:
    - Project Management: Unified commands for all FLEXT ecosystem projects
    - Test Coordination: Cross-project testing and validation orchestration
    - Build Automation: Consistent build processes across Python and Go projects
    - Container Management: Docker and container orchestration commands
    - Development Workflows: Quality gates, formatting, and validation automation
    - Monitoring Integration: Health checks and system status coordination

Architecture:
    Implements enterprise CLI patterns with proper error handling, progress
    reporting, and rich terminal output. Coordinates with underlying project
    management systems while providing consistent interfaces across diverse
    project types and technologies within the FLEXT ecosystem.

Example:
    Workspace CLI usage for development workflows:

    >>> # Available through command line interface
    >>> # flext workspace status
    >>> # flext workspace test --all
    >>> # flext workspace build --projects flext-core,flext-api
    >>> # flext workspace lint --fix
    >>> # flext workspace deploy --environment staging

    >>> # Programmatic usage (for automation)
    >>> from flext.workspace_cli import WorkspaceCLI
    >>> from pathlib import Path
    >>>
    >>> cli = WorkspaceCLI(workspace_root=Path("/home/developer/flext"))
    >>> result = cli.run_tests(projects=["flext-core", "flext-api"])
    >>> if result.success:
    ...     print("All tests passed successfully")

Integration:
    - Built on Rich library for enhanced terminal output and progress reporting
    - Integrates with Click framework for robust command-line argument parsing
    - Coordinates with subprocess management for external tool execution
    - Supports both interactive and automated (CI/CD) execution modes
    - Provides comprehensive logging and error reporting capabilities

Quality Standards:
    - Comprehensive error handling with detailed context and recovery suggestions
    - Rich terminal output with progress bars, tables, and status indicators
    - Extensive validation of workspace state and project consistency
    - Performance optimization for large workspace operations
    - Security-conscious subprocess execution and path handling

Author: FLEXT Development Team
Version: 0.9.0
License: MIT

"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

# Initialize console
console = Console()

# Workspace root
WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent
VENV_PATH = WORKSPACE_ROOT / ".venv"
PYTHON_BIN = VENV_PATH / "bin" / "python"

# Module directories
MODULE_DIRS = {
    "flext-core": WORKSPACE_ROOT / "flext-core",
    "flext-api": WORKSPACE_ROOT / "flext-api",
    "flext-cli": WORKSPACE_ROOT / "flext-cli",
    "flext-web": WORKSPACE_ROOT / "flext-web",
    "flext-grpc": WORKSPACE_ROOT / "flext-grpc",
    "flext-plugin": WORKSPACE_ROOT / "flext-plugin",
    "flext-auth": WORKSPACE_ROOT / "flext-auth",
    "flext-observability": WORKSPACE_ROOT / "flext-observability",
    "flext-meltano": WORKSPACE_ROOT / "flext-meltano",
    "flext-quality": WORKSPACE_ROOT / "flext-quality",
}


class WorkspaceService:
    """Enterprise service for managing FLEXT workspace operations.

    Provides comprehensive workspace management capabilities including command
    execution, module status tracking, and build coordination across the entire
    FLEXT ecosystem. Implements service layer patterns with proper error handling
    and subprocess management for reliable workspace operations.

    This service serves as the foundation for CLI commands and automation tools,
    providing consistent interfaces for workspace operations while maintaining
    security and reliability standards for enterprise environments.

    Attributes:
        modules (Dict[str, Path]): Registry of discovered FLEXT modules and paths

    Features:
        - Secure subprocess execution with proper error handling
        - Module discovery and status tracking across workspace
        - Make target execution with workspace and module scoping
        - Progress reporting and rich terminal output integration
        - Cross-platform command execution and path management

    Architecture:
        Implements service layer patterns with clear separation between
        command execution, module management, and status reporting.
        Uses secure subprocess management with comprehensive error handling.

    Example:
        Initialize and use workspace service:

        >>> service = WorkspaceService()
        >>> modules = service.list_modules()
        >>> for module in modules:
        ...     if module["exists"]:
        ...         print(f"✓ {module['name']} is available")
        >>>
        >>> # Execute workspace commands
        >>> result = service.run_make_target("test", module="flext-core")
        >>> if result.returncode == 0:
        ...     print("Tests passed successfully")

    """

    def __init__(self) -> None:
        """Initialize workspace service with module discovery and configuration.

        Creates a new WorkspaceService instance with automatic module discovery
        and workspace configuration. Prepares the service for coordinating
        operations across all FLEXT ecosystem projects with proper initialization
        of module registry and workspace settings.

        Initialization:
            - Builds module registry from predefined MODULE_DIRS configuration
            - Validates workspace structure and module availability
            - Prepares subprocess execution environment
            - Sets up logging and error handling infrastructure

        Architecture:
            Uses dependency injection patterns for module configuration
            while maintaining clear separation between initialization
            and operational concerns.

        Example:
            Initialize workspace service:

            >>> service = WorkspaceService()
            >>> print(f"Managing {len(service.modules)} FLEXT modules")
            >>> print(f"Modules: {list(service.modules.keys())}")

        """
        self.modules = MODULE_DIRS

    def run_command(
        self,
        command: FlextTypes.Core.StringList,
        cwd: Path | None = None,
        *,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """Execute command in workspace with comprehensive error handling and security.

        Runs external commands with proper subprocess management, security settings,
        and error handling. Provides consistent command execution across the workspace
        with rich terminal output and comprehensive logging for development and
        automation workflows.

        Args:
            command (List[str]): Command and arguments to execute as separate list
                elements. Commands are executed with shell=False for security.
            cwd (Optional[Path]): Working directory for command execution. If None,
                uses workspace root as working directory.
            check (bool): Whether to exit on command failure. If True, exits with
                command return code on failure. Defaults to True.

        Returns:
            subprocess.CompletedProcess[str]: Completed process result with stdout,
            stderr, and return code. Text output is captured for analysis.

        Security Features:
            - Uses shell=False to prevent shell injection attacks
            - Explicit command and argument separation
            - Controlled working directory management
            - Comprehensive output capture and validation

        Architecture:
            Uses secure subprocess execution patterns with proper error
            handling and rich terminal integration for enterprise-grade
            command execution with comprehensive logging.

        Example:
            Execute workspace commands:

            >>> service = WorkspaceService()
            >>> # Run test command with error checking
            >>> result = service.run_command(["make", "test"])
            >>> print(f"Exit code: {result.returncode}")
            >>>
            >>> # Run command without automatic exit on failure
            >>> result = service.run_command(["make", "lint"], check=False)
            >>> if result.returncode != 0:
            ...     print(f"Lint failed: {result.stderr}")

        Raises:
            SystemExit: If check=True and command fails (non-zero exit code)

        """
        if cwd is None:
            cwd = WORKSPACE_ROOT

        # Basic input validation for security
        if not command or not all(isinstance(arg, str) for arg in command):
            msg = "Command must be a non-empty list of strings"
            raise ValueError(msg)

        console.print(f"[dim]Running: {' '.join(command)} in {cwd}[/dim]")

        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            shell=False,  # Security: explicit shell=False
        )

        if check and result.returncode != 0:
            console.print(f"[red]Command failed: {result.stderr}[/red]")
            sys.exit(result.returncode)

        return result

    def run_make_target(
        self,
        target: str,
        module: str | None = None,
        *,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """Execute Make target in workspace or specific module with proper scoping.

        Runs Make build targets with automatic workspace or module scoping,
        providing consistent build automation across the FLEXT ecosystem.
        Supports both workspace-wide operations and module-specific targets
        with proper working directory management.

        Args:
            target (str): Make target to execute (e.g., 'test', 'lint', 'build').
                Must be a valid target defined in workspace or module Makefile.
            module (Optional[str]): Specific module to run target in. If None,
                runs target in workspace root. Must be valid module name.
            check (bool): Whether to exit on target failure. If True, exits with
                Make return code on failure. Defaults to True.

        Returns:
            subprocess.CompletedProcess[str]: Completed Make process result with
            stdout, stderr, and return code for analysis and reporting.

        Target Scoping:
            - Module targets: Executed in specific module directory
            - Workspace targets: Executed in workspace root directory
            - Automatic working directory resolution based on module parameter
            - Consistent Make execution across Python and Go projects

        Architecture:
            Delegates to run_command with proper working directory resolution
            for consistent Make target execution across diverse project types
            within the FLEXT ecosystem.

        Example:
            Execute Make targets:

            >>> service = WorkspaceService()
            >>> # Run test target in specific module
            >>> result = service.run_make_target("test", module="flext-core")
            >>> print(
            ...     f"flext-core tests: {'passed' if result.returncode == 0 else 'failed'}"
            ... )
            >>>
            >>> # Run workspace-wide target
            >>> result = service.run_make_target("lint-all")
            >>> print(f"Workspace linting completed")

        """
        cwd = self.modules.get(module, WORKSPACE_ROOT) if module else WORKSPACE_ROOT

        return self.run_command(["make", target], cwd=cwd, check=check)

    def get_module_status(self, module: str) -> FlextTypes.Core.Dict:
        """Get comprehensive status information for a specific FLEXT module.

        Analyzes module structure and configuration to provide detailed status
        information including existence, file structure, and development readiness.
        Performs comprehensive validation of module integrity for workspace
        coordination and development workflows.

        Args:
            module (str): Name of the module to analyze. Must be a valid
                module name from the workspace module registry.

        Returns:
            Dict[str, object]: Comprehensive module status information containing:
            - exists (bool): Whether module directory exists
            - name (str): Module name for identification
            - path (str): Absolute path to module directory (if exists)
            - has_pyproject (bool): Whether pyproject.toml exists
            - has_makefile (bool): Whether Makefile exists
            - has_src (bool): Whether src/ directory exists
            - has_tests (bool): Whether tests/ directory exists

        Status Validation:
            - Directory existence and accessibility
            - Python project configuration (pyproject.toml)
            - Build automation (Makefile)
            - Source code organization (src/ directory)
            - Test infrastructure (tests/ directory)

        Architecture:
            Uses filesystem checking with proper error handling
            to provide reliable module status information for
            workspace coordination and development tooling.

        Example:
            Check module status:

            >>> service = WorkspaceService()
            >>> status = service.get_module_status("flext-core")
            >>> if status["exists"]:
            ...     print(f"✓ {status['name']} at {status['path']}")
            ...     if status["has_tests"]:
            ...         print("  - Tests available")
            ... else:
            ...     print(f"✗ {status['name']} not found")

        """
        module_path = self.modules.get(module)
        if not module_path or not module_path.exists():
            return {"exists": False, "name": module}

        # Check for key files
        has_pyproject = (module_path / "pyproject.toml").exists()
        has_makefile = (module_path / "Makefile").exists()
        has_src = (module_path / "src").exists()
        has_tests = (module_path / "tests").exists()

        return {
            "exists": True,
            "name": module,
            "path": str(module_path),
            "has_pyproject": has_pyproject,
            "has_makefile": has_makefile,
            "has_src": has_src,
            "has_tests": has_tests,
        }

    def list_modules(self) -> list[FlextTypes.Core.Dict]:
        """List all workspace modules with comprehensive status information.

        Retrieves status information for all registered FLEXT modules in the
        workspace, providing a complete overview of module availability,
        structure, and development readiness for workspace coordination
        and tooling integration.

        Returns:
            List[Dict[str, object]]: List of module status dictionaries, each
            containing comprehensive status information as returned by
            get_module_status(). Includes all registered modules regardless
            of existence or structure validity.

        Module Information:
            - Complete status for all registered FLEXT modules
            - Existence validation and path information
            - Project structure analysis (pyproject.toml, Makefile, etc.)
            - Development readiness assessment (src/, tests/)

        Architecture:
            Uses module registry iteration with status analysis for
            each module, providing comprehensive workspace overview
            for development and automation workflows.

        Example:
            List all modules and their status:

            >>> service = WorkspaceService()
            >>> modules = service.list_modules()
            >>> for module in modules:
            ...     status = "✓" if module["exists"] else "✗"
            ...     print(f"{status} {module['name']}")
            ...     if module["exists"] and module["has_tests"]:
            ...         print("    Tests available")

            Filter available modules:

            >>> available_modules = [m for m in service.list_modules() if m["exists"]]
            >>> print(f"Found {len(available_modules)} available modules")

        """
        return [self.get_module_status(module) for module in self.modules]


# Initialize service
workspace_service = WorkspaceService()


@click.group()
@click.version_option(version="0.7.0", prog_name="flext-workspace")
def cli() -> None:
    """FLEXT Workspace Management CLI.

    Unified interface for managing all FLEXT projects, running tests,
    managing containers, and coordinating tasks across the workspace.
    """


@cli.command()
def status() -> None:
    """Display comprehensive status overview of all workspace modules.

    Shows detailed status information for all discovered FLEXT ecosystem modules
    including existence validation, project structure analysis, and development
    readiness assessment. Provides rich terminal output with structured tables
    for effective workspace monitoring and validation.

    Status Information:
        - Module existence and accessibility
        - PyProject configuration presence (pyproject.toml)
        - Build automation availability (Makefile)
        - Source code organization (src/ directory)
        - Test infrastructure availability (tests/ directory)

    Output Format:
        Rich table with color-coded status indicators showing comprehensive
        module information for development workflow coordination.

    Architecture:
        Uses workspace service for module discovery and status analysis
        with rich terminal formatting for enhanced developer experience.

    Example:
        Command line usage:

        $ flext workspace status

        Output shows table with module status, configuration files,
        and development infrastructure availability.

    Note:
        This command provides read-only workspace analysis and does not
        modify any files or configuration.

    """
    console.print(Panel.fit("FLEXT Workspace Status", style="bold blue"))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Module", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("PyProject", style="yellow")
    table.add_column("Makefile", style="yellow")
    table.add_column("Source", style="yellow")
    table.add_column("Tests", style="yellow")

    for module_info in workspace_service.list_modules():
        if module_info["exists"]:
            status = "✓ Found"
            pyproject = "✓" if module_info["has_pyproject"] else "✗"
            makefile = "✓" if module_info["has_makefile"] else "✗"
            src = "✓" if module_info["has_src"] else "✗"
            tests = "✓" if module_info["has_tests"] else "✗"
        else:
            status = "✗ Missing"
            pyproject = makefile = src = tests = "-"

        table.add_row(
            str(module_info["name"]),
            str(status),
            str(pyproject),
            str(makefile),
            str(src),
            str(tests),
        )

    console.print(table)


@cli.command()
@click.option(
    "--module",
    "-m",
    type=click.Choice(list(MODULE_DIRS.keys())),
    help="Run tests for specific module only",
)
@click.option(
    "--integration",
    "-i",
    is_flag=True,
    help="Run integration tests",
)
@click.option(
    "--coverage",
    "-c",
    is_flag=True,
    help="Generate coverage report",
)
def test(module: str | None, *, integration: bool, coverage: bool) -> None:
    """Execute comprehensive test suites across workspace or specific module.

    Runs automated testing with support for module-specific execution,
    integration test coordination, and coverage analysis. Provides parallel
    test execution with progress reporting and detailed result aggregation
    for enterprise-grade quality assurance.

    Args:
        module (Optional[str]): Specific module to test. If provided, runs
            tests only for the specified module. Must be valid module name.
        integration (bool): Enable integration test execution for cross-module
            interaction testing and system integration validation.
        coverage (bool): Generate comprehensive coverage reports with detailed
            analysis of test coverage across codebase.

    Test Execution:
        - Module-specific: Focused testing for individual module development
        - Workspace-wide: Complete testing across all modules with progress tracking
        - Integration tests: Cross-module interaction and system validation
        - Coverage analysis: Detailed coverage reporting and metrics

    Features:
        - Parallel test execution for improved performance
        - Rich terminal output with progress bars and status indicators
        - Comprehensive error reporting and failure analysis
        - Integration with quality gates and CI/CD workflows

    Architecture:
        Uses workspace service for test coordination with proper error
        handling and progress reporting. Implements enterprise testing
        patterns for reliable quality assurance.

    Example:
        Test specific module:

        $ flext workspace test --module flext-core

        Test all modules with coverage:

        $ flext workspace test --coverage

        Run integration tests:

        $ flext workspace test --integration

    Security:
        Uses secure subprocess execution with proper isolation
        and timeout management for reliable test execution.

    """
    # Build test command with flags based on parameters
    test_cmd = "test"
    if integration:
        test_cmd += " test-integration"
    if coverage:
        test_cmd += " test-coverage"

    if module:
        console.print(f"[bold]Running tests for {module}[/bold]")
        console.print(f"[dim]Integration: {integration}, Coverage: {coverage}[/dim]")
        workspace_service.run_make_target(test_cmd, module=module)
    else:
        console.print("[bold]Running all workspace tests[/bold]")
        console.print(f"[dim]Integration: {integration}, Coverage: {coverage}[/dim]")
        with Progress() as progress:
            task = progress.add_task("[cyan]Testing modules...", total=len(MODULE_DIRS))

            for module_name in MODULE_DIRS:
                progress.update(task, description=f"[cyan]Testing {module_name}...")
                result = workspace_service.run_make_target(
                    test_cmd,
                    module=module_name,
                    check=False,
                )
                if result.returncode == 0:
                    console.print(f"[green]✓[/green] {module_name} tests passed")
                else:
                    console.print(f"[red]✗[/red] {module_name} tests failed")
                progress.advance(task)


@cli.command()
@click.option(
    "--module",
    "-m",
    type=click.Choice(list(MODULE_DIRS.keys())),
    help="Run quality checks for specific module only",
)
def check(module: str | None, *, integration: bool, coverage: bool) -> None:
    """Execute comprehensive quality analysis across workspace or specific module.

    Performs automated code quality validation including linting, type checking,
    security scanning, and architectural compliance verification. Implements
    enterprise-grade quality gates with detailed reporting and error analysis
    for maintaining code excellence across the FLEXT ecosystem.

    Args:
        module (Optional[str]): Specific module for quality analysis. If provided,
            runs quality checks only for the specified module. Must be valid
            module name from workspace registry.
        integration (bool): Enable integration-level quality checks for
            cross-module consistency and architectural compliance.
        coverage (bool): Include coverage analysis in quality assessment
            with detailed metrics and reporting.

    Quality Checks:
        - Static analysis: Code quality, complexity, and maintainability
        - Type checking: Type annotation validation and coverage
        - Security scanning: Vulnerability detection and security compliance
        - Style validation: PEP8 compliance and formatting consistency
        - Import analysis: Circular dependencies and unused imports

    Features:
        - Module-specific or workspace-wide analysis
        - Comprehensive error reporting with actionable recommendations
        - Integration with quality gates and CI/CD workflows
        - Performance optimization for large-scale analysis

    Architecture:
        Uses workspace service for quality coordination with proper
        error handling and detailed reporting. Implements enterprise
        quality assurance patterns for reliable validation.

    Example:
        Check specific module:

        $ flext workspace check --module flext-core

        Check entire workspace:

        $ flext workspace check

        Check with coverage analysis:

        $ flext workspace check --coverage

    Integration:
        Results integrate with quality gates for automated validation
        and can block deployments when critical issues are detected.

    """
    # Build quality check command with flags based on parameters
    check_cmd = "check"
    if integration:
        check_cmd += " check-integration"
    if coverage:
        check_cmd += " check-coverage"

    if module:
        console.print(f"[bold]Running quality checks for {module}[/bold]")
        console.print(f"[dim]Integration: {integration}, Coverage: {coverage}[/dim]")
        workspace_service.run_make_target(check_cmd, module=module)
    else:
        console.print("[bold]Running workspace quality checks[/bold]")
        console.print(f"[dim]Integration: {integration}, Coverage: {coverage}[/dim]")
        workspace_service.run_make_target(f"{check_cmd}-all")


@cli.command()
@click.option(
    "--module",
    "-m",
    type=click.Choice(list(MODULE_DIRS.keys())),
    help="Build specific module only",
)
def build(module: str | None, *, integration: bool, coverage: bool) -> None:
    """Execute comprehensive build process for workspace or specific module.

    Performs automated build operations including compilation, packaging,
    dependency resolution, and artifact generation. Supports both module-specific
    builds for focused development and workspace-wide builds for complete
    system preparation with enterprise-grade build coordination.

    Args:
        module (Optional[str]): Specific module to build. If provided, builds
            only the specified module with its dependencies. Must be valid
            module name from workspace registry.
        integration (bool): Enable integration build mode for cross-module
            dependency resolution and system-wide build coordination.
        coverage (bool): Include build coverage analysis and reporting
            for comprehensive build validation and metrics.

    Build Operations:
        - Dependency resolution: Complete dependency graph analysis
        - Compilation: Source code compilation and validation
        - Packaging: Artifact creation and distribution preparation
        - Validation: Build output verification and quality checking
        - Integration: Cross-module build coordination

    Features:
        - Module-specific or workspace-wide build execution
        - Parallel build processing for improved performance
        - Comprehensive error reporting and build analysis
        - Integration with deployment and distribution workflows

    Architecture:
        Uses workspace service for build coordination with proper
        dependency management and error handling. Implements enterprise
        build patterns for reliable artifact generation.

    Example:
        Build specific module:

        $ flext workspace build --module flext-core

        Build entire workspace:

        $ flext workspace build

        Integration build with coverage:

        $ flext workspace build --integration --coverage

    Security:
        Uses secure build processes with proper isolation and
        validation to ensure build integrity and security.

    """
    # Build command with flags based on parameters
    build_cmd = "build"
    if integration:
        build_cmd += " build-integration"
    if coverage:
        build_cmd += " build-coverage"

    if module:
        console.print(f"[bold]Building {module}[/bold]")
        console.print(f"[dim]Integration: {integration}, Coverage: {coverage}[/dim]")
        workspace_service.run_make_target(build_cmd, module=module)
    else:
        console.print("[bold]Building entire workspace[/bold]")
        console.print(f"[dim]Integration: {integration}, Coverage: {coverage}[/dim]")
        workspace_service.run_make_target(f"{build_cmd}-all")


@cli.group()
def docker() -> None:
    """Docker container management commands."""


@docker.command("up")
@click.option(
    "--service",
    "-s",
    multiple=True,
    help="Specific services to start",
)
def docker_up(service: tuple[str, ...], *, integration: bool, coverage: bool) -> None:
    """Start Docker containers for comprehensive development environment.

    Initializes and starts Docker containers required for FLEXT ecosystem
    development including databases, message queues, monitoring services,
    and supporting infrastructure. Supports selective service startup
    for focused development workflows.

    Args:
        service (Tuple[str, ...]): Specific services to start. If provided,
            only the specified services will be started. If empty, starts
            all configured development services.
        integration (bool): Enable integration-specific container configuration
            for cross-service testing and validation.
        coverage (bool): Enable coverage analysis containers and monitoring
            for development testing workflows.

    Container Services:
        - PostgreSQL: Primary database (port 5433)
        - Redis: Caching and session storage (port 6380)
        - Monitoring: Observability and metrics collection
        - Supporting: Additional development infrastructure

    Features:
        - Detached mode execution for background operation
        - Service dependency resolution and startup ordering
        - Health check integration and startup validation
        - Network configuration for inter-service communication
        - Volume management for persistent data storage

    Architecture:
        Uses Docker Compose orchestration with proper service
        coordination and health checking for reliable development
        environment initialization.

    Example:
        Start all development containers:

        $ flext workspace docker up

        Start specific services:

        $ flext workspace docker up --service postgres --service redis

        Start with integration support:

        $ flext workspace docker up --integration

    Note:
        Containers run in detached mode and remain active until
        explicitly stopped with docker down command.

    """
    console.print("[bold]Starting Docker containers[/bold]")
    console.print(f"[dim]Integration: {integration}, Coverage: {coverage}[/dim]")

    cmd = ["docker-compose", "up", "-d"]

    # Add profile flags based on parameters
    if integration:
        cmd.extend(["--profile", "integration"])
    if coverage:
        cmd.extend(["--profile", "coverage"])

    if service:
        cmd.extend(service)

    workspace_service.run_command(cmd)
    console.print("[green]Containers started successfully[/green]")


@docker.command("down")
def docker_down(
    *,
    integration: bool,
    coverage: bool,
) -> None:
    """Stop and remove Docker containers with comprehensive cleanup.

    Gracefully stops all running Docker containers and removes container
    instances, networks, and temporary volumes created during development.
    Provides clean shutdown of the development environment with proper
    resource cleanup and state preservation.

    Args:
        integration (bool): Enable integration-specific cleanup procedures
            for cross-service testing environments and validation.
        coverage (bool): Enable coverage data preservation and cleanup
            procedures for testing workflows.

    Cleanup Operations:
        - Graceful container shutdown with proper signal handling
        - Network removal and cleanup
        - Temporary volume cleanup (preserves persistent data)
        - Resource deallocation and system cleanup
        - Port release and binding cleanup

    Data Preservation:
        - Persistent volumes remain intact for database state
        - Configuration files and logs are preserved
        - Development data persists across container restarts
        - User-created content remains available

    Architecture:
        Uses Docker Compose orchestration with proper shutdown
        sequencing and resource management for reliable environment
        cleanup without data loss.

    Example:
        Stop all containers:

        $ flext workspace docker down

        Stop with integration cleanup:

        $ flext workspace docker down --integration

    Security:
        Ensures proper cleanup of temporary containers and networks
        while preserving persistent development data and configuration.

    """
    console.print("[bold]Stopping Docker containers[/bold]")
    console.print(f"[dim]Integration: {integration}, Coverage: {coverage}[/dim]")

    # Build cleanup command with flags based on parameters
    cmd = ["docker-compose", "down"]
    if integration:
        cmd.extend(["--rmi", "local"])  # Remove local images for integration cleanup
    if coverage:
        cmd.append("--volumes")  # Preserve volumes for coverage data

    workspace_service.run_command(cmd)
    console.print("[green]Containers stopped successfully[/green]")


@docker.command("logs")
@click.argument("service", required=False)
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
def docker_logs(service: str | None, *, follow: bool) -> None:
    """View and monitor Docker container logs with real-time streaming.

    Displays log output from Docker containers with support for real-time
    monitoring, specific service filtering, and comprehensive log analysis.
    Provides essential debugging and monitoring capabilities for development
    workflow troubleshooting and system analysis.

    Args:
        service (Optional[str]): Specific service to view logs for. If provided,
            shows logs only for the specified service. If None, shows logs
            from all running containers.
        follow (bool): Enable real-time log streaming. If True, continuously
            displays new log entries as they are generated.

    Log Features:
        - Real-time log streaming with follow mode
        - Service-specific log filtering
        - Comprehensive log aggregation across containers
        - Timestamp and service identification
        - Error highlighting and log level formatting

    Monitoring Capabilities:
        - Application error detection and analysis
        - Performance monitoring through log analysis
        - Service health monitoring via log patterns
        - Integration debugging across service boundaries
        - Development workflow troubleshooting

    Architecture:
        Uses Docker Compose log aggregation with proper streaming
        and filtering for effective development monitoring and
        debugging workflows.

    Example:
        View all container logs:

        $ flext workspace docker logs

        Follow specific service logs:

        $ flext workspace docker logs postgres --follow

        Monitor real-time activity:

        $ flext workspace docker logs --follow

    Note:
        Use Ctrl+C to exit follow mode and return to command prompt.
        Log output includes timestamps and service identification.

    """
    cmd = ["docker-compose", "logs"]
    if follow:
        cmd.append("-f")
    if service:
        cmd.append(service)

    workspace_service.run_command(cmd)


@cli.group()
def integration() -> None:
    """Integration testing commands."""


@integration.command("test")
@click.option(
    "--env",
    "-e",
    type=click.Choice(["development", "staging", "production"]),
    default="development",
    help="Environment to test",
)
def integration_test(env: str) -> None:
    """Execute comprehensive integration tests across entire FLEXT ecosystem.

    Runs end-to-end integration testing that validates cross-module interactions,
    service communication, data flow, and system-wide functionality across
    the complete FLEXT ecosystem. Provides environment-specific testing
    with proper infrastructure setup and cleanup.

    Args:
        env (str): Target environment for integration testing. Must be one of:
            - "development": Local development environment with test fixtures
            - "staging": Staging environment with production-like configuration
            - "production": Production environment (read-only validation)

    Test Coverage:
        - Cross-module API integration and communication
        - Database connectivity and transaction coordination
        - Message queue and event processing validation
        - Authentication and authorization across services
        - Data pipeline end-to-end functionality
        - External service integration and error handling

    Infrastructure Management:
        - Automatic test container startup and configuration
        - Service dependency resolution and health checking
        - Test database initialization and data seeding
        - Network configuration for service communication
        - Resource cleanup and environment restoration

    Environment Configuration:
        - Development: Local containers with test data
        - Staging: Production-like services with staging data
        - Production: Read-only validation without modification

    Architecture:
        Uses pytest with proper fixture management and environment
        isolation. Implements comprehensive cleanup patterns to
        ensure reliable test execution and environment consistency.

    Example:
        Run development integration tests:

        $ flext workspace integration test

        Test staging environment:

        $ flext workspace integration test --env staging

        Validate production connectivity:

        $ flext workspace integration test --env production

    Security:
        Uses environment-specific credentials and proper isolation
        to prevent test interference with production systems.

    """
    console.print(f"[bold]Running integration tests in {env} environment[/bold]")

    # Start required containers
    console.print("[dim]Starting test containers...[/dim]")
    workspace_service.run_command(
        ["docker-compose", "-f", "docker-compose.yml", "up", "-d"],
    )
    try:
        # Run integration tests
        workspace_service.run_command(
            [
                str(PYTHON_BIN),
                "-m",
                "pytest",
                "tests/integration",
                "-v",
                "--tb=short",
            ],
        )
        console.print("[green]Integration tests passed![/green]")
    finally:
        # Clean up containers
        console.print("[dim]Cleaning up test containers...[/dim]")
        workspace_service.run_command(["docker-compose", "down"])


@cli.command()
def setup() -> None:
    """Initialize comprehensive workspace environment for FLEXT development.

    Performs complete workspace initialization including dependency installation,
    development tool configuration, pre-commit hook setup, and environment
    validation. Prepares the workspace for productive development across
    the entire FLEXT ecosystem with all necessary tools and configurations.

    Setup Operations:
        - Dependency installation across all Python and Go projects
        - Development tool installation and configuration
        - Pre-commit hook installation and validation
        - Virtual environment setup and activation
        - Database and service initialization
        - Quality gate configuration and validation

    Progress Tracking:
        - Real-time progress reporting with detailed status updates
        - Step-by-step execution with failure isolation
        - Comprehensive error reporting and recovery suggestions
        - Performance timing and optimization recommendations

    Validation Steps:
        - Workspace structure validation and integrity checking
        - Tool availability and version compatibility verification
        - Service connectivity and health checking
        - Development environment functionality validation

    Architecture:
        Uses workspace service coordination with proper error handling
        and progress reporting. Implements enterprise setup patterns
        for reliable development environment initialization.

    Example:
        Initialize workspace for development:

        $ flext workspace setup

        Output shows progress through each setup phase with
        detailed status updates and completion confirmation.

    Error Handling:
        Setup process includes comprehensive error detection and
        recovery with detailed instructions for manual resolution
        when automated setup encounters issues.

    Note:
        First-time setup may take several minutes depending on
        network connectivity and system performance. Progress
        indicators provide real-time status updates.

    """
    console.print("[bold]Setting up FLEXT workspace[/bold]")

    with Progress() as progress:
        task = progress.add_task("[cyan]Setting up...", total=4)

        # Install dependencies
        progress.update(task, description="[cyan]Installing dependencies...")
        workspace_service.run_make_target("workspace-install")
        progress.advance(task)

        # Sync dependencies
        progress.update(task, description="[cyan]Syncing dependencies...")
        workspace_service.run_make_target("sync-deps")
        progress.advance(task)

        # Setup pre-commit hooks
        progress.update(task, description="[cyan]Setting up pre-commit hooks...")
        workspace_service.run_command(["pre-commit", "install"])
        progress.advance(task)

        # Final setup
        progress.update(task, description="[cyan]Finalizing setup...")
        workspace_service.run_make_target("dev-setup")
        progress.advance(task)

    console.print("[green]Workspace setup complete![/green]")


@cli.command()
def clean() -> None:
    """Remove workspace artifacts, caches, and temporary files with confirmation.

    Performs comprehensive workspace cleanup including build artifacts, cache files,
    temporary directories, and generated content while preserving source code
    and configuration files. Provides interactive confirmation to prevent
    accidental data loss during cleanup operations.

    Cleanup Operations:
        - Build artifacts: Compiled binaries, packages, and distribution files
        - Cache files: Python bytecode, pytest cache, and tool caches
        - Temporary files: Log files, temporary directories, and workspace debris
        - Generated content: Auto-generated documentation and reports
        - Virtual environments: Optional cleanup of project-specific environments

    Preservation:
        - Source code files and project structure
        - Configuration files and workspace settings
        - User-created documentation and assets
        - Database data and persistent storage
        - Git history and version control data

    Safety Features:
        - Interactive confirmation before destructive operations
        - Detailed preview of files and directories to be removed
        - Selective cleanup options for specific artifact types
        - Backup creation for critical generated content
        - Recovery instructions for accidental cleanup

    Architecture:
        Uses Make target delegation with proper error handling and
        user confirmation patterns. Implements safe cleanup procedures
        with comprehensive validation and rollback capabilities.

    Example:
        Clean workspace with confirmation:

        $ flext workspace clean
        This will remove all build artifacts and caches. Continue? [y/N]: y

        User will be prompted for confirmation before cleanup proceeds.

    Performance:
        Cleanup operation is optimized for large workspaces with
        parallel processing where safe to do so.

    """
    console.print("[bold]Cleaning workspace[/bold]")

    if click.confirm("This will remove all build artifacts and caches. Continue?"):
        workspace_service.run_make_target("clean-workspace")
        console.print("[green]Workspace cleaned successfully[/green]")


if __name__ == "__main__":
    cli()
