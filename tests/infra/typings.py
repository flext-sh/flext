"""FLEXT infra test helpers for typings.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsTypes
from tests import t


class TestsFlextRootTypes(t):
    """Infrastructure test typings facade — extends flext_infra typings."""

    class Tests(FlextTestsTypes.Tests):
        """Test typings composing shared test + workspace type namespaces."""


__all__: list[str] = ["TestsFlextRootTypes"]
