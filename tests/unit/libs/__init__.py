# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Libs package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes

    from tests.unit.libs import versioning_tests
    from tests.unit.libs.versioning_tests import TestVersioning

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "TestVersioning": "tests.unit.libs.versioning_tests",
    "versioning_tests": "tests.unit.libs.versioning_tests",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
