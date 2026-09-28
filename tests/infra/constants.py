"""FLEXT infra test helpers for constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final

from flext_infra import c
from flext_tests import FlextTestsConstants


class TestsFlextRootConstants(c):
    """Infrastructure test constants facade — extends flext_infra constants."""

    class _RootWorkspaceConstants:
        """Root workspace test-infrastructure constants."""

        MODULE_VERSIONING: Final[str] = "libs/versioning.py"
        DEFAULT_BRANCH: Final[str] = "main"

    class TestsFlextRoot(FlextTestsConstants.Tests, _RootWorkspaceConstants):
        """Test infrastructure constants composing shared test + workspace parts."""


__all__: list[str] = ["TestsFlextRootConstants"]
