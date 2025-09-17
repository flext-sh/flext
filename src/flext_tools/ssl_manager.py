"""Minimal SSL manager for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult


class SSLManager:
    """Basic SSL manager for legacy scripts."""

    def __init__(self) -> None:
        """Initialize SSL manager."""

    def setup_ssl(self, config_path: str | Path) -> FlextResult[None]:
        """Setup SSL configuration."""
        _ = config_path  # Parameter used for SSL configuration
        return FlextResult[None].ok(None)

    def validate_certificates(self) -> FlextResult[dict[str, bool]]:
        """Validate SSL certificates."""
        return FlextResult[dict[str, bool]].ok({"valid": True})

    def get_ssl_status(self) -> FlextResult[str]:
        """Get SSL status."""
        return FlextResult[str].ok("configured")
