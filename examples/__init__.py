# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Examples package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    import examples.acl_processing_example as _examples_acl_processing_example

    acl_processing_example = _examples_acl_processing_example
    import examples.advanced_processing_example as _examples_advanced_processing_example
    from examples.acl_processing_example import (
        AclProcessingExample,
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
_LAZY_IMPORTS = build_lazy_import_map(
    {
        "examples.acl_processing_example": (
            "acl_processing_example",
            "AclProcessingExample",
        ),
        "examples.advanced_processing_example": (
            "advanced_processing_example",
            "AdvancedProcessingExample",
            "ItemDict",
            "PipelineStageData",
            "StageOperation",
        ),
        "examples.complete_workflow_example": (
            "complete_workflow_example",
            "CompleteWorkflowExample",
            "ProcessingDict",
            "WorkflowContent",
            "WorkflowData",
        ),
    },
    alias_groups={
        "flext_core.constants": (("c", "FlextConstants"),),
        "flext_core.decorators": (("d", "FlextDecorators"),),
        "flext_core.exceptions": (("e", "FlextExceptions"),),
        "flext_core.handlers": (("h", "FlextHandlers"),),
        "flext_core.mixins": (("x", "FlextMixins"),),
        "flext_core.models": (("m", "FlextModels"),),
        "flext_core.protocols": (("p", "FlextProtocols"),),
        "flext_core.result": (("r", "FlextResult"),),
        "flext_core.service": (("s", "FlextService"),),
        "flext_core.typings": (("t", "FlextTypes"),),
        "flext_core.utilities": (("u", "FlextUtilities"),),
    },
)

__all__: list[str] = [
    "AclProcessingExample",
    "AdvancedProcessingExample",
    "CompleteWorkflowExample",
    "ItemDict",
    "PipelineStageData",
    "StageOperation",
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
