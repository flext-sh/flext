"""FLEXT infra test helpers for result."""

from __future__ import annotations

from flext_core import r


class TestsFlextRootResult:
    """Workspace-level result namespace for root tests."""

    Result = r


<<<<<<< HEAD
__all__: list[str] = ["TestsFlextRootResult"]
=======
__all__: list[str] = ["TestsFlextRootResult", "r"]
>>>>>>> origin/0.12.0-dev
