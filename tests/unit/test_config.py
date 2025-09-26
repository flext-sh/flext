"""FLEXT CLI Config Tests - Comprehensive configuration functionality testing.

Tests for FlextCliConfig classes using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from flext_cli.config import (
    FlextCliConfig,
    FlextCliConfigService,
)
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels


class TestFlextCliConfig:
    """Comprehensive tests for FlextCliConfig class."""

    def test_config_initialization(self) -> None:
        """Test Config initialization with proper configuration."""
        config = FlextCliConfig()
        assert config is not None
        assert isinstance(config, FlextCliConfig)

    def test_config_default_values(self) -> None:
        """Test config default values."""
        config = FlextCliConfig()

        # Test that config has expected default values
        assert config.debug is False
        assert config.verbose is False
        assert config.quiet is False

    def test_config_custom_values(self) -> None:
        """Test config with custom values."""
        config = FlextCliConfig(debug=True, verbose=True, quiet=False)

        assert config.debug is True
        assert config.verbose is True
        assert config.quiet is False

    def test_config_validation(self) -> None:
        """Test config validation."""
        config = FlextCliConfig()

        # Test that config validates properly
        assert config.debug is not None
        assert config.verbose is not None
        assert config.quiet is not None

    def test_config_serialization(self) -> None:
        """Test config serialization."""
        config = FlextCliConfig(debug=True, verbose=False)

        # Test dict conversion
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert config_dict["debug"] is True
        assert config_dict["verbose"] is False

    def test_config_deserialization(self) -> None:
        """Test config deserialization."""
        config_data = {"debug": True, "verbose": False, "quiet": True}

        config = FlextCliConfig.model_validate(config_data)
        assert config.debug is True
        assert config.verbose is False
        assert config.quiet is True


class TestLoggingConfig:
    """Comprehensive tests for LoggingConfig class."""

    def test_logging_config_initialization(self) -> None:
        """Test LoggingConfig initialization."""
        logging_config = FlextCliModels.LoggingConfig()
        assert logging_config is not None
        assert isinstance(logging_config, FlextCliModels.LoggingConfig)

    def test_logging_config_default_values(self) -> None:
        """Test logging config default values."""
        logging_config = FlextCliModels.LoggingConfig()

        # Test that logging config has expected default values
        assert logging_config.level is not None
        assert logging_config.format is not None

    def test_logging_config_custom_values(self) -> None:
        """Test logging config with custom values."""
        logging_config = FlextCliModels.LoggingConfig(
            level="DEBUG", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        assert logging_config.level == "DEBUG"
        assert "%(asctime)s" in logging_config.format


class TestCliOptions:
    """Comprehensive tests for CliOptions class."""

    def test_cli_options_initialization(self) -> None:
        """Test CliOptions initialization."""
        cli_options = FlextCliConfig.CliOptions()
        assert cli_options is not None
        assert isinstance(cli_options, FlextCliConfig.CliOptions)

    def test_cli_options_default_values(self) -> None:
        """Test CLI options default values."""
        cli_options = FlextCliConfig.CliOptions()

        # Test that CLI options have expected default values
        assert cli_options.output_format is not None
        assert cli_options.timeout is not None

    def test_cli_options_custom_values(self) -> None:
        """Test CLI options with custom values."""
        cli_options = FlextCliConfig.CliOptions(output_format="json", timeout=60)

        assert cli_options.output_format == "json"
        assert cli_options.timeout == 60


class TestMainConfig:
    """Comprehensive tests for MainConfig class."""

    def test_main_config_initialization(self) -> None:
        """Test MainConfig initialization."""
        main_config = FlextCliConfig.MainConfig()
        assert main_config is not None
        assert isinstance(main_config, FlextCliConfig.MainConfig)

    def test_main_config_default_values(self) -> None:
        """Test main config default values."""
        main_config = FlextCliConfig.MainConfig()

        # Test that main config has expected default values
        assert main_config.profile is not None
        assert main_config.debug is not None
        assert main_config.verbose is not None

    def test_main_config_custom_values(self) -> None:
        """Test main config with custom values."""
        main_config = FlextCliConfig.MainConfig(
            profile="test_profile", debug=True, verbose=False
        )

        assert main_config.profile == "test_profile"
        assert main_config.debug is True
        assert main_config.verbose is False


class TestFlextCliConfigService:
    """Comprehensive tests for FlextCliConfigService class."""

    def test_config_service_initialization(self) -> None:
        """Test ConfigService initialization."""
        config_service = FlextCliConfigService()
        assert config_service is not None
        assert isinstance(config_service, FlextCliConfigService)

    def test_config_service_execute_sync(self) -> None:
        """Test synchronous ConfigService execution."""
        config_service = FlextCliConfigService()
        result = config_service.execute()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == "flext-cli-config"

    @pytest.mark.asyncio
    async def test_config_service_execute_async(self) -> None:
        """Test asynchronous ConfigService execution."""
        config_service = FlextCliConfigService()
        result = await config_service.execute_async()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == "flext-cli-config"

    def test_config_service_load_config(self) -> None:
        """Test config loading functionality."""
        config_service = FlextCliConfigService()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"

            # Create a test config file
            test_config = {"debug": True, "verbose": False, "quiet": False}
            config_path.write_text(str(test_config).replace("'", '"'))

            # Test loading config
            result = config_service.load_config(str(config_path))
            assert result.is_success

    def test_config_service_save_config(self) -> None:
        """Test config saving functionality."""
        config_service = FlextCliConfigService()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"

            # Create a test config
            test_config = FlextCliConfig(debug=True, verbose=False)

            # Test saving config
            result = config_service.save_config(str(config_path), test_config)
            assert result.is_success

            # Verify file was created
            assert config_path.exists()

    def test_config_service_error_handling(self) -> None:
        """Test config service error handling."""
        config_service = FlextCliConfigService()

        # Test with invalid path
        result = config_service.load_config("/invalid/path/config.json")
        # Should handle gracefully
        assert result is not None

    def test_config_service_performance(self) -> None:
        """Test config service performance."""
        config_service = FlextCliConfigService()

        import time

        start_time = time.time()
        result = config_service.execute()
        execution_time = time.time() - start_time

        assert result.is_success
        # Should execute quickly
        assert execution_time < 1.0

    def test_config_service_integration(self) -> None:
        """Test config service integration."""
        config_service = FlextCliConfigService()

        # Test that config service properly integrates with its dependencies
        result = config_service.execute()
        assert result.is_success

        # Test async version
        import asyncio

        async_result = asyncio.run(config_service.execute_async())
        assert async_result.is_success

    def test_config_service_file_operations(self) -> None:
        """Test config service file operations."""
        config_service = FlextCliConfigService()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"

            # Test save and load cycle
            test_config = FlextCliConfig(debug=True)

            # Save config
            save_result = config_service.save_config(str(config_path), test_config)
            assert save_result.is_success

            # Load config
            load_result = config_service.load_config(str(config_path))
            assert load_result.is_success
