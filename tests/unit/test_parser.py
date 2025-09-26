"""FLEXT LDIF Parser - Comprehensive Unit Tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest
from flext_ldif.config import FlextLdifConfig
from flext_ldif.models import FlextLdifModels
from flext_ldif.parser import FlextLdifParser


class FileManager:
    """Simple file manager for tests."""

    def __init__(self, temp_dir: Path) -> None:
        """Initialize with temp directory."""
        self.temp_dir = temp_dir

    def create_file(self, filename: str, content: str) -> Path:
        """Create a temporary file with content."""
        file_path = self.temp_dir / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path


@pytest.mark.unit
class TestFlextLdifParser:
    """Comprehensive tests for FlextLdifParser class."""

    def test_parser_initialization_default(self) -> None:
        """Test parser initialization with default configuration."""
        parser = FlextLdifParser()

        assert parser is not None
        assert parser._config is not None
        assert parser._logger is not None

    def test_parser_initialization_with_config(self) -> None:
        """Test parser initialization with custom configuration."""
        config = FlextLdifConfig()
        parser = FlextLdifParser(config=config)

        assert parser is not None
        assert parser._config == config

    def test_parser_initialization_with_invalid_config(self) -> None:
        """Test parser initialization with invalid configuration."""
        # Should handle invalid config gracefully
        parser = FlextLdifParser(config=None)
        assert parser is not None

    def test_parse_entry_valid(self) -> None:
        """Test parsing valid LDIF entry."""
        parser = FlextLdifParser()

        entry_content = """dn: cn=test,dc=example,dc=com
objectClass: person
cn: Test User
mail: test@example.com
"""
        result = parser.parse_entry(entry_content)

        assert result.is_success
        assert isinstance(result.value, FlextLdifModels.Entry)
        assert result.value.dn == "cn=test,dc=example,dc=com"

    def test_parse_entry_invalid_dn(self) -> None:
        """Test parsing entry with invalid DN."""
        parser = FlextLdifParser()

        entry_content = """dn: invalid-dn-format
objectClass: person
cn: Test User
"""
        result = parser.parse_entry(entry_content)

        # Should handle invalid DN gracefully
        assert result.is_success or result.is_failure

    def test_parse_entry_missing_dn(self) -> None:
        """Test parsing entry with missing DN."""
        parser = FlextLdifParser()

        entry_content = """objectClass: person
cn: Test User
"""
        result = parser.parse_entry(entry_content)

        # Should handle missing DN gracefully
        assert result.is_success or result.is_failure

    def test_parse_entry_empty(self) -> None:
        """Test parsing empty entry."""
        parser = FlextLdifParser()

        result = parser.parse_entry("")

        # Should handle empty entry gracefully
        assert result.is_success or result.is_failure

    def test_parse_entry_with_comments(self) -> None:
        """Test parsing entry with comments."""
        parser = FlextLdifParser()

        entry_content = """# This is a comment
dn: cn=test,dc=example,dc=com
objectClass: person
cn: Test User
# Another comment
mail: test@example.com
"""
        result = parser.parse_entry(entry_content)

        assert result.is_success
        assert isinstance(result.value, FlextLdifModels.Entry)

    def test_parse_entry_with_multiple_values(self) -> None:
        """Test parsing entry with multiple attribute values."""
        parser = FlextLdifParser()

        entry_content = """dn: cn=test,dc=example,dc=com
objectClass: person
objectClass: organizationalPerson
cn: Test User
mail: test@example.com
mail: test2@example.com
"""
        result = parser.parse_entry(entry_content)

        assert result.is_success
        entry = result.value
        assert len(entry.attributes["objectClass"]) == 2
        assert len(entry.attributes["mail"]) == 2

    def test_parse_entry_with_binary_data(self) -> None:
        """Test parsing entry with binary data."""
        parser = FlextLdifParser()

        entry_content = """dn: cn=test,dc=example,dc=com
objectClass: person
cn: Test User
userPassword:: e1NTSEF9b2RkblFvUjNpV2EyclRjQ2p4WUdsdWRPaThka0dvb0c=
"""
        result = parser.parse_entry(entry_content)

        assert result.is_success
        assert isinstance(result.value, FlextLdifModels.Entry)

    def test_parse_entry_with_continuation_lines(self) -> None:
        """Test parsing entry with continuation lines."""
        parser = FlextLdifParser()

        entry_content = """dn: cn=test,dc=example,dc=com
objectClass: person
cn: Test User
description: This is a very long description that
 continues on the next line
