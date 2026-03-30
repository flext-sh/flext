# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext package."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes, d, e, h, r, x

    from flext import (
        constants,
        dev,
        docs,
        models,
        protocols,
        service,
        typings,
        utilities,
        workspace,
    )
    from flext.constants import FlextRootConstants, FlextRootConstants as c
    from flext.models import FlextRootModels, FlextRootModels as m
    from flext.protocols import FlextRootProtocols, FlextRootProtocols as p
    from flext.service import FlextRootServiceBase, s
    from flext.typings import FlexRootTypes, FlexRootTypes as t
    from flext.utilities import FlextRootUtilities, FlextRootUtilities as u
    from flext.workspace import main

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlexRootTypes": ["flext.typings", "FlexRootTypes"],
    "FlextRootConstants": ["flext.constants", "FlextRootConstants"],
    "FlextRootModels": ["flext.models", "FlextRootModels"],
    "FlextRootProtocols": ["flext.protocols", "FlextRootProtocols"],
    "FlextRootServiceBase": ["flext.service", "FlextRootServiceBase"],
    "FlextRootUtilities": ["flext.utilities", "FlextRootUtilities"],
    "c": ["flext.constants", "FlextRootConstants"],
    "constants": ["flext.constants", ""],
    "d": ["flext_core", "d"],
    "dev": ["flext.dev", ""],
    "docs": ["flext.docs", ""],
    "e": ["flext_core", "e"],
    "h": ["flext_core", "h"],
    "m": ["flext.models", "FlextRootModels"],
    "main": ["flext.workspace", "main"],
    "models": ["flext.models", ""],
    "p": ["flext.protocols", "FlextRootProtocols"],
    "protocols": ["flext.protocols", ""],
    "r": ["flext_core", "r"],
    "s": ["flext.service", "s"],
    "service": ["flext.service", ""],
    "t": ["flext.typings", "FlexRootTypes"],
    "typings": ["flext.typings", ""],
    "u": ["flext.utilities", "FlextRootUtilities"],
    "utilities": ["flext.utilities", ""],
    "workspace": ["flext.workspace", ""],
    "x": ["flext_core", "x"],
}

__all__ = [
    "FlexRootTypes",
    "FlextRootConstants",
    "FlextRootModels",
    "FlextRootProtocols",
    "FlextRootServiceBase",
    "FlextRootUtilities",
    "c",
    "constants",
    "d",
    "dev",
    "docs",
    "e",
    "h",
    "m",
    "main",
    "models",
    "p",
    "protocols",
    "r",
    "s",
    "service",
    "t",
    "typings",
    "u",
    "utilities",
    "workspace",
    "x",
]


_LAZY_CACHE: MutableMapping[str, FlextTypes.ModuleExport] = {}


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


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
