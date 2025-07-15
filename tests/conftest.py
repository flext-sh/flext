"""Pytest configuration for FLEXT workspace tests.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Set test environment
os.environ["FLEXT_ENV"] = "testing"
os.environ["FLEXT_DEBUG"] = "true"

# Add src to Python path
import sys

workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root / "src"))

# Import after path setup
from flext_core import FlextContainer, configure_container


@pytest.fixture(scope="session")
def workspace_root() -> Path:
    """Get workspace root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def di_container() -> FlextContainer:
    """Get a fresh DI container for each test."""
    container = FlextContainer()
    configure_container(container)
    return container


@pytest.fixture(scope="session")
def test_venv_path(workspace_root: Path) -> Path:
    """Get virtual environment path."""
    return workspace_root / ".venv"


@pytest.fixture(scope="session")
def python_executable(test_venv_path: Path) -> Path:
    """Get Python executable in venv."""
    return test_venv_path / "bin" / "python"


# Pytest configuration
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (may require external services)",
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running",
    )
    config.addinivalue_line(
        "markers",
        "docker: mark test as requiring Docker",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add integration marker to all tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add slow marker to integration tests by default
        if item.get_closest_marker("integration"):
            item.add_marker(pytest.mark.slow)
