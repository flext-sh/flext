from __future__ import annotations

from rope.base.change import ChangeSet
from rope.base.project import Project
from rope.base.resources import Resource


class Rename:
    def __init__(self, project: Project, resource: Resource, offset: int) -> None: ...

    def get_changes(
        self,
        new_name: str,
        in_file: object | None = ...,
        in_hierarchy: bool = ...,
        unsure: object | None = ...,
        docs: bool = ...,
        resources: object | None = ...,
        task_handle: object = ...,
    ) -> ChangeSet: ...

