# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext import c, m, p, t, u

    from tests import infra, unit
    from tests.base import TestsFlextRootServiceBase, s


__all__: tuple[str, ...] = (
    "TestsFlextRootServiceBase",
    "c",
    "infra",
    "m",
    "p",
    "s",
    "t",
    "u",
    "unit",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("TestsFlextRootServiceBase", "s"),
            ".infra": ("infra",),
            ".unit": ("unit",),
            "flext": ("c", "m", "p", "t", "u"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
