from __future__ import annotations

from collections.abc import Sequence


class ImportInfo:
    names_and_aliases: list[tuple[str, str | None]]


class FromImport(ImportInfo):
    module_name: str
    level: int
    names_and_aliases: list[tuple[str, str | None]]

    def __init__(
        self,
        module_name: str,
        level: int,
        names_and_aliases: Sequence[tuple[str, str | None]],
    ) -> None: ...

