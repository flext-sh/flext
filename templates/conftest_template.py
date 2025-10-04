"""Test configuration template for FLEXT projects.

This template provides standard fixtures and configuration that all FLEXT projects
should implement. Copy and customize this file for your project's tests/conftest.py.

Usage:
1. Copy this file to your project's tests/conftest.py
2. Uncomment sections relevant to your project type
3. Add project-specific fixtures as needed
4. Ensure all imports work with your project's dependencies

Version: 1.0.0
Standards: FLEXT_TESTING_STANDARDS.md
Based on: flext-core proven patterns
"""

import os
from collections.abc import Generator
from unittest.mock import Mock

import pytest
from flext_core import FlextTypes

# FLEXT Core imports (adjust path if needed)
try:
    from flext_core import FlextContainer, FlextLogger

    FLEXT_CORE_AVAILABLE = True
except ImportError:
    FLEXT_CORE_AVAILABLE = False


# =============================================================================
# CORE FIXTURES (ALL PROJECTS)
# =============================================================================


@pytest.fixture
def clean_container() -> Generator[object]:
    """Provide a clean dependency injection container for isolated testing.

    This fixture ensures each test gets a fresh container without any
    previously registered services, preventing test interference.
    """
    if FLEXT_CORE_AVAILABLE:
        container = FlextContainer()
        yield container
        container.clear()
    else:
        # Mock container for projects without flext-core
        mock_container = Mock()
        mock_container.register = Mock(return_value=Mock(is_success=True))
        mock_container.get = Mock(return_value=Mock(is_success=True, unwrap=Mock()))
        yield mock_container


@pytest.fixture
def logger() -> Mock | object:
    """Provide a test logger instance.

    Returns a properly configured logger for testing purposes.
    Captures log output for test assertions.
    """
    if FLEXT_CORE_AVAILABLE:
        return FlextLogger("test")
    # Mock logger for projects without flext-core
    mock_logger = Mock()
    mock_logger.info = Mock()
    mock_logger.warning = Mock()
    mock_logger.error = Mock()
    mock_logger.debug = Mock()
    return mock_logger


@pytest.fixture
def sample_data() -> FlextTypes.Dict:
    """Provide standard sample data for testing.

    Customize this fixture with data relevant to your domain.
    """
    return {
        "id": "test-id-123",
        "name": "Test Item",
        "description": "Test description",
        "created_at": "2025-09-26T10:00:00Z",
        "is_active": True,
        "metadata": {"version": "1.0", "source": "test"},
    }


@pytest.fixture
def invalid_data() -> FlextTypes.Dict:
    """Provide invalid data for error testing.

    Use this fixture to test validation and error handling paths.
    """
    return {
        "id": "",  # Invalid empty ID
        "name": None,  # Invalid None name
        "description": "x" * 1000,  # Invalid too long description
        "created_at": "invalid-date",  # Invalid date format
        "is_active": "not_boolean",  # Invalid boolean
    }


# =============================================================================
# DOMAIN-SPECIFIC FIXTURES (UNCOMMENT AS NEEDED)
# =============================================================================

# FOR USER/ACCOUNT DOMAIN PROJECTS
# @pytest.fixture
# def sample_user_data() -> FlextTypes.Dict:
#     """Provide valid user data for testing."""
#     return {
#         "name": "Test User",
#         "email": "test@example.com",
#         "age": 30,
#         "role": "user",
#         "is_active": True
#     }

# @pytest.fixture
# def invalid_user_data() -> FlextTypes.Dict:
#     """Provide invalid user data for error testing."""
#     return {
#         "name": "",  # Empty name
#         "email": "invalid-email",  # Invalid email format
#         "age": -5,  # Invalid age
#         "role": "invalid_role"  # Invalid role
#     }

# FOR DATABASE PROJECTS
# @pytest.fixture(scope="session")
# def database_connection():
#     """Provide database connection for integration tests.
#
#     Scope: session - created once per test session
#     Use for integration tests that need real database connectivity.
#     """
#     # Setup database connection
#     connection = create_test_database_connection()
#     yield connection
#     # Cleanup
#     connection.close()

# @pytest.fixture
# def database_transaction(database_connection):
#     """Provide database transaction that rolls back after test.
#
#     Use this for tests that modify database state but want isolation.
#     """
#     transaction = database_connection.begin()
#     yield transaction
#     transaction.rollback()

# FOR ORACLE PROJECTS
# @pytest.fixture(scope="session")
# def oracle_client():
#     """Provide Oracle client for Oracle-specific tests."""
#     from flext_db_oracle import FlextOracleClient
#
#     config = {
#         "host": "localhost",
#         "port": 1521,
#         "service_name": "XEPDB1",
#         "username": "test",
#         "password": "test"
#     }
#
#     client = FlextOracleClient(config)
#     yield client
#     client.close()

# FOR LDAP PROJECTS
# @pytest.fixture(scope="session")
# def ldap_connection():
#     """Provide LDAP connection for LDAP tests."""
#     from flext_ldap import FlextLdapClient
#
#     config = {
#         "server": "ldap://localhost:389",
#         "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
#         "bind_password": "REDACTED_LDAP_BIND_PASSWORD"
#     }
#
#     client = FlextLdapClient(config)
#     yield client
#     client.disconnect()

