"""Minimal monitoring manager for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult


class MonitoringManager:
    """Basic monitoring manager for legacy scripts."""

    def __init__(self) -> None:
        """Initialize monitoring manager."""

    def start_monitoring(self) -> FlextResult[None]:
        """Start monitoring."""
        return FlextResult[None].ok(None)

    def stop_monitoring(self) -> FlextResult[None]:
        """Stop monitoring."""
        return FlextResult[None].ok(None)

    def get_metrics(self) -> FlextResult[dict[str, str]]:
        """Get monitoring metrics."""
        return FlextResult[dict[str, str]].ok({})

    def get_health_status(self) -> FlextResult[str]:
        """Get health status."""
        return FlextResult[str].ok("healthy")

    def setup_monitoring(self) -> FlextResult[None]:
        """Setup monitoring configuration."""
        return FlextResult[None].ok(None)
