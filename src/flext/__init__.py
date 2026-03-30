# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext.constants import *
    from flext.models import *
    from flext.protocols import *
    from flext.service import *
    from flext.typings import *
    from flext.utilities import *
    from flext.workspace import *


_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlexRootTypes": "flext.typings",
    "FlextRootConstants": "flext.constants",
    "FlextRootModels": "flext.models",
    "FlextRootProtocols": "flext.protocols",
    "FlextRootServiceBase": "flext.service",
    "FlextRootUtilities": "flext.utilities",
    "c": ["flext.constants", "FlextRootConstants"],
    "constants": "flext.constants",
    "d": "flext_core",
    "dev": "flext.dev",
    "docs": "flext.docs",
    "e": "flext_core",
    "h": "flext_core",
    "m": ["flext.models", "FlextRootModels"],
    "main": "flext.workspace",
    "models": "flext.models",
    "p": ["flext.protocols", "FlextRootProtocols"],
    "protocols": "flext.protocols",
    "r": "flext_core",
    "s": "flext.service",
    "service": "flext.service",
    "t": ["flext.typings", "FlexRootTypes"],
    "typings": "flext.typings",
    "u": ["flext.utilities", "FlextRootUtilities"],
    "utilities": "flext.utilities",
    "workspace": "flext.workspace",
    "x": "flext_core",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
