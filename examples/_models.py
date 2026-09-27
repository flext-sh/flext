"""Example models for workspace root namespace.

This module provides shared model definitions used across workspace examples,
establishing the FlextRoot.Root namespace pattern for workspace-level exports.

Scope: Model definitions used in example modules within the workspace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar

from examples import m, u
from examples._constants import FlextRootExamplesConstants as c


class ValidationRules(m.BaseModel):
    """Validation rules for ACL processing examples.

    Defines required permissions and forbidden permission combinations
    for validating ACL entries across different server types.
    """

    required_permissions: tuple[c.Permission, ...] = u.Field(
        description="List of permissions that must be present in valid ACL entries"
    )
    forbidden_combinations: tuple[tuple[c.Permission, ...], ...] = u.Field(
        description="Permission combinations that are not allowed together"
    )


class AclSource(m.BaseModel):
        """Validated LDAP entry at the example's input boundary."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(extra="forbid")

        dn: str
        attributes: Mapping[str, str | tuple[str, ...]]

class AclContext(m.BaseModel):
        """Extraction metadata for one ACL."""

        index: int
        raw_value: str
        server_type: c.ServerType
        extraction_time: float

class AclEntry(m.BaseModel):
        """One extracted ACL with its source and permissions."""

        dn: str
        acl_attribute: str
        permissions: tuple[c.Permission, ...]
        context: AclContext
        server_type: c.ServerType

class AclValidation(m.BaseModel):
        """Observable result of validating one ACL."""

        entry_dn: str
        valid: bool
        violations: tuple[str, ...]
        warnings: tuple[str, ...]
        processing_time: float

class AclRun(m.BaseModel):
        """Observable output of the ACL example."""

        acls: tuple[AclEntry, ...]
        validation_results: tuple[AclValidation, ...]
        server_types: tuple[c.ServerType, ...]
        total_acls: int
        valid_acls: int
        invalid_acls: int
        total_violations: int
        total_warnings: int
        processing_time_seconds: float
        throughput_entries_per_second: float
        throughput_acls_per_second: float
        efficiency_ratio: float


class FlextRootExamplesModels:
    """Examples models facade — access via FlextRootExamplesModels.*."""

    AclSource = AclSource
    AclContext = AclContext
    AclEntry = AclEntry
    AclValidation = AclValidation
    AclRun = AclRun
    ValidationRules = ValidationRules


__all__: list[str] = ["FlextRootExamplesModels", "ValidationRules"]
