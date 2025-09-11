"""FLEXT Terminal Output Utilities - Color Constants and Formatting.

Provides standardized color constants and terminal formatting utilities for
consistent output across the FLEXT ecosystem. This module centralizes color
definitions and output helpers that delegate to the ecosystem's standard
formatting conventions.

The module implements a lightweight wrapper around ANSI color codes with
integration to flext-cli formatters and flext-observability logging for
comprehensive output management across all FLEXT tools and services.

Key Components:
    - Colors: ANSI color constants for terminal formatting
    - colorize: Function for wrapping text with color codes
    - print_colored: Integrated output function with logging

Example:
    Basic color usage:

    >>> from flext_tools.utils.colors import Colors, print_colored, colorize
    >>> print_colored("Success!", Colors.GREEN)
    >>> colored_text = colorize("Warning", Colors.YELLOW)
    >>> print(f"Status: {colored_text}")

Integration:
    - Delegates to flext-cli PlainFormatter for consistent formatting
    - Integrates with flext-observability for structured logging
    - Provides foundation for consistent UX across scripts and tools

Author: FLEXT Development Team
Version: 0.9.0
License: MIT

"""

from flext_core import FlextLogger


class Colors:
    """ANSI color constants for consistent terminal formatting and output.

    Provides standardized color constants for terminal output across the FLEXT
    ecosystem. These constants work with standard ANSI-compatible terminals and
    are designed for consistent user experience across all tools and services.

    The color constants follow semantic naming conventions where possible,
    with specific colors mapped to common use cases (success=green,
    error=red, warning=yellow, etc.).

    Attributes:
        HEADER (str): Magenta color for headers and titles.
        BLUE (str): Standard blue for informational messages.
        CYAN (str): Cyan for secondary information and highlights.
        GREEN (str): Green for success messages and confirmations.
        WARNING (str): Yellow for warning messages.
        FAIL (str): Red for error and failure messages.
        ENDC (str): Legacy end color (use RESET instead).
        BOLD (str): Bold text modifier.
        UNDERLINE (str): Underlined text modifier.
        YELLOW (str): Yellow for warnings and cautions.
        RED (str): Red for errors and critical messages.
        MAGENTA (str): Magenta for special highlights.
        ORANGE (str): Orange for intermediate status messages.
        GRAY (str): Gray for dimmed or secondary text.
        WHITE (str): White for high-contrast text.
        RESET (str): Resets all formatting to default.

    Example:
        Basic color usage:

        >>> print(f"{Colors.GREEN}Success!{Colors.RESET}")
        >>> colored_text = f"{Colors.BLUE}Info: {Colors.BOLD}Important{Colors.RESET}"
        >>> print(f"{Colors.WARNING}Warning: Check this{Colors.RESET}")

    Note:
        Always use RESET after applying colors to prevent formatting from
        bleeding into subsequent output.

    """

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    ORANGE = "\033[38;5;208m"
    GRAY = "\033[90m"
    WHITE = "\033[37m"
    RESET = "\033[0m"


def colorize(message: str, color: str = "") -> str:
    r"""Wrap message with ANSI color codes for terminal formatting.

    This function is side-effect free and preferred for composing output
    that will be used in multiple contexts or stored for later use. It
    automatically adds reset codes to prevent color bleeding.

    Args:
        message: The text message to colorize.
        color: ANSI color code to apply. Use Colors constants for consistency.
            Empty string returns message unchanged.

    Returns:
        The message wrapped with color codes and reset sequence if color
        is provided, otherwise the original message unchanged.

    Example:
        Basic colorization:

        >>> colorize("Success!", Colors.GREEN)
        '\033[92mSuccess!\033[0m'
        >>> colorize("No color", "")
        'No color'
        >>> colored = colorize("Warning", Colors.YELLOW)
        >>> print(f"Status: {colored}")

    Note:
        This function does not perform any output - it only returns the
        formatted string for use elsewhere.

    """
    return f"{color}{message}{Colors.RESET}" if color else message


_logger = FlextLogger("flext_tools.output")


def print_colored(message: str, color: str = "") -> None:
    """Output colored text with integrated logging and formatting.

    Outputs colored text to console and logs it simultaneously using the
    FLEXT ecosystem's standard logging patterns. Uses flext-core logger
    for comprehensive output management with simple terminal output.

    This function provides the primary interface for colored terminal output
    across FLEXT tools, ensuring consistent formatting and logging behavior.

    Args:
        message: The text message to display and log.
        color: ANSI color code to apply. Use Colors constants for consistency.
            Empty string displays message without coloring.

    Example:
        Colored console output with logging:

        >>> print_colored("Success!", Colors.GREEN)
        # Displays green "Success!" to console and logs it
        >>> print_colored("Warning: Check this", Colors.YELLOW)
        # Displays yellow warning to console and logs it
        >>> print_colored("Processing...", Colors.BLUE)
        # Displays blue text and logs the message

    Note:
        This function has side effects (console output and logging).
        Use colorize() if you only need the formatted string without output.

    """
    colorize(message, color)
    _logger.info(message)  # Log without color codes for clean logs


__all__ = ["Colors", "colorize", "print_colored"]
