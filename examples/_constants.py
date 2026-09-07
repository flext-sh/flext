"""Shared constants for FLEXT runnable examples.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum, unique


@unique
class ExamplesServerType(StrEnum):
    """Server type enumeration used across directory-service examples."""

    OPENLDAP = "openldap"
    ORACLE_OID = "oracle_oid"
    ORACLE_UNIFIED_DIRECTORY = "oracle_unified_directory"
    ACTIVE_DIRECTORY = "active_directory"
    APACHE_DS = "apache_ds"
    UNKNOWN = "unknown"


@unique
class ExamplesPermission(StrEnum):
    """Permission enumeration used across ACL examples."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SEARCH = "search"
    UNKNOWN = "unknown"


@unique
class ExamplesStage(StrEnum):
    """Processing stage enumeration used across pipeline examples."""

    VALIDATE = "validate"
    PROCESS = "process"
    ANALYZE = "analyze"


@unique
class ExamplesWorkflowStage(StrEnum):
    """Processing stage enumeration used across complete-workflow examples."""

    VALIDATION = "validation"
    PROCESSING = "processing"
    ANALYSIS = "analysis"
    AGGREGATION = "aggregation"


__all__: list[str] = [
    "ExamplesPermission",
    "ExamplesServerType",
    "ExamplesStage",
    "ExamplesWorkflowStage",
]
