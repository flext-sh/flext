#!/usr/bin/env python3
"""FLEXT Core Scripts - Enterprise Script Foundation Framework.

Provides comprehensive base classes and utilities for creating FLEXT scripts with
enterprise-grade error handling, logging, command-line interfaces, and execution
patterns. This module implements standardized script patterns that ensure
consistency, reliability, and maintainability across all FLEXT ecosystem
automation and operational scripts.

The script framework provides structured patterns for script lifecycle management,
validation, execution, and cleanup with comprehensive error handling and rich
terminal output. All scripts follow Clean Architecture principles and integrate
with FLEXT observability and monitoring systems.

Key Components:
    - FlextScript: Abstract base class for enterprise-grade script implementation
    - ScriptMetadata: Comprehensive metadata management for scripts
    - Script Lifecycle: Structured validation, execution, and cleanup patterns
    - Error Handling: Comprehensive error handling with context preservation
    - CLI Integration: Rich command-line interface with consistent patterns
    - Logging Integration: Structured logging with performance monitoring

Architecture:
    Implements enterprise script patterns with proper separation of concerns,
    validation boundaries, and error handling strategies. Scripts provide
    consistent interfaces while allowing for specialized implementation
    of business logic and operational requirements.

Example:
    Creating enterprise-grade FLEXT scripts:

    >>> from flext_tools.core.script_base import FlextScript, ScriptMetadata
    >>> from flext_tools.core.script_base import create_simple_script
    >>>
    >>> class DataProcessingScript(FlextScript):
    ...     @property
    ...     def metadata(self) -> ScriptMetadata:
    ...         return ScriptMetadata(
    ...             name="data-processor",
    ...             description="Process FLEXT data with validation and monitoring",
    ...             category="data-operations",
    ...             version="2.0.0",
    ...             requires_confirmation=True,
    ...         )
    ...
    ...     def validate_preconditions(self) -> bool:
    ...         # Validate environment and dependencies
    ...         return True
    ...
    ...     def execute_main_logic(self) -> bool:
    ...         # Implement data processing logic
    ...         self.logger.info("Processing data with enterprise patterns")
    ...         return True
    ...
    ...     def cleanup(self) -> None:
    ...         # Cleanup resources and temporary files
    ...         pass
    >>>
    >>> # Simple script creation for automation
    >>> def process_pipeline() -> bool:
    ...     # Simple processing logic
    ...     return True
    >>>
    >>> SimpleProcessorScript = create_simple_script(
    ...     name="pipeline-processor",
    ...     description="Simple pipeline processing automation",
    ...     category="automation",
    ...     main_func=process_pipeline,
    ... )

Integration:
    - Built on flext-core patterns with comprehensive error handling
    - Integrates with flext-observability for script monitoring and metrics
    - Supports rich terminal output with progress indication and status reporting
    - Coordinates with logging systems for audit trails and debugging
    - Provides foundation for automation, operations, and maintenance scripts

Quality Standards:
    - Comprehensive error handling with detailed context and recovery patterns
    - Full type annotation coverage for enhanced development experience
    - Structured lifecycle management with validation and cleanup boundaries
    - Performance monitoring and execution time tracking built-in
    - Security-conscious execution with proper privilege and resource management

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

import argparse
import inspect
import logging
import time
from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import ParamSpec

from flext_core import (
    FlextDomainService,
    FlextLogger,
    FlextModels,
    FlextResult,
)
from flext_core.container import FlextContainer

from .colors import Colors, print_colored
from .quality_gateway import (
    QualityCheckConfig,
    QualityGateway,
    all_quality_checks_passed,
    get_quality_failure_summary,
)

P_main_func = ParamSpec("P_main_func")

# Use flext-core logger
logger = FlextLogger(__name__)


class ScriptMetadata(FlextModels.Value):
    """Comprehensive metadata for FLEXT scripts using value object patterns.

    Encapsulates all metadata required for script identification, lifecycle
    management, and execution control. Built on flext-core FlextModels.Value for
    immutability and business rule validation with enterprise-grade metadata
    management for the FLEXT ecosystem.

    This value object ensures consistent script metadata structure across all
    FLEXT automation and operational scripts, providing standardized attributes
    for script categorization, versioning, and execution preferences.

    Attributes:
        name: Unique script identifier using kebab-case naming convention.
        description: Human-readable description of script purpose and functionality.
        category: Script category for organization (e.g., "automation", "maintenance").
        version: Semantic version string for script versioning and compatibility.
        requires_confirmation: Whether script requires user confirmation before execution.
        dry_run_supported: Whether script supports dry-run mode for safe testing.

    Example:
        Create script metadata with validation:

        >>> metadata = ScriptMetadata(
        ...     name="data-processor",
        ...     description="Process FLEXT data with validation",
        ...     category="data-operations",
        ...     version="2.1.0",
        ...     requires_confirmation=True,
        ... )
        >>> validation = metadata.validate_business_rules()
        >>> if validation.success:
        ...     print(f"Script: {metadata.name} v{metadata.version}")

    Note:
        Uses flext-core value object patterns for immutability and
        comprehensive business rule validation.

    """

    name: str
    description: str
    category: str
    version: str = "1.0.0"
    requires_confirmation: bool = False
    dry_run_supported: bool = True

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate script metadata business rules."""
        if not self.name.strip():
            return FlextResult[None].fail("Script name cannot be empty")

        if not self.description.strip():
            return FlextResult[None].fail("Script description cannot be empty")

        if not self.category.strip():
            return FlextResult[None].fail("Script category cannot be empty")

        return FlextResult[None].ok(None)


