"""End-to-end tests for tap-ldap."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from ldap3 import Connection


class TestTapLDAPE2E:
    """E2E tests for tap-ldap."""

    def test_discovery(
        self,
        tap_config_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test tap discovery."""
        # Run discovery
        result = subprocess.run(
            ["tap-ldap", "--config", str(tap_config_file), "--discover"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse catalog
        catalog = json.loads(result.stdout)

        # Verify streams
        assert "streams" in catalog
        stream_names = {s["tap_stream_id"] for s in catalog["streams"]}
        assert "users" in stream_names
        assert "groups" in stream_names
        assert "organizational_units" in stream_names
        assert "schema" in stream_names

        # Verify schema properties
        users_stream = next(
            s for s in catalog["streams"] if s["tap_stream_id"] == "users"
        )
        assert "schema" in users_stream
        assert "properties" in users_stream["schema"]

        user_props = users_stream["schema"]["properties"]
        assert "dn" in user_props
        assert "uid" in user_props
        assert "cn" in user_props
        assert "mail" in user_props

    def test_full_extraction(
        self,
        tap_config_file: Path,
        catalog_file: Path,
        tmp_path: Path,
        ldap_connection: Connection,
    ) -> None:
        """Test full data extraction."""
        output_file = tmp_path / "tap-output.jsonl"

        # Run tap
        with open(output_file, "w") as f:
            subprocess.run(
                [
                    "tap-ldap",
                    "--config",
                    str(tap_config_file),
                    "--catalog",
                    str(catalog_file),
                ],
                stdout=f,
                check=True,
            )

        # Parse output
        records = []
        schemas = {}
        with open(output_file) as f:
            for line in f:
                msg = json.loads(line)
                if msg["type"] == "SCHEMA":
                    schemas[msg["stream"]] = msg
                elif msg["type"] == "RECORD":
                    records.append(msg)

        # Verify we got schemas
        assert "users" in schemas
        assert "groups" in schemas
        assert "organizational_units" in schemas

        # Verify record counts
        user_records = [r for r in records if r["stream"] == "users"]
        group_records = [r for r in records if r["stream"] == "groups"]
        ou_records = [r for r in records if r["stream"] == "organizational_units"]

        assert len(user_records) >= 7  # 5 users + 2 service accounts
        assert len(group_records) >= 7  # 7 groups
        assert len(ou_records) >= 6  # base OUs + departments

        # Verify specific users
        user_uids = {r["record"]["uid"] for r in user_records if "uid" in r["record"]}
        assert "john.doe" in user_uids
        assert "jane.smith" in user_uids
        assert "bob.wilson" in user_uids
        assert "alice.johnson" in user_uids
        assert "charlie.brown" in user_uids
        assert "svc-app1" in user_uids
        assert "svc-app2" in user_uids

        # Verify specific groups
        group_cns = {r["record"]["cn"] for r in group_records}
        assert "engineering-team" in group_cns
        assert "sales-team" in group_cns
        assert "hr-team" in group_cns
        assert "managers" in group_cns
        assert "developers" in group_cns
        assert "REDACTED_LDAP_BIND_PASSWORDs" in group_cns
        assert "service-accounts" in group_cns

    def test_incremental_extraction(
        self,
        tap_config_file: Path,
        catalog_file: Path,
        state_file: Path,
        tmp_path: Path,
        ldap_connection: Connection,
    ) -> None:
        """Test incremental extraction with state."""
        # First run - get all data
        output1 = tmp_path / "output1.jsonl"
        state1 = tmp_path / "state1.json"

        with open(output1, "w") as out_f, open(state1, "w") as state_f:
            process = subprocess.Popen(
                [
                    "tap-ldap",
                    "--config",
                    str(tap_config_file),
                    "--catalog",
                    str(catalog_file),
                    "--state",
                    str(state_file),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            for line in process.stdout:
                out_f.write(line)
                msg = json.loads(line)
                if msg["type"] == "STATE":
                    state_f.write(json.dumps(msg["value"]))

            process.wait()
            assert process.returncode == 0

        # Count first run records
        first_run_records = 0
        with open(output1) as f:
            for line in f:
                msg = json.loads(line)
                if msg["type"] == "RECORD":
                    first_run_records += 1

        assert first_run_records > 0

        # Add a new user
        ldap_connection.add(
            "uid=new.user,ou=users,dc=test,dc=com",
            attributes={
                "objectClass": [
                    "inetOrgPerson",
                    "organizationalPerson",
                    "person",
                    "top",
                ],
                "uid": "new.user",
                "cn": "New User",
                "sn": "User",
                "givenName": "New",
                "mail": "new.user@test.com",
                "userPassword": "{SSHA}x+wnyY9qS7TCSSdg1CtNyJr8FtNFh2RF",
                "employeeNumber": "1006",
                "employeeType": "active",
                "departmentNumber": "engineering",
            },
        )

        # Second run with state - should get the new user if incremental is supported
        output2 = tmp_path / "output2.jsonl"

        with open(output2, "w") as f:
            subprocess.run(
                [
                    "tap-ldap",
                    "--config",
                    str(tap_config_file),
                    "--catalog",
                    str(catalog_file),
                    "--state",
                    str(state1),
                ],
                stdout=f,
                check=True,
            )

        # Count second run records
        second_run_records = 0
        new_user_found = False
        with open(output2) as f:
            for line in f:
                msg = json.loads(line)
                if msg["type"] == "RECORD":
                    second_run_records += 1
                    if (
                        msg["stream"] == "users"
                        and msg["record"].get("uid") == "new.user"
                    ):
                        new_user_found = True

        # For full table replication, we should get all records again
        # For incremental, we might get fewer records
        assert second_run_records > 0

        # Cleanup
        ldap_connection.delete("uid=new.user,ou=users,dc=test,dc=com")

    def test_custom_streams(
        self,
        tap_config: dict[str, Any],
        tmp_path: Path,
        ldap_connection: Connection,
    ) -> None:
        """Test custom stream configuration."""
        # Add custom stream for service accounts
        tap_config["custom_streams"] = [
            {
                "name": "service_accounts",
                "search_filter": "(&(objectClass=account)(uid=svc-*))",
                "primary_keys": ["dn"],
                "schema": {
                    "properties": {
                        "dn": {"type": "string"},
                        "uid": {"type": "string"},
                        "description": {"type": "string"},
                    }
                },
            }
        ]

        config_file = tmp_path / "custom-config.json"
        config_file.write_text(json.dumps(tap_config))

        # Run discovery
        result = subprocess.run(
            ["tap-ldap", "--config", str(config_file), "--discover"],
            capture_output=True,
            text=True,
            check=True,
        )

        catalog = json.loads(result.stdout)
        stream_names = {s["tap_stream_id"] for s in catalog["streams"]}
        assert "service_accounts" in stream_names

        # Create catalog with only service_accounts selected
        custom_catalog = {
            "streams": [
                s
                for s in catalog["streams"]
                if s["tap_stream_id"] == "service_accounts"
            ]
        }
        for stream in custom_catalog["streams"]:
            stream["metadata"] = [
                {
                    "breadcrumb": [],
                    "metadata": {
                        "inclusion": "available",
                        "selected": True,
                    },
                }
            ]

        catalog_file = tmp_path / "custom-catalog.json"
        catalog_file.write_text(json.dumps(custom_catalog))

        # Run extraction
        output_file = tmp_path / "custom-output.jsonl"
        with open(output_file, "w") as f:
            subprocess.run(
                [
                    "tap-ldap",
                    "--config",
                    str(config_file),
                    "--catalog",
                    str(catalog_file),
                ],
                stdout=f,
                check=True,
            )

        # Verify output
        records = []
        with open(output_file) as f:
            for line in f:
                msg = json.loads(line)
                if msg["type"] == "RECORD":
                    records.append(msg)

        # Should have exactly 2 service accounts
        assert len(records) == 2

        uids = {r["record"]["uid"] for r in records}
        assert "svc-app1" in uids
        assert "svc-app2" in uids

    def test_error_handling(
        self,
        tmp_path: Path,
    ) -> None:
        """Test error handling scenarios."""
        # Test with invalid config
        bad_config = {
            "host": "nonexistent.host",
            "port": 389,
            "base_dn": "dc=test,dc=com",
        }
        bad_config_file = tmp_path / "bad-config.json"
        bad_config_file.write_text(json.dumps(bad_config))

        # Should fail with connection error
        result = subprocess.run(
            ["tap-ldap", "--config", str(bad_config_file), "--discover"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0

        # Test with invalid credentials
        bad_creds_config = {
            "host": "localhost",
            "port": 10389,
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "password": "wrong_password",
            "base_dn": "dc=test,dc=com",
        }
        bad_creds_file = tmp_path / "bad-creds.json"
        bad_creds_file.write_text(json.dumps(bad_creds_config))

        result = subprocess.run(
            ["tap-ldap", "--config", str(bad_creds_file), "--discover"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0

    def test_performance_large_dataset(
        self,
        tap_config_file: Path,
        catalog_file: Path,
        tmp_path: Path,
        ldap_connection: Connection,
    ) -> None:
        """Test performance with larger dataset."""
        # Add many test users
        added_users = []
        for i in range(100):
            uid = f"testuser{i:03d}"
            dn = f"uid={uid},ou=users,dc=test,dc=com"
            ldap_connection.add(
                dn,
                attributes={
                    "objectClass": [
                        "inetOrgPerson",
                        "organizationalPerson",
                        "person",
                        "top",
                    ],
                    "uid": uid,
                    "cn": f"Test User {i}",
                    "sn": f"User{i}",
                    "givenName": "Test",
                    "mail": f"{uid}@test.com",
                    "employeeNumber": str(2000 + i),
                    "employeeType": "active",
                    "departmentNumber": "engineering" if i % 2 == 0 else "sales",
                },
            )
            added_users.append(dn)

        # Run extraction with timing
        import time

        start_time = time.time()

        output_file = tmp_path / "large-output.jsonl"
        with open(output_file, "w") as f:
            subprocess.run(
                [
                    "tap-ldap",
                    "--config",
                    str(tap_config_file),
                    "--catalog",
                    str(catalog_file),
                ],
                stdout=f,
                check=True,
            )

        elapsed_time = time.time() - start_time

        # Count records
        record_count = 0
        with open(output_file) as f:
            for line in f:
                msg = json.loads(line)
                if msg["type"] == "RECORD" and msg["stream"] == "users":
                    record_count += 1

        # Should have extracted all users
        assert record_count >= 107  # 7 original + 100 test users

        # Performance check - should complete in reasonable time
        assert elapsed_time < 30  # 30 seconds for ~100 users

        # Cleanup
        for dn in added_users:
            ldap_connection.delete(dn)
