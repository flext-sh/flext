# Copyright (c) 2026 FLEXT Team. All rights reserved.

"""Service base for flext-workspace tests."""

from __future__ import annotations

from flext_tests import FlextTestsServiceBase


class TestsFlextRootServiceBase(FlextTestsServiceBase):
    """Workspace root test service base."""


s = TestsFlextRootServiceBase

__all__: list[str] = ["TestsFlextRootServiceBase", "s"]
