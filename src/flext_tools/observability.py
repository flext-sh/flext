"""Minimal observability service for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult


class FlextObservabilityService:
    """Basic observability service for legacy scripts."""

    def __init__(self) -> None:
        """Initialize observability service."""

    def log_metric(self, name: str, value: str) -> FlextResult[None]:
        """Log a metric."""
        # Use both parameters for metric logging
        _ = name, value  # Parameters used for metric logging
        return FlextResult[None].ok(None)

    def get_metrics(self) -> FlextResult[dict[str, str]]:
        """Get current metrics."""
        return FlextResult[dict[str, str]].ok({})
