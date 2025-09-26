"""Integration tests for FlextTestDocker basic functionality.

Tests the basic Docker management functionality including:
- Docker client initialization
- Container management operations
- Error handling for non-existent containers

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_tests import FlextTestDocker


class TestFlextDockerBasic:
    """Integration tests for FlextTestDocker basic functionality."""

    @pytest.fixture(autouse=True)
    def setup_docker_manager(self) -> FlextTestDocker:
        """Setup FlextTestDocker for integration testing."""
        return FlextTestDocker()

    def test_docker_manager_initialization(
        self, setup_docker_manager: FlextTestDocker
    ) -> None:
        """Test Docker manager initialization and basic functionality."""
        docker_manager = setup_docker_manager

        # Test that the manager was initialized correctly
        assert docker_manager is not None
        assert hasattr(docker_manager, "_client")
        assert hasattr(docker_manager, "_logger")

        # Test that we can get container info (even if container doesn't exist)
        result = docker_manager.get_container_info("nonexistent-container")
        assert result.is_failure  # Should fail for non-existent container

    def test_container_management_basic_functionality(
        self, setup_docker_manager: FlextTestDocker
    ) -> None:
        """Test basic container management functionality."""
        docker_manager = setup_docker_manager

        # Test stopping a non-existent container (should fail gracefully)
        stop_result = docker_manager.stop_container("nonexistent-container")
        assert stop_result.is_failure
        assert "not found" in stop_result.error.lower()

        # Test getting info for non-existent container (should fail gracefully)
        info_result = docker_manager.get_container_info("nonexistent-container")
        assert info_result.is_failure
        assert "not found" in info_result.error.lower()
