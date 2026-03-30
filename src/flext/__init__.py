# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_core import d, e, h, r, x

    from flext import (
        constants as constants,
        dev as dev,
        docs as docs,
        models as models,
        protocols as protocols,
        service as service,
        typings as typings,
        utilities as utilities,
        workspace as workspace,
    )
    from flext.constants import (
        FlextRootConstants as FlextRootConstants,
        FlextRootConstants as c,
    )
    from flext.models import FlextRootModels as FlextRootModels, FlextRootModels as m
    from flext.protocols import (
        FlextRootProtocols as FlextRootProtocols,
        FlextRootProtocols as p,
    )
    from flext.service import FlextRootServiceBase as FlextRootServiceBase, s as s
    from flext.typings import FlexRootTypes as FlexRootTypes, FlexRootTypes as t
    from flext.utilities import (
        FlextRootUtilities as FlextRootUtilities,
        FlextRootUtilities as u,
    )
    from flext.workspace import main as main

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlexRootTypes": ["flext.typings", "FlexRootTypes"],
    "FlextRootConstants": ["flext.constants", "FlextRootConstants"],
    "FlextRootModels": ["flext.models", "FlextRootModels"],
    "FlextRootProtocols": ["flext.protocols", "FlextRootProtocols"],
    "FlextRootServiceBase": ["flext.service", "FlextRootServiceBase"],
    "FlextRootUtilities": ["flext.utilities", "FlextRootUtilities"],
    "c": ["flext.constants", "FlextRootConstants"],
    "constants": ["flext.constants", ""],
    "d": ["flext_core", "d"],
    "dev": ["flext.dev", ""],
    "docs": ["flext.docs", ""],
    "e": ["flext_core", "e"],
    "h": ["flext_core", "h"],
    "m": ["flext.models", "FlextRootModels"],
    "main": ["flext.workspace", "main"],
    "models": ["flext.models", ""],
    "p": ["flext.protocols", "FlextRootProtocols"],
    "protocols": ["flext.protocols", ""],
    "r": ["flext_core", "r"],
    "s": ["flext.service", "s"],
    "service": ["flext.service", ""],
    "t": ["flext.typings", "FlexRootTypes"],
    "typings": ["flext.typings", ""],
    "u": ["flext.utilities", "FlextRootUtilities"],
    "utilities": ["flext.utilities", ""],
    "workspace": ["flext.workspace", ""],
    "x": ["flext_core", "x"],
}

_EXPORTS: Sequence[str] = [
    "FlexRootTypes",
    "FlextRootConstants",
    "FlextRootModels",
    "FlextRootProtocols",
    "FlextRootServiceBase",
    "FlextRootUtilities",
    "c",
    "constants",
    "d",
    "dev",
    "docs",
    "e",
    "h",
    "m",
    "main",
    "models",
    "p",
    "protocols",
    "r",
    "s",
    "service",
    "t",
    "typings",
    "u",
    "utilities",
    "workspace",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
