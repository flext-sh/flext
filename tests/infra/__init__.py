# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.infra package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.infra.constants import TestsFlextRootConstants, c
    from tests.infra.models import TestsFlextRootModels, m
    from tests.infra.protocols import TestsFlextRootProtocols, p
    from tests.infra.result import TestsFlextRootResult, r
    from tests.infra.typings import TestsFlextRootTypes, t
    from tests.infra.utilities import TestsFlextRootUtilities, u


__all__: tuple[str, ...] = (
    "TestsFlextRootConstants",
    "TestsFlextRootModels",
    "TestsFlextRootProtocols",
    "TestsFlextRootResult",
    "TestsFlextRootTypes",
    "TestsFlextRootUtilities",
    "c",
    "m",
    "p",
    "r",
    "t",
    "u",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextRootConstants": ".constants",
        "TestsFlextRootModels": ".models",
        "TestsFlextRootProtocols": ".protocols",
        "TestsFlextRootResult": ".result",
        "TestsFlextRootTypes": ".typings",
        "TestsFlextRootUtilities": ".utilities",
        "c": ".constants",
        "m": ".models",
        "p": ".protocols",
        "r": ".result",
        "t": ".typings",
        "u": ".utilities",
    }),
    public_exports=__all__,
)
