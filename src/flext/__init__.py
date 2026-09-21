# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_core import d, e, h, r, x

    from . import services
    from .api import FlextRoot, api, flext
    from .base import FlextRootServiceBase, FlextRootServiceBase as s
    from .cli import FlextRootCli, main
    from .config import FlextRootConfig, config
    from .constants import FlextRootConstants, FlextRootConstants as c
    from .dev import FlextRootDev
    from .docs import FlextRootDocs
    from .models import FlextRootModels, FlextRootModels as m
    from .protocols import FlextRootProtocols, FlextRootProtocols as p
    from .settings import FlextRootSettings, settings
    from .typings import FlextRootTypes, FlextRootTypes as t
    from .utilities import FlextRootUtilities, FlextRootUtilities as u
    from .workspace import FlextRootWorkspace
__all__: tuple[str, ...] = (
    "FlextRoot",
    "FlextRootCli",
    "FlextRootConfig",
    "FlextRootConstants",
    "FlextRootDev",
    "FlextRootDocs",
    "FlextRootModels",
    "FlextRootProtocols",
    "FlextRootServiceBase",
    "FlextRootSettings",
    "FlextRootTypes",
    "FlextRootUtilities",
    "FlextRootWorkspace",
    "api",
    "c",
    "config",
    "d",
    "e",
    "flext",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "services",
    "settings",
    "t",
    "u",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".api": ("FlextRoot", "api", "flext"),
            ".base": ("FlextRootServiceBase", "s"),
            ".cli": ("FlextRootCli", "main"),
            ".config": ("FlextRootConfig", "config"),
            ".constants": ("FlextRootConstants", "c"),
            ".dev": ("FlextRootDev",),
            ".docs": ("FlextRootDocs",),
            ".models": ("FlextRootModels", "m"),
            ".protocols": ("FlextRootProtocols", "p"),
            ".services": ("services",),
            ".settings": ("FlextRootSettings", "settings"),
            ".typings": ("FlextRootTypes", "t"),
            ".utilities": ("FlextRootUtilities", "u"),
            ".workspace": ("FlextRootWorkspace",),
            "flext_core": ("d", "e", "h", "r", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
