"""FLEXT DBT Oracle WMS Configuration Types - Simplified version.

This module provides configuration type definitions for the FLEXT DBT Oracle WMS
integration using basic types.

IMPORTANT: This module is for Oracle WMS API integration, NOT Oracle Database.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field


# Simple DBT Oracle WMS Configuration
class FlextDBTOracleWMSConfig(BaseModel):
    """FLEXT DBT Oracle WMS configuration."""

    project_name: str = Field(default="flext-dbt-oracle-wms")
    version: str = Field(default="2.0.0")
    profile: str = Field(default="flext_oracle_wms")

    # DBT configurations
    model_paths: list[str] = Field(default_factory=lambda: ["models"])
    analysis_paths: list[str] = Field(default_factory=lambda: ["analyses"])
    test_paths: list[str] = Field(default_factory=lambda: ["tests"])
    seed_paths: list[str] = Field(default_factory=lambda: ["seeds"])
    macro_paths: list[str] = Field(default_factory=lambda: ["macros"])

    # Oracle WMS specific
    oracle_wms_schema: str = Field(default="wms_raw")
    wms_entities: list[str] = Field(default_factory=lambda: [
        "allocation", "order_hdr", "order_dtl", "inventory",
    ])

    # Performance settings
    enable_incremental_models: bool = Field(default=True)
    incremental_lookback_days: int = Field(default=7)

    # Data quality
    enable_audit_logging: bool = Field(default=True)
    enable_lineage_tracking: bool = Field(default=True)


# Basic configuration TypedDicts
class DBTOracleWMSConfiguration(TypedDict):
    """Basic DBT Oracle WMS configuration."""

    project_name: str
    version: str
    profile: str


class DBTOracleWMSModelConfiguration(TypedDict):
    """DBT model configuration."""

    materialized: Literal["table", "view", "incremental"]
    schema: str
    tags: list[str]


class DBTOracleWMSSourceConfiguration(TypedDict):
    """DBT source configuration."""

    name: str
    schema: str
    tables: list[dict[str, Any]]


class DBTOracleWMSTestConfiguration(TypedDict):
    """DBT test configuration."""

    store_failures: bool
    schema: str


class DBTOracleWMSMacroConfiguration(TypedDict):
    """DBT macro configuration."""

    name: str
    description: str
    arguments: list[str]


class DBTOracleWMSProfileConfiguration(TypedDict):
    """DBT profile configuration."""

    target: str
    outputs: dict[str, Any]
