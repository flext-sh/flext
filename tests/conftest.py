"""Centralized pytest configuration and fixtures for all tests.

Provides dependency injection for c, t, p, m, u objects and shared fixtures.
Follows FLEXT architecture with centralized fixture management.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

import pytest

from flext_tests import (
    FlextTestsConstants,
    FlextTestsModels,
    FlextTestsProtocols,
    FlextTestsTypes,
    FlextTestsUtilities,
)


@pytest.fixture(scope="session")
def c() -> type[FlextTestsConstants]:
    """Constants facade for test configuration and parametrization.

    Returns:
        The FlextTestsConstants facade class.

    """
    return FlextTestsConstants


@pytest.fixture(scope="session")
def t() -> type[FlextTestsTypes]:
    """Types facade for type aliases and protocols.

    Returns:
        The FlextTestsTypes facade class.

    """
    return FlextTestsTypes


@pytest.fixture(scope="session")
def p() -> type[FlextTestsProtocols]:
    """Protocols facade for interface contracts.

    Returns:
        The FlextTestsProtocols facade class.

    """
    return FlextTestsProtocols


@pytest.fixture(scope="session")
def m() -> type[FlextTestsModels]:
    """Models facade for Pydantic test models.

    Returns:
        The FlextTestsModels facade class.

    """
    return FlextTestsModels


@pytest.fixture(scope="session")
def u() -> type[FlextTestsUtilities]:
    """Utilities facade for test helpers and builders.

    Returns:
        The FlextTestsUtilities facade class.

    """
    return FlextTestsUtilities


@pytest.fixture(scope="session")
def test_fixtures_dir() -> Path:
    """Path to the centralized test fixtures directory.

    Returns:
        Path to fixtures directory.

    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Path to test data files.

    Returns:
        Path to test data directory.

    """
    return Path(__file__).parent / "fixtures" / "data"


@pytest.fixture
def reset_global_state() -> None:
    """Reset any global state before each test to ensure isolation."""
    return


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers.

    Args:
        config: The pytest config object.

    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
