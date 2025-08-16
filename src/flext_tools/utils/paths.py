"""FLEXT Tools Path Utilities - Path Manipulation and Analysis Utilities.

This utility module provides path manipulation functions and directory filtering
for the FLEXT ecosystem workspace analysis. Used by dependency discovery and
project management tools to navigate the FLEXT workspace structure.

Key Components:
    - IGNORE_DIRS: Set of directories to exclude from analysis
    - should_ignore_path: Path filtering function for workspace operations

Integration:
    - Core utility used by FLEXT workspace dependency analysis
    - Provides consistent path handling across all FLEXT tools

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

Author: FLEXT Development Team
Version: 2.0.0
License: MIT
"""

from pathlib import Path

# Directories that should be ignored during workspace analysis
IGNORE_DIRS: set[str] = {
    # Archive and backup directories
    "archive",
    ".archive",
    "backup",
    "old",
    "deprecated",
    "outdated",
    "temp",
    "tmp",
    # Version control systems
    ".git",
    ".svn",
    ".hg",
    ".bzr",
    # Python cache and build directories
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".coverage",
    "htmlcov",
    ".hypothesis",
    # Build and distribution directories
    "build",
    "dist",
    "*.egg-info",
    "_build",
    "wheelhouse",
    # Node.js directories
    "node_modules",
    ".npm",
    ".yarn",
    # IDE and editor files
    ".idea",
    ".vscode",
    ".vs",
    "*.swp",
    "*.swo",
    # Virtual environments and configurations
    "venv",
    ".venv",
    "env",
    ".env",
    "virtualenv",
}


def should_ignore_path(path: Path) -> bool:
    """Check if a path should be ignored during workspace analysis."""
    parts = path.parts
    return any(ignore_dir in parts for ignore_dir in IGNORE_DIRS)
