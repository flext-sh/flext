"""Minimal monitoring manager for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self

from flext_core import FlextCore


class MonitoringManager:
    """Basic monitoring manager for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize monitoring manager."""

    def start_monitoring(self: Self) -> FlextCore.Result[None]:
        """Start monitoring."""
        return FlextCore.Result[None].ok(None)

    def stop_monitoring(self: Self) -> FlextCore.Result[None]:
        """Stop monitoring."""
        return FlextCore.Result[None].ok(None)

    def get_metrics(self: Self) -> FlextCore.Result[FlextCore.Types.StringDict]:
        """Get monitoring metrics."""
        return FlextCore.Result[FlextCore.Types.StringDict].ok({})

    def get_health_status(self: Self) -> FlextCore.Result[str]:
        """Get health status."""
        return FlextCore.Result[str].ok("healthy")

    def setup_monitoring(self: Self) -> FlextCore.Result[None]:
        """Setup monitoring configuration."""
        return FlextCore.Result[None].ok(None)
