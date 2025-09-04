"""FLEXT Docker Test Fixtures - Docker-specific fixtures for integration tests.

This module provides Docker-specific fixtures for integration testing. These fixtures
are conditionally loaded and provide Docker container management for tests that require
external services like databases, LDAP servers, etc.
"""

from __future__ import annotations

import time
from collections.abc import Generator

import pytest

# Check if Docker is available
try:
    import docker

    DOCKER_AVAILABLE = True
except ImportError:
    docker = None  # type: ignore
    DOCKER_AVAILABLE = False


@pytest.fixture(scope="session")
def docker_client() -> Generator[docker.DockerClient]:  # type: ignore
    """Docker client fixture for tests that need Docker access."""
    if not DOCKER_AVAILABLE:
        pytest.skip("Docker not available")

    client = docker.from_env()  # type: ignore
    try:
        # Test connection
        client.ping()
        yield client
    finally:
        client.close()


@pytest.fixture
def postgres_container(docker_client: docker.DockerClient) -> Generator[str]:  # type: ignore
    """PostgreSQL container fixture for database integration tests."""
    if not DOCKER_AVAILABLE:
        pytest.skip("Docker not available")

    container = None
    try:
        # Create and start PostgreSQL container
        container = docker_client.containers.run(  # type: ignore
            "postgres:15-alpine",
            environment={
                "POSTGRES_DB": "testdb",
                "POSTGRES_USER": "testuser",
                "POSTGRES_PASSWORD": "testpass",
            },
            ports={"5432/tcp": None},  # Auto-assign port
            detach=True,
            remove=True,
        )

        # Wait for container to be ready
        time.sleep(5)

        # Get the assigned port
        container_info = docker_client.api.inspect_container(container.id)  # type: ignore
        port = container_info["NetworkSettings"]["Ports"]["5432/tcp"][0]["HostPort"]

        yield f"postgresql://testuser:testpass@localhost:{port}/testdb"

    finally:
        if container:
            container.stop()


@pytest.fixture
def ldap_container(docker_client: docker.DockerClient) -> Generator[str]:  # type: ignore
    """OpenLDAP container fixture for LDAP integration tests."""
    if not DOCKER_AVAILABLE:
        pytest.skip("Docker not available")

    container = None
    try:
        # Create and start OpenLDAP container
        container = docker_client.containers.run(  # type: ignore
            "osixia/openldap:1.5.0",
            environment={
                "LDAP_DOMAIN": "example.com",
                "LDAP_ADMIN_PASSWORD": "REDACTED_LDAP_BIND_PASSWORDpass",
            },
            ports={"389/tcp": None},  # Auto-assign port
            detach=True,
            remove=True,
        )

        # Wait for container to be ready
        time.sleep(10)

        # Get the assigned port
        container_info = docker_client.api.inspect_container(container.id)  # type: ignore
        port = container_info["NetworkSettings"]["Ports"]["389/tcp"][0]["HostPort"]

        yield f"ldap://localhost:{port}"

    finally:
        if container:
            container.stop()
