"""FLEXT LDIF Exceptions - Comprehensive Unit Tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_ldif.exceptions import FlextLdifExceptions


@pytest.mark.unit
class TestFlextLdifExceptions:
    """Comprehensive tests for FlextLdifExceptions factory methods."""

    def test_validation_error_creation(self) -> None:
        """Test validation error FlextResult creation."""
        result = FlextLdifExceptions.validation_error("Test validation error")

        assert result is not None
        assert result.is_failure
        assert "Test validation error" in str(result.error)

    def test_validation_error_with_field(self) -> None:
        """Test validation error creation with field information."""
        result = FlextLdifExceptions.validation_error(
            "Test validation error", field="test_field", value="test_value"
        )

        assert result is not None
        assert result.is_failure
        assert "Test validation error" in str(result.error)

    def test_parse_error_creation(self) -> None:
        """Test parse error FlextResult creation."""
        result = FlextLdifExceptions.parse_error("Parse error message")

        assert result is not None
        assert result.is_failure
        assert "Parse error message" in str(result.error)

    def test_processing_error_creation(self) -> None:
        """Test processing error FlextResult creation."""
        result = FlextLdifExceptions.processing_error("Processing error message")

        assert result is not None
        assert result.is_failure
        assert "Processing error message" in str(result.error)

    def test_processing_error_with_operation(self) -> None:
        """Test processing error creation with operation information."""
        result = FlextLdifExceptions.processing_error(
            "Processing error message",
            business_rule="test_rule",
            operation="test_operation",
        )

        assert result is not None
        assert result.is_failure
        assert "Processing error message" in str(result.error)

    def test_file_error_creation(self) -> None:
        """Test file error FlextResult creation."""
        result = FlextLdifExceptions.file_error("File error message")

        assert result is not None
        assert result.is_failure
        assert "File error message" in str(result.error)

    def test_exception_from_dict(self) -> None:
        """Test creating error from dictionary data."""
        error_dict = {
            "message": "Test error from dict",
            "error_code": "DICT_ERROR",
            "details": {"key": "value"},
        }

        result = FlextLdifExceptions.validation_error(
            error_dict["message"], field="test_field"
        )

        assert result is not None
        assert result.is_failure
        assert error_dict["message"] in str(result.error)
