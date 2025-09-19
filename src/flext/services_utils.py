"""FLEXT Service Utilities - Facade for flext-core Utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

ANTI-DUPLICATION ENFORCEMENT: This module provides ONLY a facade to flext-core
utility patterns, eliminating ALL code duplication and ensuring consistent
utility usage across the FLEXT ecosystem.

ZERO TOLERANCE: NO local implementations - delegates exclusively to flext-core.
DOMAIN SEPARATION: Domain-specific functionality (LDIF, Oracle, etc.) belongs
in dedicated ecosystem projects (flext-ldif, flext-db-oracle, etc.).
"""

from __future__ import annotations

# Use flext-core utilities exclusively - NO LOCAL IMPLEMENTATIONS
from flext_core import (
    FlextLogger,
    FlextResult,
    FlextUtilities,
)

# Export flext-core utility patterns exclusively
__all__ = [
    "FlextLogger",
    "FlextResult",
    # Core utility patterns
    "FlextUtilities",
]
