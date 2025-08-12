"""Workspace output utilities aligned with flext-core/flext-cli patterns.

This module centralizes color constants and thin output helpers which delegate
to the ecosystem's standard formatting conventions. Prefer using these helpers
for consistent UX across scripts and tools.
"""

from flext_cli.core.formatters import PlainFormatter
from flext_core import get_logger
from rich.console import Console


class Colors:
    """ANSI color constants for terminal formatting and output.

    Provides standardized color constants for consistent terminal output
    across the FLEXT ecosystem. These constants work with standard
    ANSI-compatible terminals.

    Attributes:
        HEADER: Magenta color for headers and titles.
        BLUE: Standard blue for informational messages.
        CYAN: Cyan for secondary information and highlights.
        GREEN: Green for success messages and confirmations.
        WARNING: Yellow for warning messages.
        FAIL: Red for error and failure messages.
        ENDC: Legacy end color (use RESET instead).
        BOLD: Bold text modifier.
        UNDERLINE: Underlined text modifier.
        YELLOW: Yellow for warnings and cautions.
        RED: Red for errors and critical messages.
        MAGENTA: Magenta for special highlights.
        ORANGE: Orange for intermediate status messages.
        GRAY: Gray for dimmed or secondary text.
        WHITE: White for high-contrast text.
        RESET: Resets all formatting to default.

    Example:
        >>> print(f"{Colors.GREEN}Success!{Colors.RESET}")
        >>> colored_text = f"{Colors.BLUE}Info: {Colors.BOLD}Important{Colors.RESET}"

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
    r"""Return message wrapped with ANSI color codes when a color is provided.

    This function is side-effect free and preferred for composing output
    that will be used in multiple contexts or stored for later use.

    Args:
        message: The text message to colorize.
        color: ANSI color code to apply. Use Colors constants for consistency.
               Empty string returns message unchanged.

    Returns:
        The message wrapped with color codes and reset sequence if color
        is provided, otherwise the original message unchanged.

    Example:
        >>> colorize("Success!", Colors.GREEN)
        '\033[92mSuccess!\033[0m'
        >>> colorize("No color", "")
        'No color'

    """
    return f"{color}{message}{Colors.RESET}" if color else message


_logger = get_logger("flext_tools.output")
_plain_formatter = PlainFormatter()
_console = Console()


def print_colored(message: str, color: str = "") -> None:
    """Emit colored text using flext-cli PlainFormatter + rich Console + flext-core logger.

    Outputs colored text to console and logs it simultaneously using
    the FLEXT ecosystem's standard logging and formatting patterns.

    Args:
        message: The text message to display and log.
        color: ANSI color code to apply. Use Colors constants for consistency.
               Empty string displays message without coloring.

    Example:
        >>> print_colored("Success!", Colors.GREEN)
        # Displays green "Success!" to console and logs it
        >>> print_colored("Warning: Check this", Colors.YELLOW)
        # Displays yellow warning to console and logs it

    """
    _plain_formatter.format(colorize(message, color), _console)
    _logger.info(colorize(message, color))
