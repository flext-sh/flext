"""FLEXT Project Types - Single Responsibility Module.

Project type enumerations consolidated into flext-core for ecosystem consistency.
This module now provides compatibility imports from the centralized FlextTypes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Literal

# Import centralized types from flext-core foundation

# Import WorkspaceStatus from the correct location
WorkspaceStatus = Literal["ACTIVE", "INACTIVE", "ARCHIVED", "MAINTENANCE"]


class FlextProjectTypes:
    """Unified project types service using flext-core foundation."""

    # Use centralized enums from FlextTypes
    ProjectType = Literal["PYTHON", "GO", "RUST", "NODEJS", "JAVA", "DOTNET", "UNKNOWN"]


# Convenience aliases for test compatibility
ProjectType = FlextProjectTypes.ProjectType

__all__ = [
    "FlextProjectTypes",
    "ProjectType",
    "WorkspaceStatus",
]
