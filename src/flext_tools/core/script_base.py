#!/usr/bin/env python3
"""Base class for FLEXT scripts.

Provides a standard interface for creating scripts with consistent
error handling, logging, and command-line interface.
"""

from __future__ import annotations

import argparse
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from flext_tools.utils.colors import Colors, print_colored

if TYPE_CHECKING:
    from collections.abc import Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


@dataclass
class ScriptMetadata:
    """Metadata for a FLEXT script."""

    name: str
    description: str
    category: str
    version: str = "1.0.0"
    requires_confirmation: bool = False
    dry_run_supported: bool = True


class FlextScript(ABC):
    """Base class for FLEXT scripts following enterprise patterns."""

    def __init__(self) -> None:
        """Initialize the script."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.start_time = time.time()

    @property
    @abstractmethod
    def metadata(self) -> ScriptMetadata:
        """Return script metadata."""

    @abstractmethod
    def validate_preconditions(self) -> bool:
        """Validate that script can run successfully.

        Returns:
            True if preconditions are met, False otherwise

        """

    @abstractmethod
    def execute_main_logic(self) -> bool:
        """Execute the main script logic.

        Returns:
            True if execution was successful, False otherwise

        """

    @abstractmethod
    def cleanup(self) -> None:
        """Perform cleanup operations after execution."""

    def setup(self) -> bool:
        """Perform any setup operations before main execution.

        Returns:
            True if setup was successful, False otherwise

        """
        return True

    def run(self, **kwargs: Any) -> int:
        """Run the complete script with error handling.

        Args:
            **kwargs: Additional arguments passed to execute_main_logic

        Returns:
            0 for success, non-zero for failure

        """
        try:
            self._print_header()

            # Validate preconditions
            if not self.validate_preconditions():
                print_colored("❌ Preconditions not met", Colors.RED)
                return 1

            # Setup
            if not self.setup():
                print_colored("❌ Setup failed", Colors.RED)
                return 1

            # Execute main logic
            if self.execute_main_logic():
                self._print_success()
                return 0
            print_colored("❌ Execution failed", Colors.RED)
            return 1

        except KeyboardInterrupt:
            print_colored("\n❌ Script interrupted by user", Colors.YELLOW)
            return 1
        except Exception as e:
            print_colored(f"❌ Unexpected error: {e}", Colors.RED)
            self.logger.exception("Script failed with exception")
            return 1
        finally:
            self.cleanup()

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
            logging.getLogger().setLevel(logging.DEBUG)

        return self.run(**vars(args))


def create_simple_script(
    name: str,
    description: str,
    category: str,
    main_func: Callable[..., bool],
    setup_func: Callable[..., bool] | None = None,
    validate_func: Callable[..., bool] | None = None,
) -> type[FlextScript]:
    """Create a simple script class from functions.

    Args:
        name: Script name
        description: Script description
        category: Script category
        main_func: Main execution function
        setup_func: Optional setup function
        validate_func: Optional validation function

    Returns:
        FlextScript subclass

    """

    class SimpleScript(FlextScript):
        @property
        def metadata(self) -> ScriptMetadata:
            return ScriptMetadata(name=name, description=description, category=category)

        def validate_preconditions(self) -> bool:
            return validate_func() if validate_func else True

        def setup(self) -> bool:
            return setup_func() if setup_func else True

        def execute_main_logic(self, **kwargs: Any) -> bool:
            result = main_func(**kwargs)
            return bool(result)

        def cleanup(self) -> None:
            pass

    return SimpleScript
