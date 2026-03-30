# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Github package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.unit.scripts.github import test_pr_workspace as test_pr_workspace
    from tests.unit.scripts.github.test_pr_workspace import (
        TestPrWorkspace as TestPrWorkspace,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "TestPrWorkspace": [
        "tests.unit.scripts.github.test_pr_workspace",
        "TestPrWorkspace",
    ],
    "test_pr_workspace": ["tests.unit.scripts.github.test_pr_workspace", ""],
}

_EXPORTS: Sequence[str] = [
    "TestPrWorkspace",
    "test_pr_workspace",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
