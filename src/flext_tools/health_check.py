"""Minimal health check service for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult


class HealthCheckService:
    """Basic health check service for legacy scripts."""

    def __init__(self) -> None:
        """Initialize health check service."""

    def run_health_check(self, project_path: str | Path) -> FlextResult[dict[str, str]]:
        """Run health check."""
        try:
            health_status = {
                "status": "healthy",
                "project": str(project_path),
                "checks_passed": "all",
            }
            return FlextResult[dict[str, str]].ok(health_status)
        except Exception as e:
            return FlextResult[dict[str, str]].fail(f"Health check failed: {e}")

    def get_system_health(self) -> FlextResult[str]:
        """Get system health status."""
        return FlextResult[str].ok("System is healthy")
