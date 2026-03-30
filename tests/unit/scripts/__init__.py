# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Scripts package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.unit.scripts import sync_tests
    from tests.unit.scripts.github import *
    from tests.unit.scripts.sync_tests import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "TestPrWorkspace": "tests.unit.scripts.github.test_pr_workspace",
    "TestSyncScripts": "tests.unit.scripts.sync_tests",
    "github": "tests.unit.scripts.github",
    "sync_tests": "tests.unit.scripts.sync_tests",
    "test_pr_workspace": "tests.unit.scripts.github.test_pr_workspace",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
