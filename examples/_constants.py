"""Shared constants for FLEXT runnable examples.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum, unique
from types import MappingProxyType
from typing import ClassVar
from collections.abc import Mapping


class FlextRootExamplesConstants:
    """Examples constants facade — access via FlextRootExamplesConstants.*."""

    @unique
    class Permission(StrEnum):
        """Permission enumeration used across ACL examples."""

        READ = "read"
        WRITE = "write"
        DELETE = "delete"
        SEARCH = "search"
        UNKNOWN = "unknown"

    @unique
    class ServerType(StrEnum):
        """Server type enumeration used across directory-service examples."""

        OPENLDAP = "openldap"
        ORACLE_OID = "oracle_oid"
        ORACLE_UNIFIED_DIRECTORY = "oracle_unified_directory"
        ACTIVE_DIRECTORY = "active_directory"
        APACHE_DS = "apache_ds"
        UNKNOWN = "unknown"

    SERVER_SIGNATURES: ClassVar[Mapping[ServerType, tuple[str, ...]]] = MappingProxyType({
        ServerType.OPENLDAP: ("olcAccess", "olcACL"),
        ServerType.ORACLE_OID: ("orclACI", "orclACL"),
        ServerType.ORACLE_UNIFIED_DIRECTORY: ("ds-cfg-global-aci", "aci"),
        ServerType.ACTIVE_DIRECTORY: ("ntSecurityDescriptor",),
        ServerType.APACHE_DS: ("accessControlSubentry",),
    })
    SERVER_ACL_ATTRIBUTES: ClassVar[Mapping[ServerType, tuple[str, ...]]] = MappingProxyType({
        ServerType.OPENLDAP: ("olcAccess", "olcACL"),
        ServerType.ORACLE_OID: ("orclACI", "orclACL"),
        ServerType.ORACLE_UNIFIED_DIRECTORY: ("aci", "ds-cfg-global-aci"),
        ServerType.ACTIVE_DIRECTORY: ("ntSecurityDescriptor",),
        ServerType.APACHE_DS: ("accessControlSubentry",),
    })
    REQUIRED_PERMISSIONS: ClassVar[Mapping[ServerType, tuple[Permission, ...]]] = MappingProxyType({
        ServerType.OPENLDAP: (Permission.READ, Permission.WRITE, Permission.SEARCH),
        ServerType.ORACLE_OID: (Permission.SEARCH, Permission.READ),
    })
    FORBIDDEN_COMBINATIONS: ClassVar[Mapping[ServerType, tuple[tuple[Permission, ...], ...]]] = MappingProxyType({
        ServerType.OPENLDAP: ((Permission.READ, Permission.DELETE),),
        ServerType.ORACLE_OID: ((Permission.WRITE, Permission.DELETE),),
    })
    MAX_RECOMMENDED_PERMISSIONS: ClassVar[int] = 10

    @unique
    class Stage(StrEnum):
        """Processing stage enumeration used across pipeline examples."""

        VALIDATE = "validate"
        PROCESS = "process"
        ANALYZE = "analyze"

    @unique
    class WorkflowStage(StrEnum):
        """Processing stage enumeration used across complete-workflow examples."""

        VALIDATION = "validation"
        PROCESSING = "processing"
        ANALYSIS = "analysis"
        AGGREGATION = "aggregation"


__all__: list[str] = ["FlextRootExamplesConstants"]
