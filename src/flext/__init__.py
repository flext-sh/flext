# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .cli import FlextRootCli, main
    from .config import FlextRootConfig, config
    from .constants import FlextRootConstants, FlextRootConstants as c
    from .models import FlextRootModels, FlextRootModels as m
    from .protocols import FlextRootProtocols, FlextRootProtocols as p
    from .settings import FlextRootSettings, FlextRootSettings as settings
    from .typings import FlextRootTypes, FlextRootTypes as t
    from .utilities import FlextRootUtilities, FlextRootUtilities as u


__all__: tuple[str, ...] = (
    "FlextRootCli",
    "FlextRootConfig",
    "FlextRootConstants",
    "FlextRootModels",
    "FlextRootProtocols",
    "FlextRootSettings",
    "FlextRootTypes",
    "FlextRootUtilities",
    "c",
    "config",
    "m",
    "main",
    "p",
    "settings",
    "t",
    "u",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".cli": ("FlextRootCli", "main"),
            ".config": ("FlextRootConfig", "config"),
            ".constants": ("FlextRootConstants", "c"),
            ".models": ("FlextRootModels", "m"),
            ".protocols": ("FlextRootProtocols", "p"),
            ".settings": ("FlextRootSettings", "settings"),
            ".typings": ("FlextRootTypes", "t"),
            ".utilities": ("FlextRootUtilities", "u"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
