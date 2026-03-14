# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Github package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextTypes, cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from tests.unit.scripts.github.test_pr_workspace import (
        test_main_respects_fail_fast,
        test_main_runs_projects_and_root,
        test_run_pr_uses_make_for_non_root_repo,
        test_run_pr_uses_pr_manager_for_workspace_root,
    )

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "test_main_respects_fail_fast": ("tests.unit.scripts.github.test_pr_workspace", "test_main_respects_fail_fast"),
    "test_main_runs_projects_and_root": ("tests.unit.scripts.github.test_pr_workspace", "test_main_runs_projects_and_root"),
    "test_run_pr_uses_make_for_non_root_repo": ("tests.unit.scripts.github.test_pr_workspace", "test_run_pr_uses_make_for_non_root_repo"),
    "test_run_pr_uses_pr_manager_for_workspace_root": ("tests.unit.scripts.github.test_pr_workspace", "test_run_pr_uses_pr_manager_for_workspace_root"),
}

__all__ = [
    "test_main_respects_fail_fast",
    "test_main_runs_projects_and_root",
    "test_run_pr_uses_make_for_non_root_repo",
    "test_run_pr_uses_pr_manager_for_workspace_root",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
