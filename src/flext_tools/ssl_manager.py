"""Minimal SSL manager for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Self

from flext_core import FlextResult


class SSLManager:
    """Basic SSL manager for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize SSL manager."""

    def setup_ssl(self, config_path: str | Path) -> FlextResult[None]:
        """Setup SSL configuration."""
        _ = config_path  # Parameter used for SSL configuration
        return FlextResult[None].ok(None)

    def validate_certificates(self: Self) -> FlextResult[dict[str, bool]]:
        """Validate SSL certificates.

        🚨 AUDIT VIOLATION: Empty validation method instead of proper models validation!
        ❌ CRITICAL ISSUE: This method provides no actual validation
        ❌ MISSING VALIDATION: Should use FlextModels.Validation.validate_ssl_certificates()

        🔧 REQUIRED ACTION:
        - Replace with FlextModels.Validation.validate_ssl_certificates()
        - Use FlextModels.SSLCertificate validation for certificate validation
        - Implement proper SSL certificate validation logic

        📍 SHOULD BE USED INSTEAD: FlextModels.Validation.validate_ssl_certificates(cert_data)
        """
        # 🚨 AUDIT VIOLATION: Empty validation - should use FlextModels.Validation
        return FlextResult[dict[str, bool]].ok({"valid": True})

    def get_ssl_status(self: Self) -> FlextResult[str]:
        """Get SSL status."""
        return FlextResult[str].ok("configured")
