# @generated AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_core import d as d
    from flext_core import e as e
    from flext_core import h as h
    from flext_core import r as r
    from flext_core import s as s
    from flext_core import x as x

    from .constants import FlextRootConstants as FlextRootConstants

    c: type[FlextRootConstants]
    from .dev import FlextRootDev as FlextRootDev
    from .docs import FlextRootDocs as FlextRootDocs
    from .models import FlextRootModels as FlextRootModels

    m: type[FlextRootModels]
    from .protocols import FlextRootProtocols as FlextRootProtocols

    p: type[FlextRootProtocols]
    from .typings import FlextRootTypes as FlextRootTypes

    t: type[FlextRootTypes]
    from .utilities import FlextRootUtilities as FlextRootUtilities

    u: type[FlextRootUtilities]
    from .workspace import FlextRootWorkspace as FlextRootWorkspace

_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    ".constants": ("FlextRootConstants", "c"),
    ".dev": ("FlextRootDev",),
    ".docs": ("FlextRootDocs",),
    ".models": ("FlextRootModels", "m"),
    ".protocols": ("FlextRootProtocols", "p"),
    ".typings": ("FlextRootTypes", "t"),
    ".utilities": ("FlextRootUtilities", "u"),
    ".workspace": ("FlextRootWorkspace",),
    "flext_core": ("d", "e", "h", "r", "s", "x"),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_PUBLIC_EXPORTS: tuple[str, ...] = (
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

__all__: tuple[str, ...] = tuple(_PUBLIC_EXPORTS)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
