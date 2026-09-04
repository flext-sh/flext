# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.infra package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import FlextTestsConstants, d, e, h, s, td, tf, tk, tm, tv, x
    from typing import Final

    from .constants import TestsFlextRootConstants, TestsFlextRootConstants as c
    from .models import TestsFlextRootModels, TestsFlextRootModels as m
    from .protocols import TestsFlextRootProtocols, TestsFlextRootProtocols as p
    from .result import TestsFlextRootResult, r
    from .typings import TestsFlextRootTypes, TestsFlextRootTypes as t
    from .utilities import TestsFlextRootUtilities, TestsFlextRootUtilities as u
__all__: tuple[str, ...] = (
    "Final",
    "FlextTestsConstants",
    "TestsFlextRootConstants",
    "TestsFlextRootModels",
    "TestsFlextRootProtocols",
    "TestsFlextRootResult",
    "TestsFlextRootTypes",
    "TestsFlextRootUtilities",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
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
            ".constants": ("TestsFlextRootConstants", "c"),
            ".models": ("TestsFlextRootModels", "m"),
            ".protocols": ("TestsFlextRootProtocols", "p"),
            ".result": ("TestsFlextRootResult", "r"),
            ".typings": ("TestsFlextRootTypes", "t"),
            ".utilities": ("TestsFlextRootUtilities", "u"),
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
                "x",
            ),
            "typing": ("Final",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
