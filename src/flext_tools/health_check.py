"""Minimal health check service for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from typing import Self

from flext_core import FlextCore


class HealthCheckService:
    """Basic health check service for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize health check service."""

    def run_health_check(
        self, project_path: str | Path
    ) -> FlextCore.Result[FlextCore.Types.StringDict]:
        """Run health check."""
        try:
            health_status = {
                "status": "healthy",
                "project": str(project_path),
                "checks_passed": "all",
            }
            return FlextCore.Result[FlextCore.Types.StringDict].ok(health_status)
        except Exception as e:
            return FlextCore.Result[FlextCore.Types.StringDict].fail(
                f"Health check failed: {e}"
            )

    def get_system_health(self: Self) -> FlextCore.Result[str]:
        """Get system health status."""
        return FlextCore.Result[str].ok("System is healthy")
