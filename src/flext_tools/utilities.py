"""Utilities for flext_tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextCore


class Colors:
    """Color constants."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


class FlextToolsUtilities:
    """Utilities for flext_tools."""

    # Add utility methods here as needed


def colorize(text: str, color: str) -> str:
    """Colorize text."""
    return f"{color}{text}{Colors.RESET}"


def get_project_root() -> Path:
    """Get project root path."""
    return Path.cwd()


def get_stdlib_modules() -> FlextCore.Types.StringList:
    """Get standard library modules."""
    return ["os", "sys", "pathlib"]


def is_stdlib_module(module_name: str) -> bool:
    """Check if module is from standard library."""
    return module_name in get_stdlib_modules()


def normalize_path(path: str | Path) -> Path:
    """Normalize path."""
    return Path(path).resolve()


def print_colored(text: str, color: str) -> None:
    """Print colored text."""


def should_ignore_path(
    path: str | Path, ignore_patterns: FlextCore.Types.StringList | None = None
) -> bool:
    """Check if path should be ignored."""
    if ignore_patterns is None:
        ignore_patterns = ["__pycache__", ".git", ".venv"]
    path_str = str(path)
    return any(pattern in path_str for pattern in ignore_patterns)
