"""Mock flext_observability for enterprise quality validation."""

from __future__ import annotations

from flext_core import t


def flext_create_metric(name: str, value: float, tags: t.Dict | None = None) -> None:
    """Create mock metric."""


def flext_create_trace(
    trace_id: str, operation: str, config: t.Dict | None = None
) -> None:
    """Create mock trace."""


def flext_create_log_entry(
    message: str, level: str = "info", context: t.Dict | None = None
) -> None:
    """Create mock log entry."""
