# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext import (
        c,
        cli,
        config,
        d,
        db_oracle,
        grpc,
        h,
        infra,
        install_local_packages,
        ldap,
        m,
        main,
        meltano,
        observability,
        oracle_oic,
        oracle_wms,
        p,
        plugin,
        quality,
        r,
        settings,
        t,
        u,
        x,
    )
    from flext_oracle_wms import e
    from flext_tests import api, td, tf, tk, tm
    from tests.base import TestsFlextRootServiceBase, s


__all__: tuple[str, ...] = (
    "TestsFlextRootServiceBase",
    "api",
    "c",
    "cli",
    "config",
    "d",
    "db_oracle",
    "e",
    "grpc",
    "h",
    "infra",
    "install_local_packages",
    "ldap",
    "m",
    "main",
    "meltano",
    "observability",
    "oracle_oic",
    "oracle_wms",
    "p",
    "plugin",
    "quality",
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
        "TestsFlextRootServiceBase": ".base",
        "api": "flext_tests",
        "c": "flext",
        "cli": "flext",
        "config": "flext",
        "d": "flext",
        "db_oracle": "flext",
        "e": "flext_oracle_wms",
        "grpc": "flext",
        "h": "flext",
        "infra": "flext",
        "install_local_packages": "flext",
        "ldap": "flext",
        "m": "flext",
        "main": "flext",
        "meltano": "flext",
        "observability": "flext",
        "oracle_oic": "flext",
        "oracle_wms": "flext",
        "p": "flext",
        "plugin": "flext",
        "quality": "flext",
        "r": "flext",
        "s": ".base",
        "settings": "flext",
        "t": "flext",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": "flext",
        "x": "flext",
    }),
    public_exports=__all__,
)
