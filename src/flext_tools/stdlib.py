"""Unified stdlib service for FLEXT platform.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from typing import Self

from flext_core import FlextResult, FlextService


class FlextStdlibService(FlextService[list[str]]):
    """Unified stdlib service with nested helpers.

    Single responsibility: Standard library module detection and management.
    """

    class _ModuleHelper:
        """Nested helper for module operations."""

        @staticmethod
        def get_stdlib_modules() -> list[str]:
            """Get list of standard library modules."""
            stdlib_modules = [
                "os",
                "sys",
                "re",
                "json",
                "urllib",
                "http",
                "pathlib",
                "collections",
                "itertools",
                "functools",
                "typing",
                "datetime",
                "argparse",
                "subprocess",
                "shutil",
                "glob",
                "tempfile",
            ]

            stdlib_modules.extend(list(sys.stdlib_module_names))
            return sorted(set(stdlib_modules))

        @staticmethod
        def is_stdlib_module(module_name: str) -> bool:
            """Check if module is from standard library."""
            return module_name in FlextStdlibService._ModuleHelper.get_stdlib_modules()

    def execute(self: Self) -> FlextResult[list[str]]:
        """Execute stdlib service - FlextService interface."""
        modules = self._ModuleHelper.get_stdlib_modules()
        return FlextResult[list[str]].ok(modules)

    def execute(self: Self) -> FlextResult[list[str]]:
        """Execute stdlib service hronously - FlextService interface."""
        modules = self._ModuleHelper.get_stdlib_modules()
        return FlextResult[list[str]].ok(modules)

    def get_stdlib_modules(self: Self) -> FlextResult[list[str]]:
        """Get stdlib modules using nested helper."""
        modules = self._ModuleHelper.get_stdlib_modules()
        return FlextResult[list[str]].ok(modules)

    def is_stdlib_module(self, module_name: str) -> FlextResult[bool]:
        """Check if module is stdlib using nested helper."""
        is_stdlib = self._ModuleHelper.is_stdlib_module(module_name)
        return FlextResult[bool].ok(is_stdlib)


# Module-level exports for backward compatibility
_service = FlextStdlibService()


def get_stdlib_modules() -> set[str]:
    """Module-level get_stdlib_modules function."""
    result = _service.get_stdlib_modules()
    return set(result.unwrap()) if result.is_success else set()


def is_stdlib_module(module_name: str) -> bool:
    """Module-level is_stdlib_module function."""
    result = _service.is_stdlib_module(module_name)
    return result.unwrap() if result.is_success else False


__all__ = ["FlextStdlibService", "get_stdlib_modules", "is_stdlib_module"]
