"""Mock flext_observability for fixed quality validation."""

from __future__ import annotations

import os
from collections.abc import (
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from flext_core import m, t

last_events = {
    "metric": None,
    "trace": None,
    "log_entry": None,
}


def flext_create_metric(name: str, value: float, tags: m.Dict | None = None) -> None:
    """Create mock metric."""
    last_events["metric"] = {
        "name": name,
        "value": value,
        "tags": dict(tags or {}),
        "quiet": os.environ.get("FLEXT_OBSERVABILITY_QUIET"),
    }


def flext_create_trace(
    trace_id: str,
    operation: str,
    config: m.Dict | None = None,
) -> None:
    """Create mock trace."""
    last_events["trace"] = {
        "trace_id": trace_id,
        "operation": operation,
        "config": dict(config or {}),
        "quiet": os.environ.get("FLEXT_OBSERVABILITY_QUIET"),
    }


def flext_create_log_entry(
    message: str,
    level: str = "info",
    context: m.Dict | None = None,
) -> None:
    """Create mock log entry."""
    last_events["log_entry"] = {
        "message": message,
        "level": level,
        "context": dict(context or {}),
        "quiet": os.environ.get("FLEXT_OBSERVABILITY_QUIET"),
    }
