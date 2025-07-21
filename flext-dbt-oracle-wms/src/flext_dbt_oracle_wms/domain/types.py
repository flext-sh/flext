"""FLEXT DBT Oracle WMS Domain Types - Unified typing system using flext-core.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

This module imports from the unified typing system in flext-core and defines
DBT Oracle WMS-specific types using modern Python 3.13 patterns, StrEnum, and
Pydantic v2.

IMPORTANT: This module is for Oracle WMS API integration, NOT Oracle Database.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TypedDict

# Import ALL types from unified core typing system - eliminate duplication
from flext_core.domain.shared_types import (
    CreatedAt,
    EntityId,
    ProjectName,
    TimeoutSeconds,
    UpdatedAt,
    Version,
)

# ==============================================================================
# DBT ORACLE WMS TYPE ALIASES USING CORE TYPES
# ==============================================================================

# Oracle WMS specific IDs using core types
type OracleWMSOperationId = EntityId
type OracleWMSConnectionId = EntityId
type OracleWMSSchemaId = EntityId
type OracleWMSQueryId = EntityId

# DBT specific timeout type aliases using core timeout types
type DBTOracleWMSProjectTimeout = TimeoutSeconds
type DBTOracleWMSModelTimeout = TimeoutSeconds
type DBTOracleWMSSourceTimeout = TimeoutSeconds
type DBTOracleWMSTestTimeout = TimeoutSeconds
type DBTOracleWMSMacroTimeout = TimeoutSeconds
type DBTOracleWMSSnapshotTimeout = TimeoutSeconds
type DBTOracleWMSAnalysisTimeout = TimeoutSeconds
type DBTOracleWMSCompilationTimeout = TimeoutSeconds
type DBTOracleWMSExecutionTimeout = TimeoutSeconds
type DBTOracleWMSDocumentationTimeout = TimeoutSeconds

# ==============================================================================
# DBT ORACLE WMS ENUMS
# ==============================================================================


class DBTOracleWMSMaterialization(StrEnum):
    """DBT Oracle WMS materialization types."""

    TABLE = "table"
    VIEW = "view"
    INCREMENTAL = "incremental"
    EPHEMERAL = "ephemeral"
    SNAPSHOT = "snapshot"


class DBTOracleWMSTestType(StrEnum):
    """DBT Oracle WMS test types."""

    UNIQUE = "unique"
    NOT_NULL = "not_null"
    ACCEPTED_VALUES = "accepted_values"
    RELATIONSHIPS = "relationships"
    CUSTOM = "custom"


class DBTOracleWMSRunStatus(StrEnum):
    """DBT Oracle WMS run status using StrEnum."""

    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"
    RUNNING = "running"
    QUEUED = "queued"


# ==============================================================================
# DBT ORACLE WMS TYPED DICTIONARIES
# ==============================================================================


class DBTOracleWMSProjectConfiguration(TypedDict):
    """DBT Oracle WMS project configuration using core types."""

    name: ProjectName
    version: Version
    profile: str
    model_paths: list[str]
    analysis_paths: list[str]
    test_paths: list[str]
    seed_paths: list[str]
    macro_paths: list[str]
    snapshot_paths: list[str]
    target_path: str
    clean_targets: list[str]
    require_dbt_version: str
    dbt_version: str
    timeout: DBTOracleWMSProjectTimeout


class DBTOracleWMSModelConfiguration(TypedDict):
    """DBT Oracle WMS model configuration."""

    name: str
    materialized: DBTOracleWMSMaterialization
    schema: str
    alias: str | None
    tags: list[str]
    meta: dict[str, str]
    docs: dict[str, str]
    config: dict[str, str]
    timeout: DBTOracleWMSModelTimeout


class DBTOracleWMSSourceConfiguration(TypedDict):
    """DBT Oracle WMS source configuration."""

    name: str
    description: str
    tables: list[dict[str, str]]
    database: str
    schema: str
    loader: str
    meta: dict[str, str]
    tags: list[str]
    config: dict[str, str]
    timeout: DBTOracleWMSSourceTimeout


class DBTOracleWMSTestConfiguration(TypedDict):
    """DBT Oracle WMS test configuration."""

    name: str
    test_type: DBTOracleWMSTestType
    model: str
    column: str | None
    values: list[str] | None
    to: str | None
    field: str | None
    severity: str
    meta: dict[str, str]
    tags: list[str]
    timeout: DBTOracleWMSTestTimeout


class DBTOracleWMSMacroConfiguration(TypedDict):
    """DBT Oracle WMS macro configuration."""

    name: str
    description: str
    arguments: list[dict[str, str]]
    meta: dict[str, str]
    tags: list[str]
    timeout: DBTOracleWMSMacroTimeout


class DBTOracleWMSSnapshotConfiguration(TypedDict):
    """DBT Oracle WMS snapshot configuration."""

    name: str
    target_schema: str
    target_database: str | None
    strategy: str
    unique_key: str
    updated_at: str | None
    check_cols: list[str] | None
    invalidate_hard_deletes: bool
    meta: dict[str, str]
    tags: list[str]
    timeout: DBTOracleWMSSnapshotTimeout


class DBTOracleWMSAnalysisConfiguration(TypedDict):
    """DBT Oracle WMS analysis configuration."""

    name: str
    description: str
    meta: dict[str, str]
    tags: list[str]
    timeout: DBTOracleWMSAnalysisTimeout


class DBTOracleWMSCompilationConfiguration(TypedDict):
    """DBT Oracle WMS compilation configuration."""

    project_dir: str
    profiles_dir: str
    target: str
    vars: dict[str, str]
    full_refresh: bool
    exclude: list[str] | None
    select: list[str] | None
    timeout: DBTOracleWMSCompilationTimeout


class DBTOracleWMSExecutionConfiguration(TypedDict):
    """DBT Oracle WMS execution configuration."""

    project_dir: str
    profiles_dir: str
    target: str
    models: list[str] | None
    exclude: list[str] | None
    full_refresh: bool
    fail_fast: bool
    threads: int
    vars: dict[str, str]
    timeout: DBTOracleWMSExecutionTimeout


class DBTOracleWMSDocumentationConfiguration(TypedDict):
    """DBT Oracle WMS documentation configuration."""

    project_dir: str
    profiles_dir: str
    target: str
    compile: bool
    timeout: DBTOracleWMSDocumentationTimeout


# ==============================================================================
# DBT ORACLE WMS DOMAIN OBJECTS
# ==============================================================================


class DBTOracleWMSProject(TypedDict):
    """DBT Oracle WMS project domain object using core types."""

    id: EntityId
    name: ProjectName
    version: Version
    configuration: DBTOracleWMSProjectConfiguration
    created_at: CreatedAt
    updated_at: UpdatedAt


class DBTOracleWMSModel(TypedDict):
    """DBT Oracle WMS model domain object using core types."""

    id: EntityId
    project_id: EntityId
    name: str
    configuration: DBTOracleWMSModelConfiguration
    sql_content: str
    created_at: CreatedAt
    updated_at: UpdatedAt


class DBTOracleWMSSource(TypedDict):
    """DBT Oracle WMS source domain object using core types."""

    id: EntityId
    project_id: EntityId
    name: str
    configuration: DBTOracleWMSSourceConfiguration
    created_at: CreatedAt
    updated_at: UpdatedAt


class DBTOracleWMSTest(TypedDict):
    """DBT Oracle WMS test domain object using core types."""

    id: EntityId
    project_id: EntityId
    model_id: EntityId | None
    name: str
    configuration: DBTOracleWMSTestConfiguration
    sql_content: str | None
    created_at: CreatedAt
    updated_at: UpdatedAt


class DBTOracleWMSMacro(TypedDict):
    """DBT Oracle WMS macro domain object using core types."""

    id: EntityId
    project_id: EntityId
    name: str
    configuration: DBTOracleWMSMacroConfiguration
    sql_content: str
    created_at: CreatedAt
    updated_at: UpdatedAt


class DBTOracleWMSSnapshot(TypedDict):
    """DBT Oracle WMS snapshot domain object using core types."""

    id: EntityId
    project_id: EntityId
    name: str
    configuration: DBTOracleWMSSnapshotConfiguration
    sql_content: str
    created_at: CreatedAt
    updated_at: UpdatedAt


class DBTOracleWMSAnalysis(TypedDict):
    """DBT Oracle WMS analysis domain object using core types."""

    id: EntityId
    project_id: EntityId
    name: str
    configuration: DBTOracleWMSAnalysisConfiguration
    sql_content: str
    created_at: CreatedAt
    updated_at: UpdatedAt


class DBTOracleWMSCompilation(TypedDict):
    """DBT Oracle WMS compilation domain object using core types."""

    id: EntityId
    project_id: EntityId
    configuration: DBTOracleWMSCompilationConfiguration
    status: DBTOracleWMSRunStatus
    output: str | None
    error: str | None
    created_at: CreatedAt
    completed_at: UpdatedAt | None


class DBTOracleWMSExecution(TypedDict):
    """DBT Oracle WMS execution domain object using core types."""

    id: EntityId
    project_id: EntityId
    configuration: DBTOracleWMSExecutionConfiguration
    status: DBTOracleWMSRunStatus
    output: str | None
    error: str | None
    created_at: CreatedAt
    completed_at: UpdatedAt | None


class DBTOracleWMSDocumentation(TypedDict):
    """DBT Oracle WMS documentation domain object using core types."""

    id: EntityId
    project_id: EntityId
    configuration: DBTOracleWMSDocumentationConfiguration
    status: DBTOracleWMSRunStatus
    output_path: str | None
    error: str | None
    created_at: CreatedAt
    completed_at: UpdatedAt | None


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "DBTOracleWMSAnalysis",
    "DBTOracleWMSAnalysisConfiguration",
    "DBTOracleWMSAnalysisTimeout",
    "DBTOracleWMSCompilation",
    "DBTOracleWMSCompilationConfiguration",
    "DBTOracleWMSCompilationTimeout",
    "DBTOracleWMSDocumentation",
    "DBTOracleWMSDocumentationConfiguration",
    "DBTOracleWMSDocumentationTimeout",
    "DBTOracleWMSExecution",
    "DBTOracleWMSExecutionConfiguration",
    "DBTOracleWMSExecutionTimeout",
    "DBTOracleWMSMacro",
    "DBTOracleWMSMacroConfiguration",
    "DBTOracleWMSMacroTimeout",
    "DBTOracleWMSMaterialization",
    "DBTOracleWMSModel",
    "DBTOracleWMSModelConfiguration",
    "DBTOracleWMSModelTimeout",
    "DBTOracleWMSProject",
    "DBTOracleWMSProjectConfiguration",
    "DBTOracleWMSProjectTimeout",
    "DBTOracleWMSRunStatus",
    "DBTOracleWMSSnapshot",
    "DBTOracleWMSSnapshotConfiguration",
    "DBTOracleWMSSnapshotTimeout",
    "DBTOracleWMSSource",
    "DBTOracleWMSSourceConfiguration",
    "DBTOracleWMSSourceTimeout",
    "DBTOracleWMSTest",
    "DBTOracleWMSTestConfiguration",
    "DBTOracleWMSTestTimeout",
    "DBTOracleWMSTestType",
    "OracleWMSConnectionId",
    "OracleWMSOperationId",
    "OracleWMSQueryId",
    "OracleWMSSchemaId",
]
