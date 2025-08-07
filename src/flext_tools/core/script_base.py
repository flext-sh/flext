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
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, ParamSpec

from flext_core import (
    FlextResult,
    FlextValue,
    get_flext_container,
    get_logger,
)

from flext_tools.utils.colors import Colors, print_colored

if TYPE_CHECKING:
    from collections.abc import Callable

P_main_func = ParamSpec("P_main_func")

# Use flext-core logger
logger = get_logger(__name__)


class ScriptMetadata(FlextValue):
    """Metadata for a FLEXT script using flext-core value object pattern."""

    name: str
    description: str
    category: str
    version: str = "1.0.0"
    requires_confirmation: bool = False
    dry_run_supported: bool = True

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate script metadata business rules."""
        if not self.name.strip():
            return FlextResult.fail("Script name cannot be empty")

        if not self.description.strip():
            return FlextResult.fail("Script description cannot be empty")

        if not self.category.strip():
            return FlextResult.fail("Script category cannot be empty")

        return FlextResult.ok(None)


class FlextScript(ABC):
    """Base class for FLEXT scripts using flext-core enterprise patterns.

    Implements Clean Architecture patterns with FlextResult for error handling,
    dependency injection container integration, and structured logging.
    """

    def __init__(self) -> None:
        """Initialize the script with flext-core infrastructure."""
        self.logger = get_logger(self.__class__.__name__)
        self.start_time = time.time()
        self.container = get_flext_container()

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

    def cleanup(self) -> FlextResult[None]:
        """Perform cleanup operations after execution.

        Returns:
            FlextResult indicating cleanup success or failure

        """
        return FlextResult.ok(None)

    def setup(self) -> FlextResult[None]:
        """Perform any setup operations before main execution.

        Returns:
            FlextResult indicating setup success or failure

        """
        return FlextResult.ok(None)

    def run(self, **kwargs: object) -> int:
        """Run the complete script with FlextResult railway-oriented programming.

        Args:
            **kwargs: Additional arguments passed to execute_main_logic

        Returns:
            0 for success, non-zero for failure

        """
        try:
            self._print_header()

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

        return parser

    def main(self) -> int:
        """Main entry point for script execution.

        Returns:
            Exit code (0 for success, non-zero for failure)

        """
        parser = self.create_parser()
        args = parser.parse_args()

        # Configure logging level
        if args.verbose:
            # Set verbose mode - our logger doesn't have set_level method

            logging.getLogger().setLevel(logging.DEBUG)

        return self.run(**vars(args))


@dataclass
class ScriptConfig[**P_main_func]:
    """Configuration for creating simple scripts."""

    name: str
    description: str
    category: str
    main_func: Callable[P_main_func, FlextResult[object]]
    setup_func: Callable[[], FlextResult[None]] | None = None
    validate_func: Callable[[], FlextResult[None]] | None = None


def create_simple_script[**P_main_func](
    config: ScriptConfig[P_main_func],
) -> type[FlextScript]:
    """Create a simple script class from configuration using flext-core patterns.

    Args:
        config: Script configuration containing all required parameters

    Returns:
        FlextScript subclass with flext-core integration

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
            return FlextResult.ok(None)

        def setup(self) -> FlextResult[None]:
            if config.setup_func:
                return config.setup_func()
            return FlextResult.ok(None)

        def execute_main_logic(self, **kwargs: object) -> FlextResult[object]:
            try:
                # Try with kwargs first
                return config.main_func(**kwargs)  # type: ignore[call-arg,arg-type]
            except TypeError:
                # Fallback for callables with no arguments
                try:
                    return config.main_func()  # type: ignore[call-arg]
                except TypeError as e:
                    return FlextResult.fail(f"Function signature mismatch: {e}")

        def cleanup(self) -> FlextResult[None]:
            return FlextResult.ok(None)

    return SimpleScript
