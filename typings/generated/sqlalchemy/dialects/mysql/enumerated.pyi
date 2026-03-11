from typings.generated.sqlalchemy.sql.type_api import _BindProcessorType
from sqlalchemy.sql.type_api import _BindProcessorType
from typings.generated.sqlalchemy.sql.type_api import _ResultProcessorType
from sqlalchemy.sql.type_api import _ResultProcessorType
from sqlalchemy.engine import Dialect
from sqlalchemy import Dialect
from csv import Dialect
from _csv import Dialect
from typings.generated.sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy import ColumnElement
from sqlalchemy.sql import ColumnElement
from typings.generated.sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.sql.elements import ColumnElement
from typings.generated.sqlalchemy.sql.type_api import TypeEngineMixin
from sqlalchemy.sql.type_api import TypeEngineMixin
from sqlalchemy.types import TypeEngine
from sqlalchemy.sql.sqltypes import TypeEngine
from typings.generated.sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.sql.type_api import TypeEngine
import enum
from typing import Any, ClassVar

import sqlalchemy.dialects.mysql.types
import sqlalchemy.sql.sqltypes
import sqlalchemy.sql.type_api

TYPE_CHECKING: bool

class ENUM(sqlalchemy.sql.type_api.NativeForEmulated, sqlalchemy.sql.sqltypes.Enum, sqlalchemy.dialects.mysql.types._StringType):
    __visit_name__: ClassVar[str] = ...
    native_enum: ClassVar[bool] = ...
    __parameters__: ClassVar[tuple] = ...
    def __init__(self, *enums: str | type[enum.Enum], **kw: Any) -> None: ...
    @classmethod
    def adapt_emulated_to_native(cls, impl: TypeEngine[Any] | TypeEngineMixin, **kw: Any) -> ENUM: ...

class SET(sqlalchemy.dialects.mysql.types._StringType):
    __visit_name__: ClassVar[str] = ...
    __parameters__: ClassVar[tuple] = ...
    def __init__(self, *values: str, **kw: Any) -> None: ...
    def column_expression(self, colexpr: ColumnElement[Any]) -> ColumnElement[Any]: ...
    def result_processor(self, dialect: Dialect, coltype: Any) -> _ResultProcessorType[Any] | None: ...
    def bind_processor(self, dialect: Dialect) -> _BindProcessorType[str | int]: ...
    def adapt(self, cls: type, **kw: Any) -> Any: ...
