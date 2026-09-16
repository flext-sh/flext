# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.infra package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
<<<<<<< HEAD
    from flext_tests import c, d, e, h, m, p, r, s, t, td, tf, tk, tm, tv, u, x
=======
    from flext_tests import c, d, e, h, m, p, s, t, td, tf, tk, tm, tv, u, x
>>>>>>> origin/0.12.0-dev

    from .constants import TestsFlextRootConstants
    from .models import TestsFlextRootModels
    from .protocols import TestsFlextRootProtocols
<<<<<<< HEAD
    from .result import TestsFlextRootResult
=======
    from .result import TestsFlextRootResult, r
>>>>>>> origin/0.12.0-dev
    from .typings import TestsFlextRootTypes
__all__: tuple[str, ...] = (
    "TestsFlextRootConstants",
    "TestsFlextRootModels",
    "TestsFlextRootProtocols",
    "TestsFlextRootResult",
    "TestsFlextRootTypes",
    "c",
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
    "tv",
    "u",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".constants": ("TestsFlextRootConstants",),
            ".models": ("TestsFlextRootModels",),
            ".protocols": ("TestsFlextRootProtocols",),
<<<<<<< HEAD
            ".result": ("TestsFlextRootResult",),
=======
            ".result": ("TestsFlextRootResult", "r"),
>>>>>>> origin/0.12.0-dev
            ".typings": ("TestsFlextRootTypes",),
            "flext_tests": (
                "c",
                "d",
                "e",
                "h",
                "m",
                "p",
<<<<<<< HEAD
                "r",
=======
>>>>>>> origin/0.12.0-dev
                "s",
                "t",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "u",
                "x",
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
