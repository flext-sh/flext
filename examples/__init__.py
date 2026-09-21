# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext import c, d, e, h, m, p, r, s, t, u, x

    from ._constants import FlextRootExamplesConstants
    from ._models import FlextRootExamplesModels, ValidationRules
    from .acl_processing_example import (
        FlextRootAclProcessingExample,
        _AclExtractor,
        _AclPermissionParser,
        _AclValidator,
        _ServerDetector,
    )
    from .advanced_processing_example import (
        FlextRootAdvancedProcessingExample,
        PipelinePayload,
        PipelineStageData,
        _Constants,
        _DataValueMap,
        _JsonMappingOrNone,
        _JsonMappingSequence,
        _ScalarDict,
        _StringSequence,
    )
    from .complete_workflow_example import (
        FlextRootCompleteWorkflowExample,
        _ImmutableMappings,
    )
__all__: tuple[str, ...] = (
    "FlextRootAclProcessingExample",
    "FlextRootAdvancedProcessingExample",
    "FlextRootCompleteWorkflowExample",
    "FlextRootExamplesConstants",
    "FlextRootExamplesModels",
    "PipelinePayload",
    "PipelineStageData",
    "ValidationRules",
    "_AclExtractor",
    "_AclPermissionParser",
    "_AclValidator",
    "_Constants",
    "_DataValueMap",
    "_ImmutableMappings",
    "_JsonMappingOrNone",
    "_JsonMappingSequence",
    "_ScalarDict",
    "_ServerDetector",
    "_StringSequence",
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
            "._constants": ("FlextRootExamplesConstants",),
            "._models": ("FlextRootExamplesModels", "ValidationRules"),
            ".acl_processing_example": (
                "FlextRootAclProcessingExample",
                "_AclExtractor",
                "_AclPermissionParser",
                "_AclValidator",
                "_ServerDetector",
            ),
            ".advanced_processing_example": (
                "FlextRootAdvancedProcessingExample",
                "PipelinePayload",
                "PipelineStageData",
                "_Constants",
                "_DataValueMap",
                "_JsonMappingOrNone",
                "_JsonMappingSequence",
                "_ScalarDict",
                "_StringSequence",
            ),
            ".complete_workflow_example": (
                "FlextRootCompleteWorkflowExample",
                "_ImmutableMappings",
            ),
            "flext": ("c", "d", "e", "h", "m", "p", "r", "s", "t", "u", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
