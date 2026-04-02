# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Infra package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.service import FlextService as s
    from tests.infra import constants, models, protocols, result, typings, utilities
    from tests.infra.constants import FlextWorkspaceTestConstants, c
    from tests.infra.models import FlextWorkspaceTestModels, m
    from tests.infra.protocols import FlextWorkspaceTestProtocols, p
    from tests.infra.result import r
    from tests.infra.typings import FlextWorkspaceTestTypes, t
    from tests.infra.utilities import FlextWorkspaceTestUtilities, u

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlextWorkspaceTestConstants": "tests.infra.constants",
    "FlextWorkspaceTestModels": "tests.infra.models",
    "FlextWorkspaceTestProtocols": "tests.infra.protocols",
    "FlextWorkspaceTestTypes": "tests.infra.typings",
    "FlextWorkspaceTestUtilities": "tests.infra.utilities",
    "c": "tests.infra.constants",
    "constants": "tests.infra.constants",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": "tests.infra.models",
    "models": "tests.infra.models",
    "p": "tests.infra.protocols",
    "protocols": "tests.infra.protocols",
    "r": "tests.infra.result",
    "result": "tests.infra.result",
    "s": ("flext_core.service", "FlextService"),
    "t": "tests.infra.typings",
    "typings": "tests.infra.typings",
    "u": "tests.infra.utilities",
    "utilities": "tests.infra.utilities",
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
