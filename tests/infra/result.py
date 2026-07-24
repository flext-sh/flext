"""FLEXT infra test helpers for result."""

from __future__ import annotations

from flext_core import r as _r


class TestsFlextRootResult:
    """Workspace-level result namespace for root tests."""

    Result = _r


r = _r

__all__: list[str] = ["TestsFlextRootResult", "r"]
