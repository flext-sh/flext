"""Mock flext_observability for enterprise quality validation."""

from __future__ import annotations

from typing import Any


def flext_create_metric(
    name: str, value: float, tags: dict[str, Any] | None = None
) -> None:
    """Create mock metric."""
    print(f"📊 Metric: {name}={value} {tags or {}}")  # noqa: T201


def flext_create_trace(
    trace_id: str, operation: str, config: dict[str, Any] | None = None
) -> None:
    """Create mock trace."""
    print(f"🔍 Trace: {trace_id} {operation} {config or {}}")  # noqa: T201


def flext_create_log_entry(
    message: str, level: str = "info", context: dict[str, Any] | None = None
) -> None:
    """Create mock log entry."""
    print(f"📝 Log [{level}]: {message} {context or {}}")  # noqa: T201
