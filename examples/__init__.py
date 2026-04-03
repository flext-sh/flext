# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Examples package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import examples.acl_processing_example as _examples_acl_processing_example

    acl_processing_example = _examples_acl_processing_example
    import examples.advanced_processing_example as _examples_advanced_processing_example
    from examples.acl_processing_example import (
        AclProcessingExample,
        ContextDict,
        EntryDict,
    )

    advanced_processing_example = _examples_advanced_processing_example
    import examples.complete_workflow_example as _examples_complete_workflow_example
    from examples.advanced_processing_example import (
        AdvancedProcessingExample,
        ItemDict,
        PipelineStageData,
        StageOperation,
    )

    complete_workflow_example = _examples_complete_workflow_example
    from examples.complete_workflow_example import (
        CompleteWorkflowExample,
        ProcessingDict,
        WorkflowContent,
        WorkflowData,
    )
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
_LAZY_IMPORTS = {
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
    "c": ("flext_core.constants", "FlextConstants"),
    "complete_workflow_example": "examples.complete_workflow_example",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
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
    "WorkflowContent",
    "WorkflowData",
    "acl_processing_example",
    "advanced_processing_example",
    "c",
    "complete_workflow_example",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
