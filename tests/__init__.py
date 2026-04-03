# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.decorators import FlextDecorators as d
from flext_core.exceptions import FlextExceptions as e
from flext_core.handlers import FlextHandlers as h
from flext_core.lazy import install_lazy_exports, merge_lazy_imports
from flext_core.mixins import FlextMixins as x
from flext_core.result import FlextResult as r
from flext_core.service import FlextService as s
from tests.infra.constants import (
    FlextWorkspaceTestConstants,
    FlextWorkspaceTestConstants as c,
)
from tests.infra.models import (
    FlextWorkspaceTestModels,
    FlextWorkspaceTestModels as m,
)
from tests.infra.protocols import (
    FlextWorkspaceTestProtocols,
    FlextWorkspaceTestProtocols as p,
)
from tests.infra.typings import (
    FlextWorkspaceTestTypes,
    FlextWorkspaceTestTypes as t,
)
from tests.infra.utilities import (
    FlextWorkspaceTestUtilities,
    FlextWorkspaceTestUtilities as u,
)
from tests.unit.libs.versioning_tests import TestVersioning
from tests.unit.scripts.github.test_pr_workspace import TestPrWorkspace
from tests.unit.scripts.sync_tests import TestSyncScripts

if _t.TYPE_CHECKING:
    import tests.infra as _tests_infra

    infra = _tests_infra
    import tests.infra.constants as _tests_infra_constants

    constants = _tests_infra_constants
    import tests.infra.models as _tests_infra_models

    models = _tests_infra_models
    import tests.infra.protocols as _tests_infra_protocols

    protocols = _tests_infra_protocols
    import tests.infra.result as _tests_infra_result

    result = _tests_infra_result
    import tests.infra.typings as _tests_infra_typings

    typings = _tests_infra_typings
    import tests.infra.utilities as _tests_infra_utilities

    utilities = _tests_infra_utilities
    import tests.tf as _tests_tf

    tf = _tests_tf
    import tests.tm as _tests_tm

    tm = _tests_tm

    _ = (
        FlextWorkspaceTestConstants,
        FlextWorkspaceTestModels,
        FlextWorkspaceTestProtocols,
        FlextWorkspaceTestTypes,
        FlextWorkspaceTestUtilities,
        TestPrWorkspace,
        TestSyncScripts,
        TestVersioning,
        c,
        constants,
        d,
        e,
        h,
        infra,
        m,
        models,
        p,
        protocols,
        r,
        result,
        s,
        t,
        tf,
        tm,
        typings,
        u,
        utilities,
        x,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    ("tests.infra",),
    {
        "TestPrWorkspace": "tests.unit.scripts.github.test_pr_workspace",
        "TestSyncScripts": "tests.unit.scripts.sync_tests",
        "TestVersioning": "tests.unit.libs.versioning_tests",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "infra": "tests.infra",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "tf": "tests.tf",
        "tm": "tests.tm",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)

__all__ = [
    "FlextWorkspaceTestConstants",
    "FlextWorkspaceTestModels",
    "FlextWorkspaceTestProtocols",
    "FlextWorkspaceTestTypes",
    "FlextWorkspaceTestUtilities",
    "TestPrWorkspace",
    "TestSyncScripts",
    "TestVersioning",
    "c",
    "constants",
    "d",
    "e",
    "h",
    "infra",
    "m",
    "models",
    "p",
    "protocols",
    "r",
    "result",
    "s",
    "t",
    "tf",
    "tm",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
