# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Infra package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import d, e, h, s, x

    from tests.infra import (
        constants as constants,
        models as models,
        protocols as protocols,
        result as result,
        typings as typings,
        utilities as utilities,
    )
    from tests.infra.constants import (
        FlextWorkspaceTestConstants as FlextWorkspaceTestConstants,
        c as c,
    )
    from tests.infra.models import (
        FlextWorkspaceTestModels as FlextWorkspaceTestModels,
        m as m,
    )
    from tests.infra.protocols import (
        FlextWorkspaceTestProtocols as FlextWorkspaceTestProtocols,
        p as p,
    )
    from tests.infra.result import r as r
    from tests.infra.typings import (
        FlextWorkspaceTestTypes as FlextWorkspaceTestTypes,
        t as t,
    )
    from tests.infra.utilities import (
        FlextWorkspaceTestUtilities as FlextWorkspaceTestUtilities,
        u as u,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextWorkspaceTestConstants": ["tests.infra.constants", "FlextWorkspaceTestConstants"],
    "FlextWorkspaceTestModels": ["tests.infra.models", "FlextWorkspaceTestModels"],
    "FlextWorkspaceTestProtocols": ["tests.infra.protocols", "FlextWorkspaceTestProtocols"],
    "FlextWorkspaceTestTypes": ["tests.infra.typings", "FlextWorkspaceTestTypes"],
    "FlextWorkspaceTestUtilities": ["tests.infra.utilities", "FlextWorkspaceTestUtilities"],
    "c": ["tests.infra.constants", "c"],
    "constants": ["tests.infra.constants", ""],
    "d": ["flext_tests", "d"],
    "e": ["flext_tests", "e"],
    "h": ["flext_tests", "h"],
    "m": ["tests.infra.models", "m"],
    "models": ["tests.infra.models", ""],
    "p": ["tests.infra.protocols", "p"],
    "protocols": ["tests.infra.protocols", ""],
    "r": ["tests.infra.result", "r"],
    "result": ["tests.infra.result", ""],
    "s": ["flext_tests", "s"],
    "t": ["tests.infra.typings", "t"],
    "typings": ["tests.infra.typings", ""],
    "u": ["tests.infra.utilities", "u"],
    "utilities": ["tests.infra.utilities", ""],
    "x": ["flext_tests", "x"],
}

_EXPORTS: Sequence[str] = [
    "FlextWorkspaceTestConstants",
    "FlextWorkspaceTestModels",
    "FlextWorkspaceTestProtocols",
    "FlextWorkspaceTestTypes",
    "FlextWorkspaceTestUtilities",
    "c",
    "constants",
    "d",
    "e",
    "h",
    "m",
    "models",
    "p",
    "protocols",
    "r",
    "result",
    "s",
    "t",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
