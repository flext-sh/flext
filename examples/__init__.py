# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Examples package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes

    from examples.acl_processing_example import (
        AclProcessingExample,
        ContextDict,
        EntryDict,
    )
    from examples.advanced_processing_example import (
        AdvancedProcessingExample,
        ItemDict,
        PipelineStageData,
        StageOperation,
    )
    from examples.complete_workflow_example import (
        CompleteWorkflowExample,
        ProcessingDict,
        WorkflowData,
    )

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "AclProcessingExample": ("examples.acl_processing_example", "AclProcessingExample"),
    "AdvancedProcessingExample": (
        "examples.advanced_processing_example",
        "AdvancedProcessingExample",
    ),
    "CompleteWorkflowExample": (
        "examples.complete_workflow_example",
        "CompleteWorkflowExample",
    ),
    "ContextDict": ("examples.acl_processing_example", "ContextDict"),
    "EntryDict": ("examples.acl_processing_example", "EntryDict"),
    "ItemDict": ("examples.advanced_processing_example", "ItemDict"),
    "PipelineStageData": ("examples.advanced_processing_example", "PipelineStageData"),
    "ProcessingDict": ("examples.complete_workflow_example", "ProcessingDict"),
    "StageOperation": ("examples.advanced_processing_example", "StageOperation"),
    "WorkflowData": ("examples.complete_workflow_example", "WorkflowData"),
}

__all__ = [
    "AclProcessingExample",
    "AdvancedProcessingExample",
    "CompleteWorkflowExample",
    "ContextDict",
    "EntryDict",
    "ItemDict",
    "PipelineStageData",
    "ProcessingDict",
    "StageOperation",
    "WorkflowData",
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
