from __future__ import annotations

from collections.abc import Sequence

from rope.base.change import ChangeSet
from rope.base.pycore import PyCore
from rope.base.pyobjects import PyModule
from rope.base.resources import Resource


class _ProjectRoot:
    real_path: str


class Project:
    root: _ProjectRoot
    pycore: PyCore

    def __init__(
        self,
        projectroot: str,
        ropefolder: str = ...,
        save_objectdb: bool = ...,
        ignored_resources: Sequence[str] | None = ...,
        source_folders: Sequence[str] | None = ...,
    ) -> None: ...

    def get_resource(self, resource_path: str) -> Resource: ...
    def get_pymodule(self, resource: Resource) -> PyModule: ...
    def do(self, changes: ChangeSet) -> None: ...
    def close(self) -> None: ...