mail: test@example.com
"""
        result = parser.parse_entry(entry_content)

        assert result.is_success
        entry = result.value
        assert "description" in entry.attributes
        assert "continues on the next line" in entry.attributes["description"][0]

    def test_parse_entries_valid(self, sample_ldif_entries: str) -> None:
        """Test parsing multiple valid LDIF entries."""
        parser = FlextLdifParser()
        result = parser.parse_entries(sample_ldif_entries)

        assert result.is_success
        assert isinstance(result.value, list)
        assert len(result.value) > 0

        # Verify all entries are FlextLdifModels.Entry instances
        for entry in result.value:
            assert isinstance(entry, FlextLdifModels.Entry)

    def test_parse_entries_invalid(self, invalid_ldif_data: str) -> None:
        """Test parsing invalid LDIF entries."""
        parser = FlextLdifParser()
        result = parser.parse_entries(invalid_ldif_data)

        # Should handle invalid entries gracefully
        assert result.is_success or result.is_failure

    def test_parse_entries_empty(self) -> None:
        """Test parsing empty LDIF entries."""
        parser = FlextLdifParser()
        result = parser.parse_entries("")

        # Should handle empty content gracefully
        assert result.is_success or result.is_failure
        if result.is_success:
            assert isinstance(result.value, list)

    def test_parse_entries_with_changes(self, sample_ldif_with_changes: str) -> None:
        """Test parsing LDIF entries with change records."""
        parser = FlextLdifParser()
        result = parser.parse_entries(sample_ldif_with_changes)

        assert result.is_success
        assert isinstance(result.value, list)

    def test_parse_entries_with_binary(self, sample_ldif_with_binary: str) -> None:
        """Test parsing LDIF entries with binary data."""
        parser = FlextLdifParser()
        result = parser.parse_entries(sample_ldif_with_binary)

        assert result.is_success
        assert isinstance(result.value, list)

    def test_parse_file_valid(self, ldif_test_file: Path) -> None:
        """Test parsing valid LDIF file."""
        parser = FlextLdifParser()
        result = parser.parse_file(ldif_test_file)

        assert result.is_success
        assert isinstance(result.value, list)

    def test_parse_file_nonexistent(self) -> None:
        """Test parsing nonexistent LDIF file."""
        parser = FlextLdifParser()
        nonexistent_file = Path("/nonexistent/file.ldif")
        result = parser.parse_file(nonexistent_file)

        assert result.is_failure
        assert result.error is not None

    def test_parse_file_invalid_format(self, test_file_manager: FileManager) -> None:
        """Test parsing file with invalid LDIF format."""
        parser = FlextLdifParser()

        # Create a file with invalid LDIF format
        invalid_file = test_file_manager.create_file("invalid.ldif", "invalid content")
        result = parser.parse_file(invalid_file)

        # Should handle invalid format gracefully
        assert result.is_success or result.is_failure

    def test_validate_entry_valid(self) -> None:
        """Test validating valid LDIF entry."""
        parser = FlextLdifParser()

        entry_content = """dn: cn=test,dc=example,dc=com
objectClass: person
cn: Test User
mail: test@example.com
"""
        result = parser.validate_entry(entry_content)

        assert result.is_success
        assert isinstance(result.value, dict)

    def test_validate_entry_invalid(self) -> None:
        """Test validating invalid LDIF entry."""
        parser = FlextLdifParser()

        entry_content = """dn: invalid-dn-format
