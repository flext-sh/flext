"""End-to-end tests for flx-ldap complete pipeline."""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING, Any

from .conftest import (
    count_jsonl_records,
    count_ldap_entries,
    get_jsonl_streams,
    get_ldap_entry,
    query_postgres,
    run_flx_ldap_command,
    table_exists_postgres,
)

if TYPE_CHECKING:
    from pathlib import Path

    from ldap3 import Connection


class TestFlxLDAPCompleteE2E:
    """Complete end-to-end tests for flx-ldap pipeline."""

    def test_validate_configuration(
        self,
        migration_config_file: Path,
        e2e_infrastructure: Any,
    ) -> None:
        """Test configuration validation."""
        result = run_flx_ldap_command(
            ["validate"],
            migration_config_file,
        )

        assert result.returncode == 0
        assert "Component Status" in result.output

    def test_extract_pipeline(
        self,
        migration_config_file: Path,
        source_ldap_connection: Connection,
        data_dir: Path,
    ) -> None:
        """Test complete data extraction pipeline."""
        # Run extraction
        result = run_flx_ldap_command(
            ["extract", "--output", str(data_dir / "extract.jsonl")],
            migration_config_file,
        )

        assert result.returncode == 0
        assert "Extraction Summary" in result.output

        # Verify output file exists
        output_file = data_dir / "extract.jsonl"
        assert output_file.exists()

        # Verify streams were extracted
        streams = get_jsonl_streams(output_file)
        expected_streams = {
            "users",
            "groups",
            "organizational_units",
            "service_accounts",
            "access_groups",
        }
        assert expected_streams.issubset(streams)

        # Verify record counts
        user_count = count_jsonl_records(output_file, "users")
        group_count = count_jsonl_records(output_file, "groups")
        service_count = count_jsonl_records(output_file, "service_accounts")

        # Should have 6 active users (inactive users filtered out)
        assert user_count == 6

        # Should have multiple groups
        assert group_count >= 8

        # Should have 3 service accounts
        assert service_count == 3

        # Verify specific records
        with open(output_file, encoding="utf-8") as f:
            found_users: set = set()
            found_groups: set = set()

            for line in f:
                record = json.loads(line)
                if record.get("type") == "RECORD":
                    if record.get("stream") == "users":
                        found_users.add(record["record"].get("uid"))
                    elif record.get("stream") == "groups":
                        found_groups.add(record["record"].get("cn"))

            # Verify expected users (only active ones due to filter)
            expected_users = {
                "alice.johnson",
                "john.doe",
                "bob.wilson",
                "carol.smith",
                "david.brown",
                "emma.davis",
            }
            assert expected_users.issubset(found_users)

            # Frank Miller should not be included (inactive)
            assert "frank.miller" not in found_users

            # Verify expected groups
            expected_groups = {
                "dept-engineering",
                "dept-sales",
                "managers",
                "developers",
                "executives",
                "all-employees",
            }
            assert expected_groups.issubset(found_groups)

    def test_transform_pipeline(
        self,
        migration_config_file: Path,
        postgres_connection: Any,
        data_dir: Path,
    ) -> None:
        """Test dbt transformation pipeline."""
        # First extract data (prerequisite)
        run_flx_ldap_command(
            ["extract", "--output", str(data_dir / "extract.jsonl")],
            migration_config_file,
        )

        # Run transformations
        result = run_flx_ldap_command(
            ["transform"],
            migration_config_file,
        )

        assert result.returncode == 0

        # Verify staging tables were created
        assert table_exists_postgres(postgres_connection, "staging_ldap", "stg_users")
        assert table_exists_postgres(postgres_connection, "staging_ldap", "stg_groups")
        assert table_exists_postgres(
            postgres_connection,
            "staging_ldap",
            "stg_org_units",
        )

        # Verify dimensional tables were created
        assert table_exists_postgres(postgres_connection, "analytics_ldap", "dim_users")
        assert table_exists_postgres(
            postgres_connection,
            "analytics_ldap",
            "dim_groups",
        )
        assert table_exists_postgres(
            postgres_connection,
            "analytics_ldap",
            "fact_memberships",
        )

        # Verify data quality
        users = query_postgres(
            postgres_connection,
            'SELECT COUNT(*) FROM "analytics_ldap"."dim_users" WHERE is_active = true',
        )
        assert users[0][0] >= 6  # At least 6 active users

        # Verify transformations worked correctly
        john_data = query_postgres(
            postgres_connection,
            """
            SELECT full_name, department, title, email_domain
            FROM "analytics_ldap"."dim_users"
            WHERE uid = 'john.doe'
            """,
        )
        assert len(john_data) == 1
        assert john_data[0][0] == "John Doe"
        assert john_data[0][1] == "engineering"
        assert john_data[0][2] == "Senior Software Engineer"
        assert john_data[0][3] == "source.com"

    def test_load_pipeline(
        self,
        migration_config_file: Path,
        target_ldap_connection: Connection,
        data_dir: Path,
    ) -> None:
        """Test data loading pipeline."""
        # First extract data
        run_flx_ldap_command(
            ["extract", "--output", str(data_dir / "extract.jsonl")],
            migration_config_file,
        )

        # Run loading
        result = run_flx_ldap_command(
            ["load", "--input", str(data_dir / "extract.jsonl")],
            migration_config_file,
        )

        assert result.returncode == 0

        # Verify users were loaded with correct DN transformation
        migrated_users = count_ldap_entries(
            target_ldap_connection,
            "ou=users,ou=migrated,dc=target,dc=com",
            "(objectClass=inetOrgPerson)",
        )
        assert migrated_users >= 6

        # Verify groups were loaded
        migrated_groups = count_ldap_entries(
            target_ldap_connection,
            "ou=groups,dc=target,dc=com",
            "(objectClass=groupOfNames)",
        )
        assert migrated_groups >= 8

        # Verify service accounts were loaded
        service_accounts = count_ldap_entries(
            target_ldap_connection,
            "ou=service-accounts,dc=target,dc=com",
            "(objectClass=account)",
        )
        assert service_accounts == 3

        # Verify specific user was migrated correctly
        john_entry = get_ldap_entry(
            target_ldap_connection,
            "uid=john.doe,ou=users,ou=migrated,dc=target,dc=com",
        )
        assert john_entry is not None
        assert john_entry["cn"] == ["John Doe"]
        assert john_entry["mail"] == ["john.doe@source.com"]
        assert john_entry["title"] == ["Senior Software Engineer"]

    def test_complete_sync_pipeline(
        self,
        migration_config_file: Path,
        source_ldap_connection: Connection,
        target_ldap_connection: Connection,
        postgres_connection: Any,
        data_dir: Path,
    ) -> None:
        """Test complete sync pipeline (extract + transform + load)."""
        # Run complete sync
        result = run_flx_ldap_command(
            ["sync"],
            migration_config_file,
        )

        assert result.returncode == 0
        assert "Sync pipeline completed successfully" in result.output

        # Verify all components worked

        # 1. Verify extraction happened (check raw data)
        assert table_exists_postgres(postgres_connection, "raw_ldap", "users")

        # 2. Verify transformation happened (check dimensional data)
        assert table_exists_postgres(postgres_connection, "analytics_ldap", "dim_users")

        # 3. Verify loading happened (check target LDAP)
        migrated_users = count_ldap_entries(
            target_ldap_connection,
            "ou=users,ou=migrated,dc=target,dc=com",
            "(objectClass=inetOrgPerson)",
        )
        assert migrated_users >= 6

    def test_migration_workflow(
        self,
        migration_config_file: Path,
        source_ldap_connection: Connection,
        target_ldap_connection: Connection,
        data_dir: Path,
    ) -> None:
        """Test complete migration workflow with comparison."""
        # Get initial target count
        initial_target_count = count_ldap_entries(
            target_ldap_connection,
            "dc=target,dc=com",
            "(objectClass=inetOrgPerson)",
        )

        # Run migration
        result = run_flx_ldap_command(
            ["migrate"],
            migration_config_file,
        )

        assert result.returncode == 0
        assert "Migration completed successfully" in result.output

        # Verify comparison output
        assert "Source vs Target Comparison" in result.output

        # Verify migration results
        final_target_count = count_ldap_entries(
            target_ldap_connection,
            "dc=target,dc=com",
            "(objectClass=inetOrgPerson)",
        )

        # Should have more users after migration
        assert final_target_count > initial_target_count

        # Verify specific migrated users
        migrated_users = [
            "alice.johnson",
            "john.doe",
            "bob.wilson",
            "carol.smith",
            "david.brown",
            "emma.davis",
        ]

        for uid in migrated_users:
            entry = get_ldap_entry(
                target_ldap_connection,
                f"uid={uid},ou=users,ou=migrated,dc=target,dc=com",
            )
            assert entry is not None, f"User {uid} not migrated"

    def test_incremental_sync(
        self,
        migration_config_file: Path,
        source_ldap_connection: Connection,
        target_ldap_connection: Connection,
        data_dir: Path,
        state_dir: Path,
    ) -> None:
        """Test incremental sync with state management."""
        # First sync with state
        state_file = state_dir / "sync-state.json"

        result1 = run_flx_ldap_command(
            ["sync", "--state", str(state_file)],
            migration_config_file,
        )

        assert result1.returncode == 0
        assert state_file.exists()

        # Get initial counts
        initial_target_count = count_ldap_entries(
            target_ldap_connection,
            "ou=users,ou=migrated,dc=target,dc=com",
            "(objectClass=inetOrgPerson)",
        )

        # Add new user to source
        source_ldap_connection.add(
            "uid=new.employee,ou=people,dc=source,dc=com",
            attributes={
                "objectClass": [
                    "inetOrgPerson",
                    "organizationalPerson",
                    "person",
                    "top",
                ],
                "uid": "new.employee",
                "cn": "New Employee",
                "sn": "Employee",
                "givenName": "New",
                "mail": "new.employee@source.com",
                "employeeNumber": "1099",
                "employeeType": "active",
                "departmentNumber": "engineering",
                "title": "Junior Developer",
            },
        )

        # Second sync should pick up the new user
        result2 = run_flx_ldap_command(
            ["sync", "--state", str(state_file)],
            migration_config_file,
        )

        assert result2.returncode == 0

        # Verify new user was synced
        new_target_count = count_ldap_entries(
            target_ldap_connection,
            "ou=users,ou=migrated,dc=target,dc=com",
            "(objectClass=inetOrgPerson)",
        )

        assert new_target_count == initial_target_count + 1

        # Verify the new user exists
        new_entry = get_ldap_entry(
            target_ldap_connection,
            "uid=new.employee,ou=users,ou=migrated,dc=target,dc=com",
        )
        assert new_entry is not None
        assert new_entry["title"] == ["Junior Developer"]

        # Cleanup
        source_ldap_connection.delete("uid=new.employee,ou=people,dc=source,dc=com")

    def test_error_recovery(
        self,
        migration_config_file: Path,
        target_ldap_connection: Connection,
        data_dir: Path,
    ) -> None:
        """Test error recovery and partial failure handling."""
        # Create invalid configuration (wrong target host)
        with open(migration_config_file, encoding="utf-8") as f:
            config = json.load(f)

        config["target"]["host"] = "nonexistent-host"

        invalid_config_file = data_dir / "invalid-config.json"
        with open(invalid_config_file, "w", encoding="utf-8") as f:
            json.dump(config, f)

        # Should fail gracefully
        result = run_flx_ldap_command(
            ["sync"],
            invalid_config_file,
        )

        assert result.returncode != 0

        # Should not crash and should provide meaningful error
        assert len(result.stderr) > 0 or "error" in result.stdout.lower()

    def test_custom_stream_migration(
        self,
        migration_config_file: Path,
        target_ldap_connection: Connection,
        data_dir: Path,
    ) -> None:
        """Test migration of custom streams (service accounts, access groups)."""
        # Run sync to migrate custom streams
        result = run_flx_ldap_command(
            ["sync"],
            migration_config_file,
        )

        assert result.returncode == 0

        # Verify service accounts were migrated
        service_accounts = count_ldap_entries(
            target_ldap_connection,
            "ou=service-accounts,dc=target,dc=com",
            "(objectClass=account)",
        )
        assert service_accounts == 3

        # Verify access groups were migrated
        access_groups = count_ldap_entries(
            target_ldap_connection,
            "ou=access,dc=target,dc=com",
            "(objectClass=groupOfNames)",
        )
        assert access_groups >= 2  # ldap-admins, vpn-users

        # Verify specific service account
        backup_svc = get_ldap_entry(
            target_ldap_connection,
            "uid=svc-backup,ou=service-accounts,dc=target,dc=com",
        )
        assert backup_svc is not None
        assert backup_svc["description"] == ["Backup Service Account"]

    def test_performance_large_dataset(
        self,
        migration_config_file: Path,
        source_ldap_connection: Connection,
        target_ldap_connection: Connection,
        data_dir: Path,
    ) -> None:
        """Test performance with larger dataset."""
        # Add many users to source
        added_users: list = []
        for i in range(50):
            uid = f"perfuser{i:03d}"
            dn = f"uid={uid},ou=people,dc=source,dc=com"

            source_ldap_connection.add(
                dn,
                attributes={
                    "objectClass": [
                        "inetOrgPerson",
                        "organizationalPerson",
                        "person",
                        "top",
                    ],
                    "uid": uid,
                    "cn": f"Performance User {i}",
                    "sn": f"User{i}",
                    "givenName": "Performance",
                    "mail": f"{uid}@source.com",
                    "employeeNumber": str(3000 + i),
                    "employeeType": "active",
                    "departmentNumber": "engineering",
                    "title": "Test User",
                },
            )
            added_users.append(dn)

        # Run sync with timing
        start_time = time.time()

        result = run_flx_ldap_command(
            ["sync"],
            migration_config_file,
        )

        elapsed_time = time.time() - start_time

        assert result.returncode == 0

        # Verify all users were migrated
        migrated_count = count_ldap_entries(
            target_ldap_connection,
            "ou=users,ou=migrated,dc=target,dc=com",
            "(objectClass=inetOrgPerson)",
        )

        assert migrated_count >= 56  # 6 original + 50 test users

        # Performance check - should complete in reasonable time
        assert elapsed_time < 120  # 2 minutes for ~50 users

        # Cleanup
        for dn in added_users:
            try:
                source_ldap_connection.delete(dn)
            except Exception:
                pass  # Ignore cleanup errors

    def test_algar_oud_mig_compatibility(
        self,
        migration_config_file: Path,
        data_dir: Path,
    ) -> None:
        """Test compatibility with algar-oud-mig migration patterns."""
        # Test specific patterns used by algar-oud-mig

        # 1. Custom filters for specific object types
        with open(migration_config_file, encoding="utf-8") as f:
            config = json.load(f)

        # Add algar-specific custom streams
        config["tap"]["custom_streams"].append(
            {
                "name": "sudoers",
                "search_filter": "(objectClass=sudoRole)",
                "primary_keys": ["cn"],
                "schema": {
                    "properties": {
                        "cn": {"type": "string"},
                        "sudoUser": {"type": "array", "items": {"type": "string"}},
                        "sudoHost": {"type": "array", "items": {"type": "string"}},
                        "sudoCommand": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
        )

        # 2. Hierarchical DN transformation
        config["target"]["dn_templates"]["sudoers"] = (
            "cn={cn},ou=sudo,ou=access,{base_dn}"
        )

        # 3. Complex filtering for active employees only
        config["tap"]["user_filter"] = (
            "(&(objectClass=inetOrgPerson)(employeeType=active)(!(uid=svc-*)))"
        )

        algar_config_file = data_dir / "algar-config.json"
        with open(algar_config_file, "w", encoding="utf-8") as f:
            json.dump(config, f)

        # Test extraction with algar patterns
        result = run_flx_ldap_command(
            ["extract", "--output", str(data_dir / "algar-extract.jsonl")],
            algar_config_file,
        )

        assert result.returncode == 0

        # Verify filtering worked (service accounts should be excluded from users)
        output_file = data_dir / "algar-extract.jsonl"
        user_count = count_jsonl_records(output_file, "users")

        # Should have 6 regular users (service accounts filtered out)
        assert user_count == 6

        # Verify service accounts are captured in separate stream
        service_count = count_jsonl_records(output_file, "service_accounts")
        assert service_count == 3

    def test_monitoring_and_logging(
        self,
        migration_config_file: Path,
        data_dir: Path,
    ) -> None:
        """Test monitoring and logging capabilities."""
        # Run sync with verbose logging
        with open(migration_config_file, encoding="utf-8") as f:
            config = json.load(f)

        config["log_level"] = "DEBUG"

        debug_config_file = data_dir / "debug-config.json"
        with open(debug_config_file, "w", encoding="utf-8") as f:
            json.dump(config, f)

        result = run_flx_ldap_command(
            ["sync"],
            debug_config_file,
        )

        assert result.returncode == 0

        # Verify detailed output is provided
        assert "Extract" in result.output
        assert "Transform" in result.output or "dbt" in result.output
        assert "Load" in result.output

        # Check for progress indicators
        assert "Step" in result.output or "✓" in result.output
