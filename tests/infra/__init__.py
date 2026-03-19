# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Infra package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes
    from flext_tests.decorators import d
    from flext_tests.exceptions import e
    from flext_tests.handlers import h
    from flext_tests.mixins import x
    from flext_tests.service import s

    from .constants import FlextWorkspaceTestConstants, c
    from .models import FlextWorkspaceTestModels, m
    from .protocols import FlextWorkspaceTestProtocols, p
    from .result import r
    from .typings import FlextWorkspaceTestTypes, t
    from .utilities import FlextWorkspaceTestUtilities, u

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
    "c": ("tests.infra.constants", "c"),
    "d": ("flext_tests.decorators", "d"),
    "e": ("flext_tests.exceptions", "e"),
    "h": ("flext_tests.handlers", "h"),
    "m": ("tests.infra.models", "m"),
    "p": ("tests.infra.protocols", "p"),
    "r": ("tests.infra.result", "r"),
    "s": ("flext_tests.service", "s"),
    "t": ("tests.infra.typings", "t"),
    "u": ("tests.infra.utilities", "u"),
    "x": ("flext_tests.mixins", "x"),
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


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
