"""FLEXT infra test helpers for constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext import c
from flext_tests import FlextTestsConstants


class TestsFlextRootConstants(c):
    """Infrastructure test constants facade — extends flext_infra constants."""

    class Tests(FlextTestsConstants.Tests):
        """Test infrastructure constants composing shared test + workspace parts."""

        MODULE_VERSIONING: ClassVar[str] = "libs/versioning.py"
        DEFAULT_BRANCH: ClassVar[str] = "main"


__all__: list[str] = ["TestsFlextRootConstants"]
