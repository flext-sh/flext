"""Flext workspace package.

This module provides the main entry point and shared components for the flext package.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_cli import FlextCliCommonParams, FlextCliSettings
    from flext_core import (
        FlextConstants,
        FlextContainer,
        FlextContext,
        FlextDecorators,
        FlextDispatcher,
        FlextExceptions,
        FlextHandlers,
        FlextModels,
        FlextProtocols,
        FlextResult,
        FlextRuntime,
        FlextService,
        FlextService as FlextServiceBase,
        FlextSettings,
        FlextTypes,
        FlextUtilities,
    )

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextCliCommonParams": ("flext_cli", "FlextCliCommonParams"),
    "FlextCliSettings": ("flext_cli", "FlextCliSettings"),
    "FlextConstants": ("flext_core", "FlextConstants"),
    "FlextContainer": ("flext_core", "FlextContainer"),
    "FlextContext": ("flext_core", "FlextContext"),
    "FlextDecorators": ("flext_core", "FlextDecorators"),
    "FlextDispatcher": ("flext_core", "FlextDispatcher"),
    "FlextExceptions": ("flext_core", "FlextExceptions"),
    "FlextHandlers": ("flext_core", "FlextHandlers"),
    "FlextModels": ("flext_core", "FlextModels"),
    "FlextProtocols": ("flext_core", "FlextProtocols"),
    "FlextResult": ("flext_core", "FlextResult"),
    "FlextRuntime": ("flext_core", "FlextRuntime"),
    "FlextService": ("flext_core", "FlextService"),
    "FlextServiceBase": ("flext_core", "FlextService"),
    "FlextSettings": ("flext_core", "FlextSettings"),
    "FlextTypes": ("flext_core", "FlextTypes"),
    "FlextUtilities": ("flext_core", "FlextUtilities"),
}

__all__ = [
    "FlextCliCommonParams",
    "FlextCliSettings",
    "FlextConstants",
    "FlextContainer",
    "FlextContext",
    "FlextDecorators",
    "FlextDispatcher",
    "FlextExceptions",
    "FlextHandlers",
    "FlextModels",
    "FlextProtocols",
    "FlextResult",
    "FlextRuntime",
    "FlextService",
    "FlextServiceBase",
    "FlextSettings",
    "FlextTypes",
    "FlextUtilities",
]


def __getattr__(name: str) -> Any:  # noqa: ANN401
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
