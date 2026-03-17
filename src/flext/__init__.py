# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Flext workspace package.

This module provides the main entry point and shared components for the flext package.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from flext.constants import FlextConstants, c
    from flext.models import FlextModels, m
    from flext.protocols import FlextProtocols, p
    from flext.service import FlextServiceBase, s
    from flext.typings import FlextTypes, t
    from flext.utilities import FlextUtilities, u
    from flext.workspace import main

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextConstants": ("flext.constants", "FlextConstants"),
    "FlextModels": ("flext.models", "FlextModels"),
    "FlextProtocols": ("flext.protocols", "FlextProtocols"),
    "FlextServiceBase": ("flext.service", "FlextServiceBase"),
    "FlextTypes": ("flext.typings", "FlextTypes"),
    "FlextUtilities": ("flext.utilities", "FlextUtilities"),
    "c": ("flext.constants", "c"),
    "m": ("flext.models", "m"),
    "main": ("flext.workspace", "main"),
    "p": ("flext.protocols", "p"),
    "s": ("flext.service", "s"),
    "t": ("flext.typings", "t"),
    "u": ("flext.utilities", "u"),
}

__all__ = [
    "FlextConstants",
    "FlextModels",
    "FlextProtocols",
    "FlextServiceBase",
    "FlextTypes",
    "FlextUtilities",
    "c",
    "m",
    "main",
    "p",
    "s",
    "t",
    "u",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
