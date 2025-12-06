"""Protocol definitions for flext package.

This module provides centralized protocol definitions for the flext package,
inheriting from FlextCliProtocols and extending with workspace-specific protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCliProtocols


class FlextProtocols(FlextCliProtocols):
    """Centralized protocol definitions for flext package."""

    # Add workspace-specific protocols here if needed


# Alias for convenience
p = FlextProtocols
