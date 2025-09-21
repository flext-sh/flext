"""Unified color service for FLEXT platform.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import flext_cli
from flext_core import FlextDomainService, FlextLogger, FlextResult

# FlextCli availability flag
FLEXT_CLI_AVAILABLE = True


class FlextColorService(FlextDomainService[str]):
    """Unified color service with nested helpers.

    Single responsibility: Terminal color formatting and output.
    """

    class Colors:
        """ANSI color codes for terminal output."""

        # Basic colors
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        CYAN = "\033[96m"
        MAGENTA = "\033[95m"
        WHITE = "\033[97m"
        GRAY = "\033[90m"
        ORANGE = "\033[38;5;208m"

        # Formatting
        BOLD = "\033[1m"
        UNDERLINE = "\033[4m"
        RESET = "\033[0m"

        # Semantic aliases
        WARNING = YELLOW
        FAIL = RED
        HEADER = MAGENTA
        ENDC = RESET

    class _FormattingHelper:
        """Nested helper for color formatting."""

        @staticmethod
        def colorize(message: str, color: str) -> str:
            """Colorize text with ANSI color codes.

            Returns:
                str: Message with ANSI color codes applied.

            """
            if not color:
                return message
            return f"{color}{message}{FlextColorService.Colors.RESET}"

    class _OutputHelper:
        """Nested helper for output operations."""

        @staticmethod
        def print_colored(
            message: str,
            color: str = "",
            logger: FlextLogger | None = None,
        ) -> FlextResult[None]:
            """Print text with color formatting and logging.

            Returns:
                FlextResult[None]: Success result or failure if CLI not available.

            """
            # Log message regardless of flext_cli availability
            if logger:
                logger.info(message)

            if not FLEXT_CLI_AVAILABLE:
                return FlextResult[None].fail(
                    "FlextCli not available for colored output",
                )

            # flext_cli is available
            formatter = flext_cli.FlextCliFormatters()

            if color:
                colored_message = FlextColorService._FormattingHelper.colorize(
                    message,
                    color,
                )
                formatter.console.print(colored_message)
            else:
                formatter.console.print(message)

            return FlextResult[None].ok(None)

    def __init__(self) -> None:
        """Initialize color service."""
        super().__init__()
        self._logger = FlextLogger(__name__)

    def execute(self) -> FlextResult[str]:
        """Execute color service - FlextDomainService interface."""
        return FlextResult[str].ok("Color service ready")

    def colorize(self, message: str, color: str) -> FlextResult[str]:
        """Colorize text using nested helper."""
        result = self._FormattingHelper.colorize(message, color)
        return FlextResult[str].ok(result)

    def print_colored(self, message: str, color: str = "") -> FlextResult[None]:
        """Print colored text using nested helper."""
        return self._OutputHelper.print_colored(message, color, self._logger)


# LEGACY ALIASES AND FUNCTIONS ELIMINATED
# Use FlextColorService directly:
# - FlextColorService.Colors
# - FlextColorService().colorize()
# - FlextColorService().print_colored()

# Convenience imports for test compatibility - delegate to unified service
Colors = FlextColorService.Colors


def colorize(message: str, color: str) -> str:
    """Convenience function for colorize - delegates to FlextColorService."""
    service = FlextColorService()
    result = service.colorize(message, color)
    return result.unwrap() if result.is_success else message


def print_colored(message: str, color: str = "") -> None:
    """Convenience function for print_colored - delegates to FlextColorService."""
    service = FlextColorService()
    service.print_colored(message, color)


__all__ = ["Colors", "FlextColorService", "colorize", "print_colored"]
