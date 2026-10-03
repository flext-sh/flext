# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext.cli import FlextRootCli, main
    from flext.config import FlextRootConfig, config
    from flext.constants import FlextRootConstants, c
    from flext.models import FlextRootModels, m
    from flext.protocols import FlextRootProtocols, p
    from flext.settings import FlextRootSettings, settings
    from flext.typings import FlextRootTypes, t
    from flext.utilities import FlextRootUtilities, u


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
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
