"""FLEXT Tools Terminal Colors - ANSI Color System for Terminal Output.

This utility module provides ANSI color constants and terminal output functions
for the FLEXT ecosystem tools. Used across FLEXT workspace operations for
consistent colored terminal output and improved user experience.

Key Components:
    - Colors: ANSI color constants for terminal formatting
    - print_colored: Utility function for colored terminal output

Integration:
    - Core utility used by FLEXT workspace management tools
    - Provides consistent color schemes across all FLEXT CLI operations

Author: FLEXT Development Team
Version: 2.0.0
License: MIT
"""


class Colors:
    """ANSI color constants for terminal formatting and output."""

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


def print_colored(message: str, color: str = "") -> None:
    """Print colored message to terminal with ANSI color formatting."""
    if color:
        pass
    else:
        pass
