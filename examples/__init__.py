# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from examples._constants import ExamplesFlextRootConstants
    from flext import c, config, m, p, t, u


__all__: tuple[str, ...] = (
    "ExamplesFlextRootConstants",
    "c",
    "config",
    "m",
    "p",
    "t",
    "u",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "ExamplesFlextRootConstants": "._constants",
        "c": "flext",
        "config": "flext",
        "m": "flext",
        "p": "flext",
        "t": "flext",
        "u": "flext",
    }),
    public_exports=__all__,
)
