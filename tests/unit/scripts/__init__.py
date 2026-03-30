# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Scripts package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.unit.scripts import github as github, sync_tests as sync_tests
    from tests.unit.scripts.github import test_pr_workspace as test_pr_workspace
    from tests.unit.scripts.github.test_pr_workspace import (
        TestPrWorkspace as TestPrWorkspace,
    )
    from tests.unit.scripts.sync_tests import TestSyncScripts as TestSyncScripts

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "TestPrWorkspace": [
        "tests.unit.scripts.github.test_pr_workspace",
        "TestPrWorkspace",
    ],
    "TestSyncScripts": ["tests.unit.scripts.sync_tests", "TestSyncScripts"],
    "github": ["tests.unit.scripts.github", ""],
    "sync_tests": ["tests.unit.scripts.sync_tests", ""],
    "test_pr_workspace": ["tests.unit.scripts.github.test_pr_workspace", ""],
}

_EXPORTS: Sequence[str] = [
    "TestPrWorkspace",
    "TestSyncScripts",
    "github",
    "sync_tests",
    "test_pr_workspace",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