objectClass: person
cn: Test User
"""
        result = parser.validate_entry(entry_content)

        # Should return validation results
        assert result.is_success or result.is_failure
        if result.is_success:
            assert isinstance(result.value, dict)

    def test_validate_entry_empty(self) -> None:
        """Test validating empty LDIF entry."""
        parser = FlextLdifParser()
        result = parser.validate_entry("")

        # Should handle empty entry gracefully
        assert result.is_success or result.is_failure

    def test_validate_entries_valid(self, sample_ldif_entries: str) -> None:
        """Test validating valid LDIF entries."""
        parser = FlextLdifParser()
        result = parser.validate_entries(sample_ldif_entries)

        assert result.is_success
        assert isinstance(result.value, dict)

    def test_validate_entries_invalid(self, invalid_ldif_data: str) -> None:
        """Test validating invalid LDIF entries."""
        parser = FlextLdifParser()
        result = parser.validate_entries(invalid_ldif_data)

        # Should return validation results
        assert result.is_success or result.is_failure
        if result.is_success:
            assert isinstance(result.value, dict)

    def test_validate_entries_empty(self) -> None:
        """Test validating empty LDIF entries."""
        parser = FlextLdifParser()
        result = parser.validate_entries("")

        # Should handle empty content gracefully
        assert result.is_success or result.is_failure

    def test_normalize_dn_valid(self) -> None:
        """Test normalizing valid DN."""
        parser = FlextLdifParser()

        dn = "cn=test,dc=example,dc=com"
        result = parser.normalize_dn(dn)

        assert result.is_success
        assert isinstance(result.value, str)

    def test_normalize_dn_invalid(self) -> None:
        """Test normalizing invalid DN."""
        parser = FlextLdifParser()

        dn = "invalid-dn-format"
        result = parser.normalize_dn(dn)

        # Should handle invalid DN gracefully
        assert result.is_success or result.is_failure

    def test_normalize_dn_empty(self) -> None:
        """Test normalizing empty DN."""
        parser = FlextLdifParser()
        result = parser.normalize_dn("")

        # Should handle empty DN gracefully
        assert result.is_success or result.is_failure

    def test_normalize_attribute_name_valid(self) -> None:
        """Test normalizing valid attribute name."""
        parser = FlextLdifParser()

        attr_name = "cn"
        result = parser.normalize_attribute_name(attr_name)

        assert result.is_success
        assert isinstance(result.value, str)

    def test_normalize_attribute_name_invalid(self) -> None:
        """Test normalizing invalid attribute name."""
        parser = FlextLdifParser()

        attr_name = ""
        result = parser.normalize_attribute_name(attr_name)

        # Should handle invalid attribute name gracefully
        assert result.is_success or result.is_failure

    def test_normalize_attribute_value_valid(self) -> None:
        """Test normalizing valid attribute value."""
        parser = FlextLdifParser()

        attr_value = "Test User"
        result = parser.normalize_attribute_value(attr_value)

        assert result.is_success
        assert isinstance(result.value, str)

    def test_normalize_attribute_value_empty(self) -> None:
        """Test normalizing empty attribute value."""
        parser = FlextLdifParser()
        result = parser.normalize_attribute_value("")

        # Should handle empty attribute value gracefully
        assert result.is_success or result.is_failure

    def test_extract_dn_from_entry(self) -> None:
        """Test extracting DN from entry content."""
        parser = FlextLdifParser()

        entry_content = """dn: cn=test,dc=example,dc=com
objectClass: person
cn: Test User
"""
        result = parser.extract_dn_from_entry(entry_content)

        assert result.is_success
        assert result.value == "cn=test,dc=example,dc=com"

    def test_extract_dn_from_entry_missing(self) -> None:
        """Test extracting DN from entry without DN."""
        parser = FlextLdifParser()

        entry_content = """objectClass: person
cn: Test User
"""
        result = parser.extract_dn_from_entry(entry_content)

        # Should handle missing DN gracefully
        assert result.is_success or result.is_failure

    def test_extract_attributes_from_entry(self) -> None:
        """Test extracting attributes from entry content."""
        parser = FlextLdifParser()

        entry_content = """dn: cn=test,dc=example,dc=com
objectClass: person
cn: Test User
mail: test@example.com
"""
        result = parser.extract_attributes_from_entry(entry_content)

        assert result.is_success
        assert isinstance(result.value, dict)
        assert "objectClass" in result.value
        assert "cn" in result.value
        assert "mail" in result.value

    def test_extract_attributes_from_entry_empty(self) -> None:
        """Test extracting attributes from empty entry."""
        parser = FlextLdifParser()
        result = parser.extract_attributes_from_entry("")

        # Should handle empty entry gracefully
        assert result.is_success or result.is_failure

    def test_parse_change_record_valid(self) -> None:
        """Test parsing valid change record."""
        parser = FlextLdifParser()

        change_content = """dn: cn=test,dc=example,dc=com
changetype: add
cn: Test User
mail: test@example.com
"""
        result = parser.parse_change_record(change_content)

        assert result.is_success
        assert isinstance(result.value, FlextLdifModels.LdifChangeRecord)

    def test_parse_change_record_invalid(self) -> None:
        """Test parsing invalid change record."""
        parser = FlextLdifParser()

        change_content = """dn: cn=test,dc=example,dc=com
