#!/usr/bin/env python3
"""
Comprehensive E2E Infrastructure Validation Script

This script validates that all E2E test infrastructure is properly set up
for the four LDAP projects: tap-ldap, target-ldap, dbt-ldap, and flx-ldap.

Usage:
    python scripts/validate_e2e_infrastructure.py
    python scripts/validate_e2e_infrastructure.py --project tap-ldap
    python scripts/validate_e2e_infrastructure.py --run-docker-tests
"""

import contextlib
import subprocess
import time
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

PROJECTS = ["tap-ldap", "target-ldap", "dbt-ldap", "flx-ldap"]


def run_command(
    cmd: list[str], cwd: Path | None = None, check: bool = True
) -> subprocess.CompletedProcess:
    """Run command and return result."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
        check=check,
    )


def validate_project_structure(project_path: Path) -> dict[str, Any]:
    """Validate E2E test structure for a project."""
    results = {
        "project_exists": project_path.exists(),
        "e2e_tests_exist": False,
        "docker_compose_exists": False,
        "conftest_exists": False,
        "test_files": [],
        "config_files": [],
        "ldif_files": [],
        "missing_files": [],
    }

    if not results["project_exists"]:
        return results

    # Check E2E test directory
    e2e_dir = project_path / "tests" / "e2e"
    results["e2e_tests_exist"] = e2e_dir.exists()

    if results["e2e_tests_exist"]:
        # Check conftest.py
        conftest_file = e2e_dir / "conftest.py"
        results["conftest_exists"] = conftest_file.exists()

        # Find test files
        results["test_files"] = list(e2e_dir.glob("test_*.py"))

        # Check configs
        configs_dir = e2e_dir / "configs"
        if configs_dir.exists():
            results["config_files"] = list(configs_dir.glob("*.json"))

        # Check LDIF files (for tap/target projects)
        ldif_dir = e2e_dir / "ldif"
        if ldif_dir.exists():
            results["ldif_files"] = list(ldif_dir.glob("*.ldif"))

    # Check docker-compose.yml
    docker_compose_file = project_path / "docker-compose.yml"
    results["docker_compose_exists"] = docker_compose_file.exists()

    # Expected files based on project type
    expected_files = {
        "tap-ldap": [
            "tests/e2e/conftest.py",
            "tests/e2e/test_tap_e2e.py",
            "docker-compose.yml",
            "tests/e2e/ldif/01-base.ldif",
            "tests/e2e/ldif/02-users.ldif",
        ],
        "target-ldap": [
            "tests/e2e/conftest.py",
            "tests/e2e/test_target_e2e.py",
            "docker-compose.yml",
            "tests/e2e/ldif/01-base.ldif",
        ],
        "dbt-ldap": [
            "tests/e2e/conftest.py",
            "tests/e2e/test_dbt_e2e.py",
            "docker-compose.yml",
        ],
        "flx-ldap": [
            "tests/e2e/conftest.py",
            "tests/e2e/test_flx_ldap_e2e.py",
            "docker-compose.yml",
            "tests/e2e/configs/migration-config.json",
        ],
    }

    project_name = project_path.name
    if project_name in expected_files:
        for expected_file in expected_files[project_name]:
            file_path = project_path / expected_file
            if not file_path.exists():
                results["missing_files"].append(expected_file)

    return results


def validate_docker_compose(project_path: Path) -> dict[str, Any]:
    """Validate docker-compose configuration."""
    results = {
        "valid_yaml": False,
        "services": [],
        "ports": [],
        "errors": [],
    }

    docker_compose_file = project_path / "docker-compose.yml"
    if not docker_compose_file.exists():
        results["errors"].append("docker-compose.yml not found")
        return results

    try:
        # Try to parse the docker-compose file
        result = run_command(
            ["docker-compose", "-f", str(docker_compose_file), "config"],
            cwd=project_path,
            check=False,
        )

        if result.returncode == 0:
            results["valid_yaml"] = True

            # Extract services and ports from output
            import yaml

            config = yaml.safe_load(result.stdout)

            if "services" in config:
                for service_name, service_config in config["services"].items():
                    results["services"].append(service_name)

                    if "ports" in service_config:
                        for port in service_config["ports"]:
                            results["ports"].append(port)
            results["errors"].append(
                f"Docker compose validation failed: {result.stderr}"
            )

    except Exception as e:
        results["errors"].append(f"Error validating docker-compose: {e}")

    return results


def test_docker_infrastructure(project_path: Path) -> dict[str, Any]:
    """Test Docker infrastructure by starting containers."""
    results = {
        "containers_started": False,
        "containers_healthy": False,
        "services_accessible": [],
        "errors": [],
    }

    docker_compose_file = project_path / "docker-compose.yml"
    if not docker_compose_file.exists():
        results["errors"].append("docker-compose.yml not found")
        return results

    try:
        # Start containers
        console.print(
            f"🐳 Starting Docker containers for {
                project_path.name}...")

        start_result = run_command(
            ["docker-compose", "-f", str(docker_compose_file), "up", "-d"],
            cwd=project_path,
            check=False,
        )

        if start_result.returncode == 0:
            results["containers_started"] = True

            # Wait a bit for services to start
            time.sleep(10)

            # Check container health
            ps_result = run_command(
                ["docker-compose", "-f", str(docker_compose_file), "ps"],
                cwd=project_path,
                check=False,
            )

            if ps_result.returncode == 0:
                results["containers_healthy"] = "Up" in ps_result.stdout

            # Test specific services based on project
            project_name = project_path.name

            if project_name in {"tap-ldap", "target-ldap", "flx-ldap"}:
                # Test LDAP connectivity
                try:
                    from ldap3 import Connection, Server

                    if project_name == "tap-ldap":
                        server = Server("localhost", port=30389)
                        conn = Connection(
                            server,
                            user="cn=admin,dc=test,dc=com",
                            password="admin_password",
                        )
                        if conn.bind():
                            results["services_accessible"].append("openldap")
                            conn.unbind()
                    elif project_name == "target-ldap":
                        # Test both source and target LDAP
                        for port, name in [
                            (30389, "source-ldap"),
                            (31389, "target-ldap"),
                        ]:
                            server = Server("localhost", port=port)
                            conn = Connection(
                                server,
                                user=f"cn=admin,dc={
                                    name.split('-')[0]},dc=com",
                                password=f"{
                                    name.split('-')[0]}_password",
                            )
                            if conn.bind():
                                results["services_accessible"].append(name)
                                conn.unbind()
                    elif project_name == "flx-ldap":
                        # Test all services
                        ldap_tests = [
                            (
                                30389,
                                "source-ldap",
                                "cn=admin,dc=source,dc=com",
                                "source_password",
                            ),
                            (
                                31389,
                                "target-ldap",
                                "cn=admin,dc=target,dc=com",
                                "target_password",
                            ),
                        ]

                        for port, name, bind_dn, password in ldap_tests:
                            server = Server("localhost", port=port)
                            conn = Connection(
                                server, user=bind_dn, password=password)
                            if conn.bind():
                                results["services_accessible"].append(name)
                                conn.unbind()

                        # Test PostgreSQL
                        try:
                            import psycopg2

                            pg_conn = psycopg2.connect(
                                host="localhost",
                                port=35432,
                                database="flx_ldap_test",
                                user="flx_user",
                                password="flx_password",
                            )
                            pg_conn.close()
                            results["services_accessible"].append("postgres")
                        except Exception:
                            pass

                except ImportError:
                    results["errors"].append("ldap3 not available for testing")
                except Exception as e:
                    results["errors"].append(
                        f"Service connectivity test failed: {e}")

            elif project_name == "dbt-ldap":
                # Test PostgreSQL
                try:
                    import psycopg2

                    conn = psycopg2.connect(
                        host="localhost",
                        port=35432,
                        database="dbt_ldap_test",
                        user="dbt_user",
                        password="dbt_password",
                    )
                    conn.close()
                    results["services_accessible"].append("postgres")
                except Exception:
                    pass
            results["errors"].append(
                f"Failed to start containers: {start_result.stderr}"
            )

    except Exception as e:
        results["errors"].append(f"Docker test failed: {e}")

    finally:
        # Clean up containers
        with contextlib.suppress(Exception):
            run_command(
                ["docker-compose", "-f", str(docker_compose_file), "down", "-v"],
                cwd=project_path,
                check=False,
            )

    return results


@click.command()
@click.option("--project",
              help="Specific project to validate (tap-ldap, target-ldap, dbt-ldap, flx-ldap)",
              )
@click.option("--run-docker-tests", is_flag=True,
              help="Run actual Docker container tests")
def main(project: str | None, run_docker_tests: bool) -> None:
    """Validate E2E test infrastructure for LDAP projects."""

    console.print(
        Panel.fit(
            "🧪 E2E Infrastructure Validation",
            style="bold blue"))

    pyauto_root = Path(__file__).parent.parent

    projects_to_check = [project] if project else PROJECTS

    overall_results: dict = {}

    for project_name in projects_to_check:
        project_path = pyauto_root / project_name

        console.print(f"\n📁 Validating {project_name}...")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Structure validation
            task1 = progress.add_task(
                "Checking project structure...", total=None)
            structure_results = validate_project_structure(project_path)
            progress.update(task1, completed=True)

            # Docker compose validation
            task2 = progress.add_task(
                "Validating docker-compose...", total=None)
            compose_results = validate_docker_compose(project_path)
            progress.update(task2, completed=True)

            # Docker tests (if requested)
            docker_results: dict = {}
            if run_docker_tests and structure_results["docker_compose_exists"]:
                task3 = progress.add_task(
                    "Testing Docker infrastructure...", total=None
                )
                docker_results = test_docker_infrastructure(project_path)
                progress.update(task3, completed=True)

        overall_results[project_name] = {
            "structure": structure_results,
            "compose": compose_results,
            "docker": docker_results,
        }

    # Display results
    console.print("\n📊 Validation Results")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Project", style="cyan")
    table.add_column("Structure", justify="center")
    table.add_column("Docker Compose", justify="center")
    table.add_column("Test Files", justify="center")
    table.add_column("Missing Files", justify="center")

    if run_docker_tests:
        table.add_column("Docker Test", justify="center")
        table.add_column("Services", justify="center")

    for project_name, results in overall_results.items():
        structure = results["structure"]
        compose = results["compose"]
        docker = results["docker"]

        # Structure status
        structure_status = (
            "✅"
            if structure["project_exists"] and structure["e2e_tests_exist"]
            else "❌"
        )

        # Compose status
        compose_status = "✅" if compose["valid_yaml"] else "❌"

        # Test files count
        test_count = len(structure["test_files"])

        # Missing files
        missing_count = len(structure["missing_files"])
        missing_status = "✅" if missing_count == 0 else f"❌ ({missing_count})"

        row = [
            project_name,
            structure_status,
            compose_status,
            str(test_count),
            missing_status,
        ]

        if run_docker_tests:
            # Docker test status
            if docker:
                docker_status = "✅" if docker["containers_healthy"] else "❌"
                services_count = len(docker["services_accessible"])
                services_status = (
                    f"✅ ({services_count})" if services_count > 0 else "❌"
                )
                docker_status = "⏭️"
                services_status = "⏭️"

            row.extend([docker_status, services_status])

        table.add_row(*row)

    console.print(table)

    # Detailed error reporting
    for project_name, results in overall_results.items():
        errors: list = []

        # Structure errors
        if results["structure"]["missing_files"]:
            errors.extend(
                [f"Missing: {f}" for f in results["structure"]["missing_files"]]
            )

        # Compose errors
        errors.extend(results["compose"]["errors"])

        # Docker errors
        errors.extend(results["docker"].get("errors", []))

        if errors:
            console.print(f"\n❌ Issues found in {project_name}:")
            for error in errors:
                console.print(f"  • {error}")

    # Summary
    total_projects = len(overall_results)
    valid_projects = sum(
        1
        for results in overall_results.values()
        if results["structure"]["project_exists"]
        and results["structure"]["e2e_tests_exist"]
        and results["compose"]["valid_yaml"]
        and len(results["structure"]["missing_files"]) == 0
    )

    if run_docker_tests:
        docker_working = sum(
            1
            for results in overall_results.values()
            if results["docker"].get("containers_healthy", False)
        )
        console.print(
            f"\n🎯 Summary: {valid_projects}/{total_projects} projects valid, {docker_working}/{total_projects} Docker tests passed"
        )
        console.print(
            f"\n🎯 Summary: {valid_projects}/{total_projects} projects have complete E2E infrastructure")

    if valid_projects == total_projects:
        console.print("✅ All E2E infrastructure is ready!")
        console.print("❌ Some projects need attention.")


if __name__ == "__main__":
    main()
