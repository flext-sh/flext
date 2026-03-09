# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from tests.unit.scripts.dependencies.modernize_pyproject_tests import (
        test_array_of_tables_survives_regex_fallback,
        test_audit_exit_codes_reflect_violations,
        test_bandit_skips_are_loaded_from_root_ssot,
        test_process_file_is_idempotent_with_array_of_tables,
        write_pyproject,
    )

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "test_array_of_tables_survives_regex_fallback": ("tests.unit.scripts.dependencies.modernize_pyproject_tests", "test_array_of_tables_survives_regex_fallback"),
    "test_audit_exit_codes_reflect_violations": ("tests.unit.scripts.dependencies.modernize_pyproject_tests", "test_audit_exit_codes_reflect_violations"),
    "test_bandit_skips_are_loaded_from_root_ssot": ("tests.unit.scripts.dependencies.modernize_pyproject_tests", "test_bandit_skips_are_loaded_from_root_ssot"),
    "test_process_file_is_idempotent_with_array_of_tables": ("tests.unit.scripts.dependencies.modernize_pyproject_tests", "test_process_file_is_idempotent_with_array_of_tables"),
    "write_pyproject": ("tests.unit.scripts.dependencies.modernize_pyproject_tests", "write_pyproject"),
}

__all__ = [
    "test_array_of_tables_survives_regex_fallback",
    "test_audit_exit_codes_reflect_violations",
    "test_bandit_skips_are_loaded_from_root_ssot",
    "test_process_file_is_idempotent_with_array_of_tables",
    "write_pyproject",
]


def __getattr__(name: str) -> Any:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
