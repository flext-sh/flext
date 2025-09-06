"""FLEXT Docker Test Fixtures - Docker-specific fixtures for integration tests.

This module provides Docker-specific fixtures for integration testing. These fixtures
are conditionally loaded and provide Docker container management for tests that require
external services like databases, LDAP servers, etc.
"""

from __future__ import annotations

import time
from collections.abc import Generator

import docker
import pytest
from docker.client import DockerClient
from docker.models.containers import Container


@pytest.fixture(scope="session")
def docker_client() -> Generator[DockerClient]:
    """Docker client fixture for tests that need Docker access."""
    client = docker.from_env()
    try:
        yield client
    finally:
        pass  # Client cleanup handled by Docker


@pytest.fixture
def postgres_container(docker_client: DockerClient) -> Generator[str]:
    """PostgreSQL container fixture for database integration tests."""
    container: Container | None = None
    try:
        # Create and start PostgreSQL container
        container = docker_client.containers.run(
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
        if container.id is not None:
            container_info = docker_client.api.inspect_container(container.id)
        else:
            raise RuntimeError("Container ID is None")
        port = container_info["NetworkSettings"]["Ports"]["5432/tcp"][0]["HostPort"]

        yield f"postgresql://testuser:testpass@localhost:{port}/testdb"

    finally:
        if container:
            container.stop()


@pytest.fixture
def ldap_container(docker_client: DockerClient) -> Generator[str]:
    """OpenLDAP container fixture for LDAP integration tests."""
    container: Container | None = None
    try:
        # Create and start OpenLDAP container
        container = docker_client.containers.run(
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
        if container.id is not None:
            container_info = docker_client.api.inspect_container(container.id)
        else:
            raise RuntimeError("Container ID is None")
        port = container_info["NetworkSettings"]["Ports"]["389/tcp"][0]["HostPort"]

        yield f"ldap://localhost:{port}"

    finally:
        if container:
            container.stop()
