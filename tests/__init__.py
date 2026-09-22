# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext import api, c, config, flext, m, main, p, s, settings, t, u
    from pydantic_core import from_json, to_json, to_jsonable_python

    from flext_core import core, d, e, h, lazy_attribute, r, x

    from . import infra, unit
__all__: tuple[str, ...] = (
    "api",
    "c",
    "config",
    "core",
    "d",
    "e",
    "flext",
    "from_json",
    "h",
    "infra",
    "lazy_attribute",
    "m",
    "main",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "to_json",
    "to_jsonable_python",
    "u",
    "unit",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".infra": ("infra",),
            ".unit": ("unit",),
            "flext": (
                "api",
                "c",
                "config",
                "flext",
                "m",
                "main",
                "p",
                "s",
                "settings",
                "t",
                "u",
            ),
            "flext_core": ("core", "d", "e", "h", "lazy_attribute", "r", "x"),
            "pydantic_core": ("from_json", "to_json", "to_jsonable_python"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
