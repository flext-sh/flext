# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_core import core, d, e, h, lazy_attribute, r, x

    from . import services
    from .api import FlextRoot, api, flext
    from .base import FlextRootServiceBase, s
    from .cli import FlextRootCli, main
    from .config import FlextRootConfig, config
    from .constants import FlextRootConstants, c
    from .models import FlextRootModels, m
    from .protocols import FlextRootProtocols, p
    from .settings import FlextRootSettings, FlextRootSettings as settings
    from .typings import FlextRootTypes, t
    from .utilities import FlextRootUtilities, u
__all__: tuple[str, ...] = (
    "FlextRoot",
    "FlextRootCli",
    "FlextRootConfig",
    "FlextRootConstants",
    "FlextRootModels",
    "FlextRootProtocols",
    "FlextRootServiceBase",
    "FlextRootSettings",
    "FlextRootTypes",
    "FlextRootUtilities",
    "api",
    "c",
    "config",
    "core",
    "d",
    "e",
    "flext",
    "h",
    "lazy_attribute",
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
            ".models": ("FlextRootModels", "m"),
            ".protocols": ("FlextRootProtocols", "p"),
            ".services": ("services",),
            ".settings": ("FlextRootSettings", "settings"),
            ".typings": ("FlextRootTypes", "t"),
            ".utilities": ("FlextRootUtilities", "u"),
            "flext_core": ("core", "d", "e", "h", "lazy_attribute", "r", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
