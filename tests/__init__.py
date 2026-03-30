# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_tests import d, e, h, s, x

    from tests.infra import *
    from tests.unit.libs import *
    from tests.unit.scripts import *
    from tests.unit.scripts.github import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = merge_lazy_imports(
    ("tests.infra",),
    {
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
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
