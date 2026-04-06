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
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from tests.infra import (
        TestsFlextInfraConstants,
        TestsFlextInfraConstants as c,
        TestsFlextTestModels,
        TestsFlextTestModels as m,
        TestsFlextTestProtocols,
        TestsFlextTestProtocols as p,
        TestsFlextTestTypes,
        TestsFlextTestTypes as t,
        TestsFlextTestUtilities,
        TestsFlextTestUtilities as u,
        constants,
        models,
        protocols,
        result,
        typings,
        utilities,
    )
    from tests.tf import tf
    from tests.tm import tm
    from tests.unit.libs import TestVersioning
    from tests.unit.scripts import TestSyncScripts
    from tests.unit.scripts.github import TestPrWorkspace
_LAZY_IMPORTS = merge_lazy_imports(
    ("tests.infra",),
    {
        "TestPrWorkspace": (
            "tests.unit.scripts.github.test_pr_workspace",
            "TestPrWorkspace",
        ),
        "TestSyncScripts": ("tests.unit.scripts.sync_tests", "TestSyncScripts"),
        "TestVersioning": ("tests.unit.libs.versioning_tests", "TestVersioning"),
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "infra": "tests.infra",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "tf": ("tests.tf", "tf"),
        "tm": ("tests.tm", "tm"),
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)
_ = _LAZY_IMPORTS.pop("cleanup_submodule_namespace", None)
_ = _LAZY_IMPORTS.pop("install_lazy_exports", None)
_ = _LAZY_IMPORTS.pop("lazy_getattr", None)
_ = _LAZY_IMPORTS.pop("merge_lazy_imports", None)
_ = _LAZY_IMPORTS.pop("output", None)
_ = _LAZY_IMPORTS.pop("output_reporting", None)

__all__ = [
    "TestPrWorkspace",
    "TestSyncScripts",
    "TestVersioning",
    "TestsFlextInfraConstants",
    "TestsFlextTestModels",
    "TestsFlextTestProtocols",
    "TestsFlextTestTypes",
    "TestsFlextTestUtilities",
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
