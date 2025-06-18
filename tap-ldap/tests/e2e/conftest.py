"""E2E test configuration and fixtures for tap-ldap."""

from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import docker
import ldap3
import pytest
from ldap3 import ALL, Connection, Server

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def docker_client() -> docker.DockerClient:
    """Get Docker client."""
    return docker.from_env()


@pytest.fixture(scope="session")
def e2e_dir() -> Path:
    """Get E2E test directory."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def ldap_container(
    docker_client: docker.DockerClient, project_root: Path
) -> Generator[Any]:
    """Start OpenLDAP container for testing."""
    compose_file = project_root / "docker-compose.yml"

    # Start containers
    logger.info("Starting OpenLDAP container...")
    subprocess.run(
        ["docker-compose", "-f", str(compose_file), "up", "-d"],
        check=True,
        cwd=str(project_root),
    )

    # Wait for LDAP to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            server = Server("localhost", port=10389, get_info=ALL)
            conn = Connection(
                server,
                user="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
                password="REDACTED_LDAP_BIND_PASSWORD_password",
                auto_bind=True,
            )
            conn.unbind()
            logger.info("OpenLDAP is ready")
            break
        except Exception:
            if i == max_retries - 1:
                raise
            logger.info("Waiting for OpenLDAP... (%s/%s)", i + 1, max_retries)
            time.sleep(2)

    yield

    # Stop containers
    logger.info("Stopping OpenLDAP container...")
    subprocess.run(
        ["docker-compose", "-f", str(compose_file), "down", "-v"],
        check=True,
        cwd=str(project_root),
    )


@pytest.fixture()
def ldap_connection(ldap_container: Any) -> Generator[Connection]:  # noqa: ANN401
    """Get LDAP connection for testing."""
    server = Server("localhost", port=10389, get_info=ALL)
    conn = Connection(
        server,
        user="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
        password="REDACTED_LDAP_BIND_PASSWORD_password",
        auto_bind=True,
        raise_exceptions=True,
    )

    yield conn

    if conn.bound:
        conn.unbind()


@pytest.fixture()
def tap_config(tmp_path: Path) -> dict[str, Any]:
    """Get tap configuration for testing."""
    return {
        "host": "localhost",
        "port": 10389,
        "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
        "password": "REDACTED_LDAP_BIND_PASSWORD_password",
        "base_dn": "dc=test,dc=com",
        "use_ssl": False,
        "page_size": 500,
    }


@pytest.fixture()
def tap_config_file(tap_config: dict[str, Any], tmp_path: Path) -> Path:
    """Create tap configuration file."""
    config_file = tmp_path / "tap-config.json"
    config_file.write_text(json.dumps(tap_config))
    return config_file


@pytest.fixture()
def catalog_file(tmp_path: Path) -> Path:
    """Create catalog file for testing."""
    catalog = {
        "streams": [
            {
                "tap_stream_id": "users",
                "replication_method": "FULL_TABLE",
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "available",
                            "selected": True,
                            "forced-replication-method": "FULL_TABLE",
                        },
                    }
                ],
                "schema": {
                    "type": "object",
                    "properties": {
                        "dn": {"type": "string"},
                        "uid": {"type": "string"},
                        "cn": {"type": "string"},
                        "sn": {"type": "string"},
                        "givenName": {"type": "string"},
                        "mail": {"type": "string"},
                        "employeeNumber": {"type": "string"},
                        "employeeType": {"type": "string"},
                        "departmentNumber": {"type": "string"},
                    },
                },
            },
            {
                "tap_stream_id": "groups",
                "replication_method": "FULL_TABLE",
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "available",
                            "selected": True,
                            "forced-replication-method": "FULL_TABLE",
                        },
                    }
                ],
                "schema": {
                    "type": "object",
                    "properties": {
                        "dn": {"type": "string"},
                        "cn": {"type": "string"},
                        "description": {"type": "string"},
                        "member": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            {
                "tap_stream_id": "organizational_units",
                "replication_method": "FULL_TABLE",
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "available",
                            "selected": True,
                            "forced-replication-method": "FULL_TABLE",
                        },
                    }
                ],
                "schema": {
                    "type": "object",
                    "properties": {
                        "dn": {"type": "string"},
                        "ou": {"type": "string"},
                        "description": {"type": "string"},
                    },
                },
            },
        ]
    }

    catalog_file = tmp_path / "catalog.json"
    catalog_file.write_text(json.dumps(catalog))
    return catalog_file


@pytest.fixture()
def state_file(tmp_path: Path) -> Path:
    """Create empty state file."""
    state_file = tmp_path / "state.json"
    state_file.write_text("{}")
    return state_file


def count_ldap_entries(conn: Connection, base_dn: str, search_filter: str) -> int:
    """Count LDAP entries matching filter."""
    conn.search(
        search_base=base_dn,
        search_filter=search_filter,
        search_scope=ldap3.SUBTREE,
        attributes=["dn"],
    )
    return len(conn.entries)


def verify_user_exists(conn: Connection, uid: str) -> bool:
    """Verify a user exists in LDAP."""
    conn.search(
        search_base="dc=test,dc=com",
        search_filter=f"(uid={uid})",
        search_scope=ldap3.SUBTREE,
        attributes=["*"],
    )
    return len(conn.entries) > 0


def verify_group_exists(conn: Connection, cn: str) -> bool:
    """Verify a group exists in LDAP."""
    conn.search(
        search_base="dc=test,dc=com",
        search_filter=f"(cn={cn})",
        search_scope=ldap3.SUBTREE,
        attributes=["*"],
    )
    return len(conn.entries) > 0
