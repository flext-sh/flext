"""E2E Test Configuration and Fixtures."""

import json
import os
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

import docker
import psycopg2
import pytest
from ldap3 import ALL, SUBTREE, Connection, Server
from psycopg2.extras import RealDictCursor

# Get the E2E test directory
E2E_DIR = Path(__file__).parent
PROJECT_ROOT = E2E_DIR.parent.parent
DOCKER_COMPOSE_FILE = E2E_DIR / "docker-compose.yml"


@pytest.fixture(scope="session")
def docker_client() -> Any:
    """Create Docker client."""
    return docker.from_env()


@pytest.fixture(scope="session")
def docker_compose_up(docker_client) -> Any:
    """Start docker-compose services."""

    # Change to e2e directory
    original_dir = os.getcwd()
    os.chdir(E2E_DIR)

    try:
        # Stop any existing containers
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.yml", "down", "-v"],
            capture_output=True,
            check=False,
        )

        # Start services
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.yml", "up", "-d"],
            check=True,
            capture_output=True,
        )

        # Wait for services to be ready
        _wait_for_services()

        yield

    finally:
        # Teardown
        if os.environ.get("E2E_KEEP_CONTAINERS") != "true":
            subprocess.run(
                ["docker-compose", "-f", "docker-compose.yml", "down", "-v"],
                capture_output=True,
                check=False,
            )
        os.chdir(original_dir)


def _wait_for_services(timeout: int = 60) -> Any:
    """Wait for all services to be ready."""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # Check LDAP source
            conn = Connection(
                Server("localhost", port=10389, get_info=ALL),
                user="cn=REDACTED_LDAP_BIND_PASSWORD,dc=source,dc=example,dc=com",
                password="REDACTED_LDAP_BIND_PASSWORD_source_password",
                auto_bind=True,
            )
            conn.unbind()

            # Check LDAP target
            conn = Connection(
                Server("localhost", port=11389, get_info=ALL),
                user="cn=REDACTED_LDAP_BIND_PASSWORD,dc=target,dc=example,dc=com",
                password="REDACTED_LDAP_BIND_PASSWORD_target_password",
                auto_bind=True,
            )
            conn.unbind()

            # Check PostgreSQL
            pg_conn = psycopg2.connect(
                host="localhost",
                port=15432,
                database="dbt_ldap_test",
                user="dbt_user",
                password="dbt_password",
            )
            pg_conn.close()

            return

        except Exception:
            time.sleep(2)

    raise TimeoutError("Services did not become ready in time")


@pytest.fixture
def ldap_source_connection(docker_compose_up) -> Any:
    """Create LDAP connection to source server."""
    server = Server("localhost", port=10389, get_info=ALL)
    conn = Connection(
        server,
        user="cn=REDACTED_LDAP_BIND_PASSWORD,dc=source,dc=example,dc=com",
        password="REDACTED_LDAP_BIND_PASSWORD_source_password",
        auto_bind=True,
    )
    yield conn
    conn.unbind()


@pytest.fixture
def ldap_target_connection(docker_compose_up) -> Any:
    """Create LDAP connection to target server."""
    server = Server("localhost", port=11389, get_info=ALL)
    conn = Connection(
        server,
        user="cn=REDACTED_LDAP_BIND_PASSWORD,dc=target,dc=example,dc=com",
        password="REDACTED_LDAP_BIND_PASSWORD_target_password",
        auto_bind=True,
    )
    yield conn
    conn.unbind()


@pytest.fixture
def postgres_connection(docker_compose_up) -> Any:
    """Create PostgreSQL connection."""
    conn = psycopg2.connect(
        host="localhost",
        port=15432,
        database="dbt_ldap_test",
        user="dbt_user",
        password="dbt_password",
        cursor_factory=RealDictCursor,
    )
    conn.autocommit = True
    yield conn
    conn.close()


@pytest.fixture
def clean_target_ldap(ldap_target_connection) -> Any:
    """Clean target LDAP before test."""
    # Clean all entries except base structure
    ldap_target_connection.search(
        search_base="dc=target,dc=example,dc=com",
        search_filter="(objectClass=*)",
        search_scope=SUBTREE,
        attributes=["dn"],
    )

    entries_to_delete = [
        entry.entry_dn
        for entry in ldap_target_connection.entries
        if entry.entry_dn != "dc=target,dc=example,dc=com"
        and not entry.entry_dn.startswith("ou=")
    ]

    for dn in sorted(entries_to_delete, reverse=True):
        ldap_target_connection.delete(dn)


