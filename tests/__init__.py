# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import *

    from tests import tf, tm
    from tests.infra import *
    from tests.unit.libs.versioning_tests import *
    from tests.unit.scripts.github.test_pr_workspace import *
    from tests.unit.scripts.sync_tests import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextWorkspaceTestConstants": "tests.infra.constants",
    "FlextWorkspaceTestModels": "tests.infra.models",
    "FlextWorkspaceTestProtocols": "tests.infra.protocols",
    "FlextWorkspaceTestTypes": "tests.infra.typings",
    "FlextWorkspaceTestUtilities": "tests.infra.utilities",
    "TestPrWorkspace": "tests.unit.scripts.github.test_pr_workspace",
    "TestSyncScripts": "tests.unit.scripts.sync_tests",
    "TestVersioning": "tests.unit.libs.versioning_tests",
    "c": "tests.infra.constants",
    "constants": "tests.infra.constants",
    "d": "flext_tests",
    "e": "flext_tests",
    "h": "flext_tests",
    "infra": "tests.infra",
    "m": "tests.infra.models",
    "models": "tests.infra.models",
    "p": "tests.infra.protocols",
    "protocols": "tests.infra.protocols",
    "r": "tests.infra.result",
    "result": "tests.infra.result",
    "s": "flext_tests",
    "t": "tests.infra.typings",
    "tf": "tests.tf",
    "tm": "tests.tm",
    "typings": "tests.infra.typings",
    "u": "tests.infra.utilities",
    "utilities": "tests.infra.utilities",
    "x": "flext_tests",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
