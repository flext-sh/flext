"""acl_processing_example.py - ACL Processing Example Module.

This module provides an example of advanced Access Control List (ACL) processing
capabilities in the FLEXT ecosystem. It demonstrates:
- Parallel batch processing using ThreadPoolExecutor
- Intelligent server type auto-detection from LDAP entries
- Server-specific ACL attribute extraction
- Comprehensive ACL validation with rule-based checking
- Performance analytics and railway-oriented error handling

Scope: Example implementation showing enterprise-grade ACL processing patterns,
server detection algorithms, and validation pipelines for LDAP/Directory services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from collections.abc import Mapping, MutableSequence, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import StrEnum, unique
from typing import ClassVar, TypeIs

from flext_core import r, t
from pydantic import BaseModel, ConfigDict, Field

EntryDict = Mapping[
    str, t.Scalar | t.StrSequence | Mapping[str, t.Scalar | t.StrSequence]
]

ProcessingDict = t.ContainerMapping
ContextDict = t.ContainerValueMapping


def _new_str_list() -> MutableSequence[str]:
    return []


def _is_object_list(
    value: t.NormalizedValue,
) -> TypeIs[t.ContainerList]:
    return isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray)
    )


def _is_str_object_dict(
    value: t.NormalizedValue,
) -> TypeIs[t.ContainerMapping]:
    return isinstance(value, Mapping)


def _is_entry_dict(value: t.NormalizedValue) -> TypeIs[EntryDict]:
    return isinstance(value, Mapping)


class AclProcessingExample:
    """Advanced ACL processing example demonstrating enterprise-grade ACL capabilities."""

    @unique
    class ServerType(StrEnum):
        """Server type enumeration."""

        OPENLDAP = "openldap"
        ORACLE_OID = "oracle_oid"
        ORACLE_UNIFIED_DIRECTORY = "oracle_unified_directory"
        ACTIVE_DIRECTORY = "active_directory"
        APACHE_DS = "apache_ds"
        UNKNOWN = "unknown"

    @unique
    class Permission(StrEnum):
        """Permission enumeration."""

        READ = "read"
        WRITE = "write"
        DELETE = "delete"
        SEARCH = "search"
        UNKNOWN = "unknown"

    class AclEntry(BaseModel):
        """Represents an ACL entry with context and permissions."""

        model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

        dn: str = Field(description="Distinguished name of the ACL entry")
        acl_attribute: str = Field(description="ACL attribute name")
        permissions: t.StrSequence = Field(description="List of permissions")
        context: ContextDict = Field(description="Context information")
        server_type: str = Field(description="Type of LDAP server")

    class AclValidationResult(BaseModel):
        """Result of ACL validation with detailed context."""

        model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

        entry_dn: str = Field(description="Distinguished name of the entry")
        is_valid: bool = Field(description="Whether the ACL entry is valid")
        violations: t.StrSequence = Field(
            default_factory=_new_str_list,
            description="List of validation violations",
        )
        warnings: t.StrSequence = Field(
            default_factory=_new_str_list,
            description="List of validation warnings",
        )
        processing_time: float = Field(
            default=0.0,
            description="Time taken for validation",
        )

    class Constants:
        """Constants for ACL processing."""

        SERVER_SIGNATURES: ClassVar[Mapping[str, t.StrSequence]] = {
            "openldap": ["olcAccess", "olcACL"],
            "oracle_oid": ["orclACI", "orclACL"],
            "oracle_unified_directory": ["ds-cfg-global-aci", "aci"],
            "active_directory": ["ntSecurityDescriptor"],
            "apache_ds": ["accessControlSubentry"],
        }
        SERVER_ACL_ATTRIBUTES: ClassVar[Mapping[str, t.StrSequence]] = {
            "openldap": ["olcAccess"],
            "oracle_oid": ["orclACI"],
            "oracle_unified_directory": ["aci", "ds-cfg-global-aci"],
            "active_directory": ["ntSecurityDescriptor"],
            "apache_ds": ["accessControlSubentry"],
        }

    @staticmethod
    def _parse_acl_permissions(acl_value: str) -> MutableSequence[str]:
        """Parse ACL permissions from raw ACL value."""
        acl_lower = acl_value.lower()
        permissions = [
            perm.value
            for perm in AclProcessingExample.Permission.__members__.values()
            if perm != AclProcessingExample.Permission.UNKNOWN
            and perm.value in acl_lower
        ]
        return permissions or [AclProcessingExample.Permission.UNKNOWN.value]

    @staticmethod
    def detect_server_type(entry: EntryDict) -> r[str]:
        """Auto-detect server type from entry attributes."""
        attributes = entry.get("attributes", {})
        if not isinstance(attributes, Mapping):
            return r[str].fail("Invalid entry attributes format")
        attr_keys: set[str] = set(attributes.keys())
        for (
            server_type,
            signatures,
        ) in AclProcessingExample.Constants.SERVER_SIGNATURES.items():
            if any(sig in attr_keys for sig in signatures):
                return r[str].ok(server_type)
        return r[str].fail("Unable to detect server type from entry attributes")

    @staticmethod
    def extract_acls_from_entry(
        entry: EntryDict, server_type: str
    ) -> r[Sequence[AclProcessingExample.AclEntry]]:
        """Extract ACLs using server-specific attribute detection."""
        start_time = time.time()
        acl_attrs = AclProcessingExample.Constants.SERVER_ACL_ATTRIBUTES.get(
            server_type, []
        )
        if not acl_attrs:
            return r[Sequence[AclProcessingExample.AclEntry]].fail(
                f"No ACL attributes defined for server type: {server_type}"
            )
        extracted_acls: MutableSequence[AclProcessingExample.AclEntry] = []
        attributes = entry.get("attributes", {})
        if not isinstance(attributes, Mapping):
            return r[Sequence[AclProcessingExample.AclEntry]].fail(
                "Invalid attributes format"
            )
        for attr_name in acl_attrs:
            if attr_name in attributes:
                acl_values = attributes[attr_name]
                if isinstance(acl_values, str):
                    values_list = [acl_values]
                elif isinstance(acl_values, Sequence) and not isinstance(
                    acl_values, (str, bytes, bytearray)
                ):
                    values_list = acl_values
                else:
                    continue
                for i, acl_value in enumerate(values_list):
                    acl_entry = AclProcessingExample.AclEntry(
                        dn=str(entry.get("dn", "")),
                        acl_attribute=attr_name,
                        permissions=AclProcessingExample._parse_acl_permissions(
                            str(acl_value)
                        ),
                        context={
                            "index": i,
                            "raw_value": str(acl_value),
                            "server_type": server_type,
                            "extraction_time": time.time() - start_time,
                        },
                        server_type=server_type,
                    )
                    extracted_acls.append(acl_entry)
        return r[Sequence[AclProcessingExample.AclEntry]].ok(extracted_acls)

    @staticmethod
    def validate_acl_entry(
        acl_entry: t.ContainerMapping, _context: ContextDict
    ) -> r[AclProcessingExample.AclValidationResult]:
        """Validate ACL entry with complex context evaluation."""
        start_time = time.time()
        violations: MutableSequence[str] = []
        warnings: MutableSequence[str] = []
        server_type = acl_entry.get("server_type")
        permissions_raw = acl_entry.get("permissions")
        permissions: t.StrSequence = (
            tuple(
                permission
                for permission in permissions_raw
                if isinstance(permission, str)
            )
            if isinstance(permissions_raw, Sequence)
            and not isinstance(permissions_raw, (str, bytes, bytearray))
            else ()
        )
        dn = str(acl_entry.get("dn", ""))
        required_permissions: t.StrSequence = []
        forbidden_combinations: t.StrSequence = []
        if server_type == "openldap":
            required_permissions = ["read", "write", "search"]
            forbidden_combinations = ["read|delete"]
        elif server_type == "oracle_oid":
            required_permissions = ["search", "read"]
            forbidden_combinations = ["write|delete"]

        if required_permissions:
            missing_perms: set[str] = set(required_permissions) - set(
                permissions,
            )
            if missing_perms:
                violations.append(
                    f"Missing required permissions: {tuple(missing_perms)}"
                )
            violations.extend(
                f"Forbidden permission combination: {combo}"
                for combo in forbidden_combinations
                if all(permission in permissions for permission in combo.split("|"))
            )
        if (
            _context.get("strict_mode")
            and AclProcessingExample.Permission.UNKNOWN.value in permissions
        ):
            violations.append("Unknown permissions not allowed in strict mode")
        if len(permissions) > 10:
            warnings.append(
                "Excessive permissions - consider principle of least privilege"
            )
        if not dn:
            warnings.append("Empty DN may indicate configuration issue")
        return r[AclProcessingExample.AclValidationResult].ok(
            AclProcessingExample.AclValidationResult(
                entry_dn=dn,
                is_valid=not violations,
                violations=violations,
                warnings=warnings,
                processing_time=time.time() - start_time,
            )
        )

    class AclProcessor(BaseModel):
        """Monadic ACL processor with zero-ceremony execution."""

        auto_execute: bool = True
        entries: Sequence[EntryDict]
        parallel: bool = True

        def execute(self) -> r[ProcessingDict]:
            """Execute ACL processing pipeline using monadic flow."""
            start_time = time.time()
            detect_result = self._detect_servers(self.entries)
            if detect_result.is_failure:
                return r[ProcessingDict].fail(detect_result.error)
            initial_data: ProcessingDict = {
                **detect_result.value,
                "start_time": start_time,
            }
            extract_result = (
                self._extract_acls(initial_data)
                if self.parallel
                else self._extract_sequential(initial_data)
            )
            if extract_result.is_failure:
                return r[ProcessingDict].fail(extract_result.error)
            extracted_data = extract_result.value
            validate_result = self._validate_batch(extracted_data)
            if validate_result.is_failure:
                return r[ProcessingDict].fail(validate_result.error)
            validated_data = validate_result.value
            return self._analyze_performance(validated_data)

        def _analyze_performance(self, data: ProcessingDict) -> r[ProcessingDict]:
            """Analyze processing performance."""
            total_entries = len(self.entries)
            total_acls_data = data.get("total_acls", 0)
            total_acls = total_acls_data if isinstance(total_acls_data, int) else 0
            start_time = data.get("start_time", time.time())
            processing_time = (
                time.time() - start_time if isinstance(start_time, float) else 1.0
            )
            analytics = {
                "throughput_entries_per_second": total_entries / processing_time
                if processing_time > 0
                else 0,
                "throughput_acls_per_second": total_acls / processing_time
                if processing_time > 0
                else 0,
                "efficiency_ratio": total_acls / total_entries
                if total_entries > 0
                else 0,
                "parallel_processing": self.parallel,
            }
            result_data = {
                **data,
                "performance_analytics": analytics,
                "processing_time_seconds": processing_time,
            }
            return r[ProcessingDict].ok(result_data)

        def _detect_servers(self, entries: Sequence[EntryDict]) -> r[ProcessingDict]:
            """Auto-detect server types for all entries."""
            detected_entries: MutableSequence[t.ContainerMapping] = []
            for entry in entries:
                result = AclProcessingExample.detect_server_type(entry)
                if result.is_success:
                    detected_entries.append({
                        "entry": entry,
                        "server_type": result.value,
                    })
                else:
                    return r[ProcessingDict].fail(
                        f"Server detection failed: {result.error}"
                    )
            server_types_set: set[str] = {
                str(item.get("server_type", "")) for item in detected_entries
            }
            return r[ProcessingDict].ok({
                "entries": detected_entries,
                "server_types": sorted(server_types_set),
            })

        def _extract_acls(self, data: ProcessingDict) -> r[ProcessingDict]:
            """Extract ACLs in parallel."""
            entries_data_raw = data.get("entries")
            if not _is_object_list(entries_data_raw):
                return r[ProcessingDict].fail("Invalid entries format")
            entries_with_servers: MutableSequence[tuple[EntryDict, str]] = []
            for entry_with_server_raw in entries_data_raw:
                if not _is_str_object_dict(entry_with_server_raw):
                    continue
                entry_raw = entry_with_server_raw.get("entry")
                server_type_raw = entry_with_server_raw.get("server_type")
                if not _is_entry_dict(entry_raw) or not isinstance(
                    server_type_raw, str
                ):
                    continue
                entries_with_servers.append((entry_raw, server_type_raw))
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [
                    executor.submit(
                        AclProcessingExample.extract_acls_from_entry,
                        entry_with_server[0],
                        entry_with_server[1],
                    )
                    for entry_with_server in entries_with_servers
                ]
                all_acls: MutableSequence[AclProcessingExample.AclEntry] = []
                for future in as_completed(futures):
                    result = future.result()
                    if result.is_success:
                        all_acls.extend(result.value)
                    else:
                        return r[ProcessingDict].fail(
                            f"ACL extraction failed: {result.error}"
                        )
            result_data: ProcessingDict = {
                **data,
                "acls": [
                    {
                        "dn": acl.dn,
                        "acl_attribute": acl.acl_attribute,
                        "permissions": tuple(
                            permission for permission in acl.permissions
                        ),
                        "context": {
                            key: value
                            for key, value in acl.context.items()
                            if isinstance(value, (str, int, float, bool))
                        },
                        "server_type": acl.server_type,
                    }
                    for acl in all_acls
                ],
                "total_acls": len(all_acls),
            }
            return r[ProcessingDict].ok(result_data)

        def _extract_sequential(self, data: ProcessingDict) -> r[ProcessingDict]:
            """Extract ACLs sequentially."""
            entries_data_raw = data.get("entries")
            if not _is_object_list(entries_data_raw):
                return r[ProcessingDict].fail("Invalid entries format")
            entries_with_servers: MutableSequence[tuple[EntryDict, str]] = []
            for entry_with_server_raw in entries_data_raw:
                if not _is_str_object_dict(entry_with_server_raw):
                    continue
                entry_raw = entry_with_server_raw.get("entry")
                server_type_raw = entry_with_server_raw.get("server_type")
                if not _is_entry_dict(entry_raw) or not isinstance(
                    server_type_raw, str
                ):
                    continue
                entries_with_servers.append((entry_raw, server_type_raw))
            all_acls: MutableSequence[AclProcessingExample.AclEntry] = []
            for entry_with_server in entries_with_servers:
                result = AclProcessingExample.extract_acls_from_entry(
                    entry_with_server[0],
                    entry_with_server[1],
                )
                if result.is_success:
                    all_acls.extend(result.value)
                else:
                    return r[ProcessingDict].fail(
                        f"ACL extraction failed: {result.error}"
                    )
            result_data: ProcessingDict = {
                **data,
                "acls": [
                    {
                        "dn": acl.dn,
                        "acl_attribute": acl.acl_attribute,
                        "permissions": tuple(
                            permission for permission in acl.permissions
                        ),
                        "context": {
                            key: value
                            for key, value in acl.context.items()
                            if isinstance(value, (str, int, float, bool))
                        },
                        "server_type": acl.server_type,
                    }
                    for acl in all_acls
                ],
                "total_acls": len(all_acls),
            }
            return r[ProcessingDict].ok(result_data)

        def _validate_batch(self, data: ProcessingDict) -> r[ProcessingDict]:
            """Validate all extracted ACLs."""
            acls_data_raw = data.get("acls")
            if not _is_object_list(acls_data_raw):
                return r[ProcessingDict].fail("Invalid ACLs format")
            validation_results: MutableSequence[
                AclProcessingExample.AclValidationResult
            ] = []
            acl_entries: Sequence[t.ContainerMapping] = [
                acl_item for acl_item in acls_data_raw if isinstance(acl_item, Mapping)
            ]
            for acl in acl_entries:
                result = AclProcessingExample.validate_acl_entry(
                    acl, {"strict_mode": True}
                )
                if result.is_success:
                    validation_results.append(result.value)
                else:
                    return r[ProcessingDict].fail(
                        f"ACL validation failed: {result.error}"
                    )
            result_data: ProcessingDict = {
                **data,
                "validation_results": [
                    {
                        "entry_dn": result.entry_dn,
                        "is_valid": result.is_valid,
                        "violations": tuple(
                            violation for violation in result.violations
                        ),
                        "warnings": tuple(warning for warning in result.warnings),
                        "processing_time": result.processing_time,
                    }
                    for result in validation_results
                ],
                "valid_acls": sum(1 for r in validation_results if r.is_valid),
                "invalid_acls": sum(1 for r in validation_results if not r.is_valid),
                "total_violations": sum(len(r.violations) for r in validation_results),
                "total_warnings": sum(len(r.warnings) for r in validation_results),
            }
            return r[ProcessingDict].ok(result_data)

    @staticmethod
    def create_sample_acl_entries() -> Sequence[EntryDict]:
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
