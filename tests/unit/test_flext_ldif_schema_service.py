"""Tests for FlextLdifSchema service with real data.

Tests schema parsing, validation, and transformation using real LDIF schema
definitions without mocks.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_ldif import FlextLdifModels
from flext_ldif.services.schema import FlextLdifSchema


class TestFlextLdifSchemaService:
    """Test FlextLdifSchema service with real data."""

    def test_parse_attribute_valid(self) -> None:
        """Test parsing valid attribute definition."""
        attr_def = """( 2.5.4.3 NAME 'cn' SUP name EQUALITY caseIgnoreMatch
            SUBSTR caseIgnoreSubstringsMatch SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 )"""

        service = FlextLdifSchema()
        result = service.parse_attribute(attr_def)

        assert result.is_success, f"Should parse valid attribute: {result.error}"
        attr = result.unwrap()

        assert attr.oid == "2.5.4.3"
        assert attr.name == "cn"
        assert attr.syntax is not None

    def test_parse_attribute_invalid(self) -> None:
        """Test parsing invalid attribute definition."""
        invalid_def = "not a valid attribute definition"

        service = FlextLdifSchema()
        result = service.parse_attribute(invalid_def)

        assert result.is_failure, "Should fail for invalid definition"
        assert result.error is not None

    def test_parse_attribute_empty(self) -> None:
        """Test parsing empty attribute definition."""
        service = FlextLdifSchema()
        result = service.parse_attribute("")

        assert result.is_failure, "Should fail for empty definition"
        assert "empty" in result.error.lower()

    def test_parse_objectclass_valid(self) -> None:
        """Test parsing valid objectClass definition."""
        oc_def = """( 2.5.6.6 NAME 'person' SUP top STRUCTURAL
            MUST ( sn $ cn )
            MAY ( userPassword $ telephoneNumber $ seeAlso $ description ) )"""

        service = FlextLdifSchema()
        result = service.parse_objectclass(oc_def)

        assert result.is_success, f"Should parse valid objectClass: {result.error}"
        oc = result.unwrap()

        assert oc.oid == "2.5.6.6"
        assert oc.name == "person"
        assert "sn" in oc.must
        assert "cn" in oc.must

    def test_parse_objectclass_invalid(self) -> None:
        """Test parsing invalid objectClass definition."""
        invalid_def = "not a valid objectClass definition"

        service = FlextLdifSchema()
        result = service.parse_objectclass(invalid_def)

        assert result.is_failure, "Should fail for invalid definition"
        assert result.error is not None

    def test_validate_attribute_valid(self) -> None:
        """Test validating valid attribute model."""
        attr = FlextLdifModels.SchemaAttribute(
            oid="2.5.4.3",
            name="cn",
            syntax="1.3.6.1.4.1.1466.115.121.1.15",
        )

        service = FlextLdifSchema()
        result = service.validate_attribute(attr)

        assert result.is_success, f"Should validate valid attribute: {result.error}"
        assert result.unwrap() is True

    def test_validate_attribute_empty_oid(self) -> None:
        """Test validating attribute with empty OID."""
        attr = FlextLdifModels.SchemaAttribute(
            oid="",
            name="cn",
        )

        service = FlextLdifSchema()
        result = service.validate_attribute(attr)

        assert result.is_failure, "Should fail for empty OID"
        assert "oid" in result.error.lower()

    def test_validate_attribute_empty_name(self) -> None:
        """Test validating attribute with empty name."""
        attr = FlextLdifModels.SchemaAttribute(
            oid="2.5.4.3",
            name="",
        )

        service = FlextLdifSchema()
        result = service.validate_attribute(attr)

        assert result.is_failure, "Should fail for empty name"
        assert "name" in result.error.lower()

    def test_validate_objectclass_valid(self) -> None:
        """Test validating valid objectClass model."""
        oc = FlextLdifModels.SchemaObjectClass(
            oid="2.5.6.6",
            name="person",
            must=["sn", "cn"],
        )

        service = FlextLdifSchema()
        result = service.validate_objectclass(oc)

        assert result.is_success, f"Should validate valid objectClass: {result.error}"
        assert result.unwrap() is True

    def test_validate_objectclass_empty_oid(self) -> None:
        """Test validating objectClass with empty OID."""
        oc = FlextLdifModels.SchemaObjectClass(
            oid="",
            name="person",
        )

        service = FlextLdifSchema()
        result = service.validate_objectclass(oc)

        assert result.is_failure, "Should fail for empty OID"
        assert "oid" in result.error.lower()

    def test_validate_objectclass_empty_name(self) -> None:
        """Test validating objectClass with empty name."""
        oc = FlextLdifModels.SchemaObjectClass(
            oid="2.5.6.6",
            name="",
        )

        service = FlextLdifSchema()
        result = service.validate_objectclass(oc)

        assert result.is_failure, "Should fail for empty name"
        assert "name" in result.error.lower()
