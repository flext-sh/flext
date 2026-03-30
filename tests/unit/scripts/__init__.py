# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Scripts package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.unit.scripts import github, sync_tests
    from tests.unit.scripts.github import test_pr_workspace
    from tests.unit.scripts.github.test_pr_workspace import *
    from tests.unit.scripts.sync_tests import *

from tests.unit.scripts.github import _LAZY_IMPORTS as _GITHUB_LAZY

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    **_GITHUB_LAZY,
    "TestSyncScripts": "tests.unit.scripts.sync_tests",
    "github": "tests.unit.scripts.github",
    "sync_tests": "tests.unit.scripts.sync_tests",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
