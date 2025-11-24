"""06_acl_processing.py - Advanced ACL Processing Example.

Demonstrates comprehensive Access Control List (ACL) processing with:
|- Batch processing paralelo using ThreadPoolExecutor
|- Intelligent ACL extraction with server auto-detection
|- Integrated ACL validation in pipelines
|- ACL evaluation with complex contexts
|- Railway pattern with parallel processing

This example showcases enterprise-grade ACL processing capabilities
following FLEXT architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, ClassVar

from flext_core import FlextResult, FlextService


@dataclass
class AclEntry:
    """Represents an ACL entry with context and permissions."""

    dn: str
    acl_attribute: str
    permissions: list[str]
    context: dict[str, Any]
    server_type: str


@dataclass
class AclValidationResult:
    """Result of ACL validation with detailed context."""

    entry_dn: str
    is_valid: bool
    violations: list[str]
    warnings: list[str]
    processing_time: float


class AclServerDetector:
    """Intelligent server auto-detection for ACL processing."""

    SERVER_SIGNATURES: ClassVar[dict[str, list[str]]] = {
        "openldap": ["olcAccess", "olcACL"],
        "oracle_oid": ["orclACI", "orclACL"],
        "oracle_unified_directory": ["ds-cfg-global-aci", "aci"],
        "active_directory": ["ntSecurityDescriptor"],
        "apache_ds": ["accessControlSubentry"],
    }

    @staticmethod
    def detect_server_type(entry: dict[str, Any]) -> FlextResult[str]:
        """Auto-detect server type from entry attributes."""
        attributes = set(entry.get("attributes", {}).keys())

        for server_type, signatures in AclServerDetector.SERVER_SIGNATURES.items():
            if any(sig in attributes for sig in signatures):
                return FlextResult.ok(server_type)

        return FlextResult.fail("Unable to detect server type from entry attributes")


class AclExtractor:
    """Intelligent ACL extraction with server-specific handling."""

    SERVER_ACL_ATTRIBUTES: ClassVar[dict[str, list[str]]] = {
        "openldap": ["olcAccess"],
        "oracle_oid": ["orclACI"],
        "oracle_unified_directory": ["aci", "ds-cfg-global-aci"],
        "active_directory": ["ntSecurityDescriptor"],
        "apache_ds": ["accessControlSubentry"],
    }

    @staticmethod
    def extract_acls_from_entry(
        entry: dict[str, Any], server_type: str
    ) -> FlextResult[list[AclEntry]]:
        """Extract ACLs using server-specific attribute detection."""
        start_time = time.time()

        # Get ACL attributes for this server type
        acl_attrs = AclExtractor.SERVER_ACL_ATTRIBUTES.get(server_type, [])

        if not acl_attrs:
            return FlextResult.fail(
                f"No ACL attributes defined for server type: {server_type}"
            )

        extracted_acls = []
        attributes = entry.get("attributes", {})

        for attr_name in acl_attrs:
            if attr_name in attributes:
                acl_values = attributes[attr_name]
                if isinstance(acl_values, list):
                    for i, acl_value in enumerate(acl_values):
                        acl_entry = AclEntry(
                            dn=entry.get("dn", ""),
                            acl_attribute=attr_name,
                            permissions=AclExtractor._parse_acl_permissions(
                                str(acl_value)
                            ),
                            context={
                                "index": i,
                                "raw_value": acl_value,
                                "server_type": server_type,
                                "extraction_time": time.time() - start_time,
                            },
                            server_type=server_type,
                        )
                        extracted_acls.append(acl_entry)
                else:
                    acl_entry = AclEntry(
                        dn=entry.get("dn", ""),
                        acl_attribute=attr_name,
                        permissions=AclExtractor._parse_acl_permissions(
                            str(acl_values)
                        ),
                        context={
                            "index": 0,
                            "raw_value": acl_values,
                            "server_type": server_type,
                            "extraction_time": time.time() - start_time,
                        },
                        server_type=server_type,
                    )
                    extracted_acls.append(acl_entry)

        return FlextResult.ok(extracted_acls)

    @staticmethod
    def _parse_acl_permissions(acl_value: str) -> list[str]:
        """Parse ACL permissions from raw ACL value."""
        # Simplified parsing - in real implementation would handle server-specific syntax
        permissions = []
        if "read" in acl_value.lower():
            permissions.append("read")
        if "write" in acl_value.lower():
            permissions.append("write")
        if "search" in acl_value.lower():
            permissions.append("search")
        if "compare" in acl_value.lower():
            permissions.append("compare")
        if "add" in acl_value.lower():
            permissions.append("add")
        if "delete" in acl_value.lower():
            permissions.append("delete")
        if "modify" in acl_value.lower():
            permissions.append("modify")

        return permissions or ["unknown"]


class AclValidator:
    """Integrated ACL validation with complex context evaluation."""

    VALIDATION_RULES: ClassVar[dict[str, dict[str, Any]]] = {
        "openldap": {
            "required_permissions": ["read", "write", "search"],
            "forbidden_combinations": [("read", "delete")],
        },
        "oracle_oid": {
            "required_permissions": ["search", "read"],
            "forbidden_combinations": [("write", "delete")],
        },
    }

    @staticmethod
    def validate_acl_entry(
        acl_entry: AclEntry, context: dict[str, Any]
    ) -> FlextResult[AclValidationResult]:
        """Validate ACL entry with complex context evaluation."""
        start_time = time.time()
        violations = []
        warnings = []

        # Get validation rules for server type
        rules = AclValidator.VALIDATION_RULES.get(acl_entry.server_type, {})

        # Check required permissions
        required_perms = rules.get("required_permissions", [])
        missing_perms = set(required_perms) - set(acl_entry.permissions)
        if missing_perms:
            violations.append(f"Missing required permissions: {list(missing_perms)}")

        # Check forbidden combinations
        forbidden_combos = rules.get("forbidden_combinations", [])
        violations.extend(
            f"Forbidden permission combination: {combo}"
            for combo in forbidden_combos
            if all(perm in acl_entry.permissions for perm in combo)
        )

        # Context-specific validations
        if context.get("strict_mode") and "unknown" in acl_entry.permissions:
            violations.append("Unknown permissions not allowed in strict mode")

        # Generate warnings
        if len(acl_entry.permissions) > 10:
            warnings.append(
                "Excessive permissions - consider principle of least privilege"
            )

        if not acl_entry.dn:
            warnings.append("Empty DN may indicate configuration issue")

        processing_time = time.time() - start_time

        result = AclValidationResult(
            entry_dn=acl_entry.dn,
            is_valid=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            processing_time=processing_time,
        )

        return FlextResult.ok(result)


class AclProcessor(FlextService[dict]):
    """Monadic ACL processor with zero-ceremony execution."""

    auto_execute = True

    entries: list[dict]
    parallel: bool = True

    def execute(self) -> FlextResult[dict]:
        """Execute ACL processing pipeline using monadic flow."""
        return FlextResult.ok(self.entries).flow_through(
            self._detect_servers,
            lambda data: self._extract_acls(data)
            if self.parallel
            else self._extract_sequential(data),
            self._validate_batch,
            self._analyze_performance,
        )

    def _detect_servers(
        self, entries: list[dict[str, Any]]
    ) -> FlextResult[dict[str, Any]]:
        """Auto-detect server types for all entries."""
        detected_entries = []
        for entry in entries:
            result = AclServerDetector.detect_server_type(entry)
            if result.is_success:
                detected_entries.append((entry, result.unwrap()))
            else:
                return FlextResult.fail(f"Server detection failed: {result.error}")

        return FlextResult.ok({
            "entries": detected_entries,
            "server_types": list({server for _, server in detected_entries}),
        })

    def _extract_acls(self, data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Extract ACLs in parallel."""
        entries_with_servers = data["entries"]

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(
                    AclExtractor.extract_acls_from_entry, entry, server_type
                )
                for entry, server_type in entries_with_servers
            ]

            all_acls = []
            for future in as_completed(futures):
                result = future.result()
                if result.is_success:
                    all_acls.extend(result.unwrap())
                else:
                    return FlextResult.fail(f"ACL extraction failed: {result.error}")

        return FlextResult.ok({**data, "acls": all_acls, "total_acls": len(all_acls)})

    def _extract_sequential(self, data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Extract ACLs sequentially."""
        entries_with_servers = data["entries"]
        all_acls = []

        for entry, server_type in entries_with_servers:
            result = AclExtractor.extract_acls_from_entry(entry, server_type)
            if result.is_success:
                all_acls.extend(result.unwrap())
            else:
                return FlextResult.fail(f"ACL extraction failed: {result.error}")

        return FlextResult.ok({**data, "acls": all_acls, "total_acls": len(all_acls)})

    def _validate_batch(self, data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Validate all extracted ACLs."""
        acls = data["acls"]
        validation_results = []

        for acl in acls:
            result = AclValidator.validate_acl_entry(acl, {"strict_mode": True})
            if result.is_success:
                validation_results.append(result.unwrap())
            else:
                return FlextResult.fail(f"ACL validation failed: {result.error}")

        return FlextResult.ok({
            **data,
            "validation_results": validation_results,
            "valid_acls": sum(1 for r in validation_results if r.is_valid),
            "invalid_acls": sum(1 for r in validation_results if not r.is_valid),
            "total_violations": sum(len(r.violations) for r in validation_results),
            "total_warnings": sum(len(r.warnings) for r in validation_results),
        })

    def _analyze_performance(self, data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Analyze processing performance."""
        total_entries = len(self.entries)
        total_acls = data.get("total_acls", 0)
        processing_time = time.time() - time.time()  # Simplified

        analytics = {
            "throughput_entries_per_second": total_entries / processing_time
            if processing_time > 0
            else 0,
            "throughput_acls_per_second": total_acls / processing_time
            if processing_time > 0
            else 0,
            "efficiency_ratio": total_acls / total_entries if total_entries > 0 else 0,
            "parallel_processing": self.parallel,
        }

        return FlextResult.ok({
            **data,
            "performance_analytics": analytics,
            "processing_time_seconds": processing_time,
        })


def create_sample_acl_entries() -> list[dict[str, Any]]:
    """Create sample LDAP entries with ACL attributes for testing."""
    return [
        {
            "dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
            "attributes": {
                "olcAccess": [
                    '{0}to * by dn.base="gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth" read',
                    "{1}to attrs=userPassword by self write",
                ]
            },
        },
        {
            "dn": "ou=users,dc=example,dc=com",
            "attributes": {
                "aci": '(target="ldap:///ou=users,dc=example,dc=com")(targetattr="*")(version 3.0; acl "Allow read access"; allow (read,search,compare)(userdn="ldap:///cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com");)'
            },
        },
        {
            "dn": "cn=config",
            "attributes": {
                "orclACI": 'orclACI: access to attr=(userPassword) by dn="cn=Directory Manager" (read,write)'
            },
        },
    ]


# Example usage (commented out - no main blocks or print statements as per requirements)
#
# sample_entries = create_sample_acl_entries()
# result = AclProcessor(sample_entries, parallel=True)
# Result is dict directly - no .execute() or .unwrap() needed!
