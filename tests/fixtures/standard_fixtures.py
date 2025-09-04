"""FLEXT Standard Test Fixtures - Reusable fixtures for the entire workspace.

This module provides standard, reusable pytest fixtures that are available across
the entire FLEXT workspace without explicit imports. These fixtures provide common
test data and setup that can be used by any test module.
"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def temp_workspace_dir() -> Generator[Path]:
    """Create a temporary directory for workspace operations."""
    with tempfile.TemporaryDirectory(prefix="flext_test_") as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="session")
def sample_config_file(temp_workspace_dir: Path) -> Path:
    """Create a sample configuration file for testing."""
    config_file = temp_workspace_dir / "config.yaml"
    config_content = """
workspace:
  name: test_workspace
  version: "1.0.0"
  description: Test workspace for FLEXT

projects:
  - name: flext-core
    path: ./flext-core
  - name: flext-cli
    path: ./flext-cli
"""
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def mock_ldif_content() -> str:
    """Sample LDIF content for testing."""
    return """dn: dc=example,dc=com
objectClass: top
objectClass: domain
dc: example

dn: ou=users,dc=example,dc=com
objectClass: top
objectClass: organizationalUnit
ou: users
"""


@pytest.fixture
def mock_sql_content() -> str:
    """Sample SQL content for testing."""
    return """-- Sample SQL for testing
CREATE TABLE test_table (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO test_table (name) VALUES ('test_record');
"""
