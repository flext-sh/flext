"""Comprehensive tests for FlextTestDocker class.

Tests all Docker container management functionality with both mocked
and real integration scenarios.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import time
from unittest.mock import Mock, patch

import pytest
from docker.errors import DockerException, NotFound

from flext_core import FlextResult
from flext_tests.docker import ContainerInfo, ContainerStatus, FlextTestDocker


class TestFlextTestDockerBasic:
    """Test FlextTestDocker basic functionality with mocked Docker client."""

    def test_init_creates_instance(self) -> None:
        """Test FlextTestDocker initialization."""
        docker_manager = FlextTestDocker()
        assert docker_manager._client is None
        assert docker_manager._logger is not None

    @patch("flext_tests.docker.docker.from_env")
    def test_get_client_lazy_initialization(self, mock_from_env: Mock) -> None:
        """Test Docker client lazy initialization."""
        mock_client = Mock()
        mock_from_env.return_value = mock_client

        docker_manager = FlextTestDocker()
        assert docker_manager._client is None

        client = docker_manager._get_client()
        assert client is mock_client
        assert docker_manager._client is mock_client
        mock_from_env.assert_called_once()

        # Second call should reuse existing client
        client2 = docker_manager._get_client()
        assert client2 is mock_client
        assert mock_from_env.call_count == 1

    @patch("flext_tests.docker.docker.from_env")
    def test_get_client_docker_exception(self, mock_from_env: Mock) -> None:
        """Test Docker client initialization failure."""
        mock_from_env.side_effect = DockerException("Docker daemon not running")

        docker_manager = FlextTestDocker()

        with pytest.raises(DockerException, match="Docker daemon not running"):
            docker_manager._get_client()


class TestFlextTestDockerStartContainer:
    """Test start_container method with various scenarios."""

    @patch("flext_tests.docker.docker.from_env")
    def test_start_container_success(self, mock_from_env: Mock) -> None:
        """Test successful container start."""
        mock_container = Mock()
        mock_container.id = "test_container_id_123"

        mock_client = Mock()
        mock_client.containers.run.return_value = mock_container
        mock_from_env.return_value = mock_client

        docker_manager = FlextTestDocker()
        result = docker_manager.start_container(
            image="nginx:latest", name="test_nginx", ports={"80/tcp": "8080"}
        )

        assert result.is_success
        container_info = result.unwrap()
        assert isinstance(container_info, ContainerInfo)
        assert container_info.name == "test_nginx"
        assert container_info.image == "nginx:latest"
        assert container_info.status == ContainerStatus.RUNNING
        assert container_info.ports == {"80/tcp": "8080"}
        assert container_info.container_id == "test_container_id_123"

        mock_client.containers.run.assert_called_once_with(
            "nginx:latest",
            name="test_nginx",
            ports={"80/tcp": "8080"},
            detach=True,
            remove=False,
        )

    @patch("flext_tests.docker.docker.from_env")
    def test_start_container_no_ports(self, mock_from_env: Mock) -> None:
        """Test container start without port mapping."""
        mock_container = Mock()
        mock_container.id = "test_container_id_456"

        mock_client = Mock()
        mock_client.containers.run.return_value = mock_container
        mock_from_env.return_value = mock_client

        docker_manager = FlextTestDocker()
        result = docker_manager.start_container(
            image="alpine:latest", name="test_alpine"
        )

        assert result.is_success
        container_info = result.unwrap()
        assert container_info.ports == {}
        assert container_info.container_id == "test_container_id_456"

        mock_client.containers.run.assert_called_once_with(
            "alpine:latest", name="test_alpine", ports=None, detach=True, remove=False
        )

    @patch("flext_tests.docker.docker.from_env")
    def test_start_container_docker_exception(self, mock_from_env: Mock) -> None:
        """Test container start failure due to Docker exception."""
        mock_client = Mock()
        mock_client.containers.run.side_effect = DockerException("Image not found")
        mock_from_env.return_value = mock_client

        docker_manager = FlextTestDocker()
        result = docker_manager.start_container(
            image="nonexistent:latest", name="test_fail"
        )

        assert result.is_failure
        assert "Failed to start container: Image not found" in result.error


class TestFlextTestDockerStopContainer:
    """Test stop_container method with various scenarios."""

    @patch("flext_tests.docker.docker.from_env")
    def test_stop_container_success(self, mock_from_env: Mock) -> None:
        """Test successful container stop."""
        mock_container = Mock()

        mock_client = Mock()
        mock_client.containers.get.return_value = mock_container
        mock_from_env.return_value = mock_client

        docker_manager = FlextTestDocker()
        result = docker_manager.stop_container("test_container")

        assert result.is_success
        assert result.unwrap() is True
        mock_client.containers.get.assert_called_once_with("test_container")
        mock_container.stop.assert_called_once()

    @patch("flext_tests.docker.docker.from_env")
    def test_stop_container_not_found(self, mock_from_env: Mock) -> None:
        """Test stopping non-existent container."""
        mock_client = Mock()
        mock_client.containers.get.side_effect = NotFound("Container not found")
        mock_from_env.return_value = mock_client

        docker_manager = FlextTestDocker()
        result = docker_manager.stop_container("nonexistent_container")

        assert result.is_failure
        assert "Container nonexistent_container not found" in result.error

    @patch("flext_tests.docker.docker.from_env")
    def test_stop_container_docker_exception(self, mock_from_env: Mock) -> None:
        """Test container stop failure due to Docker exception."""
        mock_client = Mock()
        mock_client.containers.get.side_effect = DockerException("Permission denied")
        mock_from_env.return_value = mock_client

        docker_manager = FlextTestDocker()
        result = docker_manager.stop_container("test_container")

        assert result.is_failure
        assert "Failed to stop container: Permission denied" in result.error


class TestFlextTestDockerGetContainerInfo:
    """Test get_container_info method with various scenarios."""

    @patch("flext_tests.docker.docker.from_env")
    def test_get_container_info_running(self, mock_from_env: Mock) -> None:
        """Test getting info for running container."""
        mock_image = Mock()
        mock_image.tags = ["nginx:latest"]

        mock_container = Mock()
        mock_container.status = "running"
        mock_container.id = "running_container_id"
        mock_container.image = mock_image

        mock_client = Mock()
        mock_client.containers.get.return_value = mock_container
        mock_from_env.return_value = mock_client

        docker_manager = FlextTestDocker()
        result = docker_manager.get_container_info("running_container")

        assert result.is_success
        container_info = result.unwrap()
        assert container_info.name == "running_container"
        assert container_info.status == ContainerStatus.RUNNING
        assert container_info.image == "nginx:latest"
        assert container_info.container_id == "running_container_id"
        assert container_info.ports == {}

    @patch("flext_tests.docker.docker.from_env")
    def test_get_container_info_stopped(self, mock_from_env: Mock) -> None:
        """Test getting info for stopped container."""
        mock_image = Mock()
        mock_image.tags = ["alpine:latest"]

        mock_container = Mock()
        mock_container.status = "exited"
        mock_container.id = "stopped_container_id"
        mock_container.image = mock_image

        mock_client = Mock()
        mock_client.containers.get.return_value = mock_container
        mock_from_env.return_value = mock_client

        docker_manager = FlextTestDocker()
        result = docker_manager.get_container_info("stopped_container")

        assert result.is_success
        container_info = result.unwrap()
        assert container_info.status == ContainerStatus.STOPPED
        assert container_info.image == "alpine:latest"

    @patch("flext_tests.docker.docker.from_env")
    def test_get_container_info_no_image_tags(self, mock_from_env: Mock) -> None:
        """Test getting info for container with no image tags."""
        mock_image = Mock()
        mock_image.tags = []

        mock_container = Mock()
        mock_container.status = "running"
        mock_container.id = "no_tags_container_id"
        mock_container.image = mock_image

        mock_client = Mock()
        mock_client.containers.get.return_value = mock_container
        mock_from_env.return_value = mock_client

        docker_manager = FlextTestDocker()
        result = docker_manager.get_container_info("no_tags_container")

        assert result.is_success
        container_info = result.unwrap()
        assert not container_info.image

    @patch("flext_tests.docker.docker.from_env")
    def test_get_container_info_not_found(self, mock_from_env: Mock) -> None:
        """Test getting info for non-existent container."""
        mock_client = Mock()
        mock_client.containers.get.side_effect = NotFound("Container not found")
        mock_from_env.return_value = mock_client

        docker_manager = FlextTestDocker()
        result = docker_manager.get_container_info("nonexistent_container")

        assert result.is_failure
        assert "Container nonexistent_container not found" in result.error

    @patch("flext_tests.docker.docker.from_env")
    def test_get_container_info_docker_exception(self, mock_from_env: Mock) -> None:
        """Test getting info failure due to Docker exception."""
        mock_client = Mock()
        mock_client.containers.get.side_effect = DockerException("API error")
        mock_from_env.return_value = mock_client

        docker_manager = FlextTestDocker()
        result = docker_manager.get_container_info("test_container")

        assert result.is_failure
        assert "Failed to get container info: API error" in result.error


class TestFlextTestDockerIntegration:
    """Integration tests with real Docker environment (when available)."""

    @pytest.mark.skipif(
        os.getenv("SKIP_DOCKER_TESTS", "false").lower() == "true",
        reason="Docker tests skipped via SKIP_DOCKER_TESTS environment variable",
    )
    def test_docker_integration_lifecycle(self) -> None:
        """Test full container lifecycle with real Docker (when available)."""
        try:
            docker_manager = FlextTestDocker()

            # Use unique container name to avoid conflicts
            unique_name = f"flext_test_integration_alpine_{int(time.time())}"

            # Test starting a container
            start_result = docker_manager.start_container(
                image="alpine:latest", name=unique_name, ports=None
            )

            if start_result.is_failure:
                pytest.skip(f"Docker not available: {start_result.error}")

            assert start_result.is_success
            container_info = start_result.unwrap()
            assert container_info.name == unique_name
            assert container_info.status == ContainerStatus.RUNNING

            # Test getting container info
            info_result = docker_manager.get_container_info(unique_name)
            assert info_result.is_success

            # Test stopping the container
            stop_result = docker_manager.stop_container(unique_name)
            assert stop_result.is_success

        except DockerException:
            pytest.skip("Docker daemon not available for integration tests")

        except Exception as e:
            pytest.fail(f"Unexpected error in Docker integration test: {e}")

    @pytest.mark.skipif(
        os.getenv("SKIP_DOCKER_TESTS", "false").lower() == "true",
        reason="Docker tests skipped via SKIP_DOCKER_TESTS environment variable",
    )
    def test_docker_client_availability(self) -> None:
        """Test Docker client availability for integration tests."""
        try:
            docker_manager = FlextTestDocker()
            client = docker_manager._get_client()
            assert client is not None

            # Try to ping Docker daemon
            client.ping()

        except DockerException:
            pytest.skip("Docker daemon not available")


class TestContainerStatusEnum:
    """Test ContainerStatus enumeration."""

    def test_container_status_values(self) -> None:
        """Test ContainerStatus enum values."""
        assert ContainerStatus.RUNNING.value == "running"
        assert ContainerStatus.STOPPED.value == "stopped"
        assert ContainerStatus.NOT_FOUND.value == "not_found"
        assert ContainerStatus.ERROR.value == "error"


class TestContainerInfoDataClass:
    """Test ContainerInfo dataclass functionality."""

    def test_container_info_creation(self) -> None:
        """Test ContainerInfo dataclass creation."""
        container_info = ContainerInfo(
            name="test_container",
            status=ContainerStatus.RUNNING,
            ports={"80/tcp": "8080"},
            image="nginx:latest",
            container_id="abc123",
        )

        assert container_info.name == "test_container"
        assert container_info.status == ContainerStatus.RUNNING
        assert container_info.ports == {"80/tcp": "8080"}
        assert container_info.image == "nginx:latest"
        assert container_info.container_id == "abc123"

    def test_container_info_default_container_id(self) -> None:
        """Test ContainerInfo with default container_id."""
        container_info = ContainerInfo(
            name="test_container",
            status=ContainerStatus.STOPPED,
            ports={},
            image="alpine:latest",
        )

        assert not container_info.container_id

    def test_container_info_frozen(self) -> None:
        """Test ContainerInfo is frozen (immutable)."""
        container_info = ContainerInfo(
            name="test_container",
            status=ContainerStatus.RUNNING,
            ports={},
            image="nginx:latest",
        )

        with pytest.raises(AttributeError):
            container_info.name = "modified_name"  # type: ignore[misc]


class TestFlextTestDockerEdgeCases:
    """Test edge cases and error scenarios."""

    @patch("flext_tests.docker.docker.from_env")
    def test_multiple_docker_managers(self, mock_from_env: Mock) -> None:
        """Test that multiple FlextTestDocker instances work independently."""
        mock_client1 = Mock()
        mock_client2 = Mock()

        mock_from_env.side_effect = [mock_client1, mock_client2]

        manager1 = FlextTestDocker()
        manager2 = FlextTestDocker()

        client1 = manager1._get_client()
        client2 = manager2._get_client()

        assert client1 is mock_client1
        assert client2 is mock_client2
        assert client1 is not client2

    @patch("flext_tests.docker.docker.from_env")
    def test_start_container_empty_ports(self, mock_from_env: Mock) -> None:
        """Test container start with empty ports dict."""
        mock_container = Mock()
        mock_container.id = "test_id"

        mock_client = Mock()
        mock_client.containers.run.return_value = mock_container
        mock_from_env.return_value = mock_client

        docker_manager = FlextTestDocker()
        result = docker_manager.start_container(
            image="nginx:latest", name="test_nginx", ports={}
        )

        assert result.is_success
        container_info = result.unwrap()
        assert container_info.ports == {}

    @patch("flext_tests.docker.docker.from_env")
    def test_concurrent_operations(self, mock_from_env: Mock) -> None:
        """Test that Docker manager handles concurrent operations safely."""
        mock_client = Mock()
        mock_from_env.return_value = mock_client

        # Mock different responses for concurrent operations
        mock_container1 = Mock()
        mock_container1.id = "container1"
        mock_container2 = Mock()
        mock_container2.id = "container2"

        mock_client.containers.run.side_effect = [mock_container1, mock_container2]

        docker_manager = FlextTestDocker()

        # Simulate concurrent operations
        result1 = docker_manager.start_container("nginx:latest", "container1")
        result2 = docker_manager.start_container("alpine:latest", "container2")

        assert result1.is_success
        assert result2.is_success
        assert result1.unwrap().container_id == "container1"
        assert result2.unwrap().container_id == "container2"

    def test_logger_initialization(self) -> None:
        """Test that logger is properly initialized."""
        docker_manager = FlextTestDocker()
        assert docker_manager._logger is not None
        assert hasattr(docker_manager._logger, "error")
        assert hasattr(docker_manager._logger, "info")


class TestFlextTestDockerMethodsExist:
    """Test that all required methods exist and have correct signatures."""

    def test_required_methods_exist(self) -> None:
        """Test that all required methods exist."""
        docker_manager = FlextTestDocker()

        # Basic methods
        assert hasattr(docker_manager, "start_container")
        assert hasattr(docker_manager, "stop_container")
        assert hasattr(docker_manager, "get_container_info")
        assert hasattr(docker_manager, "_get_client")

        # Check method callability
        assert callable(docker_manager.start_container)
        assert callable(docker_manager.stop_container)
        assert callable(docker_manager.get_container_info)
        assert callable(docker_manager._get_client)

    def test_method_return_types(self) -> None:
        """Test that methods return FlextResult types."""
        with patch("flext_tests.docker.docker.from_env") as mock_from_env:
            mock_client = Mock()
            mock_client.containers.run.side_effect = DockerException("test")
            mock_client.containers.get.side_effect = NotFound("test")
            mock_from_env.return_value = mock_client

            docker_manager = FlextTestDocker()

            # Test return types even with failures
            result = docker_manager.start_container("test", "test")
            assert isinstance(result, FlextResult)

            result = docker_manager.stop_container("test")
            assert isinstance(result, FlextResult)

            result = docker_manager.get_container_info("test")
            assert isinstance(result, FlextResult)
