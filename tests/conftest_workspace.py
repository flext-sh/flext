"""Centralized pytest configuration for FLEXT workspace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from flext_core import FlextCore
from flext_tests import (
    FlextTestsBuilders,
    FlextTestsDomains,
    FlextTestsFactories,
    FlextTestsMatchers,
)


class FileManager:
    """Simple file manager for tests."""

    def __init__(self, temp_dir: Path) -> None:
        """Initialize FileManager with temporary directory."""
        self.temp_dir = temp_dir

    def create_file(self, filename: str, content: str) -> Path:
        """Create a temporary file with content."""
        file_path = self.temp_dir / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path


# =============================================================================
# CORE FLEXT FIXTURES
# =============================================================================


@pytest.fixture
def flext_container() -> FlextCore.Container:
    """Provide FlextCore.Container instance for tests."""
    return FlextCore.Container.get_global()


@pytest.fixture
def flext_logger() -> FlextCore.Logger:
    """Provide FlextCore.Logger instance for tests."""
    return FlextCore.Logger(__name__)


@pytest.fixture
def flext_result_success() -> FlextCore.Result[FlextCore.Types.Dict]:
    """Provide successful FlextCore.Result for tests."""
    return FlextCore.Result[FlextCore.Types.Dict].ok({"success": True})


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Provide temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_file_manager(temp_dir: Path) -> FileManager:
    """Provide test file manager for tests."""
    return FileManager(temp_dir)


@pytest.fixture
def flext_result_failure() -> FlextCore.Result[FlextCore.Types.Dict]:
    """Provide failed FlextCore.Result for tests."""
    return FlextCore.Result[FlextCore.Types.Dict].fail("Test error")


# =============================================================================
# TEST DATA FACTORIES
# =============================================================================


@pytest.fixture
def flext_builders() -> FlextTestsBuilders:
    """Provide FlextTestsBuilders for test data creation."""
    return FlextTestsBuilders()


@pytest.fixture
def flext_domains() -> FlextTestsDomains:
    """Provide FlextTestsDomains for test data creation."""
    return FlextTestsDomains()


@pytest.fixture
def flext_factories() -> FlextTestsFactories:
    """Provide FlextTestsFactories for test data creation."""
    return FlextTestsFactories()


@pytest.fixture
def flext_matchers() -> FlextTestsMatchers:
    """Provide FlextTestsMatchers for test assertions."""
    return FlextTestsMatchers()


# =============================================================================
# TEST DATA FIXTURES
# =============================================================================


@pytest.fixture
def test_user_data() -> FlextCore.Types.Dict:
    """Provide test user data."""
    return FlextTestsDomains.create_user()


@pytest.fixture
def test_config_data() -> FlextCore.Types.Dict:
    """Provide test configuration data."""
    return FlextTestsDomains.create_configuration()


@pytest.fixture
def test_service_data() -> FlextCore.Types.Dict:
    """Provide test service data."""
    return FlextTestsDomains.create_service()


@pytest.fixture
def test_payload_data() -> FlextCore.Types.Dict:
    """Provide test payload data."""
    return FlextTestsDomains.create_payload()


@pytest.fixture
def batch_user_data() -> list[FlextCore.Types.Dict]:
    """Provide batch of test user data."""
    return FlextTestsDomains.batch_users(5)


# =============================================================================
# VALIDATION TEST DATA
# =============================================================================


@pytest.fixture
def valid_email_cases() -> FlextCore.Types.StringList:
    """Provide valid email test cases."""
    return FlextTestsDomains.valid_email_cases()


@pytest.fixture
def invalid_email_cases() -> FlextCore.Types.StringList:
    """Provide invalid email test cases."""
    return FlextTestsDomains.invalid_email_cases()


@pytest.fixture
def valid_ages() -> FlextCore.Types.IntList:
    """Provide valid age test cases."""
    return FlextTestsDomains.valid_ages()


@pytest.fixture
def invalid_ages() -> FlextCore.Types.IntList:
    """Provide invalid age test cases."""
    return FlextTestsDomains.invalid_ages()


# =============================================================================
# REALISTIC TEST DATA
# =============================================================================


@pytest.fixture
def user_registration_data() -> FlextCore.Types.Dict:
    """Provide realistic user registration data."""
    return FlextTestsDomains.user_registration_data()


@pytest.fixture
def order_data() -> FlextCore.Types.Dict:
    """Provide realistic order data."""
    return FlextTestsDomains.order_data()


@pytest.fixture
def api_response_data() -> FlextCore.Types.Dict:
    """Provide realistic API response data."""
    return FlextTestsDomains.api_response_data()


# =============================================================================
# TEMPORARY RESOURCES
# =============================================================================


@pytest.fixture
def temp_directory() -> Generator[Path]:
    """Provide temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_file(temp_directory: Path) -> Path:
    """Provide temporary file for tests."""
    return temp_directory / "test_file.txt"


@pytest.fixture
def test_file_manager_alternative(temp_directory: Path) -> FileManager:
    """Provide test file manager for tests."""
    return FileManager(temp_directory)


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line("markers", "slow: marks tests as slow tests")
    config.addinivalue_line("markers", "docker: marks tests that require Docker")
    config.addinivalue_line("markers", "oracle: marks tests specific to Oracle")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "stress: marks tests as stress tests")
    config.addinivalue_line("markers", "resilience: marks tests as resilience tests")
    config.addinivalue_line("markers", "integrity: marks tests as integrity tests")
    config.addinivalue_line("markers", "edge_cases: marks tests as edge case tests")
    config.addinivalue_line("markers", "real: marks tests using real functionality")
    config.addinivalue_line("markers", "auth: marks tests as authentication tests")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add unit marker to tests in unit directories
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add integration marker to tests in integration directories
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add e2e marker to tests in e2e directories
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

        # Add docker marker to tests that mention docker
        if "docker" in str(item.fspath).lower():
            item.add_marker(pytest.mark.docker)

        # Add oracle marker to tests that mention oracle
        if "oracle" in str(item.fspath).lower():
            item.add_marker(pytest.mark.oracle)


@pytest.fixture
def sample_ldif_entries() -> str:
    """Sample LDIF entries for testing."""
    return """dn: cn=John Doe,ou=people,dc=example,dc=com
objectClass: inetOrgPerson
cn: John Doe
sn: Doe
mail: john.doe@example.com

dn: cn=Jane Smith,ou=people,dc=example,dc=com
objectClass: inetOrgPerson
cn: Jane Smith
sn: Smith
mail: jane.smith@example.com

dn: ou=groups,dc=example,dc=com
objectClass: organizationalUnit
ou: groups
description: Groups organizational unit
"""
