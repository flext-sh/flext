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
from typing import Annotated, ClassVar

from examples import m, p, r, t, u
from examples._constants import ExamplesPermission, ExamplesServerType


class AclProcessingExample:
    """Advanced ACL processing example demonstrating enterprise-grade ACL capabilities."""

    ServerType = ExamplesServerType
    Permission = ExamplesPermission

    class AclEntry(m.BaseModel):
        """Represents an ACL entry with context and permissions."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True
        )

        dn: str = u.Field(description="Distinguished name of the ACL entry")
        acl_attribute: str = u.Field(description="ACL attribute name")
        permissions: t.StrSequence = u.Field(description="List of permissions")
        context: t.JsonMapping = u.Field(description="Context information")
        server_type: str = u.Field(description="Type of LDAP server")

    class AclValidationResult(m.BaseModel):
        """Result of ACL validation with detailed context."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True
        )

        entry_dn: str = u.Field(description="Distinguished name of the entry")
        valid: bool = u.Field(description="Whether the ACL entry is valid")
        violations: t.StrSequence = u.Field(
            default_factory=tuple, description="List of validation violations"
        )
        warnings: t.StrSequence = u.Field(
            default_factory=tuple, description="List of validation warnings"
        )
        processing_time: Annotated[
            float, u.Field(description="Time taken for validation")
        ] = 0.0

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
        MAX_RECOMMENDED_PERMISSIONS: ClassVar[int] = 10

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
    def detect_server_type(entry: t.JsonMapping) -> p.Result[str]:
        """Auto-detect server type from entry attributes."""
        attributes = entry.get("attributes", {})
        if not isinstance(attributes, Mapping):
            return r[str].fail("Invalid attributes format")
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
        entry: t.JsonMapping, server_type: str
    ) -> p.Result[Sequence[AclProcessingExample.AclEntry]]:
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
                acl_values = attributes.get(attr_name)
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
                            acl_value
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
        return r[Sequence[AclProcessingExample.AclEntry]].ok(extracted_acls)

    @staticmethod
    def validate_acl_entry(
        acl_entry: t.JsonMapping, context: t.JsonMapping
    ) -> p.Result[AclProcessingExample.AclValidationResult]:
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
            missing_perms: set[str] = set(required_permissions) - set(permissions)
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
            context.get("strict_mode")
            and AclProcessingExample.Permission.UNKNOWN.value in permissions
        ):
            violations.append("Unknown permissions not allowed in strict mode")
        if (
            len(permissions)
            > AclProcessingExample.Constants.MAX_RECOMMENDED_PERMISSIONS
        ):
            warnings.append(
                "Excessive permissions - consider principle of least privilege"
            )
        if not dn:
            warnings.append("Empty DN may indicate configuration issue")
        return r[AclProcessingExample.AclValidationResult].ok(
            AclProcessingExample.AclValidationResult(
                entry_dn=dn,
                valid=not violations,
                violations=violations,
                warnings=warnings,
                processing_time=time.time() - start_time,
            )
        )

    class AclProcessor(m.BaseModel):
        """Monadic ACL processor with zero-ceremony execution."""

        class EntryWithServer(m.BaseModel):
            """Typed envelope for extracted entry/server pairs."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(extra="forbid")

            entry: t.JsonMapping
            server_type: str

        auto_execute: bool = True
        entries: t.SequenceOf[t.JsonMapping]
        parallel: bool = True

        def execute(self) -> p.Result[t.JsonMapping]:
            """Execute ACL processing pipeline using monadic flow."""
            start_time = time.time()
            detect_result = self._detect_servers(self.entries)
            if detect_result.failure:
                return r[t.JsonMapping].fail(detect_result.error)
            initial_data: t.JsonMapping = {
                **detect_result.value,
                "start_time": start_time,
            }
            extract_result = self._extract_acls(initial_data)
            if extract_result.failure:
                return r[t.JsonMapping].fail(extract_result.error)
            extracted_data = extract_result.value
            validate_result = self._validate_batch(extracted_data)
            if validate_result.failure:
                return r[t.JsonMapping].fail(validate_result.error)
            validated_data = validate_result.value
            return self._analyze_performance(validated_data)

        def _analyze_performance(self, data: t.JsonMapping) -> p.Result[t.JsonMapping]:
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
            return r[t.JsonMapping].ok(
                t.json_mapping_adapter().validate_python(result_data)
            )

        def _detect_servers(
            self, entries: t.SequenceOf[t.JsonMapping]
        ) -> p.Result[t.JsonMapping]:
            """Auto-detect server types for all entries."""
            detected_entries: MutableSequence[t.JsonMapping] = []
            for entry in entries:
                result = AclProcessingExample.detect_server_type(entry)
                if result.success:
                    detected_entries.append(
                        t.json_mapping_adapter().validate_python({
                            "entry": entry,
                            "server_type": result.value,
                        })
                    )
                else:
                    return r[t.JsonMapping].fail(
                        f"Server detection failed: {result.error}"
                    )
            server_types_set: set[str] = {
                str(item.get("server_type", "")) for item in detected_entries
            }
            return r[t.JsonMapping].ok(
                t.json_mapping_adapter().validate_python({
                    "entries": detected_entries,
                    "server_types": sorted(server_types_set),
                })
            )

        def _extract_acls(self, data: t.JsonMapping) -> p.Result[t.JsonMapping]:
            """Extract ACLs (parallel if ``self.parallel`` else sequential)."""
            entries_data_raw = data.get("entries")
            if not u.list_value(entries_data_raw):
                return r[t.JsonMapping].fail("Invalid entries format")

            try:
                entries_with_servers = tuple(
                    self.EntryWithServer.model_validate(entry_with_server_raw)
                    for entry_with_server_raw in entries_data_raw
                    if isinstance(entry_with_server_raw, Mapping)
                )
            except m.ValidationError as exc:
                return r[t.JsonMapping].fail(f"Invalid entries format: {exc}")

            if not entries_with_servers:
                return r[t.JsonMapping].fail("No valid entries to extract")

            extract = AclProcessingExample.extract_acls_from_entry
            all_acls: MutableSequence[AclProcessingExample.AclEntry] = []
            if self.parallel:
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = [
                        executor.submit(extract, item.entry, item.server_type)
                        for item in entries_with_servers
                    ]
                    extraction_results = [
                        future.result() for future in as_completed(futures)
                    ]
            else:
                extraction_results = [
                    extract(item.entry, item.server_type)
                    for item in entries_with_servers
                ]

            for result in extraction_results:
                if result.failure:
                    return r[t.JsonMapping].fail(
                        f"ACL extraction failed: {result.error}"
                    )
                all_acls.extend(result.value)

            result_data = {
                **data,
                "acls": [
                    t.json_mapping_adapter().validate_python({
                        "dn": acl.dn,
                        "acl_attribute": acl.acl_attribute,
                        "permissions": list(acl.permissions),
                        "context": {
                            key: value
                            for key, value in acl.context.items()
                            if isinstance(value, t.PRIMITIVES_TYPES)
                        },
                        "server_type": acl.server_type,
                    })
                    for acl in all_acls
                ],
                "total_acls": len(all_acls),
            }
            return r[t.JsonMapping].ok(
                t.json_mapping_adapter().validate_python(result_data)
            )

        def _validate_batch(self, data: t.JsonMapping) -> p.Result[t.JsonMapping]:
            """Validate all extracted ACLs."""
            acls_data_raw = data.get("acls")
            if not u.list_value(acls_data_raw):
                return r[t.JsonMapping].fail("Invalid ACLs format")
            validation_results: MutableSequence[
                AclProcessingExample.AclValidationResult
            ] = []
            acl_entries: t.SequenceOf[t.JsonMapping] = [
                acl_item for acl_item in acls_data_raw if isinstance(acl_item, Mapping)
            ]
            for acl in acl_entries:
                result = AclProcessingExample.validate_acl_entry(
                    acl, t.json_mapping_adapter().validate_python({"strict_mode": True})
                )
                if result.success:
                    validation_results.append(result.value)
                else:
                    return r[t.JsonMapping].fail(
                        f"ACL validation failed: {result.error}"
                    )
            result_data = {
                **data,
                "validation_results": [
                    t.json_mapping_adapter().validate_python({
                        "entry_dn": result.entry_dn,
                        "valid": result.valid,
                        "violations": list(result.violations),
                        "warnings": list(result.warnings),
                        "processing_time": result.processing_time,
                    })
                    for result in validation_results
                ],
                "valid_acls": sum(1 for r in validation_results if r.valid),
                "invalid_acls": sum(1 for r in validation_results if not r.valid),
                "total_violations": sum(len(r.violations) for r in validation_results),
                "total_warnings": sum(len(r.warnings) for r in validation_results),
            }
            return r[t.JsonMapping].ok(
                t.json_mapping_adapter().validate_python(result_data)
            )

    @staticmethod
    def create_sample_acl_entries() -> t.SequenceOf[t.JsonMapping]:
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
                "dn": "cn=settings",
                "attributes": {
                    "orclACI": 'orclACI: access to attr=(userPassword) by dn="cn=Directory Manager" (read,write)'
                },
            },
        ]
