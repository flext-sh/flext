"""End-to-end tests for dbt-ldap."""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from .conftest import count_rows, query_database, run_dbt_command, table_exists

if TYPE_CHECKING:
    pass


class TestDBTLDAPE2E:
    """E2E tests for dbt-ldap transformations."""

    def test_dbt_debug(
        self,
        dbt_project_dir: Path,
        dbt_profiles_dir: Path,
        postgres_container: Any,
    ) -> None:
        """Test dbt debug to verify configuration."""
        result = run_dbt_command(
            ["debug"],
            dbt_project_dir,
            dbt_profiles_dir,
        )

        assert result.returncode == 0
        assert "All checks passed!" in result.stdout

    def test_dbt_deps(
        self,
        dbt_project_dir: Path,
        dbt_profiles_dir: Path,
    ) -> None:
        """Test dbt deps to install dependencies."""
        result = run_dbt_command(
            ["deps"],
            dbt_project_dir,
            dbt_profiles_dir,
        )

        assert result.returncode == 0

    def test_staging_models(
        self,
        dbt_project_dir: Path,
        dbt_profiles_dir: Path,
        db_connection: Any,
    ) -> None:
        """Test staging model transformations."""
        # Run staging models only
        result = run_dbt_command(
            ["run", "--select", "staging"],
            dbt_project_dir,
            dbt_profiles_dir,
            vars={"ldap_base_dn": "dc=test,dc=com"},
        )

        assert result.returncode == 0

        # Verify staging tables were created
        assert table_exists(db_connection, "ldap_test", "stg_users")
        assert table_exists(db_connection, "ldap_test", "stg_groups")
        assert table_exists(db_connection, "ldap_test", "stg_org_units")

        # Verify user staging data
        user_count = count_rows(db_connection, "ldap_test", "stg_users")
        assert user_count == 6  # 5 regular users + 1 service account

        # Check specific user transformations
        users = query_database(
            db_connection,
            'SELECT user_id, uid, full_name, email_domain, is_active, is_service_account FROM "ldap_test"."stg_users" ORDER BY uid',
        )

        # Check John Doe
        john = next(u for u in users if u[1] == "john.doe")
        assert john[2] == "John Doe"  # full_name
        assert john[3] == "test.com"  # email_domain
        assert john[4] is True  # is_active
        assert john[5] is False  # is_service_account

        # Check service account
        svc = next(u for u in users if u[1] == "svc-app1")
        assert svc[5] is True  # is_service_account

        # Verify group staging data
        group_count = count_rows(db_connection, "ldap_test", "stg_groups")
        assert group_count == 6

        # Check group transformations
        groups = query_database(
            db_connection,
            'SELECT group_id, cn, member_count FROM "ldap_test"."stg_groups" ORDER BY cn',
        )

        # Check engineering team
        eng_group = next(g for g in groups if g[1] == "engineering-team")
        assert eng_group[2] == 2  # member_count

    def test_dimensional_models(
        self,
        dbt_project_dir: Path,
        dbt_profiles_dir: Path,
        db_connection: Any,
    ) -> None:
        """Test dimensional model transformations."""
        # Run all models including dimensional
        result = run_dbt_command(
            ["run", "--select", "marts"],
            dbt_project_dir,
            dbt_profiles_dir,
            vars={"ldap_base_dn": "dc=test,dc=com"},
        )

        assert result.returncode == 0

        # Verify dimensional tables were created
        assert table_exists(db_connection, "ldap_test", "dim_users")
        assert table_exists(db_connection, "ldap_test", "dim_groups")
        assert table_exists(db_connection, "ldap_test", "dim_org_units")
        assert table_exists(db_connection, "ldap_test", "fact_memberships")

        # Verify dim_users
        dim_users = query_database(
            db_connection,
            'SELECT user_key, uid, full_name, department, title, is_active FROM "ldap_test"."dim_users" WHERE is_active = true ORDER BY uid',
        )

        active_users = [u for u in dim_users if u[5]]  # is_active
        assert len(active_users) == 4  # john, jane, bob, alice (charlie is inactive)

        # Check specific user details
        john = next(u for u in dim_users if u[1] == "john.doe")
        assert john[3] == "engineering"  # department
        assert john[4] == "Senior Engineer"  # title

        # Verify fact_memberships
        memberships = query_database(
            db_connection,
            """
            SELECT fm.user_key, fm.group_key, du.uid, dg.group_name
            FROM "ldap_test"."fact_memberships" fm
            JOIN "ldap_test"."dim_users" du ON fm.user_key = du.user_key
            JOIN "ldap_test"."dim_groups" dg ON fm.group_key = dg.group_key
            ORDER BY du.uid, dg.group_name
            """,
        )

        # Verify John Doe's memberships
        john_memberships = [m for m in memberships if m[2] == "john.doe"]
        john_groups = {m[3] for m in john_memberships}
        assert "engineering-team" in john_groups
        assert "managers" in john_groups
        assert "developers" in john_groups

    def test_data_quality_tests(
        self,
        dbt_project_dir: Path,
        dbt_profiles_dir: Path,
        db_connection: Any,
    ) -> None:
        """Test dbt data quality tests."""
        # First run the models
        run_dbt_command(
            ["run"],
            dbt_project_dir,
            dbt_profiles_dir,
            vars={"ldap_base_dn": "dc=test,dc=com"},
        )

        # Run dbt tests
        result = run_dbt_command(
            ["test"],
            dbt_project_dir,
            dbt_profiles_dir,
            vars={"ldap_base_dn": "dc=test,dc=com"},
        )

        assert result.returncode == 0
        assert "Completed successfully" in result.stdout

    def test_incremental_models(
        self,
        dbt_project_dir: Path,
        dbt_profiles_dir: Path,
        db_connection: Any,
    ) -> None:
        """Test incremental model behavior."""
        # First run - full refresh
        result = run_dbt_command(
            ["run", "--full-refresh"],
            dbt_project_dir,
            dbt_profiles_dir,
            vars={"ldap_base_dn": "dc=test,dc=com"},
        )

        assert result.returncode == 0

        # Count initial records
        initial_user_count = count_rows(db_connection, "ldap_test", "dim_users")
        count_rows(db_connection, "ldap_test", "dim_groups")

        # Add new test data
        with db_connection.cursor() as cur:
            cur.execute(
                """
                INSERT INTO raw_ldap.users (
                    _sdc_extracted_at, _sdc_received_at, _sdc_sequence, _sdc_table_version,
                    dn, uid, cn, sn, given_name, mail, employee_number, employee_type,
                    department_number, object_class, create_timestamp, modify_timestamp
                ) VALUES (
                    '2024-01-02 12:00:00+00', '2024-01-02 12:00:00+00', 7, 2,
                    'uid=new.user,ou=users,dc=test,dc=com', 'new.user', 'New User', 'User', 'New',
                    'new.user@test.com', '1006', 'active', 'engineering',
                    ARRAY['inetOrgPerson', 'organizationalPerson', 'person', 'top'],
                    '2024-01-02 10:00:00+00', '2024-01-02 11:00:00+00'
                )
            """
            )

        # Second run - incremental
        result = run_dbt_command(
            ["run"],
            dbt_project_dir,
            dbt_profiles_dir,
            vars={"ldap_base_dn": "dc=test,dc=com"},
        )

        assert result.returncode == 0

        # Verify new data was added
        new_user_count = count_rows(db_connection, "ldap_test", "dim_users")
        assert new_user_count == initial_user_count + 1

        # Verify the new user exists
        new_users = query_database(
            db_connection,
            'SELECT uid FROM "ldap_test"."dim_users" WHERE uid = \'new.user\'',
        )
        assert len(new_users) == 1

    def test_custom_macros(
        self,
        dbt_project_dir: Path,
        dbt_profiles_dir: Path,
        db_connection: Any,
    ) -> None:
        """Test custom LDAP macros."""
        # Test the macros indirectly through model execution
        result = run_dbt_command(
            ["run", "--select", "stg_users"],
            dbt_project_dir,
            dbt_profiles_dir,
            vars={"ldap_base_dn": "dc=test,dc=com"},
        )

        assert result.returncode == 0

        # Verify macro outputs in staging table
        users = query_database(
            db_connection,
            """
            SELECT uid, ou_from_dn, parent_ou_dn, email_domain
            FROM "ldap_test"."stg_users"
            WHERE uid = 'john.doe'
            """,
        )

        assert len(users) == 1
        user = users[0]
        assert user[1] == "users"  # ou_from_dn
        assert user[2] == "dc=test,dc=com"  # parent_ou_dn
        assert user[3] == "test.com"  # email_domain

    def test_schema_evolution(
        self,
        dbt_project_dir: Path,
        dbt_profiles_dir: Path,
        db_connection: Any,
    ) -> None:
        """Test handling of schema changes."""
        # Add new column to raw data
        with db_connection.cursor() as cur:
            cur.execute(
                """
                ALTER TABLE raw_ldap.users
                ADD COLUMN IF NOT EXISTS manager_dn TEXT
            """
            )

            # Update existing record with new field
            cur.execute(
                """
                UPDATE raw_ldap.users
                SET manager_dn = 'uid=alice.johnson,ou=users,dc=test,dc=com'
                WHERE uid = 'bob.wilson'
            """
            )

        # Run models - should handle new column gracefully
        result = run_dbt_command(
            ["run"],
            dbt_project_dir,
            dbt_profiles_dir,
            vars={"ldap_base_dn": "dc=test,dc=com"},
        )

        # Should complete successfully even with schema changes
        assert result.returncode == 0

    def test_performance_large_dataset(
        self,
        dbt_project_dir: Path,
        dbt_profiles_dir: Path,
        db_connection: Any,
    ) -> None:
        """Test performance with larger dataset."""
        # Add many test users
        with db_connection.cursor() as cur:
            for i in range(100):
                cur.execute(
                    """
                    INSERT INTO raw_ldap.users (
                        _sdc_extracted_at, _sdc_received_at, _sdc_sequence, _sdc_table_version,
                        dn, uid, cn, sn, given_name, mail, employee_number, employee_type,
                        department_number, object_class, create_timestamp, modify_timestamp
                    ) VALUES (
                        %s, %s, %s, 1,
                        %s, %s, %s, %s, %s, %s, %s, 'active', 'engineering',
                        ARRAY['inetOrgPerson', 'organizationalPerson', 'person', 'top'],
                        '2024-01-01 10:00:00+00', '2024-01-01 11:00:00+00'
                    )
                """,
                    (
                        f"2024-01-01 12:00:{i:02d}+00",
                        f"2024-01-01 12:00:{i:02d}+00",
                        1000 + i,
                        f"uid=perfuser{i:03d},ou=users,dc=test,dc=com",
                        f"perfuser{i:03d}",
                        f"Perf User {i}",
                        f"User{i}",
                        "Perf",
                        f"perfuser{i:03d}@test.com",
                        str(2000 + i),
                    ),
                )

        # Run transformations with timing
        import time

        start_time = time.time()

        result = run_dbt_command(
            ["run", "--full-refresh"],
            dbt_project_dir,
            dbt_profiles_dir,
            vars={"ldap_base_dn": "dc=test,dc=com"},
        )

        elapsed_time = time.time() - start_time

        assert result.returncode == 0

        # Verify all users were processed
        user_count = count_rows(db_connection, "ldap_test", "dim_users")
        assert user_count >= 106  # 6 original + 100 test users

        # Performance check - should complete in reasonable time
        assert elapsed_time < 60  # 60 seconds for ~100 users

    def test_error_handling(
        self,
        dbt_project_dir: Path,
        dbt_profiles_dir: Path,
        db_connection: Any,
    ) -> None:
        """Test error handling with invalid data."""
        # Add invalid data (duplicate primary key)
        with db_connection.cursor() as cur, contextlib.suppress(Exception):
            # Duplicate key error expected
            cur.execute(
                """
                    INSERT INTO raw_ldap.users (
                        _sdc_extracted_at, _sdc_received_at, _sdc_sequence, _sdc_table_version,
                        dn, uid, cn, sn, given_name
                    ) VALUES (
                        '2024-01-01 12:00:00+00', '2024-01-01 12:00:00+00', 8, 1,
                        'uid=john.doe,ou=users,dc=test,dc=com', 'john.doe.duplicate',
                        'John Doe Duplicate', 'Doe', 'John'
                    )
                """
            )

        # Models should still run successfully with proper error handling
        result = run_dbt_command(
            ["run"],
            dbt_project_dir,
            dbt_profiles_dir,
            vars={"ldap_base_dn": "dc=test,dc=com"},
        )

        # Should handle errors gracefully
        assert result.returncode == 0

    def test_documentation_generation(
        self,
        dbt_project_dir: Path,
        dbt_profiles_dir: Path,
    ) -> None:
        """Test dbt documentation generation."""
        # Generate documentation
        result = run_dbt_command(
            ["docs", "generate"],
            dbt_project_dir,
            dbt_profiles_dir,
        )

        assert result.returncode == 0

        # Verify documentation files were created
        docs_dir = dbt_project_dir / "target"
        assert (docs_dir / "catalog.json").exists()
        assert (docs_dir / "manifest.json").exists()
        assert (docs_dir / "index.html").exists()

    def test_seed_data(
        self,
        dbt_project_dir: Path,
        dbt_profiles_dir: Path,
        db_connection: Any,
    ) -> None:
        """Test dbt seed functionality if seeds exist."""
        # Check if seeds directory exists
        seeds_dir = dbt_project_dir / "seeds"
        if not seeds_dir.exists():
            pytest.skip("No seeds directory found")

        # Run seeds
        result = run_dbt_command(
            ["seed"],
            dbt_project_dir,
            dbt_profiles_dir,
        )

        assert result.returncode == 0

    def test_snapshot_functionality(
        self,
        dbt_project_dir: Path,
        dbt_profiles_dir: Path,
        db_connection: Any,
    ) -> None:
        """Test dbt snapshot functionality if snapshots exist."""
        # Check if snapshots directory exists
        snapshots_dir = dbt_project_dir / "snapshots"
        if not snapshots_dir.exists():
            pytest.skip("No snapshots directory found")

        # Run snapshots
        result = run_dbt_command(
            ["snapshot"],
            dbt_project_dir,
            dbt_profiles_dir,
            vars={"ldap_base_dn": "dc=test,dc=com"},
        )

        assert result.returncode == 0
