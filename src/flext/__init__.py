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
    from flext_oracle_oic import d, h, r, s, x
    from flext_oracle_wms import e
    from flext_tests import api, td, tf, tk, tm


__all__: tuple[str, ...] = (
    "FlextRootCli",
    "FlextRootConfig",
    "FlextRootConstants",
    "FlextRootModels",
    "FlextRootProtocols",
    "FlextRootSettings",
    "FlextRootTypes",
    "FlextRootUtilities",
    "api",
    "c",
    "config",
    "d",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "u",
    "x",
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
        "api": "flext_tests",
        "c": ".constants",
        "config": ".config",
        "d": "flext_oracle_oic",
        "e": "flext_oracle_wms",
        "h": "flext_oracle_oic",
        "m": ".models",
        "main": ".cli",
        "p": ".protocols",
        "r": "flext_oracle_oic",
        "s": "flext_oracle_oic",
        "settings": ".settings",
        "t": ".typings",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": ".utilities",
        "x": "flext_oracle_oic",
    }),
    public_exports=__all__,
)
