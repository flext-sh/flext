# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Scripts package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _t.TYPE_CHECKING:
    import tests.unit.scripts.github as _tests_unit_scripts_github

    github = _tests_unit_scripts_github
    import tests.unit.scripts.sync_tests as _tests_unit_scripts_sync_tests
    from tests.unit.scripts.github import TestPrWorkspace, test_pr_workspace

    sync_tests = _tests_unit_scripts_sync_tests
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
    from tests.unit.scripts.sync_tests import TestSyncScripts
_LAZY_IMPORTS = merge_lazy_imports(
    ("tests.unit.scripts.github",),
    {
        "TestSyncScripts": "tests.unit.scripts.sync_tests",
        "c": ("flext_core.constants", "FlextConstants"),
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "github": "tests.unit.scripts.github",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "m": ("flext_core.models", "FlextModels"),
        "p": ("flext_core.protocols", "FlextProtocols"),
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "sync_tests": "tests.unit.scripts.sync_tests",
        "t": ("flext_core.typings", "FlextTypes"),
        "u": ("flext_core.utilities", "FlextUtilities"),
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)

__all__ = [
    "TestPrWorkspace",
    "TestSyncScripts",
    "c",
    "d",
    "e",
    "github",
    "h",
    "m",
    "p",
    "r",
    "s",
    "sync_tests",
    "t",
    "test_pr_workspace",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
