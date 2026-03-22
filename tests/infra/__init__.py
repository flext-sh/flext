# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Infra package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_tests import c, d, e, h, m, p, r, s, t, u, x

    from .constants import FlextWorkspaceTestConstants
    from .models import FlextWorkspaceTestModels
    from .protocols import FlextWorkspaceTestProtocols
    from .typings import FlextWorkspaceTestTypes
    from .utilities import FlextWorkspaceTestUtilities

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextWorkspaceTestConstants": (
        "tests.infra.constants",
        "FlextWorkspaceTestConstants",
    ),
    "FlextWorkspaceTestModels": ("tests.infra.models", "FlextWorkspaceTestModels"),
    "FlextWorkspaceTestProtocols": (
        "tests.infra.protocols",
        "FlextWorkspaceTestProtocols",
    ),
    "FlextWorkspaceTestTypes": ("tests.infra.typings", "FlextWorkspaceTestTypes"),
    "FlextWorkspaceTestUtilities": (
        "tests.infra.utilities",
        "FlextWorkspaceTestUtilities",
    ),
    "c": ("flext_tests", "c"),
    "d": ("flext_tests", "d"),
    "e": ("flext_tests", "e"),
    "h": ("flext_tests", "h"),
    "m": ("flext_tests", "m"),
    "p": ("flext_tests", "p"),
    "r": ("flext_tests", "r"),
    "s": ("flext_tests", "s"),
    "t": ("flext_tests", "t"),
    "u": ("flext_tests", "u"),
    "x": ("flext_tests", "x"),
}

__all__ = [
    "FlextWorkspaceTestConstants",
    "FlextWorkspaceTestModels",
    "FlextWorkspaceTestProtocols",
    "FlextWorkspaceTestTypes",
    "FlextWorkspaceTestUtilities",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]


_LAZY_CACHE: dict[str, FlextTypes.ModuleExport] = {}


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
