"""FLEXT Tools Common Utilities - Shared Utility Functions.

This module provides common utility functions and classes used across the FLEXT
workspace tools ecosystem, including terminal colors, path handling, logging,
and Python standard library module identification.

Key Components:
    - Colors: Terminal formatting and colored output utilities
    - Path utilities: Workspace path filtering and validation
    - Logging: Structured logging for tools operations
    - Stdlib utilities: Python standard library module identification

Integration:
    - Core utilities used by all FLEXT workspace management tools
    - Provides consistent behavior across dependency analysis and project operations

Author: FLEXT Development Team
Version: 2.0.0
License: MIT
"""

from flext_tools.utils.colors import Colors, print_colored
from flext_tools.utils.logging import (
    DetailedLogger,
    LogLevel,
    get_logger,
    log_operation,
)
from flext_tools.utils.paths import should_ignore_path
from flext_tools.utils.stdlib import get_stdlib_modules

__all__ = [
    "Colors",
    "DetailedLogger",
    "LogLevel",
    "get_logger",
    "get_stdlib_modules",
    "log_operation",
    "print_colored",
    "should_ignore_path",
]
