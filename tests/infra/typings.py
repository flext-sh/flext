"""FLEXT infra test helpers for typings.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext import FlextRootTypes

if TYPE_CHECKING:
    import pytest
from flext_tests import FlextTestsTypes


class TestsFlextRootTypes(FlextRootTypes):
    """Infrastructure test typings facade — extends flext_infra typings."""

    class Tests(FlextTestsTypes.Tests):
        """Test typings composing shared test + workspace type namespaces."""

        type CapturedOutput = pytest.CaptureFixture[str]


t = TestsFlextRootTypes
__all__: list[str] = ["TestsFlextRootTypes", "t"]
