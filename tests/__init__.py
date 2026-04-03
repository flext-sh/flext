# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext import (
        constants,
        infra,
        models,
        protocols,
        result,
        tf,
        tm,
        typings,
        utilities,
    )
    from flext.infra import (
        FlextWorkspaceTestConstants,
        FlextWorkspaceTestModels,
        FlextWorkspaceTestProtocols,
        FlextWorkspaceTestTypes,
        FlextWorkspaceTestUtilities,
        c,
        m,
        p,
        r,
        t,
        u,
    )
    from flext.unit.libs import (
        TestVersioning,
        encoding,
        name,
        python,
        test_current_workspace_version_reads_project_version,
        version,
    )
    from flext.unit.scripts import TestSyncScripts
    from flext.unit.scripts.github import TestPrWorkspace
    from flext_core import FlextTypes
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.service import FlextService as s

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
    ("flext.infra",),
    {
        "TestPrWorkspace": "flext.unit.scripts.github.test_pr_workspace",
        "TestSyncScripts": "flext.unit.scripts.sync_tests",
        "TestVersioning": "flext.unit.libs.versioning_tests",
        "constants": "flext.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "encoding": "flext.unit.libs.versioning_tests",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "infra": "flext.infra",
        "models": "flext.models",
        "name": "flext.unit.libs.versioning_tests",
        "protocols": "flext.protocols",
        "python": "flext.unit.libs.versioning_tests",
        "result": "flext.result",
        "s": ("flext_core.service", "FlextService"),
        "test_current_workspace_version_reads_project_version": "flext.unit.libs.versioning_tests",
        "tf": "flext.tf",
        "tm": "flext.tm",
        "typings": "flext.typings",
        "utilities": "flext.utilities",
        "version": "flext.unit.libs.versioning_tests",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
