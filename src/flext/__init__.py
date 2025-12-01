"""Flext workspace package - Direct API access without wrappers.

This module provides direct access to FlextCli and FlextCore services
without unnecessary wrappers. Use FlextCli and FlextCore APIs directly.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Direct exports - use FlextCli and FlextCore APIs directly
from flext_cli import FlextCli
from flext_core import FlextResult, FlextService

__all__ = [
    "FlextCli",
    "FlextResult",
    "FlextService",
]
