"""FLEXT infra test helpers for constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import c as c_tests

from typing import Final


class TestsFlextRootConstants(c_tests):
    """Infrastructure test constants facade — extends flext_tests constants."""

    class TestsFlextRoot:
        """Infrastructure test path constants."""

        class Workspace:
            """Workspace-level test constants."""

            MODULE_VERSIONING: Final[str] = "libs/versioning.py"


__all__: list[str] = ["TestsFlextRootConstants"]

