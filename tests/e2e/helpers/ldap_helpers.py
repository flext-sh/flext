"""LDAP helper utilities for E2E tests."""

import base64
import hashlib
from typing import Any

from ldap3 import MODIFY_ADD, MODIFY_DELETE, SUBTREE, Connection
from ldap3.core.exceptions import LDAPException


class LDAPTestHelper:
    """Helper class for LDAP operations in tests."""

    def __init__(self, connection: Connection):
        self.connection = connection

    def create_test_user(self, uid: str, base_dn: str, **attributes) -> bool:
        """Create a test user with given attributes."""
        dn = f"uid={uid},ou=People,{base_dn}"

        # Default attributes
        attrs = {
            "objectClass": ["inetOrgPerson", "posixAccount", "shadowAccount"],
            "uid": uid,
            "cn": attributes.get("cn", f"Test User {uid}"),
            "sn": attributes.get("sn", "User"),
            "givenName": attributes.get("givenName", "Test"),
            "userPassword": self._hash_password(
                attributes.get("password", "password123")
            ),
            "uidNumber": attributes.get("uidNumber", "20000"),
            "gidNumber": attributes.get("gidNumber", "20000"),
            "homeDirectory": f"/home/{uid}",
            "loginShell": "/bin/bash",
        }

        # Add custom attributes
        for key, value in attributes.items():
            if key not in {"password", "objectClass"}:
                attrs[key] = value

        return self.connection.add(dn, attributes=attrs)

    def create_test_group(
        self, cn: str, base_dn: str, members: list[str] | None = None, **attributes
    ) -> bool:
        """Create a test group with given members."""
        dn = f"cn={cn},ou=Groups,{base_dn}"

        attrs = {
            "objectClass": ["groupOfNames"],
            "cn": cn,
            "member": members or [f"cn=admin,{base_dn}"],
        }

        # Add custom attributes
        for key, value in attributes.items():
            if key not in {"objectClass", "member"}:
                attrs[key] = value

        return self.connection.add(dn, attributes=attrs)

    def add_user_to_group(self, user_dn: str, group_dn: str) -> bool:
        """Add a user to a group."""
        return self.connection.modify(group_dn, {"member": [(MODIFY_ADD, [user_dn])]})

    def remove_user_from_group(self, user_dn: str, group_dn: str) -> bool:
        """Remove a user from a group."""
        return self.connection.modify(
            group_dn, {"member": [(MODIFY_DELETE, [user_dn])]}
        )

    def get_entry_as_dict(
        self, dn: str, attributes: list[str] | None = None
    ) -> dict[str, Any] | None:
        """Get an LDAP entry as a dictionary."""
        self.connection.search(
            search_base=dn,
            search_filter="(objectClass=*)",
            search_scope=SUBTREE,
            attributes=attributes or ["*"],
        )

        if not self.connection.entries:
            return None

        entry = self.connection.entries[0]
        result = {"dn": entry.entry_dn}

        for attr in entry:
            if attr.key != "dn":
                if len(attr.values) == 1:
                    result[attr.key] = attr.values[0]
                else:
                    result[attr.key] = attr.values

        return result

    def compare_entries(
        self,
        dn1: str,
        dn2: str,
        attributes_to_compare: list[str] | None = None,
        ignore_attributes: list[str] | None = None,
    ) -> dict[str, Any]:
        """Compare two LDAP entries."""
        entry1 = self.get_entry_as_dict(dn1)
        entry2 = self.get_entry_as_dict(dn2)

        if not entry1 or not entry2:
            return {
                "equal": False,
                "reason": "One or both entries not found",
                "entry1_exists": entry1 is not None,
                "entry2_exists": entry2 is not None,
            }

        ignore_attrs = set(
            ignore_attributes
            or [
                "dn",
                "entryUUID",
                "entryCSN",
                "createTimestamp",
                "modifyTimestamp",
                "creatorsName",
                "modifiersName",
            ]
        )

        if attributes_to_compare:
            attrs_to_check = set(attributes_to_compare)
        else:
            attrs_to_check = set(entry1.keys()) | set(entry2.keys())

        attrs_to_check -= ignore_attrs

        differences = {}
        for attr in attrs_to_check:
            val1 = entry1.get(attr)
            val2 = entry2.get(attr)

            if val1 != val2:
                differences[attr] = {"entry1": val1, "entry2": val2}

        return {
            "equal": len(differences) == 0,
            "differences": differences,
            "attributes_compared": list(attrs_to_check),
        }

    def export_to_json(
        self,
        base_dn: str,
        search_filter: str = "(objectClass=*)",
        attributes: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Export LDAP entries to JSON format."""
        self.connection.search(
            search_base=base_dn,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=attributes or ["*"],
        )

        results = []
        for entry in self.connection.entries:
            entry_dict = {"dn": entry.entry_dn}

            for attr in entry:
                if attr.key != "dn":
                    if len(attr.values) == 1:
                        entry_dict[attr.key] = attr.values[0]
                    else:
                        entry_dict[attr.key] = attr.values

            results.append(entry_dict)

        return results

    def bulk_create_users(
        self, base_dn: str, count: int, prefix: str = "testuser"
    ) -> list[str]:
        """Create multiple test users."""
        created_dns = []

        for i in range(count):
            uid = f"{prefix}{i:04d}"
            if self.create_test_user(
                uid=uid,
                base_dn=base_dn,
                cn=f"Test User {i:04d}",
                mail=f"{uid}@test.example.com",
                employeeNumber=f"TEST{i:04d}",
            ):
                created_dns.append(f"uid={uid},ou=People,{base_dn}")

        return created_dns

    def verify_schema_compliance(
        self, dn: str, expected_object_classes: list[str]
    ) -> dict[str, Any]:
        """Verify an entry complies with expected schema."""
        entry = self.get_entry_as_dict(dn, ["objectClass", "*"])

        if not entry:
            return {"compliant": False, "reason": "Entry not found"}

        actual_classes = entry.get("objectClass", [])
        if isinstance(actual_classes, str):
            actual_classes = [actual_classes]

        missing_classes = set(expected_object_classes) - set(actual_classes)

        return {
            "compliant": len(missing_classes) == 0,
            "missing_classes": list(missing_classes),
            "actual_classes": actual_classes,
        }

    def get_group_members(self, group_dn: str) -> list[str]:
        """Get all members of a group."""
        entry = self.get_entry_as_dict(group_dn, ["member"])
        if not entry:
            return []

        members = entry.get("member", [])
        if isinstance(members, str):
            members = [members]

        return members

    def count_entries(
        self, base_dn: str, search_filter: str = "(objectClass=*)"
    ) -> int:
        """Count entries matching a filter."""
        self.connection.search(
            search_base=base_dn,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=["dn"],
        )
        return len(self.connection.entries)

    def _hash_password(self, password: str) -> str:
        """Create SSHA password hash."""
        salt = base64.b64encode(os.urandom(16)).decode()
        sha = hashlib.sha1()
        sha.update(password.encode())
        sha.update(salt.encode())
        return "{SSHA}" + base64.b64encode(sha.digest() + salt.encode()).decode()

    def cleanup_test_entries(self, base_dn: str, prefix: str = "test"):
        """Clean up test entries created during tests."""
        # Find all test entries
        self.connection.search(
            search_base=base_dn,
            search_filter=f"(|(uid={prefix}*)(cn={prefix}*))",
            search_scope=SUBTREE,
            attributes=["dn"],
        )

        dns_to_delete = [entry.entry_dn for entry in self.connection.entries]

        # Delete in reverse order (deepest first)
        for dn in sorted(dns_to_delete, reverse=True):
            try:
                self.connection.delete(dn)
            except LDAPException:
                pass  # Ignore errors, entry might already be deleted


import os
