"""Shared constants for FLEXT runnable examples.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import StrEnum, unique


class FlextRootExamplesConstants:
    """Examples constants facade — access via FlextRootExamplesConstants.*."""

    EXPECTED_OID_ACL_COUNT: int = 2

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

    @unique
    class ErrorMessages(StrEnum):
        """Runtime error message constants for example execution."""

        LDIF_NO_ENTRIES = "LDIF parser produced no entries"
        ACL_PERMISSION_NOT_GRANTED = (
            "LDIF ACL example did not grant the declared permission"
        )
        OID_INSUFFICIENT_ATTRIBUTES = (
            "OID server declared fewer than two ACL attributes"
        )
        OID_ACL_ATTRIBUTE_LOST = "OID ACL example lost a declared attribute"
        ADVANCED_NO_ANALYSIS = "advanced example produced no analysis"
        COMPLETE_NO_CONTENT = "complete workflow produced no content"


__all__: list[str] = ["FlextRootExamplesConstants"]