class FlextScript(FlextDomainService[bool]):
    """Abstract base class for enterprise-grade FLEXT scripts with lifecycle management.

    Provides comprehensive foundation for creating robust, maintainable FLEXT scripts
    with integrated error handling, validation, logging, and execution patterns.
    Built on Clean Architecture principles with railway-oriented programming via
    FlextResult and full integration with the FLEXT ecosystem infrastructure.

    This base class standardizes script development across the FLEXT ecosystem,
    ensuring consistent patterns for script metadata, validation, execution,
    and cleanup with comprehensive error handling and observability integration.

    Features:
        - Railway-oriented programming with FlextResult error handling
        - Integrated validation pipeline with quality gates
        - Structured logging with performance monitoring
        - Dependency injection container integration
        - Rich terminal output with progress indication
        - Standardized command-line interface patterns
        - Comprehensive lifecycle management (setup, validate, execute, cleanup)

    Architecture:
        Implements Clean Architecture with proper separation between script logic,
        infrastructure concerns, and user interface. Scripts define business logic
        while the framework handles cross-cutting concerns like logging, validation,
        and error handling.

    Example:
        Implement enterprise-grade FLEXT script:

        >>> class DataProcessingScript(FlextScript):
        ...     @property
        ...     def metadata(self) -> ScriptMetadata:
        ...         return ScriptMetadata(
        ...             name="data-processor",
        ...             description="Process data with enterprise patterns",
        ...             category="data-operations",
        ...             version="2.0.0",
        ...         )
        ...
        ...     def validate_preconditions(self) -> FlextResult[None]:
        ...         # Validate environment and dependencies
        ...         if not self.check_database_connectivity():
        ...             return FlextResult[None].fail("Database not accessible")
        ...         return FlextResult[None].ok(None)
        ...
        ...     def execute_main_logic(self, **kwargs) -> FlextResult[object]:
        ...         # Implement business logic with error handling
        ...         result = self.process_data_safely()
        ...         return FlextResult[None].ok(result)

    Integration:
        Integrates with flext-core patterns, flext-observability monitoring,
        and quality gateway validation for comprehensive script infrastructure.

    """

    def __init__(self) -> None:
        """Initialize the script with flext-core infrastructure."""
        # Note: logger is provided by FlextDomainService base class
        self.start_time = time.time()
        self.container = FlextContainer.get_global()

    @property
    @abstractmethod
    def metadata(self) -> ScriptMetadata:
        """Return script metadata as flext-core value object."""

    @abstractmethod
    def validate_preconditions(self) -> FlextResult[None]:
        """Validate that script can run successfully using FlextResult pattern.

        Returns:
            FlextResult[None] indicating validation success or failure with context

        """

    @abstractmethod
    def execute_main_logic(self, **kwargs: object) -> FlextResult[object]:
        """Execute the main script logic with railway-oriented programming.

        Args:
            **kwargs: Additional arguments for script execution

        Returns:
            FlextResult containing execution result or error information

        """

    def execute(self) -> FlextResult[bool]:
        """Execute the script using FlextDomainService pattern.

        This method orchestrates the script execution lifecycle:
        precondition validation, main logic execution, and result handling.

        Returns:
            FlextResult[bool] indicating overall script success

        """
        # Validate preconditions first
        validation_result = self.validate_preconditions()
        if validation_result.is_failure:
            return FlextResult[bool].fail(
                validation_result.error or "Precondition validation failed"
            )

        # Execute main logic
        execution_result = self.execute_main_logic()
        if execution_result.is_failure:
            return FlextResult[bool].fail(
                execution_result.error or "Script execution failed"
            )

        # Return success
        success = True
        return FlextResult[bool].ok(success)

    def cleanup(self) -> FlextResult[None]:
        """Perform cleanup operations after execution.

        Returns:
            FlextResult indicating cleanup success or failure

        """
        return FlextResult[None].ok(None)

    def setup(self) -> FlextResult[None]:
        """Perform any setup operations before main execution.

        Returns:
            FlextResult indicating setup success or failure

        """
        return FlextResult[None].ok(None)

    def run(self, **kwargs: object) -> int:
        """Run the complete script with FlextResult railway-oriented programming.

        Args:
            **kwargs: Additional arguments passed to execute_main_logic

        Returns:
            0 for success, non-zero for failure

        """
        try:
            self._print_header()

            # Extract common flags
            is_dry_run = bool(kwargs.get("dry_run"))
            skip_validation = bool(kwargs.get("no_validate"))
            relaxed_validation = bool(kwargs.get("relaxed_validation"))

            if is_dry_run:
                print_colored("🧪 Dry-run mode: no changes will be made", Colors.YELLOW)

            # Run central FLEXT validation unless skipped
            if not skip_validation:
                validation_result = self._run_flext_validation(
                    strict=not relaxed_validation,
                )
                if not validation_result.success:
                    print_colored(
                        f"❌ Validation failed: {validation_result.error}",
                        Colors.RED,
                    )
                    return 1

            # Chain operations using FlextResult pattern
            result = (
                self.validate_preconditions()
                .flat_map(lambda _: self.setup())
                .flat_map(lambda _: self.execute_main_logic(**kwargs))
                .map(lambda _: self._print_success())
            )
            if result.success:
                return 0

            # Handle failure with detailed context
            error_msg = result.error or "Unknown error occurred"
            print_colored(f"❌ Script failed: {error_msg}", Colors.RED)
            self.logger.error(f"Script execution failed: {error_msg}")
            return 1

        except KeyboardInterrupt:
            print_colored("\n❌ Script interrupted by user", Colors.YELLOW)
            return 1
        except Exception as e:
            print_colored(f"❌ Unexpected error: {e}", Colors.RED)
            self.logger.exception("Script failed with exception")
            return 1
        finally:
            # Cleanup with error handling
            cleanup_result = self.cleanup()
            if not cleanup_result.success:
                self.logger.warning(f"Cleanup failed: {cleanup_result.error}")

    def _run_flext_validation(self, *, strict: bool) -> FlextResult[None]:
        """Run centralized FLEXT validation via QualityGateway.

        Args:
            strict: When True, missing tools fail validation; when False, they are
                reported but do not fail the validation.

        Returns:
            FlextResult indicating overall validation status.

        """
        try:
            workspace = Path.cwd()
            gateway = QualityGateway(workspace_path=workspace)
            config = QualityCheckConfig(relaxed=not strict)
            result = gateway.run_quality_checks_safe(config=config)
            if not result.success:
                return FlextResult[None].fail(result.error or "Quality checks failed")
            data = result.value or {}
            if not all_quality_checks_passed(data):
                summary = get_quality_failure_summary(data)
                return FlextResult[None].fail(summary)
            return FlextResult[None].ok(None)
        except Exception as exc:
            return FlextResult[None].fail(f"Validation error: {exc}")

    def _print_header(self) -> None:
        """Print script header with metadata."""
        print_colored("=" * 60, Colors.CYAN)
        print_colored(f"🚀 {self.metadata.name} v{self.metadata.version}", Colors.CYAN)
        print_colored(f"📋 {self.metadata.description}", Colors.BLUE)
        print_colored(f"🏷️  Category: {self.metadata.category}", Colors.BLUE)
        print_colored("=" * 60, Colors.CYAN)

    def _print_success(self) -> None:
        """Print success message with execution time."""
        duration = time.time() - self.start_time
        print_colored("=" * 60, Colors.GREEN)
        print_colored(f"✅ {self.metadata.name} completed successfully!", Colors.GREEN)
        print_colored(f"⏱️  Execution time: {duration:.2f}s", Colors.GREEN)
        print_colored("=" * 60, Colors.GREEN)

    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with common options.

        Returns:
            Configured ArgumentParser instance

        """
        parser = argparse.ArgumentParser(
            description=self.metadata.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Common arguments
        if self.metadata.dry_run_supported:
            parser.add_argument(
                "--dry-run",
                action="store_true",
                help="Show what would be done without making changes",
            )

        parser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="Enable verbose output",
        )

        parser.add_argument(
            "--no-validate",
            action="store_true",
            help="Skip centralized FLEXT validation before execution",
        )

        parser.add_argument(
            "--relaxed-validation",
            action="store_true",
            help=("Do not fail if quality tools are missing; report warnings instead"),
        )

        return parser

    def main(self) -> int:
        """Execute the script with comprehensive command-line interface.

        Returns:
            Exit code (0 for success, non-zero for failure)

        """
        parser = self.create_parser()
        args = parser.parse_args()

        # Configure logging level
        if args.verbose:
            # Set verbose mode - use flext-core logging patterns
            FlextLogger().setLevel(logging.DEBUG)
            # TODO: Integrate with flext-core centralized logging configuration

        return self.run(**vars(args))


@dataclass
class ScriptConfig[**P_main_func]:
    """Configuration model for simple script creation and factory patterns.

    Encapsulates all configuration required for creating simple FLEXT scripts
    through the factory pattern. Provides type-safe configuration with proper
    function signatures and optional lifecycle hooks for streamlined script
    development.

    This configuration enables rapid script creation while maintaining enterprise
    standards and integration with the FLEXT ecosystem infrastructure.

    Attributes:
        name: Unique script identifier for the generated script.
        description: Human-readable description of script functionality.
        category: Script category for organization and classification.
        main_func: Primary script logic function with proper type parameters.
        setup_func: Optional setup function for pre-execution initialization.
        validate_func: Optional validation function for precondition checking.

    Example:
        Configure simple script with validation:

        >>> def process_data() -> FlextResult[str]:
        ...     return FlextResult[None].ok("processed")
        >>>
        >>> def validate_environment() -> FlextResult[None]:
        ...     return FlextResult[None].ok(None)
        >>>
        >>> config = ScriptConfig(
        ...     name="data-processor",
        ...     description="Simple data processing script",
        ...     category="automation",
        ...     main_func=process_data,
        ...     validate_func=validate_environment,
        ... )

    Note:
        Uses generic type parameters to ensure type safety for the
        main function signature and parameter handling.

    """

    name: str
    description: str
    category: str
    main_func: Callable[P_main_func, FlextResult[object]]
    setup_func: Callable[[], FlextResult[None]] | None = None
    validate_func: Callable[[], FlextResult[None]] | None = None


def create_simple_script[**P_main_func](
    config: ScriptConfig[P_main_func],
) -> type[FlextScript]:
    """Create enterprise-grade script class from configuration using factory pattern.

    Generates a complete FlextScript subclass with integrated lifecycle management,
    error handling, and observability from a simple configuration object. This
    factory pattern enables rapid script development while maintaining enterprise
    standards and consistency across the FLEXT ecosystem.

    The generated script class includes comprehensive validation, setup, execution,
    and cleanup phases with proper error handling via FlextResult patterns and
    full integration with FLEXT infrastructure components.

    Args:
        config: Complete script configuration including metadata, main function,
               and optional lifecycle hooks for validation and setup.

    Returns:
        Fully configured FlextScript subclass ready for instantiation and
        execution with enterprise-grade capabilities and infrastructure integration.

    Example:
        Create script from configuration:

        >>> def process_data() -> FlextResult[str]:
        ...     return FlextResult[None].ok("Data processed successfully")
        >>>
        >>> def validate_environment() -> FlextResult[None]:
        ...     # Validate prerequisites
        ...     return FlextResult[None].ok(None)
        >>>
        >>> script_config = ScriptConfig(
        ...     name="data-processor",
        ...     description="Process enterprise data with validation",
        ...     category="data-operations",
        ...     main_func=process_data,
        ...     validate_func=validate_environment,
        ... )
        >>>
        >>> ProcessorScript = create_simple_script(script_config)
        >>> script_instance = ProcessorScript()
        >>> exit_code = script_instance.run()

    Note:
        Uses generic type parameters to ensure type safety for function
        signatures and maintains compatibility with enterprise patterns.

    """

    class SimpleScript(FlextScript):
        @property
        def metadata(self) -> ScriptMetadata:
            return ScriptMetadata(
                name=config.name,
                description=config.description,
                category=config.category,
            )

        def validate_preconditions(self) -> FlextResult[None]:
            if config.validate_func:
                return config.validate_func()
            return FlextResult[None].ok(None)

        def setup(self) -> FlextResult[None]:
            if config.setup_func:
                return config.setup_func()
            return FlextResult[None].ok(None)

        def execute_main_logic(self, **kwargs: object) -> FlextResult[object]:
            try:
                # Check function signature to determine if it accepts kwargs
                sig = inspect.signature(config.main_func)
                if sig.parameters:
                    # Function expects parameters, pass kwargs
                    result = config.main_func(**kwargs)  # type: ignore[call-arg,arg-type]
                else:
                    # Function expects no parameters
                    result = config.main_func()  # type: ignore[call-arg]
                return (
                    result
                    if isinstance(result, FlextResult)
                    else FlextResult[object].ok(result)
                )
            except TypeError as e:
                return FlextResult[object].fail(f"Function signature mismatch: {e}")

        def cleanup(self) -> FlextResult[None]:
            return FlextResult[None].ok(None)

    return SimpleScript
