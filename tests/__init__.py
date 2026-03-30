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

    from tests import infra, tf, tm
    from tests.infra import constants, models, protocols, result, typings, utilities
    from tests.infra.constants import *
    from tests.infra.models import *
    from tests.infra.protocols import *
    from tests.infra.result import *
    from tests.infra.typings import *
    from tests.infra.utilities import *
    from tests.unit.libs.versioning_tests import *
    from tests.unit.scripts.github.test_pr_workspace import *
    from tests.unit.scripts.sync_tests import *

from tests.infra import _LAZY_IMPORTS as _INFRA_LAZY

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    **_INFRA_LAZY,
    "TestPrWorkspace": "tests.unit.scripts.github.test_pr_workspace",
    "TestSyncScripts": "tests.unit.scripts.sync_tests",
    "TestVersioning": "tests.unit.libs.versioning_tests",
    "d": "flext_tests",
    "e": "flext_tests",
    "h": "flext_tests",
    "infra": "tests.infra",
    "s": "flext_tests",
    "tf": "tests.tf",
    "tm": "tests.tm",
    "x": "flext_tests",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
