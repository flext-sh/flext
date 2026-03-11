from typings.generated.sqlalchemy.sql.type_api import _LiteralProcessorType
from sqlalchemy.sql.type_api import _LiteralProcessorType
from typings.generated.sqlalchemy.sql.type_api import _BindProcessorType
from sqlalchemy.sql.type_api import _BindProcessorType
from sqlalchemy.engine import Dialect
from sqlalchemy import Dialect
from csv import Dialect
from _csv import Dialect
from typings.generated.sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.engine.interfaces import Dialect
from typing import Any, ClassVar

import sqlalchemy.sql.sqltypes

TYPE_CHECKING: bool

class JSON(sqlalchemy.sql.sqltypes.JSON):
    __parameters__: ClassVar[tuple] = ...

class _FormatTypeMixin:
    def bind_processor(self, dialect: Dialect) -> _BindProcessorType[Any]: ...
    def literal_processor(self, dialect: Dialect) -> _LiteralProcessorType[Any]: ...

class JSONIndexType(_FormatTypeMixin, sqlalchemy.sql.sqltypes.JSON.JSONIndexType):
    __parameters__: ClassVar[tuple] = ...

class JSONPathType(_FormatTypeMixin, sqlalchemy.sql.sqltypes.JSON.JSONPathType):
    __parameters__: ClassVar[tuple] = ...
