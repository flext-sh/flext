"""Tests for FlextLdifEntry service with real data.

Tests entry transformation operations using real LDIF entries without mocks.
Validates operational attribute removal and attribute removal operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_ldif import FlextLdif, FlextLdifModels
from flext_ldif.services.entries import FlextLdifEntries as FlextLdifEntry


class TestFlextLdifEntryService:
    """Test FlextLdifEntry service with real data."""

    def test_remove_operational_attributes_single(
        self,
        flext_ldif_instance: FlextLdif,
        parsed_user_entry: FlextLdifModels.Entry,
    ) -> None:
        """Test removing operational attributes from single entry."""
        # Add operational attributes to entry
        if parsed_user_entry.attributes:
            parsed_user_entry.attributes.attributes["createTimestamp"] = [
                "20250101120000Z"
            ]
            parsed_user_entry.attributes.attributes["modifyTimestamp"] = [
                "20250101120000Z"
            ]

        result = FlextLdifEntry.remove_operational_attributes(parsed_user_entry)

        assert result.is_success, f"Should succeed: {result.error}"
        cleaned_entry = result.unwrap()

        # Verify operational attributes are removed
        if cleaned_entry.attributes:
            assert "createTimestamp" not in cleaned_entry.attributes.attributes
            assert "modifyTimestamp" not in cleaned_entry.attributes.attributes

        # Verify non-operational attributes remain
        if cleaned_entry.attributes:
            assert "cn" in cleaned_entry.attributes.attributes
            assert "mail" in cleaned_entry.attributes.attributes

    def test_remove_operational_attributes_batch(
        self,
        parsed_multiple_entries: list[FlextLdifModels.Entry],
    ) -> None:
        """Test removing operational attributes from multiple entries."""
        # Add operational attributes
        for entry in parsed_multiple_entries:
            if entry.attributes:
                entry.attributes.attributes["createTimestamp"] = ["20250101120000Z"]

        result = FlextLdifEntry.remove_operational_attributes_batch(
            list(parsed_multiple_entries)
        )

        assert result.is_success, f"Should succeed: {result.error}"
        cleaned_entries = result.unwrap()

        assert len(cleaned_entries) == len(parsed_multiple_entries)

        # Verify operational attributes are removed from all entries
        for entry in cleaned_entries:
            if entry.attributes:
                assert "createTimestamp" not in entry.attributes.attributes

    def test_remove_attributes_single(
        self,
        parsed_user_entry: FlextLdifModels.Entry,
    ) -> None:
        """Test removing specific attributes from single entry."""
        # Ensure entry has attributes to remove
        if parsed_user_entry.attributes:
            parsed_user_entry.attributes.attributes["tempAttribute"] = ["tempValue"]
            parsed_user_entry.attributes.attributes["debugInfo"] = ["debug"]

        result = FlextLdifEntry.remove_attributes(
            parsed_user_entry,
            attributes=["tempAttribute", "debugInfo"],
        )

        assert result.is_success, f"Should succeed: {result.error}"
        cleaned_entry = result.unwrap()

        # Verify specified attributes are removed
        if cleaned_entry.attributes:
            assert "tempAttribute" not in cleaned_entry.attributes.attributes
            assert "debugInfo" not in cleaned_entry.attributes.attributes

        # Verify other attributes remain
        if cleaned_entry.attributes:
            assert "cn" in cleaned_entry.attributes.attributes

    def test_remove_attributes_case_insensitive(
        self,
        parsed_user_entry: FlextLdifModels.Entry,
    ) -> None:
        """Test removing attributes with case-insensitive matching."""
        if parsed_user_entry.attributes:
            parsed_user_entry.attributes.attributes["TempAttr"] = ["value"]

        result = FlextLdifEntry.remove_attributes(
            parsed_user_entry,
            attributes=["tempattr"],  # lowercase
        )

        assert result.is_success, f"Should succeed: {result.error}"
        cleaned_entry = result.unwrap()

        # Verify attribute removed (case-insensitive)
        if cleaned_entry.attributes:
            assert "TempAttr" not in cleaned_entry.attributes.attributes

    def test_execute_remove_operational_attributes(
        self,
        parsed_user_entry: FlextLdifModels.Entry,
    ) -> None:
        """Test execute method with remove_operational_attributes operation."""
        if parsed_user_entry.attributes:
            parsed_user_entry.attributes.attributes["createTimestamp"] = [
                "20250101120000Z"
            ]

        service = FlextLdifEntry(
            entries=[parsed_user_entry],
            operation="remove_operational_attributes",
        )

        result = service.execute()

        assert result.is_success, f"Should succeed: {result.error}"
        cleaned_entries = result.unwrap()

        assert len(cleaned_entries) == 1
        if cleaned_entries[0].attributes:
            assert "createTimestamp" not in cleaned_entries[0].attributes.attributes

    def test_execute_remove_attributes(
        self,
        parsed_user_entry: FlextLdifModels.Entry,
    ) -> None:
        """Test execute method with remove_attributes operation."""
        if parsed_user_entry.attributes:
            parsed_user_entry.attributes.attributes["tempAttr"] = ["value"]

        service = FlextLdifEntry(
            entries=[parsed_user_entry],
            operation="remove_attributes",
            attributes_to_remove=["tempAttr"],
        )

        result = service.execute()

        assert result.is_success, f"Should succeed: {result.error}"
        cleaned_entries = result.unwrap()

        assert len(cleaned_entries) == 1
        if cleaned_entries[0].attributes:
            assert "tempAttr" not in cleaned_entries[0].attributes.attributes

    def test_execute_unknown_operation(
        self,
        parsed_user_entry: FlextLdifModels.Entry,
    ) -> None:
        """Test execute method with unknown operation."""
        service = FlextLdifEntry(
            entries=[parsed_user_entry],
            operation="unknown_operation",
        )

        result = service.execute()

        assert result.is_failure, "Should fail for unknown operation"
        assert "Unknown operation" in result.error
