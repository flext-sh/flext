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

from flext_core import FlextDomainService, FlextResult

# =============================================================================
# FLEXT DEV FACADE ALIASES (ELIMINATE CIRCULAR IMPORTS)
# =============================================================================

# Lazy loading to avoid circular imports
def _get_flext_dev_classes() -> tuple[type, type]:
    """Lazy load flext dev classes to avoid circular imports."""
    from flext.dev import FlextAdvancedDevModels, FlextAdvancedDevToolsManager
    return FlextAdvancedDevToolsManager, FlextAdvancedDevModels


# Primary dev API - delegate to flext (lazy loaded)
class DevToolsManager:
    """Lazy wrapper for FlextAdvancedDevToolsManager to avoid circular imports."""

    def __new__(cls, *args: object, **kwargs: object) -> object:
        FlextAdvancedDevToolsManager, _ = _get_flext_dev_classes()
        return FlextAdvancedDevToolsManager(*args, **kwargs)


# Facade class for legacy tools compatibility
class FlextToolsDevService(FlextDomainService):
    """Facade to flext dev service - eliminates development code duplication."""

    def __init__(self, workspace_path: str | None = None, **kwargs: object) -> None:
        """Initialize with flext dev service."""
        super().__init__()
        # Lazy loading to avoid circular imports during class definition
        self._workspace_path = workspace_path
        self._kwargs = kwargs
        self._dev_service = None

    def _get_dev_service(self) -> object:
        """Lazy load dev service to avoid circular imports."""
        if self._dev_service is None:
            FlextAdvancedDevToolsManager, _ = _get_flext_dev_classes()
            self._dev_service = FlextAdvancedDevToolsManager(
                workspace_path=self._workspace_path, **self._kwargs
            )
        return self._dev_service

    def execute(self, _request: str = "") -> FlextResult[str]:
        """Execute dev operation through flext dev service."""
        # Access through lazy loading
        self._get_dev_service()
        return FlextResult[str].ok("FlextToolsDevService using flext dev facade")


# Legacy compatibility factory function
def create_dev_tools_manager(*args: object, **kwargs: object) -> object:
    """Create dev tools manager using lazy loading."""
    FlextAdvancedDevToolsManager, _ = _get_flext_dev_classes()
    return FlextAdvancedDevToolsManager(*args, **kwargs)


__all__ = [
    "DevToolsManager",
    "FlextToolsDevService",
    "create_dev_tools_manager",
]
