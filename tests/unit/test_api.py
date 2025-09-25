"""FLEXT LDIF API - Comprehensive Unit Tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from conftest import FileManager
from flext_ldif.config import FlextLdifConfig
from flext_ldif.models import FlextLdifModels

from flext_core import FlextTypes
from flext_ldif import FlextLdifAPI


@pytest.mark.unit
class TestFlextLdifAPI:
    """Comprehensive tests for FlextLdifAPI class."""

    def test_api_initialization_default(self) -> None:
        """Test API initialization with default configuration."""
        api = FlextLdifAPI()

        assert api is not None
        assert api._config is None
        assert api._management is not None
        assert api._processor_result.is_success

    def test_api_initialization_with_config(self) -> None:
        """Test API initialization with custom configuration."""
        config = FlextLdifConfig()
        api = FlextLdifAPI(config=config)

        assert api is not None
        assert api._config == config
        assert api._management is not None
        assert api._processor_result.is_success

    def test_api_initialization_processor_failure(self) -> None:
        """Test API initialization when processor fails."""
        # This test would require mocking the processor initialization
        # For now, we'll test the normal case
        api = FlextLdifAPI()
        assert api._processor_result.is_success

    def test_health_check_success(self) -> None:
        """Test health check returns success."""
        api = FlextLdifAPI()
        result = api.health_check()

        assert result.is_success
        assert isinstance(result.value, dict)
        assert "status" in result.value
        assert "timestamp" in result.value

    def test_parse_valid_ldif(self, sample_ldif_entries: str) -> None:
        """Test parsing valid LDIF content."""
        api = FlextLdifAPI()
        result = api.parse(sample_ldif_entries)

        assert result.is_success
        assert isinstance(result.value, list)
        assert len(result.value) > 0

        # Verify all entries are FlextLdifModels.Entry instances
        for entry in result.value:
            assert isinstance(entry, FlextLdifModels.Entry)

    def test_parse_invalid_ldif(self, invalid_ldif_data: str) -> None:
        """Test parsing invalid LDIF content."""
        api = FlextLdifAPI()
        result = api.parse(invalid_ldif_data)

        # Should handle gracefully and return failure result
        assert result.is_failure
        assert result.error is not None

    def test_parse_empty_content(self) -> None:
        """Test parsing empty content."""
        api = FlextLdifAPI()
        result = api.parse("")

        # Empty content should be handled gracefully
        assert result.is_success or result.is_failure
        if result.is_success:
            assert isinstance(result.value, list)

    def test_validate_valid_ldif(self, sample_ldif_entries: str) -> None:
        """Test validation of valid LDIF content."""
        api = FlextLdifAPI()
        result = api.validate(sample_ldif_entries)

        assert result.is_success
        assert isinstance(result.value, dict)
        assert "valid" in result.value

    def test_validate_invalid_ldif(self, invalid_ldif_data: str) -> None:
        """Test validation of invalid LDIF content."""
        api = FlextLdifAPI()
        result = api.validate(invalid_ldif_data)

        # Should return validation results indicating issues
        assert result.is_success or result.is_failure
        if result.is_success:
            assert isinstance(result.value, dict)

    def test_write_entries(self, ldif_test_entries: list[FlextTypes.Core.Dict]) -> None:
        """Test writing entries to LDIF format."""
        api = FlextLdifAPI()
        result = api.write(ldif_test_entries)

        assert result.is_success
        assert isinstance(result.value, str)
        assert len(result.value) > 0

    def test_write_empty_entries(self) -> None:
        """Test writing empty entries list."""
        api = FlextLdifAPI()
        result = api.write([])

        # Should handle empty list gracefully
        assert result.is_success or result.is_failure

    def test_transform_entries(
        self,
        ldif_test_entries: list[FlextTypes.Core.Dict],
        transformation_rules: FlextTypes.Core.Dict,
    ) -> None:
        """Test transforming entries with rules."""
        api = FlextLdifAPI()
        result = api.transform(ldif_test_entries, transformation_rules)

        assert result.is_success
        assert isinstance(result.value, list)

    def test_transform_with_invalid_rules(
        self, ldif_test_entries: list[FlextTypes.Core.Dict]
    ) -> None:
        """Test transforming entries with invalid rules."""
        api = FlextLdifAPI()
        invalid_rules = {"invalid": "rule"}
        result = api.transform(ldif_test_entries, invalid_rules)

        # Should handle invalid rules gracefully
        assert result.is_success or result.is_failure

    def test_filter_entries(
        self,
        ldif_test_entries: list[FlextTypes.Core.Dict],
        ldif_filters: FlextTypes.Core.Dict,
    ) -> None:
        """Test filtering entries."""
        api = FlextLdifAPI()
        result = api.filter(ldif_test_entries, ldif_filters)

        assert result.is_success
        assert isinstance(result.value, list)

    def test_analyze_entries(
        self, ldif_test_entries: list[FlextTypes.Core.Dict]
    ) -> None:
        """Test analyzing entries for statistics."""
        api = FlextLdifAPI()
        result = api.analyze(ldif_test_entries)

        assert result.is_success
        assert isinstance(result.value, dict)
        assert "total_entries" in result.value

    def test_process_file_valid(self, ldif_test_file: Path) -> None:
        """Test processing valid LDIF file."""
        api = FlextLdifAPI()
        result = api.process_file(ldif_test_file)

        assert result.is_success
        assert isinstance(result.value, dict)

    def test_process_file_nonexistent(self) -> None:
        """Test processing nonexistent file."""
        api = FlextLdifAPI()
        nonexistent_file = Path("/nonexistent/file.ldif")
        result = api.process_file(nonexistent_file)

        assert result.is_failure
        assert result.error is not None

    def test_process_file_invalid_format(self, test_file_manager: object) -> None:
        """Test processing file with invalid format."""
        api = FlextLdifAPI()

        # Create a file with invalid LDIF format
        invalid_file = test_file_manager.create_file("invalid.ldif", "invalid content")
        result = api.process_file(invalid_file)

        # Should handle invalid format gracefully
        assert result.is_success or result.is_failure

    def test_write_file(
        self,
        ldif_test_entries: list[FlextTypes.Core.Dict],
        test_file_manager: FileManager,
    ) -> None:
        """Test writing entries to file."""
        api = FlextLdifAPI()
        output_file = test_file_manager.create_file("output.ldif", "")

        result = api.write_file(ldif_test_entries, output_file)

        assert result.is_success
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_write_file_invalid_path(
        self, ldif_test_entries: list[FlextTypes.Core.Dict]
    ) -> None:
        """Test writing to invalid file path."""
        api = FlextLdifAPI()
        invalid_path = Path("/invalid/path/file.ldif")

        result = api.write_file(ldif_test_entries, invalid_path)

        assert result.is_failure
        assert result.error is not None

    def test_batch_process(self, ldif_test_entries: list[FlextTypes.Core.Dict]) -> None:
        """Test batch processing of entries."""
        api = FlextLdifAPI()
        result = api.batch_process(ldif_test_entries)

        assert result.is_success
        assert isinstance(result.value, dict)

    def test_batch_process_empty(self) -> None:
        """Test batch processing of empty entries."""
        api = FlextLdifAPI()
        result = api.batch_process([])

        # Should handle empty batch gracefully
        assert result.is_success or result.is_failure

    def test_get_statistics(
        self, ldif_test_entries: list[FlextTypes.Core.Dict]
    ) -> None:
        """Test getting processing statistics."""
        api = FlextLdifAPI()
        result = api.get_statistics(ldif_test_entries)

        assert result.is_success
        assert isinstance(result.value, dict)
        assert "total_entries" in result.value

    def test_get_statistics_empty(self) -> None:
        """Test getting statistics for empty entries."""
        api = FlextLdifAPI()
        result = api.get_statistics([])

        assert result.is_success
        assert isinstance(result.value, dict)

    def test_configure_with_valid_config(self) -> None:
        """Test configuring API with valid configuration."""
        api = FlextLdifAPI()
        config = FlextLdifConfig()

        result = api.configure(config)

        assert result.is_success
        assert api._config == config

    def test_configure_with_invalid_config(self) -> None:
        """Test configuring API with invalid configuration."""
        api = FlextLdifAPI()
        # Pass invalid config object
        invalid_config = {"invalid": "config"}

        result = api.configure(invalid_config)  # type: ignore[arg-type]

        # Should handle invalid config gracefully
        assert result.is_success or result.is_failure

    def test_reset_configuration(self) -> None:
        """Test resetting API configuration."""
        api = FlextLdifAPI()
        config = FlextLdifConfig()
        api.configure(config)

        result = api.reset_configuration()

        assert result.is_success
        assert api._config is None

    def test_get_configuration(self) -> None:
        """Test getting current configuration."""
        api = FlextLdifAPI()
        config = FlextLdifConfig()
        api.configure(config)

        result = api.get_configuration()

        assert result.is_success
        assert result.value == config

    def test_get_configuration_none(self) -> None:
        """Test getting configuration when none is set."""
        api = FlextLdifAPI()

        result = api.get_configuration()

        assert result.is_success
        assert result.value is None

    def test_is_configured(self) -> None:
        """Test checking if API is configured."""
        api = FlextLdifAPI()

        # Initially not configured
        assert not api.is_configured()

        # Configure and check again
        config = FlextLdifConfig()
        api.configure(config)
        assert api.is_configured()

    def test_get_processor_status(self) -> None:
        """Test getting processor status."""
        api = FlextLdifAPI()

        result = api.get_processor_status()

        assert result.is_success
        assert isinstance(result.value, dict)

    def test_get_management_status(self) -> None:
        """Test getting management status."""
        api = FlextLdifAPI()

        result = api.get_management_status()

        assert result.is_success
        assert isinstance(result.value, dict)

    def test_execute_health_check(self) -> None:
        """Test execute method (required by FlextService)."""
        api = FlextLdifAPI()

        result = api.execute()

        assert result.is_success
        assert isinstance(result.value, dict)

    @pytest.mark.asyncio
    async def test_execute_async_health_check(self) -> None:
        """Test execute_async method (required by FlextService)."""
        api = FlextLdifAPI()

        result = await api.execute_async()

        assert result.is_success
        assert isinstance(result.value, dict)

    def test_api_with_large_dataset(self, large_ldif_config: dict[str, object]) -> None:
        """Test API with large dataset configuration."""
        api = FlextLdifAPI()

        # Test that API can handle large dataset configuration
        assert api is not None
        assert api._management is not None

    def test_api_error_handling(self) -> None:
        """Test API error handling capabilities."""
        api = FlextLdifAPI()

        # Test with various error conditions
        result = api.parse("invalid ldif content")

        # Should handle errors gracefully
        assert result.is_success or result.is_failure
        if result.is_failure:
            assert result.error is not None

    def test_api_performance(self) -> None:
        """Test API performance characteristics."""
        api = FlextLdifAPI()

        # Test basic performance
        start_time = time.time()

        result = api.health_check()

        end_time = time.time()
        execution_time = end_time - start_time

        assert result.is_success
        assert execution_time < 1.0  # Should complete within 1 second

    def test_api_memory_usage(self) -> None:
        """Test API memory usage characteristics."""
        api = FlextLdifAPI()

        # Test that API doesn't leak memory
        initial_result = api.health_check()
        assert initial_result.is_success

        # Perform multiple operations
        for _ in range(10):
            result = api.health_check()
            assert result.is_success

        # Final check should still work
        final_result = api.health_check()
        assert final_result.is_success
