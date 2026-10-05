# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

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

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextRootCli": ".cli",
        "FlextRootConfig": ".config",
        "FlextRootConstants": ".constants",
        "FlextRootModels": ".models",
        "FlextRootProtocols": ".protocols",
        "FlextRootSettings": ".settings",
        "FlextRootTypes": ".typings",
        "FlextRootUtilities": ".utilities",
        "c": ".constants",
        "config": ".config",
        "m": ".models",
        "main": ".cli",
        "p": ".protocols",
        "settings": ".settings",
        "t": ".typings",
        "u": ".utilities",
    }),
    public_exports=__all__,
)
