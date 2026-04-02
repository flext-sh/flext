# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.service import FlextService as s
    from tests import infra, tf, tm
    from tests.infra import (
        FlextWorkspaceTestConstants,
        FlextWorkspaceTestModels,
        FlextWorkspaceTestProtocols,
        FlextWorkspaceTestTypes,
        FlextWorkspaceTestUtilities,
        c,
        constants,
        m,
        models,
        p,
        protocols,
        r,
        result,
        t,
        typings,
        u,
        utilities,
    )
    from tests.unit.libs import TestVersioning
    from tests.unit.scripts import TestSyncScripts
    from tests.unit.scripts.github import TestPrWorkspace

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
    ("tests.infra",),
    {
        "TestPrWorkspace": "tests.unit.scripts.github.test_pr_workspace",
        "TestSyncScripts": "tests.unit.scripts.sync_tests",
        "TestVersioning": "tests.unit.libs.versioning_tests",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "infra": "tests.infra",
        "s": ("flext_core.service", "FlextService"),
        "tf": "tests.tf",
        "tm": "tests.tm",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
