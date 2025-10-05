"""Test matchers and assertions for FLEXT ecosystem.

Provides custom pytest matchers and assertion helpers.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Any

from flext_core import FlextResult


class FlextTestsMatchers:
    """Custom test matchers for FLEXT ecosystem.

    Provides pytest-compatible matchers for common FLEXT patterns.
    """

    @staticmethod
    def assert_result_success(
        result: FlextResult[Any],
        message: str | None = None,
    ) -> None:
        """Assert that a FlextResult is successful.

        Args:
            result: FlextResult to check
            message: Custom error message

        Raises:
            AssertionError: If result is not successful

        """
        assert result.is_success, message or f"Expected success result, got: {result}"

    @staticmethod
    def assert_result_failure(
        result: FlextResult[Any],
        expected_error: str | None = None,
        message: str | None = None,
    ) -> None:
        """Assert that a FlextResult is a failure.

        Args:
            result: FlextResult to check
            expected_error: Expected error message substring
            message: Custom error message

        Raises:
            AssertionError: If result is not a failure or error doesn't match

        """
        assert result.is_failure, message or f"Expected failure result, got: {result}"

        if expected_error:
            error_str = str(result.error) if result.error else ""
            assert expected_error in error_str, (
                f"Expected error containing '{expected_error}', got: '{error_str}'"
            )

    @staticmethod
    def assert_dict_contains(
        data: dict[str, Any],
        expected: dict[str, Any],
        message: str | None = None,
    ) -> None:
        """Assert that a dictionary contains expected key-value pairs.

        Args:
            data: Dictionary to check
            expected: Expected key-value pairs
            message: Custom error message

        Raises:
            AssertionError: If dictionary doesn't contain expected pairs

        """
        for key, expected_value in expected.items():
            assert key in data, message or f"Key '{key}' not found in data"
            assert data[key] == expected_value, (
                message or f"Key '{key}': expected {expected_value}, got {data[key]}"
            )

    @staticmethod
    def assert_list_contains(
        items: list[Any],
        expected_item: Any,
        message: str | None = None,
    ) -> None:
        """Assert that a list contains an expected item.

        Args:
            items: List to check
            expected_item: Item that should be in the list
            message: Custom error message

        Raises:
            AssertionError: If item is not in the list

        """
        assert expected_item in items, (
            message or f"Expected item '{expected_item}' not found in list"
        )

    @staticmethod
    def assert_valid_email(email: str, message: str | None = None) -> None:
        """Assert that a string is a valid email format.

        Args:
            email: Email string to validate
            message: Custom error message

        Raises:
            AssertionError: If email format is invalid

        """
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        assert re.match(email_pattern, email), (
            message or f"Invalid email format: '{email}'"
        )

    @staticmethod
    def assert_config_valid(config: dict[str, Any], message: str | None = None) -> None:
        """Assert that a configuration dictionary is valid.

        Args:
            config: Configuration dictionary to validate
            message: Custom error message

        Raises:
            AssertionError: If configuration is invalid

        """
        required_keys = ["service_type", "environment"]
        for key in required_keys:
            assert key in config, message or f"Required config key '{key}' missing"

        assert config.get("timeout", 0) > 0, (
            message or "Config timeout must be positive"
        )
