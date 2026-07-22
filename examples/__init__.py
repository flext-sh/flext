# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from examples.acl_processing_example import AclProcessingExample
    from examples.advanced_processing_example import (
        AdvancedProcessingExample,
        PipelineStageData,
    )
    from examples.complete_workflow_example import CompleteWorkflowExample
    from flext import c, d, e, h, m, p, r, t, u, x
_LAZY_IMPORTS = build_lazy_import_map({
    ".acl_processing_example": ("AclProcessingExample",),
    ".advanced_processing_example": ("AdvancedProcessingExample", "PipelineStageData"),
    ".complete_workflow_example": ("CompleteWorkflowExample",),
    "flext": ("c", "d", "e", "h", "m", "p", "r", "t", "u", "x"),
})


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "AclProcessingExample",
    "AdvancedProcessingExample",
    "CompleteWorkflowExample",
    "PipelineStageData",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "t",
    "u",
    "x",
]
