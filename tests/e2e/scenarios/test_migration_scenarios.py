"""Migration scenario tests for LDAP data."""

import time
from typing import Any

from ..helpers.data_generator import LDAPDataGenerator
from ..helpers.ldap_helpers import LDAPTestHelper


class TestMigrationScenarios:
    """Test various LDAP migration scenarios."""

    def test_basic_user_migration(
        self, ldap_source_connection, ldap_target_connection, clean_target_ldap
    ):
        """Test basic user migration from source to target."""
        source_helper = LDAPTestHelper(ldap_source_connection)
        target_helper = LDAPTestHelper(ldap_target_connection)

        # Get all users from source
        source_users = source_helper.export_to_json(
            "dc=source,dc=example,dc=com", "(objectClass=inetOrgPerson)"
        )

        # Migrate users to target
        migrated_count = 0
        for user in source_users:
            # Adjust DN for target domain
            target_dn = user["dn"].replace(
                "dc=source,dc=example,dc=com", "dc=target,dc=example,dc=com"
            )

            # Remove source-specific attributes
            user_attrs = {
                k: v
                for k, v in user.items()
                if k
                not in {
                    "dn",
                    "entryDN",
                    "entryUUID",
                    "entryCSN",
                    "createTimestamp",
                    "modifyTimestamp",
                    "creatorsName",
                    "modifiersName",
                }
            }

            # Handle objectClass properly
            if "objectClass" in user_attrs:
                if isinstance(user_attrs["objectClass"], str):
                    user_attrs["objectClass"] = [user_attrs["objectClass"]]

            if target_helper.connection.add(target_dn, attributes=user_attrs):
                migrated_count += 1

        assert migrated_count == len(
            source_users
        ), f"Only {migrated_count}/{len(source_users)} users migrated"

        # Verify key attributes preserved
        for source_user in source_users[:3]:  # Check first 3 users
            uid = source_user.get("uid")
            if uid:
                comparison = source_helper.compare_entries(
                    f"uid={uid},ou=People,dc=source,dc=example,dc=com",
                    f"uid={uid},ou=People,dc=target,dc=example,dc=com",
                    attributes_to_compare=["cn", "sn", "mail", "employeeNumber"],
                )
                assert comparison[
                    "equal"
                ], f"User {uid} attributes differ: {comparison['differences']}"

    def test_group_migration_with_members(
        self, ldap_source_connection, ldap_target_connection, clean_target_ldap
    ):
        """Test group migration with member references updated."""
        source_helper = LDAPTestHelper(ldap_source_connection)
        target_helper = LDAPTestHelper(ldap_target_connection)

        # First migrate users (needed for group members)
        source_users = source_helper.export_to_json(
            "dc=source,dc=example,dc=com", "(objectClass=inetOrgPerson)"
        )

        for user in source_users:
            target_dn = user["dn"].replace(
                "dc=source,dc=example,dc=com", "dc=target,dc=example,dc=com"
            )
            user_attrs = {
                k: v
                for k, v in user.items()
                if k
                not in {
                    "dn",
                    "entryDN",
                    "entryUUID",
                    "entryCSN",
                    "createTimestamp",
                    "modifyTimestamp",
                }
            }
            target_helper.connection.add(target_dn, attributes=user_attrs)

        # Now migrate groups
        source_groups = source_helper.export_to_json(
            "dc=source,dc=example,dc=com", "(objectClass=groupOfNames)"
        )

        migrated_groups = 0
        for group in source_groups:
            target_dn = group["dn"].replace(
                "dc=source,dc=example,dc=com", "dc=target,dc=example,dc=com"
            )

            # Update member DNs to target domain
            members = group.get("member", [])
            if isinstance(members, str):
                members = [members]

            target_members = [
                member.replace(
                    "dc=source,dc=example,dc=com", "dc=target,dc=example,dc=com"
                )
                for member in members
            ]

            group_attrs = {
                "objectClass": group.get("objectClass", ["groupOfNames"]),
                "cn": group.get("cn"),
                "member": target_members,
            }

            if group.get("description"):
                group_attrs["description"] = group["description"]

            if target_helper.connection.add(target_dn, attributes=group_attrs):
                migrated_groups += 1

        assert migrated_groups == len(
            source_groups
        ), f"Only {migrated_groups}/{len(source_groups)} groups migrated"

        # Verify group memberships
        for group in ["engineering", "sales", "managers"]:
            source_members = set(
                source_helper.get_group_members(
                    f"cn={group},ou=Groups,dc=source,dc=example,dc=com"
                )
            )
            target_members = set(
                target_helper.get_group_members(
                    f"cn={group},ou=Groups,dc=target,dc=example,dc=com"
                )
            )

            # Adjust source members to target domain for comparison
            adjusted_source = {
                m.replace("dc=source,dc=example,dc=com", "dc=target,dc=example,dc=com")
                for m in source_members
            }

            assert (
                adjusted_source == target_members
            ), f"Group {group} members don't match"

    def test_organizational_structure_migration(
        self, ldap_source_connection, ldap_target_connection, clean_target_ldap
    ):
        """Test migration of organizational units and structure."""
        source_helper = LDAPTestHelper(ldap_source_connection)
        target_helper = LDAPTestHelper(ldap_target_connection)

        # Get all OUs from source
        source_ous = source_helper.export_to_json(
            "dc=source,dc=example,dc=com", "(objectClass=organizationalUnit)"
        )

        # Sort by DN length to create parent OUs first
        source_ous.sort(key=lambda x: len(x["dn"].split(",")))

        migrated_ous = 0
        for ou in source_ous:
            target_dn = ou["dn"].replace(
                "dc=source,dc=example,dc=com", "dc=target,dc=example,dc=com"
            )

            # Check if OU already exists (base OUs might be pre-created)
            existing = target_helper.get_entry_as_dict(target_dn)
            if existing:
                migrated_ous += 1
                continue

            ou_attrs = {
                "objectClass": ["organizationalUnit"],
                "ou": ou.get("ou"),
                "description": ou.get("description", f"Migrated {ou.get('ou')}"),
            }

            if target_helper.connection.add(target_dn, attributes=ou_attrs):
                migrated_ous += 1

        # Verify structure
        target_ou_count = target_helper.count_entries(
            "dc=target,dc=example,dc=com", "(objectClass=organizationalUnit)"
        )

        assert target_ou_count >= len(
            source_ous
        ), "Not all organizational units were migrated"

    def test_filtered_migration(
        self, ldap_source_connection, ldap_target_connection, clean_target_ldap
    ):
        """Test migration with filters (e.g., only active users)."""
        source_helper = LDAPTestHelper(ldap_source_connection)
        target_helper = LDAPTestHelper(ldap_target_connection)

        # Get only active users (not terminated)
        active_users = source_helper.export_to_json(
            "dc=source,dc=example,dc=com",
            "(&(objectClass=inetOrgPerson)(!(employeeType=terminated)))",
        )

        # Get all users for comparison
        all_users = source_helper.export_to_json(
            "dc=source,dc=example,dc=com", "(objectClass=inetOrgPerson)"
        )

        # Migrate only active users
        migrated_count = 0
        for user in active_users:
            target_dn = user["dn"].replace(
                "dc=source,dc=example,dc=com", "dc=target,dc=example,dc=com"
            )

            user_attrs = {
                k: v for k, v in user.items() if k not in {"dn", "entryDN", "entryUUID"}
            }

            if target_helper.connection.add(target_dn, attributes=user_attrs):
                migrated_count += 1

        # Verify only active users migrated
        assert migrated_count == len(
            active_users
        ), f"Expected {len(active_users)} active users, migrated {migrated_count}"

        assert len(active_users) < len(all_users), "Filter didn't exclude any users"

        # Verify no terminated users in target
        terminated_in_target = target_helper.count_entries(
            "dc=target,dc=example,dc=com",
            "(&(objectClass=inetOrgPerson)(employeeType=terminated))",
        )

        assert (
            terminated_in_target == 0
        ), f"Found {terminated_in_target} terminated users in target"

    def test_attribute_transformation_migration(
        self, ldap_source_connection, ldap_target_connection, clean_target_ldap
    ):
        """Test migration with attribute transformations."""
        source_helper = LDAPTestHelper(ldap_source_connection)
        target_helper = LDAPTestHelper(ldap_target_connection)
        generator = LDAPDataGenerator(seed=123)

        # Create test users with attributes to transform
        test_users = []
        for i in range(5):
            user_data = generator.generate_user()
            uid = f"transform_test_{i}"

            source_helper.create_test_user(
                uid=uid, base_dn="dc=source,dc=example,dc=com", **user_data
            )
            test_users.append(uid)

        # Define transformations
        def transform_user(user: dict[str, Any]) -> dict[str, Any]:
            """Apply transformations to user attributes."""
            transformed = user.copy()

            # Transform email domain
            if "mail" in transformed:
                transformed["mail"] = transformed["mail"].replace(
                    "@source.example.com", "@target.example.com"
                )

            # Add migration metadata
            transformed["description"] = (
                f"Migrated from source on {time.strftime('%Y-%m-%d')}. "
                f"Original: {user.get('description', 'No description')}"
            )

            # Normalize phone numbers
            for phone_attr in ["telephoneNumber", "mobile"]:
                if phone_attr in transformed:
                    # Remove all non-digits
                    digits = "".join(filter(str.isdigit, str(transformed[phone_attr])))
                    if len(digits) == 10:
                        transformed[phone_attr] = (
                            f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"
                        )

            return transformed

        # Migrate with transformations
        for uid in test_users:
            source_user = source_helper.get_entry_as_dict(
                f"uid={uid},ou=People,dc=source,dc=example,dc=com"
            )

            if source_user:
                # Apply transformations
                transformed = transform_user(source_user)

                # Update DN
                target_dn = transformed["dn"].replace(
                    "dc=source,dc=example,dc=com", "dc=target,dc=example,dc=com"
                )

                # Clean attributes
                user_attrs = {
                    k: v
                    for k, v in transformed.items()
                    if k not in {"dn", "entryDN", "entryUUID"}
                }

                target_helper.connection.add(target_dn, attributes=user_attrs)

        # Verify transformations
        for uid in test_users:
            target_user = target_helper.get_entry_as_dict(
                f"uid={uid},ou=People,dc=target,dc=example,dc=com"
            )

            assert target_user is not None, f"User {uid} not found in target"

            # Check email transformation
            if "mail" in target_user:
                assert (
                    "@target.example.com" in target_user["mail"]
                ), f"Email not transformed: {target_user['mail']}"

            # Check description added
            assert "Migrated from source" in target_user.get(
                "description", ""
            ), "Migration metadata not added"

    def test_conflict_resolution_migration(
        self, ldap_source_connection, ldap_target_connection, clean_target_ldap
    ):
        """Test handling of conflicts during migration."""
        source_helper = LDAPTestHelper(ldap_source_connection)
        target_helper = LDAPTestHelper(ldap_target_connection)

        # Create conflicting user in target
        target_helper.create_test_user(
            uid="conflict_user",
            base_dn="dc=target,dc=example,dc=com",
            cn="Target Conflict User",
            mail="conflict@target.example.com",
            employeeNumber="TARGET001",
        )

        # Create same user in source with different attributes
        source_helper.create_test_user(
            uid="conflict_user",
            base_dn="dc=source,dc=example,dc=com",
            cn="Source Conflict User",
            mail="conflict@source.example.com",
            employeeNumber="SOURCE001",
        )

        # Define conflict resolution strategies
        def resolve_conflict(source_entry: dict, target_entry: dict) -> dict:
            """Merge source and target entries with conflict resolution."""
            merged = target_entry.copy()

            # Keep target employee number, add source as alternate
            if "employeeNumber" in source_entry:
                merged["employeeID"] = source_entry["employeeNumber"]

            # Merge email addresses
            source_mail = source_entry.get("mail", [])
            target_mail = target_entry.get("mail", [])

            if isinstance(source_mail, str):
                source_mail = [source_mail]
            if isinstance(target_mail, str):
                target_mail = [target_mail]

            all_mails = list(set(source_mail + target_mail))
            if len(all_mails) > 1:
                merged["mail"] = all_mails

            # Add conflict note
            merged["description"] = (
                f"CONFLICT RESOLVED: Merged from source. "
                f"Original target: {target_entry.get('cn')}, "
                f"Original source: {source_entry.get('cn')}"
            )

            return merged

        # Get entries
        source_user = source_helper.get_entry_as_dict(
            "uid=conflict_user,ou=People,dc=source,dc=example,dc=com"
        )
        target_user = target_helper.get_entry_as_dict(
            "uid=conflict_user,ou=People,dc=target,dc=example,dc=com"
        )

        # Resolve conflict
        merged = resolve_conflict(source_user, target_user)

        # Update target with merged data
        mods = {}
        for attr, value in merged.items():
            if attr not in {"dn", "uid", "objectClass"}:
                mods[attr] = [(target_helper.connection.MODIFY_REPLACE, value)]

        target_helper.connection.modify(
            "uid=conflict_user,ou=People,dc=target,dc=example,dc=com", mods
        )

        # Verify resolution
        resolved_user = target_helper.get_entry_as_dict(
            "uid=conflict_user,ou=People,dc=target,dc=example,dc=com"
        )

        assert "CONFLICT RESOLVED" in resolved_user.get(
            "description", ""
        ), "Conflict resolution not recorded"

        assert (
            resolved_user.get("employeeID") == "SOURCE001"
        ), "Source employee number not preserved"
