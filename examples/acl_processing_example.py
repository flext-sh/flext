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
from typing import Annotated, ClassVar, cast

from examples import ExamplesPermission, ExamplesServerType, m, p, t, u
from flext_core import r


class _Constants:
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


class _AclPermissionParser:
    """Helper to parse ACL permissions."""

    @staticmethod
    def parse(
        acl_value: str, permission_enum: type[ExamplesPermission]
    ) -> MutableSequence[str]:
        """Parse ACL permissions from raw ACL value."""
        acl_lower = acl_value.lower()
        permissions = [
            perm.value
            for perm in permission_enum.__members__.values()
            if perm != permission_enum.UNKNOWN and perm.value in acl_lower
        ]
        return permissions or [permission_enum.UNKNOWN.value]


class _ServerDetector:
    """Helper to detect server type."""

    @staticmethod
    def detect(entry: t.JsonMapping) -> p.Result[str]:
        """Auto-detect server type from entry attributes."""
        attributes = entry.get("attributes", {})
        if not isinstance(attributes, Mapping):
            return r[str].fail("Invalid attributes format")
        attr_keys: set[str] = set(attributes.keys())
        for server_type, signatures in _Constants.SERVER_SIGNATURES.items():
            if any(sig in attr_keys for sig in signatures):
                return r[str].ok(server_type)
        return r[str].fail("Unable to detect server type from entry attributes")


class _AclExtractor:
    """Helper to extract ACLs from entries."""

    @staticmethod
    def extract(
        entry: t.JsonMapping,
        server_type: str,
        permission_enum: type[ExamplesPermission],
    ) -> p.Result[t.SequenceOf[t.JsonMapping]]:
        """Extract ACLs using server-specific attribute detection."""
        start_time = time.time()
        acl_attrs = _Constants.SERVER_ACL_ATTRIBUTES.get(server_type, [])
        if not acl_attrs:
            return r[t.SequenceOf[t.JsonMapping]].fail(
                f"No ACL attributes defined for server type: {server_type}"
            )
        extracted_acls: list[t.JsonMapping] = []
        attributes = entry.get("attributes", {})
        if not isinstance(attributes, Mapping):
            return r[t.SequenceOf[t.JsonMapping]].fail("Invalid attributes format")
        for attr_name in acl_attrs:
            if attr_name in attributes:
                acl_values = attributes.get(attr_name)
                values_list: Sequence[str]
                if isinstance(acl_values, str):
                    values_list = [acl_values]
                elif isinstance(acl_values, Sequence) and not isinstance(
                    acl_values, (str, bytes, bytearray)
                ):
                    values_list = [str(value) for value in acl_values]
                else:
                    continue
                for i, acl_value in enumerate(values_list):
                    acl_entry = {
                        "dn": str(entry.get("dn", "")),
                        "acl_attribute": attr_name,
                        "permissions": _AclPermissionParser.parse(
                            acl_value, permission_enum
                        ),
                        "context": {
                            "index": i,
                            "raw_value": acl_value,
                            "server_type": server_type,
                            "extraction_time": time.time() - start_time,
                        },
                        "server_type": server_type,
                    }
                    extracted_acls.append(cast("t.JsonMapping", acl_entry))
        return r[t.SequenceOf[t.JsonMapping]].ok(extracted_acls)


class _AclValidator:
    """Helper to validate ACL entries."""

    @staticmethod
    def validate(
        acl_entry: t.JsonMapping,
        context: t.JsonMapping,
        permission_enum: type[ExamplesPermission],
    ) -> p.Result[t.JsonMapping]:
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
        if context.get("strict_mode") and permission_enum.UNKNOWN.value in permissions:
            violations.append("Unknown permissions not allowed in strict mode")
        if len(permissions) > _Constants.MAX_RECOMMENDED_PERMISSIONS:
            warnings.append(
                "Excessive permissions - consider principle of least privilege"
            )
        if not dn:
            warnings.append("Empty DN may indicate configuration issue")
        return r[t.JsonMapping].ok({
            "entry_dn": dn,
            "valid": not violations,
            "violations": list(violations),
            "warnings": list(warnings),
            "processing_time": time.time() - start_time,
        })


class FlextRootAclProcessingExample:
    """Advanced ACL processing example demonstrating enterprise-grade ACL capabilities."""

    ServerType = ExamplesServerType
    Permission = ExamplesPermission

    def __init__(self, *, max_workers: int = 8) -> None:
        """Initialize the ACL processing pipeline."""
        self._max_workers = max_workers

    def process_acls_with_pipeline(
        self,
        *,
        raw_entries: t.SequenceOf[t.JsonMapping],
        server_context: t.JsonMapping,
        parallel: bool = True,
    ) -> p.Result[t.JsonMapping]:
        """Process ACL entries through the pipeline."""
        return self.AclProcessor(entries=raw_entries, parallel=parallel).execute()

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
                result = _ServerDetector.detect(entry)
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
                return r[t.JsonMapping].fail(
                    f"Invalid entries format: {exc}", exception=exc
                )

            if not entries_with_servers:
                return r[t.JsonMapping].fail("No valid entries to extract")

            extract = _AclExtractor.extract
            all_acls: t.MutableSequenceOf[t.JsonMapping] = []
            if self.parallel:
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = [
                        executor.submit(
                            extract, item.entry, item.server_type, ExamplesPermission
                        )
                        for item in entries_with_servers
                    ]
                    extraction_results = [
                        future.result() for future in as_completed(futures)
                    ]
            else:
                extraction_results = [
                    extract(item.entry, item.server_type, ExamplesPermission)
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
                        "dn": cast("str", acl["dn"]),
                        "acl_attribute": cast("str", acl["acl_attribute"]),
                        "permissions": list(cast("list", acl["permissions"])),
                        "context": {
                            key: value
                            for key, value in cast(
                                "t.JsonMapping", acl["context"]
                            ).items()
                            if isinstance(value, t.PRIMITIVES_TYPES)
                        },
                        "server_type": cast("str", acl["server_type"]),
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
            validation_results: t.MutableSequenceOf[t.JsonMapping] = []
            acl_entries: t.SequenceOf[t.JsonMapping] = [
                acl_item for acl_item in acls_data_raw if isinstance(acl_item, Mapping)
            ]
            for acl in acl_entries:
                result = _AclValidator.validate(
                    acl,
                    t.json_mapping_adapter().validate_python({"strict_mode": True}),
                    ExamplesPermission,
                )
                if result.success:
                    validation_results.append(result.value)
                else:
                    return r[t.JsonMapping].fail(
                        f"ACL validation failed: {result.error}"
                    )
            validated_results = [
                t.json_mapping_adapter().validate_python(result)
                for result in validation_results
            ]
            result_data = {
                **data,
                "validation_results": [
                    t.json_mapping_adapter().validate_python({
                        "entry_dn": cast("str", r["entry_dn"]),
                        "valid": cast("bool", r["valid"]),
                        "violations": list(cast("list", r["violations"])),
                        "warnings": list(cast("list", r["warnings"])),
                        "processing_time": cast("float", r["processing_time"]),
                    })
                    for r in validated_results
                ],
                "valid_acls": sum(
                    1 for r in validated_results if cast("bool", r["valid"])
                ),
                "invalid_acls": sum(
                    1 for r in validated_results if not cast("bool", r["valid"])
                ),
                "total_violations": sum(
                    len(cast("list", r["violations"])) for r in validated_results
                ),
                "total_warnings": sum(
                    len(cast("list", r["warnings"])) for r in validated_results
                ),
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
