# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Libs package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.unit.libs import versioning_tests as versioning_tests
    from tests.unit.libs.versioning_tests import TestVersioning as TestVersioning

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "TestVersioning": ["tests.unit.libs.versioning_tests", "TestVersioning"],
    "versioning_tests": ["tests.unit.libs.versioning_tests", ""],
}

_EXPORTS: Sequence[str] = [
    "TestVersioning",
    "versioning_tests",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
