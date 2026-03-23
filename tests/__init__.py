# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_tests import d, e, h, s, x

    from tests import infra
    from tests.infra.constants import FlextWorkspaceTestConstants, c
    from tests.infra.models import FlextWorkspaceTestModels, m
    from tests.infra.protocols import FlextWorkspaceTestProtocols, p
    from tests.infra.result import r
    from tests.infra.typings import FlextWorkspaceTestTypes, t
    from tests.infra.utilities import FlextWorkspaceTestUtilities, u
    from tests.tf import tf
    from tests.tm import tm
    from tests.unit.libs.versioning_tests import TestVersioning
    from tests.unit.scripts.github.test_pr_workspace import TestPrWorkspace
    from tests.unit.scripts.sync_tests import TestSyncScripts

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
    "TestPrWorkspace": (
        "tests.unit.scripts.github.test_pr_workspace",
        "TestPrWorkspace",
    ),
    "TestSyncScripts": ("tests.unit.scripts.sync_tests", "TestSyncScripts"),
    "TestVersioning": ("tests.unit.libs.versioning_tests", "TestVersioning"),
    "c": ("tests.infra.constants", "c"),
    "d": ("flext_tests", "d"),
    "e": ("flext_tests", "e"),
    "h": ("flext_tests", "h"),
    "infra": ("tests.infra", ""),
    "m": ("tests.infra.models", "m"),
    "p": ("tests.infra.protocols", "p"),
    "r": ("tests.infra.result", "r"),
    "s": ("flext_tests", "s"),
    "t": ("tests.infra.typings", "t"),
    "tf": ("tests.tf", "tf"),
    "tm": ("tests.tm", "tm"),
    "u": ("tests.infra.utilities", "u"),
    "x": ("flext_tests", "x"),
}

__all__ = [
    "FlextWorkspaceTestConstants",
    "FlextWorkspaceTestModels",
    "FlextWorkspaceTestProtocols",
    "FlextWorkspaceTestTypes",
    "FlextWorkspaceTestUtilities",
    "TestPrWorkspace",
    "TestSyncScripts",
    "TestVersioning",
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
