# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.infra package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import FlextTestsConstants, d, e, h, s, td, tf, tk, tm, tv, u, x

    from .constants import TestsFlextRootConstants
    from .models import TestsFlextRootModels
    from .protocols import TestsFlextRootProtocols
    from .result import TestsFlextRootResult
    from .typings import TestsFlextRootTypes
__all__: tuple[str, ...] = (
    "FlextTestsConstants",
    "TestsFlextRootConstants",
    "TestsFlextRootModels",
    "TestsFlextRootProtocols",
    "TestsFlextRootResult",
    "TestsFlextRootTypes",
    "d",
    "e",
    "h",
    "s",
    "td",
    "tf",
    "tk",
    "tm",
    "tv",
    "u",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".constants": ("TestsFlextRootConstants",),
            ".models": ("TestsFlextRootModels",),
            ".protocols": ("TestsFlextRootProtocols",),
            ".result": ("TestsFlextRootResult",),
            ".typings": ("TestsFlextRootTypes",),
            "flext_tests": (
                "FlextTestsConstants",
                "d",
                "e",
                "h",
                "s",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "u",
                "x",
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
