# @flext-generated: typing-stubs

from gitdb.db.base import CompoundDB

__all__ = ("ReferenceDB",)

class ReferenceDB(CompoundDB):
    ObjectDBCls = ...
    def __init__(self, ref_file) -> None: ...
    def update_cache(self, force=...):  # -> Literal[False]:
        ...
