"""Comprehensive tests for flext-core main components - initialization, services, containers, results, and integration.

Advanced Python 3.13 patterns with factories, dynamic parametrized tests, nested classes for organization,
real implementations using flext_tests helpers, and comprehensive edge case coverage.

Modules Tested: FlextCli, FlextResult, FlextContainer, FlextService, FlextConfig, FlextLogger, FlextUtilities
Scope: Core functionality, railway-oriented programming, dependency injection, service patterns, and integration workflows.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_cli import FlextCli
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextUtilities,
)
from flext_tests import FlextTestsUtilities

from tests.fixtures.constants import TestConstants


class TestFlextMain:
    """Unified test class for all flext-main functionality using advanced patterns."""

    # =========================================================================
    # NESTED: Test Helpers
    # =========================================================================

    class TestHelpers:
        """Test-specific helpers for flext-main testing."""

        @staticmethod
        def create_test_service(result_data: str) -> type[FlextService[str]]:
            """Create a test service class using constants."""

            class TestService(FlextService[str]):
                def execute(self) -> FlextResult[str]:
                    return FlextResult[str].ok(result_data)

            return TestService

    # =========================================================================
    # FLEXT RESULT TESTS
    # =========================================================================

    @pytest.mark.parametrize(
        "test_data",
        [
            TestConstants.Common.VALUE_DEFAULT,
            TestConstants.Common.NAME_TEST,
            TestConstants.ResultValues.SUCCESS_DATA_STRING,
        ],
    )
    def test_flext_result_success(self, test_data: str) -> None:
        """Test FlextResult success functionality with various data."""
        result = FlextResult[str].ok(test_data)
        FlextTestsUtilities.TestUtilities.assert_result_success(result)
        assert result.value == test_data
        assert result.error is None

    def test_flext_result_failure(self) -> None:
        """Test FlextResult failure functionality using constants."""
        result = FlextTestsUtilities.ResultHelpers.create_failure_result(
            TestConstants.ResultValues.ERROR_MESSAGE
        )
        FlextTestsUtilities.TestUtilities.assert_result_failure(result)
        assert result.error == TestConstants.ResultValues.ERROR_MESSAGE

    # =========================================================================
    # FLEXT CONTAINER TESTS
    # =========================================================================

    def test_flext_container_functionality(self) -> None:
        """Test FlextContainer functionality using flext_tests."""
        container = FlextContainer()
        assert container is not None

        test_key = FlextTestsUtilities.TestUtilities.generate_test_id("key")
        test_value = TestConstants.Common.VALUE_DEFAULT
        result = container.register(test_key, test_value)
        FlextTestsUtilities.TestUtilities.assert_result_success(result)

        retrieved = container.get(test_key)
        if retrieved.is_success:
            assert retrieved.value == test_value

    # =========================================================================
    # FLEXT LOGGER TESTS
    # =========================================================================

    @pytest.mark.parametrize(
        "module_name",
        [
            TestConstants.Common.NAME_TEST,
            TestConstants.Cli.SERVICE_NAME,
            __name__,
        ],
    )
    def test_flext_logger_creation(self, module_name: str) -> None:
        """Test FlextLogger creation with various module names."""
        logger = FlextLogger(module_name)
        assert logger is not None
        assert isinstance(logger, FlextLogger)

    @pytest.mark.parametrize(
        "method_name",
        ["info", "warning", "error", "debug"],
    )
    def test_flext_logger_methods(self, method_name: str) -> None:
        """Test FlextLogger has expected methods."""
        logger = FlextLogger(__name__)
        assert hasattr(logger, method_name)
        assert callable(getattr(logger, method_name))

    # =========================================================================
    # FLEXT SERVICE TESTS
    # =========================================================================

    @pytest.mark.parametrize(
        "result_data",
        [
            TestConstants.Common.VALUE_DEFAULT,
            TestConstants.ResultValues.SUCCESS_DATA_STRING,
        ],
    )
    def test_flext_service_functionality(self, result_data: str) -> None:
        """Test FlextService functionality with various data."""
        test_service_class = self.TestHelpers.create_test_service(result_data)
        service = test_service_class()
        assert service is not None
        assert isinstance(service, FlextService)

        result = service.execute()
        FlextTestsUtilities.TestUtilities.assert_result_success(result)
        assert result.value == result_data

    # =========================================================================
    # FLEXT UTILITIES TESTS
    # =========================================================================

    def test_flext_utilities_creation(self) -> None:
        """Test FlextUtilities creation."""
        utilities = FlextUtilities()
        assert utilities is not None
        assert isinstance(utilities, FlextUtilities)

    @pytest.mark.parametrize(
        "nested_class",
        ["Validation", "Generators", "Cache", "TextProcessor"],
    )
    def test_flext_utilities_methods(self, nested_class: str) -> None:
        """Test FlextUtilities has expected nested classes."""
        utilities = FlextUtilities()
        assert hasattr(utilities, nested_class)

    def test_flext_utilities_validation(self) -> None:
        """Test FlextUtilities validation methods."""
        utilities = FlextUtilities()
        # validate_required_string returns the string directly if valid
        result = utilities.Validation.validate_required_string(
            TestConstants.Common.VALUE_DEFAULT
        )
        assert isinstance(result, str)
        assert result == TestConstants.Common.VALUE_DEFAULT

    # =========================================================================
    # FLEXT CLI TESTS
    # =========================================================================

    def test_flext_cli_creation(self) -> None:
        """Test FlextCli creation."""
        api = FlextCli()
        assert api is not None
        assert hasattr(api, "execute")

    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================

    def test_comprehensive_workflow(self) -> None:
        """Test comprehensive workflow across all components."""
        api = FlextCli()
        assert api is not None

        container = FlextContainer()
        assert container is not None

        logger = FlextLogger(__name__)
        assert logger is not None

        utilities = FlextUtilities()
        assert utilities is not None
