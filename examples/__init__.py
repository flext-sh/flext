# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Examples package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from examples.acl_processing_example import (
        AclProcessingExample,
        ContextDict,
        EntryDict,
    )
    from examples.advanced_processing_example import AdvancedProcessingExample, ItemDict
    from examples.complete_workflow_example import (
        CompleteWorkflowExample,
        ProcessingDict,
    )

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "AclProcessingExample": ("examples.acl_processing_example", "AclProcessingExample"),
    "AdvancedProcessingExample": ("examples.advanced_processing_example", "AdvancedProcessingExample"),
    "CompleteWorkflowExample": ("examples.complete_workflow_example", "CompleteWorkflowExample"),
    "ContextDict": ("examples.acl_processing_example", "ContextDict"),
    "EntryDict": ("examples.acl_processing_example", "EntryDict"),
    "ItemDict": ("examples.advanced_processing_example", "ItemDict"),
    "ProcessingDict": ("examples.complete_workflow_example", "ProcessingDict"),
}

__all__ = [
    "AclProcessingExample",
    "AdvancedProcessingExample",
    "CompleteWorkflowExample",
    "ContextDict",
    "EntryDict",
    "ItemDict",
    "ProcessingDict",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
