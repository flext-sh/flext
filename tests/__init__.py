# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from . import infra as infra
    from .infra.constants import FlextWorkspaceTestConstants, c
    from .infra.models import FlextWorkspaceTestModels, m
    from .infra.protocols import FlextWorkspaceTestProtocols, p
    from .infra.result import r
    from .infra.typings import FlextWorkspaceTestTypes, t
    from .infra.utilities import FlextWorkspaceTestUtilities, u
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
    "c": ("tests.infra.constants", "c"),
    "infra": ("tests.infra", ""),
    "m": ("tests.infra.models", "m"),
    "p": ("tests.infra.protocols", "p"),
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    "r": ("tests.infra.result", "r"),
=======
    "r": ("tests.infra", "r"),
>>>>>>> Stashed changes
=======
    "r": ("tests.infra", "r"),
>>>>>>> Stashed changes
    "t": ("tests.infra.typings", "t"),
    "tf": ("tests.tf", "tf"),
    "tm": ("tests.tm", "tm"),
    "u": ("tests.infra.utilities", "u"),
}

__all__ = [
    "FlextWorkspaceTestConstants",
    "FlextWorkspaceTestModels",
    "FlextWorkspaceTestProtocols",
    "FlextWorkspaceTestTypes",
    "FlextWorkspaceTestUtilities",
    "c",
    "infra",
    "m",
    "p",
    "r",
    "t",
    "tf",
    "tm",
    "u",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
