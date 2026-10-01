# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.infra package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from tests.infra.constants import TestsFlextRootConstants
    from tests.infra.models import TestsFlextRootModels
    from tests.infra.protocols import TestsFlextRootProtocols
    from tests.infra.result import TestsFlextRootResult, r
    from tests.infra.typings import TestsFlextRootTypes


__all__: tuple[str, ...] = (
    "TestsFlextRootConstants",
    "TestsFlextRootModels",
    "TestsFlextRootProtocols",
    "TestsFlextRootResult",
    "TestsFlextRootTypes",
    "r",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".constants": ("TestsFlextRootConstants",),
            ".models": ("TestsFlextRootModels",),
            ".protocols": ("TestsFlextRootProtocols",),
            ".result": ("TestsFlextRootResult", "r"),
            ".typings": ("TestsFlextRootTypes",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
