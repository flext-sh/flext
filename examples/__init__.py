# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Examples package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from examples import (
        acl_processing_example,
        advanced_processing_example,
        complete_workflow_example,
    )
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
        WorkflowContent,
        WorkflowData,
    )
    from flext_core import FlextTypes

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "AclProcessingExample": "examples.acl_processing_example",
    "AdvancedProcessingExample": "examples.advanced_processing_example",
    "CompleteWorkflowExample": "examples.complete_workflow_example",
    "ContextDict": "examples.acl_processing_example",
    "EntryDict": "examples.acl_processing_example",
    "ItemDict": "examples.advanced_processing_example",
    "PipelineStageData": "examples.advanced_processing_example",
    "ProcessingDict": "examples.complete_workflow_example",
    "StageOperation": "examples.advanced_processing_example",
    "WorkflowContent": "examples.complete_workflow_example",
    "WorkflowData": "examples.complete_workflow_example",
    "acl_processing_example": "examples.acl_processing_example",
    "advanced_processing_example": "examples.advanced_processing_example",
    "complete_workflow_example": "examples.complete_workflow_example",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
