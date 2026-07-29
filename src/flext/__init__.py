# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from flext.constants import FlextRootConstants, c
    from flext.models import FlextRootModels, m
    from flext.protocols import FlextRootProtocols, p
    from flext.typings import FlextRootTypes, t
    from flext.utilities import FlextRootUtilities, u
    from flext_core import d, e, h, r, x
_LAZY_IMPORTS = build_lazy_import_map({
    ".constants": ("FlextRootConstants", "c"),
    ".models": ("FlextRootModels", "m"),
    ".protocols": ("FlextRootProtocols", "p"),
    ".typings": ("FlextRootTypes", "t"),
    ".utilities": ("FlextRootUtilities", "u"),
    "flext_core": ("d", "e", "h", "r", "x"),
})


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "FlextRootConstants",
    "FlextRootModels",
    "FlextRootProtocols",
    "FlextRootTypes",
    "FlextRootUtilities",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "t",
    "u",
    "x",
]
