"""Shared constants for FLEXT runnable examples.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum, unique


class FlextRootExamplesConstants:
    """Examples constants facade — access via FlextRootExamplesConstants.*."""

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
