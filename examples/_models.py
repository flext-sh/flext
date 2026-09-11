"""Example models for workspace root namespace.

This module provides shared model definitions used across workspace examples,
establishing the FlextRoot.Root namespace pattern for workspace-level exports.

Scope: Model definitions used in example modules within the workspace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from examples import m, t, u


class ValidationRules(m.BaseModel):
    """Validation rules for ACL processing examples.

    Defines required permissions and forbidden permission combinations
    for validating ACL entries across different server types.
    """

    required_permissions: t.StrSequence = u.Field(
        description="List of permissions that must be present in valid ACL entries"
    )
    forbidden_combinations: t.SequenceOf[t.StrSequence] = u.Field(
        description="Permission combinations that are not allowed together"
    )


__all__: list[str] = ["ValidationRules"]
