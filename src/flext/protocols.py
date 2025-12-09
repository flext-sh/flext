"""Protocol definitions for flext-core package.

This module provides centralized protocol definitions for the flext-core package.
Uses constants and types, defines protocols with protocol types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol


class FlextProtocols:
    """Centralized protocol definitions for flext-core package."""

    # =========================================================================
    # NAMESPACE: .Core - All core domain protocols
    # =========================================================================

    class Core:
        """Core domain protocols."""

        class ResultProtocol(Protocol):
            """Protocol for result types."""

            # Define protocol methods here


# Alias for convenience
p = FlextProtocols
