# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.infra package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .constants import TestsFlextRootConstants
    from .models import TestsFlextRootModels
    from .protocols import TestsFlextRootProtocols
    from .result import TestsFlextRootResult, r
    from .typings import TestsFlextRootTypes
__all__: tuple[str, ...] = (
    "TestsFlextRootConstants",
    "TestsFlextRootModels",
    "TestsFlextRootProtocols",
    "TestsFlextRootResult",
    "TestsFlextRootTypes",
    "r",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".constants": ("TestsFlextRootConstants",),
            ".models": ("TestsFlextRootModels",),
            ".protocols": ("TestsFlextRootProtocols",),
            ".result": ("TestsFlextRootResult", "r"),
            ".typings": ("TestsFlextRootTypes",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
