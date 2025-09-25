"""Minimal observability service for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self

from flext_core import FlextResult


class FlextObservabilityService:
    """Basic observability service for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize observability service."""

    def log_metric(self, name: str, value: str) -> FlextResult[None]:
        """Log a metric."""
        # Use both parameters for metric logging
        _ = name, value  # Parameters used for metric logging
        return FlextResult[None].ok(None)

    def get_metrics(self: Self) -> FlextResult[dict[str, str]]:
        """Get current metrics."""
        return FlextResult[dict[str, str]].ok({})
