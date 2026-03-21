# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Scripts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from . import github as github
    from .github.test_pr_workspace import TestPrWorkspace
    from .sync_tests import TestSyncScripts

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "TestPrWorkspace": ("tests.unit.scripts.github.test_pr_workspace", "TestPrWorkspace"),
    "TestSyncScripts": ("tests.unit.scripts.sync_tests", "TestSyncScripts"),
    "github": ("tests.unit.scripts.github", ""),
}

__all__ = [
    "TestPrWorkspace",
    "TestSyncScripts",
    "github",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
