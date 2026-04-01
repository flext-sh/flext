# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Infra package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_tests import d, e, h, s, x

    from tests.infra.constants import *
    from tests.infra.models import *
    from tests.infra.protocols import *
    from tests.infra.result import *
    from tests.infra.typings import *
    from tests.infra.utilities import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextWorkspaceTestConstants": "tests.infra.constants",
    "FlextWorkspaceTestModels": "tests.infra.models",
    "FlextWorkspaceTestProtocols": "tests.infra.protocols",
    "FlextWorkspaceTestTypes": "tests.infra.typings",
    "FlextWorkspaceTestUtilities": "tests.infra.utilities",
    "c": "tests.infra.constants",
    "constants": "tests.infra.constants",
    "d": "flext_tests",
    "e": "flext_tests",
    "h": "flext_tests",
    "m": "tests.infra.models",
    "models": "tests.infra.models",
    "p": "tests.infra.protocols",
    "protocols": "tests.infra.protocols",
    "r": "tests.infra.result",
    "result": "tests.infra.result",
    "s": "flext_tests",
    "t": "tests.infra.typings",
    "typings": "tests.infra.typings",
    "u": "tests.infra.utilities",
    "utilities": "tests.infra.utilities",
    "x": "flext_tests",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
