"""FLEXT CLI Patterns - Direct Re-exports from flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

ZERO TOLERANCE ENFORCEMENT: This module provides DIRECT re-exports from flext-cli
with NO aliases, NO wrappers, NO compatibility layers.

DIRECT USAGE: Import flext-cli classes directly - NO local aliases.
"""

from __future__ import annotations

# Direct re-exports from flext-cli - NO ALIASES, NO WRAPPERS
from flext_cli import (
    FlextCliApi,
    FlextCliContext,
    FlextCliFormatters,
    FlextCliMain,
)

# Direct exports only - NO ALIASES
__all__ = [
    "FlextCliApi",
    "FlextCliContext",
    "FlextCliFormatters",
    "FlextCliMain",
]
