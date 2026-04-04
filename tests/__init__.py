# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _t.TYPE_CHECKING:
    import tests.infra as _tests_infra

    infra = _tests_infra
    import tests.tf as _tests_tf
    from tests.infra import (
        FlextWorkspaceTestConstants,
        FlextWorkspaceTestConstants as c,
        FlextWorkspaceTestModels,
        FlextWorkspaceTestModels as m,
        FlextWorkspaceTestProtocols,
        FlextWorkspaceTestProtocols as p,
        FlextWorkspaceTestTypes,
        FlextWorkspaceTestTypes as t,
        FlextWorkspaceTestUtilities,
        FlextWorkspaceTestUtilities as u,
        constants,
        models,
        protocols,
        result,
        typings,
        utilities,
    )

    tf = _tests_tf
    import tests.tm as _tests_tm

    tm = _tests_tm
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from tests.unit.libs import TestVersioning
    from tests.unit.scripts import TestSyncScripts
    from tests.unit.scripts.github import TestPrWorkspace
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
