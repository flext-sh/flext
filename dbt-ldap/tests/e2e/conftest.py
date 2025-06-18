"""E2E test configuration and fixtures for dbt-ldap."""

from __future__ import annotations

import logging
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import docker
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
def postgres_container(
    docker_client: docker.DockerClient, project_root: Path
) -> Generator[Any]:
    """Start PostgreSQL container for testing."""
    compose_file = project_root / "docker-compose.yml"

    # Start containers
    logger.info("Starting PostgreSQL container...")
    subprocess.run(
        ["docker-compose", "-f", str(compose_file), "up", "-d", "postgres"],
        check=True,
        cwd=str(project_root),
    )

    # Wait for PostgreSQL to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=25432,
                database="dbt_ldap_test",
                user="dbt_user",
                password="dbt_password",  # noqa: S106
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
    logger.info("Stopping PostgreSQL container...")
    subprocess.run(
        ["docker-compose", "-f", str(compose_file), "down", "-v"],
        check=True,
        cwd=str(project_root),
    )


@pytest.fixture()
def db_connection(postgres_container: Any) -> Generator[Any]:
    """Get database connection for testing."""
    conn = psycopg2.connect(
        host="localhost",
        port=25432,
        database="dbt_ldap_test",
        user="dbt_user",
        password="dbt_password",  # noqa: S106
    )
    conn.autocommit = True

    yield conn

    conn.close()


@pytest.fixture()
def dbt_project_dir(project_root: Path) -> Path:
    """Get dbt project directory."""
    return project_root


@pytest.fixture()
def dbt_profiles_dir(project_root: Path) -> Path:
    """Get dbt profiles directory."""
    return project_root / "tests" / "e2e" / "profiles"


def run_dbt_command(
    command: list[str],
    project_dir: Path,
    profiles_dir: Path,
    vars: dict[str, Any] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run dbt command with proper configuration."""
    env = {
        "DBT_PROFILES_DIR": str(profiles_dir),
        "DBT_PROJECT_DIR": str(project_dir),
    }

    cmd = ["dbt", *command]
    if vars:
        var_string = " ".join(f"{k}:{v}" for k, v in vars.items())
        cmd.extend(["--vars", var_string])

    return subprocess.run(
        cmd,
        cwd=str(project_dir),
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )


def query_database(conn: Any, query: str) -> list[tuple[Any, ...]]:
    """Execute query and return results."""
    with conn.cursor() as cur:
        cur.execute(query)
        result = cur.fetchall()
        return list(result)


def table_exists(conn: Any, schema: str, table: str) -> bool:
    """Check if table exists in database."""
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
        result = cur.fetchone()
        return bool(result[0]) if result else False


def count_rows(conn: Any, schema: str, table: str) -> int:
    """Count rows in table."""
    with conn.cursor() as cur:
        cur.execute('SELECT COUNT(*) FROM "%s"."%s"', (schema, table))
        result = cur.fetchone()
        return int(result[0]) if result else 0


def get_column_names(conn: Any, schema: str, table: str) -> list[str]:
    """Get column names for table."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
            """,
            (schema, table),
        )
        return [row[0] for row in cur.fetchall()]
