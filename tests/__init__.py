# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext import c, config, m, p, t, u
    from tests import infra, unit
    from tests.base import TestsFlextRootServiceBase, s


__all__: tuple[str, ...] = (
    "TestsFlextRootServiceBase",
    "c",
    "config",
    "infra",
    "m",
    "p",
    "s",
    "t",
    "u",
    "unit",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextRootServiceBase": ".base",
        "c": "flext",
        "config": "flext",
        "infra": ".infra",
        "m": "flext",
        "p": "flext",
        "s": ".base",
        "t": "flext",
        "u": "flext",
        "unit": ".unit",
    }),
    public_exports=__all__,
)
