from __future__ import annotations

from rope.base.change import ChangeSet
from rope.base.project import Project
from rope.base.pyobjects import PyModule
from rope.base.resources import Resource
from rope.refactor.importutils.importinfo import ImportInfo


class ImportStatement:
    import_info: ImportInfo


class ModuleImports:
    imports: list[ImportStatement]

    def add_import(self, import_info: ImportInfo) -> None: ...
    def remove_duplicates(self) -> None: ...
    def sort_imports(self) -> None: ...
    def get_changed_source(self) -> str: ...


def get_module_imports(project: Project, pymodule: PyModule) -> ModuleImports: ...


class ImportOrganizer:
    def __init__(self, project: Project) -> None: ...

    def organize_imports(
        self,
        resource: Resource,
        offset: int | None = ...,
    ) -> ChangeSet | None: ...

