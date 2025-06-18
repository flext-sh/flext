"""E2E test configuration and fixtures for flx-ldap."""

from __future__ import annotations

import json
import logging
from pathlib import Path
import subprocess
import time
from typing import TYPE_CHECKING, Any

import docker
import ldap3
from ldap3 import ALL, Connection, Server
import psycopg2
import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def docker_client() -> docker.DockerClient:
    """Get Docker client."""
    return docker.from_env()


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def e2e_infrastructure(
    docker_client: docker.DockerClient, project_root: Path
) -> Generator[Any]:
    """Start all infrastructure containers for E2E testing."""
    compose_file = project_root / "docker-compose.yml"

    # Start all containers
    logger.info("Starting E2E infrastructure...")
    subprocess.run(
        ["docker-compose", "-f", str(compose_file), "up", "-d"],
        check=True,
        cwd=str(project_root),
    )

    # Wait for all services to be ready
    services = [
        (
            "source LDAP",
            "localhost",
            30389,
            "cn=REDACTED_LDAP_BIND_PASSWORD,dc=source,dc=com",
            "source_password",
        ),
        (
            "target LDAP",
            "localhost",
            31389,
            "cn=REDACTED_LDAP_BIND_PASSWORD,dc=target,dc=com",
            "target_password",
        ),
    ]

    for service_name, host, port, bind_dn, password in services:
        max_retries = 30
        for i in range(max_retries):
            try:
                server = Server(host, port=port, get_info=ALL)
                conn = Connection(
                    server, user=bind_dn, password=password, auto_bind=True
                )
                conn.unbind()
                logger.info(f"{service_name} is ready")
                break
            except Exception:
                if i == max_retries - 1:
                    raise
                logger.info(f"Waiting for {service_name}... ({i + 1}/{max_retries})")
                time.sleep(2)

    # Wait for PostgreSQL
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=35432,
                database="flx_ldap_test",
                user="flx_user",
                password="flx_password",
            )
            conn.close()
            logger.info("PostgreSQL is ready")
            break
        except Exception:
            if i == max_retries - 1:
                raise
            logger.info(f"Waiting for PostgreSQL... ({i + 1}/{max_retries})")
            time.sleep(2)

    yield

    # Stop containers
    logger.info("Stopping E2E infrastructure...")
    subprocess.run(
        ["docker-compose", "-f", str(compose_file), "down", "-v"],
        check=True,
        cwd=str(project_root),
    )


@pytest.fixture
def source_ldap_connection(e2e_infrastructure: Any) -> Generator[Connection]:
    """Get source LDAP connection for testing."""
    server = Server("localhost", port=30389, get_info=ALL)
    conn = Connection(
        server,
        user="cn=REDACTED_LDAP_BIND_PASSWORD,dc=source,dc=com",
        password="source_password",
        auto_bind=True,
        raise_exceptions=True,
    )

    yield conn

    if conn.bound:
        conn.unbind()


@pytest.fixture
def target_ldap_connection(e2e_infrastructure: Any) -> Generator[Connection]:
    """Get target LDAP connection for testing."""
    server = Server("localhost", port=31389, get_info=ALL)
    conn = Connection(
        server,
        user="cn=REDACTED_LDAP_BIND_PASSWORD,dc=target,dc=com",
        password="target_password",
        auto_bind=True,
        raise_exceptions=True,
    )

    yield conn

    if conn.bound:
        conn.unbind()


@pytest.fixture
def postgres_connection(e2e_infrastructure: Any) -> Generator[Any]:
    """Get PostgreSQL connection for testing."""
    conn = psycopg2.connect(
        host="localhost",
        port=35432,
        database="flx_ldap_test",
        user="flx_user",
        password="flx_password",
    )
    conn.autocommit = True

    yield conn

    conn.close()


@pytest.fixture
def migration_config(project_root: Path) -> dict[str, Any]:
    """Get migration configuration."""
    config_file = project_root / "tests" / "e2e" / "configs" / "migration-config.json"
    with open(config_file) as f:
        return json.load(f)


@pytest.fixture
def migration_config_file(migration_config: dict[str, Any], tmp_path: Path) -> Path:
    """Create migration configuration file."""
    config_file = tmp_path / "migration-config.json"
    config_file.write_text(json.dumps(migration_config))
    return config_file


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Create data directory for E2E tests."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def catalog_dir(tmp_path: Path) -> Path:
    """Create catalog directory for E2E tests."""
    catalog_dir = tmp_path / "catalogs"
    catalog_dir.mkdir()
    return catalog_dir


@pytest.fixture
def state_dir(tmp_path: Path) -> Path:
    """Create state directory for E2E tests."""
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    return state_dir


def run_flx_ldap_command(
    command: list[str],
    config_file: Path,
    **kwargs: Any,
) -> subprocess.CompletedProcess:
    """Run flx-ldap command with configuration."""
    cmd = ["flx-ldap", "--config", str(config_file), *command]

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        **kwargs,
    )


def count_ldap_entries(
    conn: Connection,
    base_dn: str,
    search_filter: str = "(objectClass=*)",
) -> int:
    """Count LDAP entries matching filter."""
    conn.search(
        search_base=base_dn,
        search_filter=search_filter,
        search_scope=ldap3.SUBTREE,
        attributes=["dn"],
    )
    return len(conn.entries)


def get_ldap_entry(
    conn: Connection,
    dn: str,
) -> dict[str, Any] | None:
    """Get LDAP entry by DN."""
    conn.search(
        search_base=dn,
        search_filter="(objectClass=*)",
        search_scope=ldap3.BASE,
        attributes=["*"],
    )
    if conn.entries:
        entry = conn.entries[0]
        return {str(attr.key): attr.values for attr in entry}
    return None


def query_postgres(conn: Any, query: str) -> list[tuple]:
    """Execute PostgreSQL query."""
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def table_exists_postgres(conn: Any, schema: str, table: str) -> bool:
    """Check if PostgreSQL table exists."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = %s AND table_name = %s
            )
            """,
            (schema, table),
        )
        return cur.fetchone()[0]


def count_jsonl_records(file_path: Path, stream_name: str | None = None) -> int:
    """Count records in JSONL file."""
    count = 0
    with open(file_path) as f:
        for line in f:
            record = json.loads(line)
            if record.get("type") == "RECORD":
                if stream_name is None or record.get("stream") == stream_name:
                    count += 1
    return count


def get_jsonl_streams(file_path: Path) -> set[str]:
    """Get unique stream names from JSONL file."""
    streams = set()
    with open(file_path) as f:
        for line in f:
            record = json.loads(line)
            if record.get("type") == "RECORD":
                streams.add(record.get("stream", "unknown"))
    return streams
