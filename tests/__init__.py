# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

from tests.infra import _LAZY_IMPORTS as _CHILD_LAZY_0

if TYPE_CHECKING:
    from tests.infra import *
    from tests.unit.libs import *
    from tests.unit.scripts import *
    from tests.unit.scripts.github import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    **_CHILD_LAZY_0,
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
