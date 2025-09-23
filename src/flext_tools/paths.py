"""Unified path service for FLEXT platform.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult, FlextService


class FlextPathService(FlextService[Path]):
    """Unified path service with nested helpers.

    Single responsibility: Path operations and validation.
    """

    class _ValidationHelper:
        """Nested helper for path validation."""

        @staticmethod
        def should_ignore_path(path: str | Path) -> bool:
            """Check if path should be ignored."""
            path_str = str(path)
            ignore_patterns = [
                "__pycache__",
                ".git",
                ".venv",
                "node_modules",
                ".pytest_cache",
                ".mypy_cache",
                "*.pyc",
                "*.pyo",
            ]
            return any(pattern in path_str for pattern in ignore_patterns)

    class _UtilityHelper:
        """Nested helper for path utilities."""

        @staticmethod
        def get_project_root() -> Path:
            """Get project root directory."""
            return Path.cwd()

        @staticmethod
        def normalize_path(path: str | Path) -> Path:
            """Normalize path."""
            return Path(path).resolve()

    def execute(self) -> FlextResult[Path]:
        """Execute path service - FlextService interface."""
        root = self._UtilityHelper.get_project_root()
        return FlextResult[Path].ok(root)

    def should_ignore_path(self, path: str | Path) -> FlextResult[bool]:
        """Check if path should be ignored using nested helper."""
        should_ignore = self._ValidationHelper.should_ignore_path(path)
        return FlextResult[bool].ok(should_ignore)

    def get_project_root(self) -> FlextResult[Path]:
        """Get project root using nested helper."""
        root = self._UtilityHelper.get_project_root()
        return FlextResult[Path].ok(root)

    def normalize_path(self, path: str | Path) -> FlextResult[Path]:
        """Normalize path using nested helper."""
        normalized = self._UtilityHelper.normalize_path(path)
        return FlextResult[Path].ok(normalized)


# Module-level exports for backward compatibility
_service = FlextPathService()


def get_project_root() -> Path:
    """Module-level get_project_root function."""
    result = _service.get_project_root()
    return result.unwrap() if result.success else Path.cwd()


def normalize_path(path: str | Path) -> Path:
    """Module-level normalize_path function."""
    result = _service.normalize_path(path)
    return result.unwrap() if result.success else Path(path).resolve()


def should_ignore_path(path: str | Path) -> bool:
    """Module-level should_ignore_path function."""
    result = _service.should_ignore_path(path)
    return result.unwrap() if result.success else False


__all__ = [
    "FlextPathService",
    "get_project_root",
    "normalize_path",
    "should_ignore_path",
]
