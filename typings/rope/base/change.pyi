from __future__ import annotations

from rope.base.resources import Resource


class ChangeContents:
    resource: Resource
    new_contents: str | None

    def __init__(self, resource: Resource, new_contents: str) -> None: ...


class ChangeSet:
    changes: list[ChangeContents]

    def __init__(self, description: str) -> None: ...
    def add_change(self, change: ChangeContents) -> None: ...

