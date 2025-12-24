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


# Alias for convenience
m = FlextModels
