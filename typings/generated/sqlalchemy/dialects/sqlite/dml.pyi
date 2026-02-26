from typing import (
    ClassVar,
    Self,
    _DMLTableArgument,
    _OnConflictIndexElementsT,
    _OnConflictIndexWhereT,
    _OnConflictSetT,
    _OnConflictWhereT,
)

import sqlalchemy.sql.dml
import sqlalchemy.sql.elements
from _typeshed import Incomplete

__all__ = ['Insert', 'insert']

def insert(table: _DMLTableArgument) -> Insert: ...

class Insert(sqlalchemy.sql.dml.Insert):
    stringify_dialect: ClassVar[str] = ...
    inherit_cache: ClassVar[bool] = ...
    excluded: Incomplete
    def on_conflict_do_update(self, index_elements: _OnConflictIndexElementsT = ..., index_where: _OnConflictIndexWhereT = ..., set_: _OnConflictSetT = ..., where: _OnConflictWhereT = ...) -> Self: ...
    def on_conflict_do_nothing(self, index_elements: _OnConflictIndexElementsT = ..., index_where: _OnConflictIndexWhereT = ...) -> Self: ...

class OnConflictClause(sqlalchemy.sql.elements.ClauseElement):
    stringify_dialect: ClassVar[str] = ...
    def __init__(self, index_elements: _OnConflictIndexElementsT = ..., index_where: _OnConflictIndexWhereT = ...) -> None: ...

class OnConflictDoNothing(OnConflictClause):
    __visit_name__: ClassVar[str] = ...

class OnConflictDoUpdate(OnConflictClause):
    __visit_name__: ClassVar[str] = ...
    def __init__(self, index_elements: _OnConflictIndexElementsT = ..., index_where: _OnConflictIndexWhereT = ..., set_: _OnConflictSetT = ..., where: _OnConflictWhereT = ...) -> None: ...
