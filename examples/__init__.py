# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext import c, d, e, h, m, p, r, s, t, u, x

    from ._models import ValidationRules
    from .acl_processing_example import AclProcessingExample
    from .advanced_processing_example import (
        AdvancedProcessingExample,
        MAX_VALUE_LENGTH,
        PipelineStageData,
    )
    from .complete_workflow_example import CompleteWorkflowExample
__all__: tuple[str, ...] = (
    "MAX_VALUE_LENGTH",
    "AclProcessingExample",
    "AdvancedProcessingExample",
    "CompleteWorkflowExample",
    "PipelineStageData",
    "ValidationRules",
    "c",
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
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._models": ("ValidationRules",),
            ".acl_processing_example": ("AclProcessingExample",),
            ".advanced_processing_example": (
                "AdvancedProcessingExample",
                "MAX_VALUE_LENGTH",
                "PipelineStageData",
            ),
            ".complete_workflow_example": ("CompleteWorkflowExample",),
            "flext": ("c", "d", "e", "h", "m", "p", "r", "s", "t", "u", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
