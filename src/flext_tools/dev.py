"""FLEXT Tools Dev Facade - ANTI-DUPLICATION flext Integration.

CRITICAL: This module is a FACADE to flext dev functionality. It eliminates
ALL development tools duplication by delegating to the established flext dev service.

ZERO TOLERANCE ENFORCEMENT: NO local development implementations. ALL development
functionality MUST use flext dev service exclusively.

DOMAIN SEPARATION: Dev patterns belong to flext domain, NOT flext-tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import cast

from flext_core import FlextDomainService, FlextResult, FlextTypes

# Import flext dev classes directly - no lazy loading needed
from flext.dev import FlextAdvancedDevToolsManager


# Primary dev API - delegate to flext (lazy loaded)
class DevToolsManager:
    """Lazy wrapper for FlextAdvancedDevToolsManager to avoid circular imports."""

    def __new__(
        cls, *args: FlextTypes.Core.Dict, **kwargs: FlextTypes.Core.Dict
    ) -> FlextAdvancedDevToolsManager:
        """Create instance using FlextAdvancedDevToolsManager."""
        return FlextAdvancedDevToolsManager(*args, **kwargs)


# Facade class for legacy tools compatibility
class FlextToolsDevService(FlextDomainService[str]):
    """Facade to flext dev service - eliminates development code duplication."""

    def __init__(
        self, workspace_path: str | None = None, **kwargs: FlextTypes.Core.Dict
    ) -> None:
        """Initialize with flext dev service."""
        super().__init__()
        # Lazy loading to avoid circular imports during class definition
        self._workspace_path = workspace_path
        self._kwargs = kwargs
        self._dev_service = None

    def _get_dev_service(self) -> object:
        """Get dev service instance."""
        if self._dev_service is None:
            # Prepare data for FlextAdvancedDevToolsManager
            init_data: FlextTypes.Core.Dict = {
                "workspace_path": self._workspace_path or ""
            }
            # Convert kwargs to proper types
            for key, value in self._kwargs.items():
                init_data[key] = str(value) if value is not None else ""
            self._dev_service = FlextAdvancedDevToolsManager(**cast(dict[str, object], init_data))
        return self._dev_service

    def execute(self, _request: str = "") -> FlextResult[str]:
        """Execute dev operation through flext dev service."""
        # Access through lazy loading
        self._get_dev_service()
        return FlextResult[str].ok("FlextToolsDevService using flext dev facade")


# Legacy compatibility factory function
def create_dev_tools_manager(*args: object, **kwargs: object) -> object:
    """Create dev tools manager."""
    # Convert args and kwargs to proper Dict type
    init_data: FlextTypes.Core.Dict = {}
    for i, arg in enumerate(args):
        init_data[f"arg_{i}"] = str(arg) if arg is not None else ""
    for key, value in kwargs.items():
        init_data[key] = str(value) if value is not None else ""

    return FlextAdvancedDevToolsManager(**cast(dict[str, object], init_data))


__all__ = [
    "DevToolsManager",
    "FlextToolsDevService",
    "create_dev_tools_manager",
]
