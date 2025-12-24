"""Models for flext-core package.

This module provides centralized models for the flext-core package.
Uses pydantic 2 advanced features, imports constants, types, protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from flext.constants import c


class FlextModels:
    """Centralized models for flext-core package."""

    # =========================================================================
    # NAMESPACE: .Core - All core domain models
    # =========================================================================

    class Core:
        """Core domain models."""

        class WorkspaceInfo(BaseModel):
            """Workspace information model."""

            name: str = Field(
                default=c.Core.Workspace.NAME, description="Workspace name",
            )
            env_prefix: str = Field(
                default=c.Core.Workspace.ENV_PREFIX, description="Environment prefix",
            )

    class Value(BaseModel):
        """Base class for value objects - immutable and compared by value."""

        model_config = {"frozen": True}

        def __eq__(self, other: object) -> bool:
            """Compare by value."""
            if not isinstance(other, BaseModel):
                return NotImplemented
            return self.model_dump() == other.model_dump()

        def __hash__(self) -> int:
            """Hash based on values for use in sets/dicts."""
            return hash(tuple(sorted(self.model_dump().items())))


# Alias for convenience
m = FlextModels
