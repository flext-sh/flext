"""FLEXT CLI Direct Re-exports - ZERO TOLERANCE Anti-Duplication.

This module provides DIRECT re-exports from flext-cli with ZERO TOLERANCE
for local implementations, aliases, or wrappers.

CRITICAL ENFORCEMENT:
- NO local CLI implementations
- NO ALIASES
- NO WRAPPERS
- NO compatibility layers
- Direct re-exports ONLY

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Direct re-exports from flext-cli - NO ALIASES, NO WRAPPERS
from flext_cli import (
    FlextCliApi,
    FlextCliConfigs,
    FlextCliFormatters,
    FlextCliMain,
    FlextCliModels,
    FlextCliService,
)

__all__ = [
    "FlextCliApi",
    "FlextCliConfigs",
    "FlextCliFormatters",
    "FlextCliMain",
    "FlextCliModels",
    "FlextCliService",
]
