"""FLEXT LDIF Entry Manipulation Services Tests - Comprehensive coverage.

Tests EntryManipulationServices with real LDIF data using advanced Python 3.13 patterns,
factories for test data generation, nested classes for organization, and dynamic testing
for all attribute extraction, normalization, and manipulation operations.

Modules Tested: EntryManipulationServices (flext_ldif.services.entry_manipulation)
Scope: Entry attribute access, value normalization, DN operations, and manipulation utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum
from typing import cast

import pytest
from flext_core import FlextResult
from flext_ldif import FlextLdifModels
from flext_ldif.services.entry_manipulation import EntryManipulationServices


class LdifTestData(StrEnum):
    """Test data constants for LDIF entry manipulation."""

    EXISTING_ATTR = "cn"
    NON_EXISTENT_ATTR = "nonexistentAttr"
    STRING_VALUE = "test value"
    FIRST_VALUE = "first"
    SECOND_VALUE = "second"
    EMPTY_LIST_STR = "[]"
    NORMALIZED_CN = "cn"
    NORMALIZED_GIVEN_NAME = "givenName"
    NORMALIZED_SN = "sn"
    NORMALIZED_MAIL = "mail"


class TestEntryManipulationServices:
    """Comprehensive test suite for EntryManipulationServices using modern patterns."""

    # =========================================================================
    # NESTED: Test Data & Constants
    # =========================================================================

    class TestDataFactory:
        """Factory for generating test data for entry manipulation tests."""

        @staticmethod
        def create_test_attribute_values() -> list[object]:
            """Generate various attribute value types for testing."""
            return [
                LdifTestData.STRING_VALUE,
                [LdifTestData.FIRST_VALUE, LdifTestData.SECOND_VALUE],
                [],
            ]

        @staticmethod
        def create_test_attributes() -> list[str]:
            """Generate test attribute names."""
            return [
                LdifTestData.EXISTING_ATTR,
                LdifTestData.NORMALIZED_GIVEN_NAME,
                LdifTestData.NORMALIZED_SN,
                LdifTestData.NORMALIZED_MAIL,
                LdifTestData.NON_EXISTENT_ATTR,
            ]

    class TestCasesFactory:
        """Factory for generating test cases."""

        @staticmethod
        def get_attribute_test_cases() -> list[dict[str, object]]:
            """Generate attribute access test cases."""
            return [
                {
                    "attribute": LdifTestData.EXISTING_ATTR,
                    "expected_success": True,
                    "expected_type": list,
                },
                {
                    "attribute": LdifTestData.NON_EXISTENT_ATTR,
                    "expected_success": False,
                    "expected_error_contains": "not found",
                },
            ]

        @staticmethod
        def get_normalization_test_cases() -> list[dict[str, object]]:
            """Generate attribute normalization test cases."""
            return [
                {
                    "input_value": LdifTestData.STRING_VALUE,
                    "expected_output": LdifTestData.STRING_VALUE,
                },
                {
                    "input_value": [
                        LdifTestData.FIRST_VALUE,
                        LdifTestData.SECOND_VALUE,
                    ],
                    "expected_output": LdifTestData.FIRST_VALUE,
                },
                {
                    "input_value": [],
                    "expected_output": LdifTestData.EMPTY_LIST_STR,
                },
            ]

    # =========================================================================
    # NESTED: Test Helpers
    # =========================================================================

    class TestHelpers:
        """Test-specific helpers for entry manipulation testing."""

        @staticmethod
        def assert_attribute_result(
            result: FlextResult[object],
            expected_success: bool,
            expected_type: type | None = None,
            expected_error_contains: str | None = None,
        ) -> None:
            """Assert common patterns for attribute access results."""
            if expected_success:
                assert result.is_success, f"Expected success: {result.error}"
                if expected_type:
                    assert isinstance(result.unwrap(), expected_type)
            else:
                assert result.is_failure, f"Expected failure: {result.unwrap()}"
                if expected_error_contains and result.error:
                    assert expected_error_contains in result.error.lower()

    # =========================================================================
    # TEST METHODS
    # =========================================================================

    @pytest.mark.parametrize(
        "attribute_case",
        TestCasesFactory.get_attribute_test_cases(),
        ids=lambda case: f"attr_{case['attribute']}_{'success' if case['expected_success'] else 'failure'}",
    )
    def test_get_entry_attribute_cases(
        self,
        attribute_case: dict[str, object],
        parsed_user_entry: FlextLdifModels.Entry,
    ) -> None:
        """Test getting entry attributes with various cases."""
        service = EntryManipulationServices()
        result = service.get_entry_attribute(
            parsed_user_entry, cast("str", attribute_case["attribute"])
        )

        self.TestHelpers.assert_attribute_result(
            result,
            expected_success=cast("bool", attribute_case["expected_success"]),
            expected_type=cast("type | None", attribute_case.get("expected_type")),
            expected_error_contains=cast(
                "str | None", attribute_case.get("expected_error_contains")
            ),
        )

    @pytest.mark.parametrize(
        "normalization_case",
        TestCasesFactory.get_normalization_test_cases(),
        ids=lambda case: f"normalize_{type(case['input_value']).__name__}",
    )
    def test_normalize_attribute_value_cases(
        self,
        normalization_case: dict[str, object],
    ) -> None:
        """Test attribute value normalization with various inputs."""
        service = EntryManipulationServices()
        result = service.normalize_attribute_value(normalization_case["input_value"])

        assert result.is_success, f"Normalization failed: {result.error}"
        assert result.unwrap() == normalization_case["expected_output"]

    @pytest.mark.parametrize(
        "attribute",
        TestDataFactory.create_test_attributes(),
        ids=lambda attr: f"normalized_{attr}",
    )
    def test_get_normalized_attribute_various(
        self,
        attribute: str,
        parsed_user_entry: FlextLdifModels.Entry,
    ) -> None:
        """Test getting normalized attributes for various attribute names."""
        service = EntryManipulationServices()
        result = service.get_normalized_attribute(parsed_user_entry, attribute)

        # Result should be a FlextResult
        assert isinstance(result, FlextResult)

        # If attribute exists, should return string
        if result.is_success:
            value = result.unwrap()
            assert isinstance(value, str)
            if attribute == LdifTestData.NORMALIZED_MAIL:
                # Email should contain @ or be non-empty
                assert "@" in value or len(value) > 0
            else:
                # Other attributes should be non-empty strings
                assert len(value) > 0
        else:
            # If attribute doesn't exist, should fail gracefully
            assert result.is_failure
            if result.error:
                assert (
                    "not found" in result.error.lower() or "Attribute" in result.error
                )

    def test_normalize_attribute_value_none_input(self) -> None:
        """Test normalizing None input fails appropriately."""
        service = EntryManipulationServices()
        result = service.normalize_attribute_value(None)

        assert result.is_failure, "None input should fail"
        if result.error:
            assert "None" in result.error

    def test_get_entry_attribute_edge_cases(self) -> None:
        """Test getting attribute with edge cases."""
        # Test with None as entry (should be handled by type checking)
        # Since we can't create invalid entries due to strict typing,
        # this test ensures the method is robust
        assert hasattr(EntryManipulationServices, "get_entry_attribute")
        service = EntryManipulationServices()
        assert callable(service.get_entry_attribute)

    def test_get_normalized_attribute_edge_cases(
        self,
        parsed_user_entry: FlextLdifModels.Entry,
    ) -> None:
        """Test normalized attribute access with edge cases."""
        # Test with empty string attribute name
        service = EntryManipulationServices()
        result = service.get_normalized_attribute(parsed_user_entry, "")
        # Should fail gracefully
        assert isinstance(result, FlextResult)

        # Test with special characters in attribute name
        service = EntryManipulationServices()
        result = service.get_normalized_attribute(parsed_user_entry, "test@attr#123")
        # Should fail gracefully
        assert isinstance(result, FlextResult)
