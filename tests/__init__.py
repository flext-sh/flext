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
    from flext import c, config, d, h, m, p, r, t, u, x
    from flext_oracle_wms import e
    from flext_tests import api, td, tf, tk, tm
    from tests.base import TestsFlextRootServiceBase

    s = TestsFlextRootServiceBase


__all__: tuple[str, ...] = (
    "TestsFlextRootServiceBase",
    "api",
    "c",
    "config",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
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
        "config": "flext",
        "d": "flext",
        "e": "flext_oracle_wms",
        "h": "flext",
        "m": "flext",
        "p": "flext",
        "r": "flext",
        "s": ".base",
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
