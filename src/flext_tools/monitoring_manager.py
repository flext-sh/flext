"""Minimal monitoring manager for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self

from flext_core import FlextResult, FlextTypes


class MonitoringManager:
    """Basic monitoring manager for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize monitoring manager."""

    def start_monitoring(self: Self) -> FlextResult[None]:
        """Start monitoring."""
        return FlextResult[None].ok(None)

    def stop_monitoring(self: Self) -> FlextResult[None]:
        """Stop monitoring."""
        return FlextResult[None].ok(None)

    def get_metrics(self: Self) -> FlextResult[FlextTypes.StringDict]:
        """Get monitoring metrics."""
        return FlextResult[FlextTypes.StringDict].ok({})

    def get_health_status(self: Self) -> FlextResult[str]:
        """Get health status."""
        return FlextResult[str].ok("healthy")

    def setup_monitoring(self: Self) -> FlextResult[None]:
        """Setup monitoring configuration."""
        return FlextResult[None].ok(None)
