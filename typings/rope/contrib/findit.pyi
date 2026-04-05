from __future__ import annotations

from rope.base.project import Project
from rope.base.resources import Resource


class Location:
    resource: Resource
    lineno: int
    region: tuple[int, int]


def find_occurrences(
    project: Project,
    resource: Resource,
    offset: int,
    unsure: bool = ...,
    resources: object | None = ...,
    in_hierarchy: bool = ...,
    task_handle: object = ...,
) -> list[Location]: ...
