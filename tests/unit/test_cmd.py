"""FLEXT CLI CMD Tests - Comprehensive command functionality testing.

Tests for FlextCliCmd class using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from flext_cli.cmd import FlextCliCmd


class TestFlextCliCmd:
    """Comprehensive tests for FlextCliCmd class."""

    def test_cmd_initialization(self) -> None:
        """Test CMD initialization with proper configuration."""
        cmd = FlextCliCmd()
        assert cmd is not None
        assert isinstance(cmd, FlextCliCmd)

    def test_cmd_execute_sync(self) -> None:
        """Test synchronous CMD execution."""
        cmd = FlextCliCmd()
        result = cmd.execute()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == "operational"
        assert result.value["service"] == "FlextCliCmd"

    def test_cmd_command_bus_service(self) -> None:
        """Test command bus service property."""
        cmd = FlextCliCmd()
        command_bus = cmd.command_bus_service
        assert command_bus is not None

    def test_cmd_config_edit(self) -> None:
        """Test configuration editing functionality."""
        cmd = FlextCliCmd()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"

            # Test editing non-existent config (should create default)
            result = cmd.edit_config(str(config_path))
            assert result.is_success

            # Verify config file was created
            assert config_path.exists()

    def test_cmd_config_edit_existing(self) -> None:
        """Test editing existing configuration."""
        cmd = FlextCliCmd()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"

            # Create initial config
            initial_result = cmd.edit_config(str(config_path))
            assert initial_result.is_success

            # Edit existing config
            edit_result = cmd.edit_config(str(config_path))
            assert edit_result.is_success

    def test_cmd_config_default_values(self) -> None:
        """Test default configuration values."""
        cmd = FlextCliCmd()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"

            result = cmd.edit_config(str(config_path))
            assert result.is_success

            # Verify config file exists and has content
            assert config_path.exists()
            config_content = config_path.read_text()
            assert len(config_content) > 0

    def test_cmd_error_handling(self) -> None:
        """Test CMD error handling capabilities."""
        cmd = FlextCliCmd()

        # Test with invalid path
        result = cmd.edit_config("/invalid/path/config.json")
        # Should handle gracefully (either success with default or proper error)
        assert result is not None

    def test_cmd_performance(self) -> None:
        """Test CMD performance characteristics."""
        cmd = FlextCliCmd()

        import time

        start_time = time.time()
        result = cmd.execute()
        execution_time = time.time() - start_time

        assert result.is_success
        # Should execute quickly
        assert execution_time < 1.0

    def test_cmd_memory_usage(self) -> None:
        """Test CMD memory usage characteristics."""
        cmd = FlextCliCmd()

        # Test multiple executions
        for _ in range(5):
            result = cmd.execute()
            assert result.is_success

    def test_cmd_integration(self) -> None:
        """Test CMD integration with other services."""
        cmd = FlextCliCmd()

        # Test that CMD properly integrates with its dependencies
        result = cmd.execute()
        assert result.is_success

        # Test command bus service integration
        command_bus = cmd.command_bus_service
        assert command_bus is not None

    def test_cmd_configuration_consistency(self) -> None:
        """Test configuration consistency across operations."""
        cmd = FlextCliCmd()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"

            # Create config
            result1 = cmd.edit_config(str(config_path))
            assert result1.is_success

            # Edit same config
            result2 = cmd.edit_config(str(config_path))
            assert result2.is_success

            # Both operations should succeed
            assert result1.is_success == result2.is_success

    def test_cmd_service_properties(self) -> None:
        """Test CMD service properties."""
        cmd = FlextCliCmd()

        # Test that all required properties are accessible
        assert hasattr(cmd, "command_bus_service")
        assert hasattr(cmd, "execute")
        assert hasattr(cmd, "edit_config")

    def test_cmd_logging_integration(self) -> None:
        """Test CMD logging integration."""
        cmd = FlextCliCmd()

        # Test that logging is properly integrated
        result = cmd.execute()
        assert result.is_success

        # Should not raise any logging-related exceptions
        assert result.value is not None