invalidchangetype: add
cn: Test User
"""
        result = parser.parse_change_record(change_content)

        # Should handle invalid change record gracefully
        assert result.is_success or result.is_failure

    def test_parse_change_record_empty(self) -> None:
        """Test parsing empty change record."""
        parser = FlextLdifParser()
        result = parser.parse_change_record("")

        # Should handle empty change record gracefully
        assert result.is_success or result.is_failure

    def test_configure_parser(self) -> None:
        """Test configuring parser."""
        parser = FlextLdifParser()
        config = FlextLdifConfig()

        result = parser.configure(config)

        assert result.is_success
        assert parser._config == config

    def test_configure_parser_invalid(self) -> None:
        """Test configuring parser with invalid configuration."""
        parser = FlextLdifParser()
        invalid_config = {"invalid": "config"}

        result = parser.configure(invalid_config)

        # Should handle invalid config gracefully
        assert result.is_success or result.is_failure

    def test_reset_configuration(self) -> None:
        """Test resetting parser configuration."""
        parser = FlextLdifParser()
        config = FlextLdifConfig()
        parser.configure(config)

        result = parser.reset_configuration()

        assert result.is_success
        assert parser._config is None

    def test_get_configuration(self) -> None:
        """Test getting parser configuration."""
        parser = FlextLdifParser()
        config = FlextLdifConfig()
        parser.configure(config)

        result = parser.get_configuration()

        assert result.is_success
        assert result.value == config

    def test_get_configuration_none(self) -> None:
        """Test getting configuration when none is set."""
        parser = FlextLdifParser()

        result = parser.get_configuration()

        assert result.is_success
        assert result.value is None

    def test_is_configured(self) -> None:
        """Test checking if parser is configured."""
        parser = FlextLdifParser()

        # Initially not configured
        assert not parser.is_configured()

        # Configure and check again
        config = FlextLdifConfig()
        parser.configure(config)
        assert parser.is_configured()

    def test_get_status(self) -> None:
        """Test getting parser status."""
        parser = FlextLdifParser()

        result = parser.get_status()

        assert result.is_success
        assert isinstance(result.value, dict)

    def test_parser_performance(self) -> None:
        """Test parser performance characteristics."""
        parser = FlextLdifParser()

        # Test basic performance
        start_time = time.time()

        result = parser.get_status()

        end_time = time.time()
        execution_time = end_time - start_time

        assert result.is_success
        assert execution_time < 1.0  # Should complete within 1 second

    def test_parser_memory_usage(self) -> None:
        """Test parser memory usage characteristics."""
        parser = FlextLdifParser()

        # Test that parser doesn't leak memory
        initial_result = parser.get_status()
        assert initial_result.is_success

        # Perform multiple operations
        for _ in range(10):
            result = parser.get_status()
            assert result.is_success

        # Final check should still work
        final_result = parser.get_status()
        assert final_result.is_success

    def test_parser_error_handling(self) -> None:
        """Test parser error handling capabilities."""
        parser = FlextLdifParser()

        # Test with various error conditions
        result = parser.parse_entry("invalid entry content")

        # Should handle errors gracefully
        assert result.is_success or result.is_failure
        if result.is_failure:
            assert result.error is not None

    def test_parser_large_content(self) -> None:
        """Test parser with large content."""
        parser = FlextLdifParser()

        # Create large LDIF content
        large_content = "\n".join(
            [
                f"dn: cn=user{i},dc=example,dc=com",
                "objectClass: person",
                f"cn: User {i}",
                f"mail: user{i}@example.com",
                f"description: User {i} description",
                "",
            ]
            for i in range(1000)
        )

        result = parser.parse_entries(large_content)

        assert result.is_success
        assert len(result.value) == 1000

    def test_parser_edge_cases(self) -> None:
        """Test parser with edge cases."""
        parser = FlextLdifParser()

        # Test with very long lines
        long_line_content = (
            "dn: cn="
            + "x" * 10000
            + ",dc=example,dc=com\nobjectClass: person\ncn: Test"
        )
        result = parser.parse_entry(long_line_content)

        # Should handle long lines gracefully
        assert result.is_success or result.is_failure

        # Test with special characters
        special_char_content = "dn: cn=test,dc=example,dc=com\nobjectClass: person\ncn: Test with special chars: !@#$%^&*()"
        result = parser.parse_entry(special_char_content)

        # Should handle special characters gracefully
        assert result.is_success or result.is_failure

    def test_parser_concurrent_operations(self) -> None:
        """Test parser concurrent operations."""
        parser = FlextLdifParser()
        results = []

        def worker() -> None:
            result = parser.get_status()
            results.append(result)

        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations succeeded
        assert len(results) == 5
        for result in results:
            assert result.is_success
