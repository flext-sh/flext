"""FLEXT Project Types - Single Responsibility Module.

Project type enumerations consolidated into flext-core for ecosystem consistency.
This module now provides compatibility imports from the centralized FlextTypes.Project.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import centralized types from flext-core foundation
from flext_core import FlextTypes, WorkspaceStatus


class FlextProjectTypes:
    """Unified project types service using flext-core foundation."""

    # Use centralized enums from FlextTypes.Project
    ProjectType = FlextTypes.Project.ProjectType


# Convenience aliases for test compatibility
ProjectType = FlextProjectTypes.ProjectType

__all__ = [
    "FlextProjectTypes",
    "ProjectType",
    "WorkspaceStatus",
]
