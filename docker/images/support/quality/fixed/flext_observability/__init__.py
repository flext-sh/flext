"""Mock flext_observability for fixed quality validation."""

from __future__ import annotations

import os

from flext_core import m, t


def flext_create_metric(_name: str, _value: float, _tags: m.Dict | None = None) -> None:
    """Create mock metric."""
    _ = os.environ.get("FLEXT_OBSERVABILITY_QUIET")


def flext_create_trace(
    _trace_id: str,
    _operation: str,
    _config: m.Dict | None = None,
) -> None:
    """Create mock trace."""
    _ = os.environ.get("FLEXT_OBSERVABILITY_QUIET")


def flext_create_log_entry(
    _message: str,
    _level: str = "info",
    _context: m.Dict | None = None,
) -> None:
    """Create mock log entry."""
    _ = os.environ.get("FLEXT_OBSERVABILITY_QUIET")
