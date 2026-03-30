# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Scripts package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

from tests.unit.scripts.github import _LAZY_IMPORTS as _CHILD_LAZY_0

if TYPE_CHECKING:
    from tests.unit.scripts.github import *
    from tests.unit.scripts.sync_tests import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    **_CHILD_LAZY_0,
    "TestSyncScripts": "tests.unit.scripts.sync_tests",
    "github": "tests.unit.scripts.github",
    "sync_tests": "tests.unit.scripts.sync_tests",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
