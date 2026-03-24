"""Mock flext_observability for fixed quality validation."""

from __future__ import annotations

import os

from flext_core import t


def flext_create_metric(_name: str, _value: float, _tags: t.Dict | None = None) -> None:
    """Create mock metric."""
    if not os.environ.get("FLEXT_OBSERVABILITY_QUIET"):
        pass


def flext_create_trace(
    _trace_id: str,
    _operation: str,
    _config: t.Dict | None = None,
) -> None:
    """Create mock trace."""
    if not os.environ.get("FLEXT_OBSERVABILITY_QUIET"):
        pass


def flext_create_log_entry(
    _message: str,
    _level: str = "info",
    _context: t.Dict | None = None,
) -> None:
    """Create mock log entry."""
    if not os.environ.get("FLEXT_OBSERVABILITY_QUIET"):
        pass
