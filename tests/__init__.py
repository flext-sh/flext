# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes
    from flext_tests import c, d, e, h, m, p, r, s, t, u, x

    from . import infra as infra
    from .infra.constants import FlextWorkspaceTestConstants
    from .infra.models import FlextWorkspaceTestModels
    from .infra.protocols import FlextWorkspaceTestProtocols
    from .infra.typings import FlextWorkspaceTestTypes
    from .infra.utilities import FlextWorkspaceTestUtilities
    from .tf import tf
    from .tm import tm

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
    "infra": ("tests.infra", ""),
    "m": ("flext_tests", "m"),
    "p": ("flext_tests", "p"),
    "r": ("flext_tests", "r"),
    "s": ("flext_tests", "s"),
    "t": ("flext_tests", "t"),
    "tf": ("tests.tf", "tf"),
    "tm": ("tests.tm", "tm"),
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
    "infra",
    "m",
    "p",
    "r",
    "s",
    "t",
    "tf",
    "tm",
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