@pytest.fixture
def clean_postgres(postgres_connection) -> Any:
    """Clean PostgreSQL tables before test."""
    with postgres_connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE ldap_raw.users CASCADE")
        cursor.execute("TRUNCATE TABLE ldap_raw.groups CASCADE")
        cursor.execute("TRUNCATE TABLE ldap_raw.organizational_units CASCADE")
        cursor.execute("TRUNCATE TABLE ldap_raw.sync_audit CASCADE")


@pytest.fixture
def sync_id() -> Any:
    """Generate a unique sync ID for the test run."""
    return str(uuid4())


@pytest.fixture
def tap_ldap_config() -> Any:
    """Create tap-ldap configuration."""
    return {
        "host": "localhost",
        "port": 10389,
        "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=source,dc=example,dc=com",
        "password": "REDACTED_LDAP_BIND_PASSWORD_source_password",
        "base_dn": "dc=source,dc=example,dc=com",
        "page_size": 100,
        "filter": "(objectClass=*)",
        "attributes": None,  # Get all attributes
        "ssl": False,
        "validate_certificates": False,
    }


@pytest.fixture
def target_ldap_config() -> Any:
    """Create target-ldap configuration."""
    return {
        "host": "localhost",
        "port": 11389,
        "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=target,dc=example,dc=com",
        "password": "REDACTED_LDAP_BIND_PASSWORD_target_password",
        "base_dn": "dc=target,dc=example,dc=com",
        "ssl": False,
        "validate_certificates": False,
    }


@pytest.fixture
def dbt_ldap_config() -> Any:
    """Create dbt-ldap configuration."""
    return {
        "profiles_dir": str(E2E_DIR / "configs"),
        "project_dir": str(PROJECT_ROOT / "dbt-ldap"),
        "profile": "e2e_test",
        "target": "test",
        "vars": {"sync_id": "{{ var('sync_id') }}", "source_system": "ldap_source"},
    }


@pytest.fixture
def flx_ldap_config(tap_ldap_config, target_ldap_config, dbt_ldap_config) -> Any:
    """Create flx-ldap configuration."""
    return {
        "tap": {"name": "tap-ldap", "config": tap_ldap_config},
        "target": {"name": "target-ldap", "config": target_ldap_config},
        "transformations": {"dbt": dbt_ldap_config},
        "sync_id": "{{ sync_id }}",
        "pipeline_name": "e2e_test_pipeline",
    }


@contextmanager
def temporary_config_file(config: dict[str, Any], prefix: str = "config") -> Any:
    """Create a temporary configuration file."""
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", prefix=f"{prefix}_", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(config, f, indent=2)
        temp_path = f.name

    try:
        yield temp_path
    finally:
        os.unlink(temp_path)


def count_ldap_entries(connection: Connection, base_dn: str, object_class: str) -> int:
    """Count entries of a specific object class."""
    connection.search(
        search_base=base_dn,
        search_filter=f"(objectClass={object_class})",
        search_scope=SUBTREE,
        attributes=["dn"],
    )
    return len(connection.entries)


def verify_user_migrated(
    source_conn: Connection, target_conn: Connection, uid: str
) -> bool:
    """Verify a user was properly migrated."""
    # Get from source
    source_conn.search(
        search_base="dc=source,dc=example,dc=com",
        search_filter=f"(uid={uid})",
        search_scope=SUBTREE,
        attributes=["*"],
    )

    if not source_conn.entries:
        return False

    source_user = source_conn.entries[0]

    # Get from target
    target_conn.search(
        search_base="dc=target,dc=example,dc=com",
        search_filter=f"(uid={uid})",
        search_scope=SUBTREE,
        attributes=["*"],
    )

    if not target_conn.entries:
        return False

    target_user = target_conn.entries[0]

    # Compare key attributes
    attrs_to_check = ["cn", "sn", "givenName", "mail", "employeeNumber"]
    for attr in attrs_to_check:
        if hasattr(source_user, attr) and hasattr(target_user, attr):
            if getattr(source_user, attr) != getattr(target_user, attr):
                return False

    return True


def get_postgres_record_count(connection, table: str) -> int:
    """Get record count from PostgreSQL table."""
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        return cursor.fetchone()["count"]
