"""FLEXT Development Tools Enums - Single Responsibility Module.

Enterprise-grade development operation enumerations using modern Python 3.13
patterns and FLEXT architectural standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from enum import Enum


class FlextDevEnums:
    """FLEXT Development Tools Enums - Unified enumeration container.

    Provides all development operation enumerations in a single unified class
    following FLEXT architectural patterns for single-class-per-module compliance.
    """

    class OperationStatus(str, Enum):
        """Development operation status enumeration."""

        PENDING = "pending"
        RUNNING = "running"
        SUCCESS = "success"
        FAILED = "failed"
        CANCELLED = "cancelled"

    class OperationType(str, Enum):
        """Development operation types."""

        TEST = "test"
        LINT = "lint"
        FORMAT = "format"
        BUILD = "build"
        SECURITY = "security"


# Convenience aliases for test compatibility
OperationStatus = FlextDevEnums.OperationStatus
OperationType = FlextDevEnums.OperationType

__all__ = [
    "FlextDevEnums",
    "OperationStatus",
    "OperationType",
]
