"""Mock flext_observability for simple quality validation."""

from __future__ import annotations

import os
from collections.abc import MutableMapping

from flext_core import m, t

type EventFieldValue = t.Scalar | m.Dict | None
type EventPayload = dict[str, EventFieldValue]


last_events: MutableMapping[str, EventPayload | None] = {
    "metric": None,
    "trace": None,
    "log_entry": None,
}


def _copy_mapping(value: m.Dict | None) -> m.Dict:
    """Copy optional mapping values into a Dict container."""
    if value is None:
        return m.Dict(root={})
    return m.Dict(root=dict(value.root))


def flext_create_metric(name: str, value: float, tags: m.Dict | None = None) -> None:
    """Create mock metric."""
    metric_event: EventPayload = {
        "name": name,
        "value": value,
        "tags": _copy_mapping(tags),
        "quiet": os.environ.get("FLEXT_OBSERVABILITY_QUIET"),
    }
    last_events["metric"] = metric_event


def flext_create_trace(
    trace_id: str,
    operation: str,
    config: m.Dict | None = None,
) -> None:
    """Create mock trace."""
    trace_event: EventPayload = {
        "trace_id": trace_id,
        "operation": operation,
        "config": _copy_mapping(config),
        "quiet": os.environ.get("FLEXT_OBSERVABILITY_QUIET"),
    }
    last_events["trace"] = trace_event


def flext_create_log_entry(
    message: str,
    level: str = "info",
    context: m.Dict | None = None,
) -> None:
    """Create mock log entry."""
    log_event: EventPayload = {
        "message": message,
        "level": level,
        "context": _copy_mapping(context),
        "quiet": os.environ.get("FLEXT_OBSERVABILITY_QUIET"),
    }
    last_events["log_entry"] = log_event
