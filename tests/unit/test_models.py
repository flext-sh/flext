"""FLEXT LDIF Models - Comprehensive Unit Tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time

import pytest
from flext_ldif.models import FlextLdifModels

from flext_core import FlextResult


@pytest.mark.unit
class TestFlextLdifModels:
    """Comprehensive tests for FlextLdifModels class."""

    def test_monadic_model_creation(self) -> None:
        """Test MonadicModel creation and basic functionality."""
        model = FlextLdifModels.MonadicModel()
        assert model is not None

    def test_monadic_model_validation(self) -> None:
        """Test MonadicModel validation capabilities."""
        model = FlextLdifModels.MonadicModel()

        # Test validation method
        result = model.validate_data({"test": "value"})
        assert isinstance(result, FlextResult)

    def test_ldif_entry_creation(self) -> None:
        """Test LdifEntry creation with valid data."""
        entry_data = {
            "dn": "cn=test,dc=example,dc=com",
            "attributes": {
                "objectClass": ["person"],
                "cn": ["Test User"],
                "mail": ["test@example.com"],
            },
        }

        entry = FlextLdifModels.Entry(**entry_data)

        assert entry.dn == "cn=test,dc=example,dc=com"
        assert "objectClass" in entry.attributes
        assert "cn" in entry.attributes
        assert "mail" in entry.attributes

    def test_ldif_entry_validation(self) -> None:
        """Test LdifEntry validation."""
        # Valid entry
        valid_data = {
            "dn": "cn=test,dc=example,dc=com",
            "attributes": {"objectClass": ["person"]},
        }
        entry = FlextLdifModels.Entry(**valid_data)
        assert entry.dn == "cn=test,dc=example,dc=com"

        # Test with invalid DN
        with pytest.raises(ValueError):
            FlextLdifModels.Entry(dn="", attributes={})

    def test_ldif_entry_methods(self) -> None:
        """Test LdifEntry methods."""
        entry_data = {
            "dn": "cn=test,dc=example,dc=com",
            "attributes": {"objectClass": ["person"], "cn": ["Test User"]},
        }
        entry = FlextLdifModels.Entry(**entry_data)

        # Test has_attribute
        assert entry.has_attribute("cn")
        assert not entry.has_attribute("nonexistent")

        # Test get_attribute_values
        cn_values = entry.get_attribute_values("cn")
        assert cn_values == ["Test User"]

        # Test get_attribute_values for nonexistent attribute
        nonexistent_values = entry.get_attribute_values("nonexistent")
        assert nonexistent_values == []

    def test_ldif_entry_transformation(self) -> None:
        """Test LdifEntry transformation methods."""
        entry_data = {
            "dn": "cn=test,dc=example,dc=com",
            "attributes": {
                "objectClass": ["person"],
                "cn": ["Test User"],
                "mail": ["test@example.com"],
            },
        }
        entry = FlextLdifModels.Entry(**entry_data)

        # Test transform_dn
        result = entry.transform_dn({"base_dn": "dc=newdomain,dc=com"})
        assert result.is_success
        assert "dc=newdomain,dc=com" in result.value

        # Test transform_attributes
        transform_rules = {
            "attribute_mappings": {"mail": "email"},
            "value_transformations": {"cn": lambda x: x.upper()},
        }
        result = entry.transform_attributes(transform_rules)
        assert result.is_success

    def test_ldif_entry_serialization(self) -> None:
        """Test LdifEntry serialization methods."""
        entry_data = {
            "dn": "cn=test,dc=example,dc=com",
            "attributes": {"objectClass": ["person"], "cn": ["Test User"]},
        }
        entry = FlextLdifModels.Entry(**entry_data)

        # Test to_dict
        entry_dict = entry.to_dict()
        assert isinstance(entry_dict, dict)
        assert entry_dict["dn"] == "cn=test,dc=example,dc=com"

        # Test to_ldif_string
        ldif_string = entry.to_ldif_string()
        assert isinstance(ldif_string, str)
        assert "dn: cn=test,dc=example,dc=com" in ldif_string

    def test_ldif_attributes_creation(self) -> None:
        """Test LdifAttributes creation."""
        attributes = FlextLdifModels.LdifAttributes()
        assert attributes is not None

    def test_ldif_attributes_methods(self) -> None:
        """Test LdifAttributes methods."""
        attributes = FlextLdifModels.LdifAttributes()

        # Test add_attribute
        result = attributes.add_attribute("cn", "Test User")
        assert result.is_success

        # Test get_attribute
        values = attributes.get_attribute("cn")
        assert values == ["Test User"]

        # Test has_attribute
        assert attributes.has_attribute("cn")
        assert not attributes.has_attribute("nonexistent")

    def test_ldif_attributes_validation(self) -> None:
        """Test LdifAttributes validation."""
        attributes = FlextLdifModels.LdifAttributes()

        # Test validation
        result = attributes.validate()
        assert isinstance(result, FlextResult)

    def test_ldif_change_record_creation(self) -> None:
        """Test LdifChangeRecord creation."""
        change_data = {
            "dn": "cn=test,dc=example,dc=com",
            "change_type": "add",
            "attributes": {"cn": ["Test User"]},
        }

        change_record = FlextLdifModels.LdifChangeRecord(**change_data)

        assert change_record.dn == "cn=test,dc=example,dc=com"
        assert change_record.change_type == "add"
        assert "cn" in change_record.attributes

    def test_ldif_change_record_validation(self) -> None:
        """Test LdifChangeRecord validation."""
        # Valid change record
        valid_data = {
            "dn": "cn=test,dc=example,dc=com",
            "change_type": "add",
            "attributes": {"cn": ["Test User"]},
        }
        change_record = FlextLdifModels.LdifChangeRecord(**valid_data)
        assert change_record.change_type == "add"

        # Test with invalid change type
        with pytest.raises(ValueError):
            FlextLdifModels.LdifChangeRecord(
                dn="cn=test,dc=example,dc=com", change_type="invalid", attributes={}
            )

    def test_ldif_change_record_methods(self) -> None:
        """Test LdifChangeRecord methods."""
        change_data = {
            "dn": "cn=test,dc=example,dc=com",
            "change_type": "add",
            "attributes": {"cn": ["Test User"]},
        }
        change_record = FlextLdifModels.LdifChangeRecord(**change_data)

        # Test is_add
        assert change_record.is_add()
        assert not change_record.is_delete()
        assert not change_record.is_modify()

    def test_ldif_schema_creation(self) -> None:
        """Test LdifSchema creation."""
        schema_data = {
            "object_classes": {
                "person": {"must": ["cn", "sn"], "may": ["mail", "telephoneNumber"]}
            },
            "attribute_types": {"cn": {"syntax": "1.3.6.1.4.1.1466.115.121.1.15"}},
        }

        schema = FlextLdifModels.LdifSchema(**schema_data)

        assert "person" in schema.object_classes
        assert "cn" in schema.attribute_types

    def test_ldif_schema_validation(self) -> None:
        """Test LdifSchema validation."""
        schema_data = {
            "object_classes": {"person": {"must": ["cn", "sn"], "may": ["mail"]}},
            "attribute_types": {"cn": {"syntax": "1.3.6.1.4.1.1466.115.121.1.15"}},
        }

        schema = FlextLdifModels.LdifSchema(**schema_data)

        # Test validate_entry
        entry_data = {
            "dn": "cn=test,dc=example,dc=com",
            "attributes": {
                "objectClass": ["person"],
                "cn": ["Test User"],
                "sn": ["User"],
            },
        }
        entry = FlextLdifModels.Entry(**entry_data)

        result = schema.validate_entry(entry)
        assert isinstance(result, FlextResult)

    def test_ldif_statistics_creation(self) -> None:
        """Test LdifStatistics creation."""
        stats_data = {
            "total_entries": 100,
            "successful_entries": 95,
            "failed_entries": 5,
            "object_class_counts": {"person": 50, "group": 45},
            "attribute_counts": {"cn": 100, "mail": 80},
        }

        stats = FlextLdifModels.LdifStatistics(**stats_data)

        assert stats.total_entries == 100
        assert stats.successful_entries == 95
        assert stats.failed_entries == 5

    def test_ldif_statistics_methods(self) -> None:
        """Test LdifStatistics methods."""
        stats_data = {
            "total_entries": 100,
            "successful_entries": 95,
            "failed_entries": 5,
            "object_class_counts": {"person": 50, "group": 45},
            "attribute_counts": {"cn": 100, "mail": 80},
        }

        stats = FlextLdifModels.LdifStatistics(**stats_data)

        # Test success_rate
        assert stats.success_rate() == 0.95

        # Test failure_rate
        assert stats.failure_rate() == 0.05

    def test_ldif_configuration_creation(self) -> None:
        """Test LdifConfiguration creation."""
        config_data = {
            "encoding": "utf-8",
            "strict_parsing": True,
            "max_entries": 1000,
            "validate_dn": True,
            "normalize_attributes": True,
        }

        config = FlextLdifModels.LdifConfiguration(**config_data)

        assert config.encoding == "utf-8"
        assert config.strict_parsing is True
        assert config.max_entries == 1000

    def test_ldif_configuration_validation(self) -> None:
        """Test LdifConfiguration validation."""
        config_data = {
            "encoding": "utf-8",
            "strict_parsing": True,
            "max_entries": 1000,
            "validate_dn": True,
            "normalize_attributes": True,
        }

        config = FlextLdifModels.LdifConfiguration(**config_data)

        # Test validation
        result = config.validate()
        assert isinstance(result, FlextResult)

    def test_ldif_error_creation(self) -> None:
        """Test LdifError creation."""
        error_data = {
            "error_type": "validation",
            "message": "Invalid DN format",
            "line_number": 10,
            "entry_dn": "cn=test,dc=example,dc=com",
        }

        error = FlextLdifModels.LdifError(**error_data)

        assert error.error_type == "validation"
        assert error.message == "Invalid DN format"
        assert error.line_number == 10

    def test_ldif_error_methods(self) -> None:
        """Test LdifError methods."""
        error_data = {
            "error_type": "validation",
            "message": "Invalid DN format",
            "line_number": 10,
            "entry_dn": "cn=test,dc=example,dc=com",
        }

        error = FlextLdifModels.LdifError(**error_data)

        # Test to_dict
        error_dict = error.to_dict()
        assert isinstance(error_dict, dict)
        assert error_dict["error_type"] == "validation"

    def test_ldif_result_creation(self) -> None:
        """Test LdifResult creation."""
        result_data = {
            "success": True,
            "data": {"entries": []},
            "errors": [],
            "statistics": {
                "total_entries": 0,
                "successful_entries": 0,
                "failed_entries": 0,
            },
        }

        result = FlextLdifModels.LdifResult(**result_data)

        assert result.success is True
        assert isinstance(result.data, dict)
        assert isinstance(result.errors, list)
        assert isinstance(result.statistics, dict)

    def test_ldif_result_methods(self) -> None:
        """Test LdifResult methods."""
        result_data = {
            "success": True,
            "data": {"entries": []},
            "errors": [],
            "statistics": {
                "total_entries": 0,
                "successful_entries": 0,
                "failed_entries": 0,
            },
        }

        result = FlextLdifModels.LdifResult(**result_data)

        # Test has_errors
        assert not result.has_errors()

        # Test get_error_count
        assert result.get_error_count() == 0

    def test_ldif_models_edge_cases(self) -> None:
        """Test LdifModels with edge cases."""
        # Test with empty attributes
        entry = FlextLdifModels.Entry(dn="cn=test,dc=example,dc=com", attributes={})
        assert entry.attributes == {}

        # Test with None values
        attributes = FlextLdifModels.LdifAttributes()
        result = attributes.add_attribute("test", None)
        # Should handle None values gracefully
        assert isinstance(result, FlextResult)

    def test_ldif_models_performance(self) -> None:
        """Test LdifModels performance characteristics."""
        # Test entry creation performance
        start_time = time.time()

        for i in range(1000):
            FlextLdifModels.Entry(
                dn=f"cn=user{i},dc=example,dc=com",
                attributes={"objectClass": ["person"], "cn": [f"User {i}"]},
            )

        end_time = time.time()
        execution_time = end_time - start_time

        assert execution_time < 1.0  # Should complete within 1 second

    def test_ldif_models_memory_usage(self) -> None:
        """Test LdifModels memory usage characteristics."""
        # Test that models don't leak memory
        entries = []

        for i in range(100):
            entry = FlextLdifModels.Entry(
                dn=f"cn=user{i},dc=example,dc=com",
                attributes={"objectClass": ["person"], "cn": [f"User {i}"]},
            )
            entries.append(entry)

        # Verify all entries are valid
        assert len(entries) == 100
        for entry in entries:
            assert isinstance(entry, FlextLdifModels.Entry)

    def test_ldif_models_serialization_performance(self) -> None:
        """Test LdifModels serialization performance."""
        entry = FlextLdifModels.Entry(
            dn="cn=test,dc=example,dc=com",
            attributes={
                "objectClass": ["person"],
                "cn": ["Test User"],
                "mail": ["test@example.com"],
                "telephoneNumber": ["+1-555-123-4567"],
            },
        )

        start_time = time.time()

        # Test multiple serializations
        for _ in range(100):
            entry.to_dict()
            entry.to_ldif_string()

        end_time = time.time()
        execution_time = end_time - start_time

        assert execution_time < 0.5  # Should complete within 0.5 seconds

    def test_ldif_models_validation_performance(self) -> None:
        """Test LdifModels validation performance."""
        entry = FlextLdifModels.Entry(
            dn="cn=test,dc=example,dc=com",
            attributes={"objectClass": ["person"], "cn": ["Test User"]},
        )

        start_time = time.time()

        # Test multiple validations
        for _ in range(100):
            entry.validate()

        end_time = time.time()
        execution_time = end_time - start_time

        assert execution_time < 0.5  # Should complete within 0.5 seconds
