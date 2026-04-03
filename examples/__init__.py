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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
