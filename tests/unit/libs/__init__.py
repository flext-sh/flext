# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Libs package."""

from __future__ import annotations

import typing as _t
from collections.abc import (
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import tests.unit.libs.versioning_tests as _tests_unit_libs_versioning_tests

    versioning_tests = _tests_unit_libs_versioning_tests
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
    from tests.unit.libs.versioning_tests import TestVersioning
_LAZY_IMPORTS = {
    "TestVersioning": ("tests.unit.libs.versioning_tests", "TestVersioning"),
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "u": ("flext_core.utilities", "FlextUtilities"),
    "versioning_tests": "tests.unit.libs.versioning_tests",
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__: list[str] = [
    "TestVersioning",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "versioning_tests",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
