# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_core import d, e, h, r, s, x

    from .constants import FlextRootConstants, FlextRootConstants as c
    from .dev import FlextRootDev
    from .docs import FlextRootDocs
    from .models import FlextRootModels, FlextRootModels as m
    from .protocols import FlextRootProtocols, FlextRootProtocols as p
    from .typings import FlextRootTypes, FlextRootTypes as t
    from .utilities import FlextRootUtilities, FlextRootUtilities as u
    from .workspace import FlextRootWorkspace

__all__: tuple[str, ...] = (
    "FlextRootConstants",
    "FlextRootDev",
    "FlextRootDocs",
    "FlextRootModels",
    "FlextRootProtocols",
    "FlextRootTypes",
    "FlextRootUtilities",
    "FlextRootWorkspace",
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

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType(
        build_lazy_import_map(
            MappingProxyType({
                ".constants": ("FlextRootConstants", "c"),
                ".dev": ("FlextRootDev",),
                ".docs": ("FlextRootDocs",),
                ".models": ("FlextRootModels", "m"),
                ".protocols": ("FlextRootProtocols", "p"),
                ".typings": ("FlextRootTypes", "t"),
                ".utilities": ("FlextRootUtilities", "u"),
                ".workspace": ("FlextRootWorkspace",),
                "flext_core": ("d", "e", "h", "r", "s", "x"),
            }),
            alias_groups=MappingProxyType({}),
            sort_keys=False,
        )
    ),
    public_exports=__all__,
)