# FOR API PROJECTS
# @pytest.fixture
# def api_client():
#     """Provide test API client."""
#     from fastapi.testclient import TestClient
#     from your_project.main import app
#
#     return TestClient(app)

# @pytest.fixture
# def authenticated_headers() -> Dict[str, str]:
#     """Provide authenticated headers for API tests."""
#     return {
#         "Authorization": "Bearer test-token",
#         "Content-Type": "application/json"
#     }

# FOR CLI PROJECTS
# @pytest.fixture
# def cli_runner():
#     """Provide CLI test runner."""
#     from click.testing import CliRunner
#     return CliRunner()

# FOR MELTANO/SINGER PROJECTS
# @pytest.fixture
# def meltano_project():
#     """Provide Meltano project for testing."""
#     from meltano.core.project import Project
#
#     # Setup test project
#     project = Project.find()
#     yield project
#     # Cleanup if needed

# @pytest.fixture
# def singer_config() -> FlextTypes.Dict:
#     """Provide Singer tap/target configuration."""
#     return {
#         "host": "localhost",
#         "port": 5432,
#         "database": "test_db",
#         "username": "test",
#         "password": "test"
#     }

# FOR DBT PROJECTS
# @pytest.fixture
# def dbt_project():
#     """Provide DBT project for testing."""
#     import dbt
#
#     # Setup test DBT project
#     project = dbt.main.get_dbt_project()
#     yield project

# =============================================================================
# PERFORMANCE TESTING FIXTURES
# =============================================================================


@pytest.fixture
def performance_threshold() -> FlextTypes.FloatDict:
    """Provide performance thresholds for benchmark tests.

    Customize these values based on your project's performance requirements.
    """
    return {
        "max_response_time": 1.0,  # seconds
        "max_memory_usage": 100,  # MB
        "max_cpu_usage": 80,  # percentage
        "min_throughput": 1000,  # operations per second
    }


@pytest.fixture
def large_dataset() -> list:
    """Provide large dataset for performance testing.

    Adjust size based on your performance testing needs.
    """
    return [{"id": i, "value": f"item_{i}"} for i in range(10000)]


# =============================================================================
# MOCK FIXTURES
# =============================================================================


@pytest.fixture
def mock_external_service() -> Mock:
    """Provide mock external service for testing.

    Use this for testing components that depend on external services
    without making actual network calls.
    """
    mock_service = Mock()
    mock_service.call_api.return_value = {"status": "success", "data": "mock_data"}
    mock_service.is_healthy.return_value = True
    return mock_service


@pytest.fixture
def mock_repository() -> Mock:
    """Provide mock repository for testing.

    Use this for testing service layer without database dependencies.
    """
    mock_repo = Mock()
    mock_repo.save.return_value = Mock(is_success=True)
    mock_repo.find_by_id.return_value = Mock(is_success=True)
    mock_repo.delete.return_value = Mock(is_success=True)
    return mock_repo


# =============================================================================
# FIXTURE COMBINATIONS
# =============================================================================


@pytest.fixture
def test_environment(
    clean_container: object, logger: object, sample_data: object
) -> FlextTypes.Dict:
    """Provide complete test environment with common dependencies.

    This is a convenience fixture that combines commonly used fixtures.
    """
    return {"container": clean_container, "logger": logger, "data": sample_data}


# =============================================================================
# AUTO-USE FIXTURES (GLOBAL SETUP)
# =============================================================================


@pytest.fixture(autouse=True)
def reset_global_state() -> None:
    """Reset global state before each test.

    This fixture automatically runs before each test to ensure
    clean state and prevent test interference.
    """
    # Add any global state reset logic here
    # For example:
    # - Clear global caches
    # - Reset singleton instances
    # - Clear environment variables

    return

    # Cleanup after test
    # Add any cleanup logic here


@pytest.fixture(autouse=True, scope="session")
def configure_test_environment() -> None:
    """Configure test environment for the entire test session."""
    # Set test-specific environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"

    # Cleanup session-level resources


# =============================================================================
# PYTEST CONFIGURATION HOOKS
# =============================================================================


def pytest_configure(config: object) -> None:
    """Configure pytest markers and settings.

    This function is called during pytest startup and can be used
    to register custom markers or configure pytest behavior.
    """
    # Markers are already defined in pyproject.toml, but you can add
    # additional configuration here if needed


def pytest_collection_modifyitems(config: object, items: FlextTypes.List) -> None:
    """Modify collected test items.

    This hook can be used to:
    - Add markers to tests based on their names or locations
    - Skip tests based on conditions
    - Reorder tests
    """
    # Example: Mark all tests in test_integration.py as integration tests
    for item in items:
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)

        # Example: Mark slow tests based on naming convention
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)


# =============================================================================
# PROJECT-SPECIFIC CONFIGURATIONS
# =============================================================================

# Add any project-specific pytest configuration here
# Examples:
# - Custom assertion helpers
# - Project-specific data generators
# - Domain-specific test utilities
# - Integration with project's dependency injection
# - Custom test parametrization helpers
