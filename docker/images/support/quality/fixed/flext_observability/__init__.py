"""Mock flext_observability for fixed quality validation."""

from __future__ import annotations

import os
from collections.abc import MutableMapping

from flext_core import m, t

last_events: MutableMapping[str, dict[str, t.JsonPayload] | None] = {
    "metric": None,
    "trace": None,
    "log_entry": None,
}


def _copy_mapping(value: m.Dict | None) -> dict[str, t.JsonPayload]:
    """Copy optional mapping values into a mutable JSON mapping."""
    if value is None:
        empty_mapping: dict[str, t.JsonPayload] = {}
        return empty_mapping
    return dict(value)


def flext_create_metric(name: str, value: float, tags: m.Dict | None = None) -> None:
    """Create mock metric."""
    last_events["metric"] = {
        "name": name,
        "value": value,
        "tags": _copy_mapping(tags),
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
        "config": _copy_mapping(config),
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
        "context": _copy_mapping(context),
        "quiet": os.environ.get("FLEXT_OBSERVABILITY_QUIET"),
    }
