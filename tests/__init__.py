# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from . import infra as infra
    from . import unit as unit
    from flext_tests import d, e, h, s, td, tf, tk, tm, tv, x
    from typing import Final

    from .infra.constants import TestsFlextRootConstants, TestsFlextRootConstants as c
    from .infra.models import TestsFlextRootModels, TestsFlextRootModels as m
    from .infra.protocols import TestsFlextRootProtocols, TestsFlextRootProtocols as p
    from .infra.result import TestsFlextRootResult, r
    from .infra.typings import TestsFlextRootTypes, TestsFlextRootTypes as t
    from .infra.utilities import TestsFlextRootUtilities
    from .utilities import TestsFlextTestUtilities, TestsFlextTestUtilities as u
__all__: tuple[str, ...] = (
    "Final",
    "TestsFlextRootConstants",
    "TestsFlextRootModels",
    "TestsFlextRootProtocols",
    "TestsFlextRootResult",
    "TestsFlextRootTypes",
    "TestsFlextRootUtilities",
    "TestsFlextTestUtilities",
    "c",
    "d",
    "e",
    "h",
    "infra",
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
    "unit",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".infra": ("infra",),
            ".infra.constants": ("TestsFlextRootConstants", "c"),
            ".infra.models": ("TestsFlextRootModels", "m"),
            ".infra.protocols": ("TestsFlextRootProtocols", "p"),
            ".infra.result": ("TestsFlextRootResult", "r"),
            ".infra.typings": ("TestsFlextRootTypes", "t"),
            ".infra.utilities": ("TestsFlextRootUtilities",),
            ".unit": ("unit",),
            ".utilities": ("TestsFlextTestUtilities", "u"),
            "flext_tests": ("d", "e", "h", "s", "td", "tf", "tk", "tm", "tv", "x"),
            "typing": ("Final",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
