"""FLEXT infra test helpers for result."""

from __future__ import annotations

from flext_core import r


class TestsFlextRootResult:
    """Workspace-level result namespace for root tests."""

    Result = r


__all__: list[str] = ["TestsFlextRootResult"]
