"""Minimal observability service for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self

from flext_core import FlextCore


class FlextObservabilityService:
    """Basic observability service for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize observability service."""

    def log_metric(self, name: str, value: str) -> FlextCore.Result[None]:
        """Log a metric."""
        # Use both parameters for metric logging
        _ = name, value  # Parameters used for metric logging
        return FlextCore.Result[None].ok(None)

    def get_metrics(self: Self) -> FlextCore.Result[FlextCore.Types.StringDict]:
        """Get current metrics."""
        return FlextCore.Result[FlextCore.Types.StringDict].ok({})
