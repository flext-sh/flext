"""Test models and assertions module for workspace tests.

Provides tm alias for test assertions and models with namespace pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import p, r


class TestModels:
    """Test models and assertion helpers."""

    @staticmethod
    def ok[TResult](result: p.Result[TResult]) -> None:
        """Assert result is success."""
        if result.failure:
            msg = f"Expected success but got failure: {result.exception}"
            raise AssertionError(msg)

    @staticmethod
    def fail[TResult](result: p.Result[TResult], has: str | None = None) -> None:
        """Assert result is failure, optionally checking error message."""
        if r.successful_result(result):
            msg = "Expected failure but got success"
            raise AssertionError(msg)
        if has and has not in str(result.exception):
            msg = f"Expected error to contain '{has}' but got: {result.exception}"
            raise AssertionError(msg)

    @staticmethod
    def that[TValue](value: TValue, eq: TValue | None = None) -> None:
        """Assert value equals expected."""
        if eq is not None and value != eq:
            msg = f"Expected {eq} but got {value}"
            raise AssertionError(msg)


tm = TestModels
__all__: list[str] = ["tm"]
