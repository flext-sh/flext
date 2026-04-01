# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Scripts package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_core import FlextTypes

    from tests.unit.scripts import github, sync_tests
    from tests.unit.scripts.github import TestPrWorkspace, test_pr_workspace
    from tests.unit.scripts.sync_tests import TestSyncScripts

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = merge_lazy_imports(
    ("tests.unit.scripts.github",),
    {
        "TestSyncScripts": "tests.unit.scripts.sync_tests",
        "github": "tests.unit.scripts.github",
        "sync_tests": "tests.unit.scripts.sync_tests",
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
