"""Mock flext_observability for enterprise quality validation."""

from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from flext_core import m, t


def flext_create_metric(name: str, value: float, tags: m.Dict | None = None) -> None:
    """Create mock metric."""


def flext_create_trace(
    trace_id: str,
    operation: str,
    settings: m.Dict | None = None,
) -> None:
    """Create mock trace."""


def flext_create_log_entry(
    message: str,
    level: str = "info",
    context: m.Dict | None = None,
) -> None:
    """Create mock log entry."""
