# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Libs package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes
    from tests.unit.libs.versioning_tests import (
        test_current_workspace_version_reads_project_version,
        test_parse_and_bump_semver,
        test_release_tag_from_branch_patterns,
        test_replace_project_version_updates_only_project_table,
    )

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "test_current_workspace_version_reads_project_version": (
        "tests.unit.libs.versioning_tests",
        "test_current_workspace_version_reads_project_version",
    ),
    "test_parse_and_bump_semver": (
        "tests.unit.libs.versioning_tests",
        "test_parse_and_bump_semver",
    ),
    "test_release_tag_from_branch_patterns": (
        "tests.unit.libs.versioning_tests",
        "test_release_tag_from_branch_patterns",
    ),
    "test_replace_project_version_updates_only_project_table": (
        "tests.unit.libs.versioning_tests",
        "test_replace_project_version_updates_only_project_table",
    ),
}

__all__ = [
    "test_current_workspace_version_reads_project_version",
    "test_parse_and_bump_semver",
    "test_release_tag_from_branch_patterns",
    "test_replace_project_version_updates_only_project_table",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
