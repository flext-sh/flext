"""FLEXT Workspace Root Conftest - Centralized pytest configuration and fixtures.

This module provides centralized pytest configuration and shared fixtures for the entire FLEXT workspace.
All fixtures are available across all test modules without explicit imports.

Configuration:
    - pytest_plugins: Registers fixture modules for the entire workspace
    - Warnings: Configures warning filters for clean test output
    - Markers: Defines custom pytest markers for test categorization

Available fixture modules:
    - tests.fixtures.standard_fixtures: Standard reusable fixtures
    - tests.fixtures.docker_fixtures: Docker-specific integration test fixtures
"""

from __future__ import annotations

import warnings

import pytest
from flext_core import FlextCore

# Register fixture modules for the entire workspace
# pytest_plugins will be added as fixtures are implemented
pytest_plugins = []

# Configure warnings for clean test output
warnings.filterwarnings(
    "ignore",
    message=".*pkg_resources.*",
    category=DeprecationWarning,
)


# Custom pytest markers for test categorization
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "docker: marks tests that require Docker")


@pytest.fixture(autouse=True)
def _reset_flext_core_state() -> None:
    """Ensure FlextCore global state does not leak between tests.

    This preserves singleton identity while clearing per-test specialized configs,
    preventing cross-test interference (e.g., logging_config set in one test
    affecting another expecting default None).
    """
    core = FlextCore.get_instance()
    # Clear specialized configurations that tests may set/inspect
    core._specialized_configs.pop("database_config", None)
    core._specialized_configs.pop("security_config", None)
    core._specialized_configs.pop("logging_config", None)
