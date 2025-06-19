"""Edge case tests for LDAP pipeline components."""

import json
import subprocess
from pathlib import Path

import pytest

from ..conftest import temporary_config_file
from ..helpers.ldap_helpers import LDAPTestHelper


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_empty_ldap_source(
        self,
        ldap_source_connection,
        ldap_target_connection,
        clean_target_ldap,
        tap_ldap_config,
        target_ldap_config,
    ):
        """Test handling of empty LDAP source."""
        source_helper = LDAPTestHelper(ldap_source_connection)

        # Clean all entries from a specific OU
        source_helper.cleanup_test_entries(
            base_dn="dc=source,dc=example,dc=com",
            prefix="",  # Clean everything
        )

        # Run tap with empty source
        with temporary_config_file(tap_ldap_config, "tap_ldap"):
            # Override base_dn to search in a non-existent OU
            empty_config = tap_ldap_config.copy()
            empty_config["base_dn"] = "ou=NonExistent,dc=source,dc=example,dc=com"

            with temporary_config_file(empty_config, "tap_ldap_empty") as empty_cfg:
                result = subprocess.run(
                    ["python", "-m", "tap_ldap", "--config", empty_cfg],
                    cwd=str(Path(__file__).parent.parent.parent.parent / "tap-ldap"),
                    capture_output=True,
                    text=True,
                    check=False,
                )

                # Should succeed even with no data
                assert result.returncode == 0, (
                    f"tap-ldap failed on empty source: {result.stderr}"
                )

                # Verify output contains schema but no records
                has_schema = False
                has_records = False

                for line in result.stdout.strip().split("\n"):
                    try:
                        msg = json.loads(line)
                        if msg.get("type") == "SCHEMA":
                            has_schema = True
                        elif msg.get("type") == "RECORD":
                            has_records = True
                    except json.JSONDecodeError:
                        continue

                assert has_schema, "No schema output for empty source"
                assert not has_records, "Found records in empty source"

    def test_special_characters_in_dn(
        self, ldap_source_connection, ldap_target_connection, clean_target_ldap
    ):
        """Test handling of special characters in DNs and attributes."""
        source_helper = LDAPTestHelper(ldap_source_connection)
        LDAPTestHelper(ldap_target_connection)

        # Create users with special characters
        special_users = [
            {
                "uid": "john.o'neill",
                "cn": "John O'Neill",
                "sn": "O'Neill",
                "description": 'User with quotes "and" apostrophes',
            },
            {
                "uid": "maria-josé",
                "cn": "María José García",
                "sn": "García",
                "description": "User with UTF-8: ñáéíóú",
            },
            {
                "uid": "user_with_comma",
                "cn": "Smith, John",
                "sn": "Smith",
                "description": "DN with comma: cn=Smith\\, John",
            },
            {
                "uid": "user+with+plus",
                "cn": "User Plus",
                "sn": "Plus",
                "description": "UID with + signs",
            },
        ]

        created_users = []
        for user in special_users:
            if source_helper.create_test_user(
                uid=user["uid"], base_dn="dc=source,dc=example,dc=com", **user
            ):
                created_users.append(user["uid"])

        # Export and verify special characters preserved
        exported = source_helper.export_to_json(
            "dc=source,dc=example,dc=com",
            f"(|(uid={created_users[0]})(uid={created_users[1]}))",
        )

        assert len(exported) >= 2, "Special character users not exported"

        # Verify attributes preserved
        for entry in exported:
            if "O'Neill" in entry.get("cn", ""):
                assert "'" in entry["cn"], "Apostrophe not preserved"
            if "García" in entry.get("sn", ""):
                assert "í" in entry["sn"], "UTF-8 not preserved"

    def test_large_attribute_values(self, ldap_source_connection, tap_ldap_config) -> Any:
        """Test handling of large attribute values."""
        source_helper = LDAPTestHelper(ldap_source_connection)

        # Create user with large attributes
        large_description = "A" * 10000  # 10KB description
        large_notes = [
            "Note " + str(i) * 100 for i in range(100)
        ]  # Multiple large values

        source_helper.create_test_user(
            uid="large_attr_user",
            base_dn="dc=source,dc=example,dc=com",
            description=large_description,
            info=large_notes,
        )

        # Run tap and verify large attributes handled
        with temporary_config_file(tap_ldap_config, "tap_ldap") as config_file:
            result = subprocess.run(
                ["python", "-m", "tap_ldap", "--config", config_file],
                cwd=str(Path(__file__).parent.parent.parent.parent / "tap-ldap"),
                capture_output=True,
                text=True,
                check=False,
            )

            assert result.returncode == 0, "Failed with large attributes"

            # Find the large user in output
            found_large_user = False
            for line in result.stdout.strip().split("\n"):
                try:
                    msg = json.loads(line)
                    if (
                        msg.get("type") == "RECORD"
                        and msg.get("record", {}).get("uid") == "large_attr_user"
                    ):
                        found_large_user = True
                        # Verify large description preserved
                        desc = msg["record"].get("description", "")
                        assert len(desc) >= 10000, "Large description truncated"
                except json.JSONDecodeError:
                    continue

            assert found_large_user, "Large attribute user not found"

    def test_circular_group_membership(
        self, ldap_source_connection, ldap_target_connection
    ):
        """Test handling of circular group memberships."""
        source_helper = LDAPTestHelper(ldap_source_connection)

        # Create groups with circular membership
        base_dn = "dc=source,dc=example,dc=com"

        # Create initial groups
        source_helper.create_test_group(
            cn="group_a", base_dn=base_dn, members=[f"cn=admin,{base_dn}"]
        )

        source_helper.create_test_group(
            cn="group_b", base_dn=base_dn, members=[f"cn=group_a,ou=Groups,{base_dn}"]
        )

        source_helper.create_test_group(
            cn="group_c", base_dn=base_dn, members=[f"cn=group_b,ou=Groups,{base_dn}"]
        )

        # Create circular reference: A -> B -> C -> A
        source_helper.add_user_to_group(
            f"cn=group_c,ou=Groups,{base_dn}", f"cn=group_a,ou=Groups,{base_dn}"
        )

        # Export groups and verify no infinite loop
        groups = source_helper.export_to_json(base_dn, "(objectClass=groupOfNames)")

        # Should have all three groups
        group_cns = [g.get("cn") for g in groups]
        assert "group_a" in group_cns
        assert "group_b" in group_cns
        assert "group_c" in group_cns

    def test_binary_attribute_handling(self, ldap_source_connection, tap_ldap_config) -> Any:
        """Test handling of binary attributes like photos."""
        source_helper = LDAPTestHelper(ldap_source_connection)

        # Create user with binary photo
        import base64

        # Create a small test image (1x1 pixel PNG)
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )

        # Create user with photo
        dn = "uid=photo_user,ou=People,dc=source,dc=example,dc=com"
        attrs = {
            "objectClass": ["inetOrgPerson", "posixAccount", "shadowAccount"],
            "uid": "photo_user",
            "cn": "Photo User",
            "sn": "User",
            "uidNumber": "30001",
            "gidNumber": "30001",
            "homeDirectory": "/home/photo_user",
            "userPassword": "{SSHA}password123",
            "jpegPhoto": png_data,  # Binary attribute
        }

        source_helper.connection.add(dn, attributes=attrs)

        # Run tap with binary attributes
        with temporary_config_file(tap_ldap_config, "tap_ldap") as config_file:
            result = subprocess.run(
                ["python", "-m", "tap_ldap", "--config", config_file],
                cwd=str(Path(__file__).parent.parent.parent.parent / "tap-ldap"),
                capture_output=True,
                text=True,
                check=False,
            )

            assert result.returncode == 0, "Failed with binary attributes"

            # Verify binary attribute handled (should be base64 encoded in JSON)
            found_photo_user = False
            for line in result.stdout.strip().split("\n"):
                try:
                    msg = json.loads(line)
                    if (
                        msg.get("type") == "RECORD"
                        and msg.get("record", {}).get("uid") == "photo_user"
                    ):
                        found_photo_user = True
                        # Binary should be base64 encoded string
                        photo = msg["record"].get("jpegPhoto")
                        assert photo is not None, "Binary attribute missing"
                        # Verify it's base64
                        try:
                            base64.b64decode(photo)
                        except Exception:
                            pytest.fail("Binary attribute not properly base64 encoded")
                except json.JSONDecodeError:
                    continue

            assert found_photo_user, "User with binary attribute not found"

    def test_pagination_edge_cases(self, ldap_source_connection, tap_ldap_config) -> Any:
        """Test pagination with exact page boundaries."""
        source_helper = LDAPTestHelper(ldap_source_connection)

        # Create exactly page_size + 1 users to test boundary
        page_size = tap_ldap_config.get("page_size", 100)

        created_users = source_helper.bulk_create_users(
            base_dn="dc=source,dc=example,dc=com",
            count=page_size + 1,
            prefix="pagetest",
        )

        # Run tap with specific page size
        config_with_page = tap_ldap_config.copy()
        config_with_page["page_size"] = page_size

        with temporary_config_file(config_with_page, "tap_ldap_page") as config_file:
            result = subprocess.run(
                ["python", "-m", "tap_ldap", "--config", config_file],
                cwd=str(Path(__file__).parent.parent.parent.parent / "tap-ldap"),
                capture_output=True,
                text=True,
                check=False,
            )

            assert result.returncode == 0, "Pagination test failed"

            # Count extracted pagetest users
            pagetest_count = 0
            for line in result.stdout.strip().split("\n"):
                try:
                    msg = json.loads(line)
                    if msg.get("type") == "RECORD" and "pagetest" in msg.get(
                        "record", {}
                    ).get("uid", ""):
                        pagetest_count += 1
                except json.JSONDecodeError:
                    continue

            assert pagetest_count == len(created_users), (
                f"Expected {len(created_users)} users, got {pagetest_count}"
            )

        # Clean up
        source_helper.cleanup_test_entries(
            base_dn="dc=source,dc=example,dc=com", prefix="pagetest"
        )

    def test_connection_failure_recovery(self, tap_ldap_config, docker_client) -> Any:
        """Test recovery from connection failures."""
        # Use invalid config to simulate connection failure
        bad_config = tap_ldap_config.copy()
        bad_config["port"] = 99999  # Invalid port

        with temporary_config_file(bad_config, "tap_ldap_bad") as config_file:
            result = subprocess.run(
                ["python", "-m", "tap_ldap", "--config", config_file],
                cwd=str(Path(__file__).parent.parent.parent.parent / "tap-ldap"),
                capture_output=True,
                text=True,
                check=False,
            )

            # Should fail gracefully
            assert result.returncode != 0, "Should fail with bad connection"
            assert (
                "error" in result.stderr.lower() or "failed" in result.stderr.lower()
            ), "No error message for connection failure"

    def test_schema_validation_edge_cases(
        self, ldap_source_connection, ldap_target_connection
    ):
        """Test schema validation with non-standard object classes."""
        source_helper = LDAPTestHelper(ldap_source_connection)

        # Create entry with minimal object class
        dn = "cn=minimal_entry,dc=source,dc=example,dc=com"
        attrs = {
            "objectClass": ["top", "device"],  # Minimal structural class
            "cn": "minimal_entry",
        }

        source_helper.connection.add(dn, attributes=attrs)

        # Create entry with auxiliary classes
        dn2 = "uid=aux_user,ou=People,dc=source,dc=example,dc=com"
        attrs2 = {
            "objectClass": [
                "inetOrgPerson",
                "posixAccount",
                "shadowAccount",
                "extensibleObject",
            ],
            "uid": "aux_user",
            "cn": "Auxiliary User",
            "sn": "User",
            "uidNumber": "40001",
            "gidNumber": "40001",
            "homeDirectory": "/home/aux_user",
            "customAttribute": "Custom Value",  # extensibleObject allows any attribute
        }

        source_helper.connection.add(dn2, attributes=attrs2)

        # Export and verify both handled
        all_entries = source_helper.export_to_json(
            "dc=source,dc=example,dc=com", "(|(cn=minimal_entry)(uid=aux_user))"
        )

        assert len(all_entries) >= 2, "Special schema entries not exported"

        # Verify custom attribute preserved
        for entry in all_entries:
            if entry.get("uid") == "aux_user":
                assert "customAttribute" in entry, "Custom attribute not preserved"

    def test_multi_valued_attribute_operations(
        self, ldap_source_connection, ldap_target_connection
    ):
        """Test operations on multi-valued attributes."""
        source_helper = LDAPTestHelper(ldap_source_connection)

        # Create user with multiple values for various attributes
        dn = "uid=multi_user,ou=People,dc=source,dc=example,dc=com"
        attrs = {
            "objectClass": ["inetOrgPerson", "posixAccount", "shadowAccount"],
            "uid": "multi_user",
            "cn": ["Multi User", "Multiple Names User", "M. User"],
            "sn": "User",
            "mail": [
                "multi.user@example.com",
                "m.user@example.com",
                "multi@example.com",
            ],
            "telephoneNumber": ["+1-555-0001", "+1-555-0002", "+1-555-0003"],
            "uidNumber": "50001",
            "gidNumber": "50001",
            "homeDirectory": "/home/multi_user",
            "description": [
                "Primary description",
                "Secondary description",
                "Additional notes",
            ],
        }

        source_helper.connection.add(dn, attributes=attrs)

        # Export and verify multi-valued attributes
        entry = source_helper.get_entry_as_dict(dn)

        assert isinstance(entry.get("cn"), list), (
            "Multi-valued cn not preserved as list"
        )
        assert len(entry.get("cn", [])) == 3, "Not all cn values preserved"
        assert isinstance(entry.get("mail"), list), "Multi-valued mail not preserved"
        assert len(entry.get("mail", [])) == 3, "Not all mail values preserved"
