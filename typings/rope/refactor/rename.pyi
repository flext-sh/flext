from collections.abc import Callable

from rope.base.change import ChangeSet
from rope.base.project import _Project
from rope.base.resources import File, Resource
from rope.base.taskhandle import NullTaskHandle

class Rename:
    project: _Project
    resource: Resource
    old_name: str
    def __init__(
        self,
        project: _Project,
        resource: Resource,
        offset: int | None = None,
    ) -> None: ...
    def get_old_name(self) -> str: ...
    def get_changes(
        self,
        new_name: str,
        in_file: Resource | None = None,
        in_hierarchy: bool = False,
        unsure: Callable[..., bool] | None = None,
        docs: bool = False,
        resources: list[File] | None = None,
        task_handle: NullTaskHandle = ...,
    ) -> ChangeSet: ...
