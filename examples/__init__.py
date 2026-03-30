# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Examples package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from examples import (
        acl_processing_example as acl_processing_example,
        advanced_processing_example as advanced_processing_example,
        complete_workflow_example as complete_workflow_example,
    )
    from examples.acl_processing_example import (
        AclProcessingExample as AclProcessingExample,
        ContextDict as ContextDict,
        EntryDict as EntryDict,
    )
    from examples.advanced_processing_example import (
        AdvancedProcessingExample as AdvancedProcessingExample,
        ItemDict as ItemDict,
        PipelineStageData as PipelineStageData,
        StageOperation as StageOperation,
    )
    from examples.complete_workflow_example import (
        CompleteWorkflowExample as CompleteWorkflowExample,
        ProcessingDict as ProcessingDict,
        WorkflowContent as WorkflowContent,
        WorkflowData as WorkflowData,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "AclProcessingExample": ["examples.acl_processing_example", "AclProcessingExample"],
    "AdvancedProcessingExample": [
        "examples.advanced_processing_example",
        "AdvancedProcessingExample",
    ],
    "CompleteWorkflowExample": [
        "examples.complete_workflow_example",
        "CompleteWorkflowExample",
    ],
    "ContextDict": ["examples.acl_processing_example", "ContextDict"],
    "EntryDict": ["examples.acl_processing_example", "EntryDict"],
    "ItemDict": ["examples.advanced_processing_example", "ItemDict"],
    "PipelineStageData": ["examples.advanced_processing_example", "PipelineStageData"],
    "ProcessingDict": ["examples.complete_workflow_example", "ProcessingDict"],
    "StageOperation": ["examples.advanced_processing_example", "StageOperation"],
    "WorkflowContent": ["examples.complete_workflow_example", "WorkflowContent"],
    "WorkflowData": ["examples.complete_workflow_example", "WorkflowData"],
    "acl_processing_example": ["examples.acl_processing_example", ""],
    "advanced_processing_example": ["examples.advanced_processing_example", ""],
    "complete_workflow_example": ["examples.complete_workflow_example", ""],
}

_EXPORTS: Sequence[str] = [
    "AclProcessingExample",
    "AdvancedProcessingExample",
    "CompleteWorkflowExample",
    "ContextDict",
    "EntryDict",
    "ItemDict",
    "PipelineStageData",
    "ProcessingDict",
    "StageOperation",
    "WorkflowContent",
    "WorkflowData",
    "acl_processing_example",
    "advanced_processing_example",
    "complete_workflow_example",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
