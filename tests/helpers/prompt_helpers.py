"""Generic helpers for CLI prompt testing.

Provides reusable helper methods that reduce test code significantly.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TypeVar

from flext_cli import FlextCliPrompts
from flext_core import FlextResult
from flext_tests import u

from tests.fixtures.constants import TestConstants

T = TypeVar("T")


class PromptTestHelpers:
    """Generic helpers for testing FlextCliPrompts.

    Reduces test code by providing reusable methods for common testing patterns.
    """

    @staticmethod
    def create_quiet_prompt() -> FlextCliPrompts:
        """Create a quiet mode prompt instance."""
        return FlextCliPrompts(quiet=True)

    @staticmethod
    def create_interactive_prompt() -> FlextCliPrompts:
        """Create an interactive mode prompt instance."""
        return FlextCliPrompts(interactive_mode=True, quiet=False)

    @staticmethod
    def create_non_interactive_prompt() -> FlextCliPrompts:
        """Create a non-interactive mode prompt instance."""
        return FlextCliPrompts(interactive_mode=False)

    @classmethod
    def test_quiet_mode_behavior(
        cls,
        method_name: str,
        *args: object,
        expected_result: object = None,
        **kwargs: object,
    ) -> dict[str, object]:
        """Test quiet mode behavior for any prompt method.

        Reduces 5+ lines per test by handling the common pattern.
        """
        prompt = cls.create_quiet_prompt()
        method = getattr(prompt, method_name)
        result = method(*args, **kwargs)

        # Assertions
        assert result.is_success, f"Expected success in quiet mode for {method_name}"
        if expected_result is not None:
            assert result.value == expected_result, (
                f"Unexpected result for {method_name}"
            )

        return {
            "prompt": prompt,
            "result": result,
            "method_name": method_name,
            "args": args,
            "kwargs": kwargs,
        }

    @classmethod
    def test_interactive_mode_setup(cls) -> FlextCliPrompts:
        """Setup interactive mode prompt with proper configuration."""
        prompt = cls.create_interactive_prompt()
        assert prompt.interactive_mode is True
        assert prompt.quiet is False
        return prompt

    @classmethod
    def test_non_interactive_defaults(
        cls,
        method_name: str,
        *args: object,
        expected_default: object,
        **kwargs: object,
    ) -> dict[str, object]:
        """Test non-interactive mode returns expected defaults.

        Reduces 3-4 lines per test.
        """
        prompt = cls.create_non_interactive_prompt()
        method = getattr(prompt, method_name)
        result = method(*args, **kwargs)

        assert result.is_success, f"Non-interactive {method_name} should succeed"
        assert result.value == expected_default, (
            f"Expected default {expected_default}"
        )

        return {
            "prompt": prompt,
            "result": result,
            "method_name": method_name,
        }

    @classmethod
    def parametrize_status_tests(cls) -> list[tuple[str, bool]]:
        """Parametrize status printing tests."""
        return TestConstants.get_status_test_cases()

    @classmethod
    def parametrize_progress_tests(cls) -> list[tuple[str, object]]:
        """Parametrize progress creation tests."""
        return TestConstants.get_progress_test_cases()

    @classmethod
    def test_result_assertions(
        cls,
        result: FlextResult[T],
        *,
        expected_success: bool = True,
        expected_data: T | None = None,
        expected_error_contains: str | None = None,
    ) -> None:
        """Generic result assertions reducing 3-5 lines per test."""
        if expected_success:
            u.Tests.Result.assert_success(result)
            if expected_data is not None:
                assert result.value == expected_data
        else:
            u.Tests.Result.assert_failure(result)
            if expected_error_contains:
                assert result.error is not None
                assert expected_error_contains in result.error

    @classmethod
    def create_test_prompt_with_history(
        cls,
        history_items: list[str],
    ) -> FlextCliPrompts:
        """Create prompt with pre-populated history."""
        prompt = cls.create_interactive_prompt()
        prompt._prompt_history.extend(history_items)
        return prompt

    @classmethod
    def assert_prompt_history_contains(
        cls,
        prompt: FlextCliPrompts,
        expected_items: list[str],
    ) -> None:
        """Assert prompt history contains expected items."""
        history = prompt.prompt_history
        for item in expected_items:
            assert item in history, f"Expected '{item}' in history: {history}"

    @classmethod
    def test_method_with_exception(
        cls,
        method_name: str,
        exception_class: type[Exception],
        exception_message: str,
        *args: object,
        **kwargs: object,
    ) -> dict[str, object]:
        """Test method raises expected exception.

        Reduces exception testing boilerplate.
        """
        prompt = cls.create_interactive_prompt()
        method = getattr(prompt, method_name)

        # Test method directly - methods handle exceptions internally
        # and return FlextResult with error information
        result = method(*args, **kwargs)

        # Methods should handle exceptions and return failure result
        # If method doesn't handle exception, it will propagate (test will fail)
        assert result.is_failure, f"Expected failure for {method_name} with exception"
        assert result.error is not None
        assert (
            exception_message in result.error
            or exception_class.__name__ in result.error
        )

        return {
            "prompt": prompt,
            "result": result,
            "exception_class": exception_class,
            "exception_message": exception_message,
        }

    @classmethod
    def bulk_test_quiet_mode_methods(
        cls, method_configs: list[dict[str, object]]
    ) -> list[dict[str, object]]:
        """Bulk test multiple methods in quiet mode.

        Significantly reduces code for testing multiple similar methods.
        """
        results = []
        for config in method_configs:
            method_name = str(config["method_name"])
            expected = config.get("expected_result")
            args_raw = config.get("args", ())
            kwargs_raw = config.get("kwargs", {})

            # Ensure args is a tuple for unpacking
            if not isinstance(args_raw, (list, tuple)):
                args = (args_raw,)
            else:
                args = tuple(args_raw) if isinstance(args_raw, list) else args_raw

            # Ensure kwargs is a dict
            kwargs: dict[str, object] = {}
            if isinstance(kwargs_raw, dict):
                kwargs = kwargs_raw

            result = cls.test_quiet_mode_behavior(
                method_name,
                *args,
                expected_result=expected,
                **kwargs,
            )
            results.append(result)

        return results

    @classmethod
    def generate_edge_case_tests(cls) -> list[dict[str, object]]:
        """Generate comprehensive edge case test configurations."""
        return [
            {
                "name": "empty_message",
                "message": TestConstants.CliPrompts.EMPTY_MESSAGE,
                "default": TestConstants.CliPrompts.DEFAULT_EMPTY,
            },
            {
                "name": "long_message",
                "message": TestConstants.CliPrompts.LONG_MESSAGE,
                "default": TestConstants.CliPrompts.DEFAULT_STRING,
            },
            {
                "name": "unicode_message",
                "message": TestConstants.EdgeCases.UNICODE_MESSAGE,
                "default": TestConstants.CliPrompts.DEFAULT_STRING,
            },
            {
                "name": "special_chars",
                "message": TestConstants.EdgeCases.SPECIAL_CHARS,
                "default": TestConstants.CliPrompts.DEFAULT_EMPTY,
            },
        ]
