"""Modern pytest configuration and fixtures.

This module provides enterprise-grade test fixtures and configurations
that pass strict linting (ruff, mypy, bandit) and follow modern patterns.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

if TYPE_CHECKING:
    from collections.abc import Generator

# Load .env if available for integration tests
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    import dotenv

    dotenv.load_dotenv(env_file)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture
def mock_config() -> dict[str, Any]:
    """Mock configuration for testing."""
    return {
        "debug": True,
        "testing": True,
        "log_level": "DEBUG",
        "database_url": "sqlite:///:memory:",
    }


@pytest.fixture
def temp_directory(tmp_path: Path) -> Path:
    """Provide temporary directory for file operations."""
    return tmp_path


@pytest.fixture
def mock_logger() -> MagicMock:
    """Mock structured logger for testing."""
    return MagicMock()


@pytest.fixture
def integration_test_enabled() -> bool:
    """Check if integration tests should run (based on .env availability)."""
    return env_file.exists()


class TestModel(BaseModel):
    """Test model for validation testing."""

    id: int
    name: str
    active: bool = True


@pytest.fixture
def sample_model() -> TestModel:
    """Provide sample model for testing."""
    return TestModel(id=1, name="test", active=True)


@pytest.fixture
def async_mock() -> AsyncMock:
    """Provide async mock for testing async operations."""
    return AsyncMock()


@pytest.fixture
def mock_singer_catalog() -> dict[str, Any]:
    """Mock Singer catalog for tap/target testing."""
    return {
        "streams": [
            {
                "tap_stream_id": "test_stream",
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                    },
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {"inclusion": "available"},
                    }
                ],
            }
        ]
    }


@pytest.fixture
def mock_singer_state() -> dict[str, Any]:
    """Mock Singer state for testing."""
    return {
        "bookmarks": {"test_stream": {"replication_key_value": "2024-01-01T00:00:00Z"}}
    }


# Integration test markers and skips
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning"),
]


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "e2e: end-to-end tests")
    config.addinivalue_line("markers", "requires_env: tests requiring .env file")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Modify test collection to handle conditional skips."""
    for item in items:
        # Skip integration tests if .env not available
        if "requires_env" in [mark.name for mark in item.iter_markers()]:
            if not env_file.exists():
                item.add_marker(
                    pytest.mark.skip(reason=".env file not found for integration tests")
                )
