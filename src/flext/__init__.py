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
    from flext_core import d, e, h, r, s, x
    from flext_core.typings import FlextTypes

    from flext.constants import FlextConstants, FlextConstants as c
    from flext.models import FlextModels, FlextModels as m
    from flext.protocols import FlextProtocols, FlextProtocols as p
    from flext.service import FlextServiceBase
    from flext.typings import FlextTypes, FlextTypes as t
    from flext.utilities import FlextUtilities, FlextUtilities as u
    from flext.workspace import main

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextConstants": ("flext.constants", "FlextConstants"),
    "FlextModels": ("flext.models", "FlextModels"),
    "FlextProtocols": ("flext.protocols", "FlextProtocols"),
    "FlextServiceBase": ("flext.service", "FlextServiceBase"),
    "FlextTypes": ("flext.typings", "FlextTypes"),
    "FlextUtilities": ("flext.utilities", "FlextUtilities"),
    "c": ("flext.constants", "FlextConstants"),
    "d": ("flext_core", "d"),
    "e": ("flext_core", "e"),
    "h": ("flext_core", "h"),
    "m": ("flext.models", "FlextModels"),
    "main": ("flext.workspace", "main"),
    "p": ("flext.protocols", "FlextProtocols"),
    "r": ("flext_core", "r"),
    "s": ("flext_core", "s"),
    "t": ("flext.typings", "FlextTypes"),
    "u": ("flext.utilities", "FlextUtilities"),
    "x": ("flext_core", "x"),
}

__all__ = [
    "FlextConstants",
    "FlextModels",
    "FlextProtocols",
    "FlextServiceBase",
    "FlextTypes",
    "FlextUtilities",
    "c",
    "d",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]


_LAZY_CACHE: dict[str, object] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.

    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
