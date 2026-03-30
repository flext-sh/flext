from rope.base.project import _Project
from rope.base.resources import File, Resource
from rope.base.taskhandle import NullTaskHandle

class Location:
    resource: Resource
    region: tuple[int, int]
    offset: int
    unsure: bool
    lineno: int

def find_occurrences(
    project: _Project,
    resource: Resource,
    offset: int,
    unsure: bool = False,
    resources: list[File] | None = None,
    in_hierarchy: bool = False,
    task_handle: NullTaskHandle = ...,
) -> list[Location]: ...
def find_implementations(
    project: _Project,
    resource: Resource,
    offset: int,
    resources: list[File] | None = None,
    task_handle: NullTaskHandle = ...,
) -> list[Location]: ...
def find_definition(
    project: _Project,
    code: str,
    offset: int,
    resource: Resource | None = None,
    maxfixes: int = 1,
) -> Location | None: ...
