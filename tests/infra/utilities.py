"""FLEXT infra test helpers for utiltiies.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext import u
from flext_tests import FlextTestsTypes


class TestsFlextRootUtilities(u):
    """Infrastructure test typings facade — extends flext_infra typings."""

    class Tests(FlextTestsTypes.Tests):
        """Test typings composing shared test + workspace type namespaces."""


u = TestsFlextRootUtilities

__all__: list[str] = ["TestsFlextRootUtilities", "u"]
