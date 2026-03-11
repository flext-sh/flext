from sqlalchemy.orm._typing import _IdentityKeyType
from sqlalchemy import RowMapping
from typings.generated.sqlalchemy.engine.row import RowMapping
from sqlalchemy.engine import RowMapping
from sqlalchemy.engine.row import RowMapping
from sqlalchemy import Row
from sqlalchemy.engine import Row
from typings.generated.sqlalchemy.engine.row import Row
from rich.table import Row
from sqlalchemy.engine.row import Row
from psycopg.rows import Row
from sqlite3 import Row
from sqlalchemy.ext.asyncio import AsyncScalarResult
from typings.generated.sqlalchemy.ext.asyncio.result import AsyncScalarResult
from sqlalchemy.ext.asyncio.result import AsyncScalarResult
from typings.generated.sqlalchemy.ext.asyncio.result import AsyncResult
from sqlalchemy.ext.asyncio import AsyncResult
from multiprocessing.pool import AsyncResult
from sqlalchemy.ext.asyncio.result import AsyncResult
from sqlalchemy.orm.session import _PKIdentityArgument
from sqlalchemy.engine import ScalarResult
from sqlalchemy import ScalarResult
from typings.generated.sqlalchemy.engine.result import ScalarResult
from sqlalchemy.engine.result import ScalarResult
from sqlalchemy.sql.selectable import ForUpdateParameter
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.engine import Connection
from redis.asyncio import Connection
from h11 import Connection
from redis import Connection
from typings.ldap3-stubs import Connection
from openpyxl.drawing.connector import Connection
from redis.connection import Connection
from sqlalchemy import Connection
from sqlalchemy.future import Connection
from oracledb import Connection
from typings.ldap3 import Connection
from psycopg import Connection
from typings.ldif3.ldap3-stubs import Connection
from typings.ldap3-stubs.core.connection import Connection
from sqlite3 import Connection
from aiohttp.connector import Connection
from sqlalchemy.future.engine import Connection
from ldap3.core.connection import Connection
from ldap3 import Connection
from websockets.asyncio.connection import Connection
from redis.asyncio.connection import Connection
from psycopg.connection import Connection
from h11._connection import Connection
from src.ldap3 import Connection
from typings.generated.sqlalchemy.engine.base import Connection
from websockets.sync.connection import Connection
from oracledb.connection import Connection
from sqlalchemy.engine.base import Connection
from multiprocessing.connection import Connection
from sqlalchemy.engine import Engine
from sqlalchemy import Engine
from sqlalchemy.future import Engine
from sqlalchemy.future.engine import Engine
from django.template.engine import Engine
from typings.generated.sqlalchemy.engine.base import Engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import _SessionBind
from sqlalchemy.sql import ClauseElement
from sqlalchemy import ClauseElement
from typings.generated.sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.sql.expression import ClauseElement
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.orm.identity import _O
from sqlalchemy.orm.bulk_persistence import _O
from sqlalchemy.orm.scoping import _O
from sqlalchemy.orm.loading import _O
from sqlalchemy.orm.base import _O
from sqlalchemy.sql.type_api import _O
from sqlalchemy.orm._typing import _O
from sqlalchemy.orm.session import _EntityBindKey
from typings.generated.sqlalchemy.engine.result import Result
from pluggy import Result
from redis.commands.search.result import Result
from sqlalchemy import Result
from sqlalchemy.engine import Result
from flext_core.result import Result
from mcp.types import Result
from typings.generated.sqlalchemy.ext.baked import Result
from rich.repr import Result
from pluggy._result import Result
from returns.result import Result
from sqlalchemy.engine.result import Result
from click.testing import Result
from sqlalchemy.orm._typing import OrmExecuteOptionsParameter
from sqlalchemy.engine.interfaces import _CoreAnyExecuteParams
from sqlalchemy.sql import Executable
from sqlalchemy import Executable
from sqlalchemy.sql.expression import Executable
from sqlalchemy.sql.base import Executable
from sqlalchemy.ext.asyncio import AsyncConnection
from psycopg import AsyncConnection
from sqlalchemy.ext.asyncio.engine import AsyncConnection
from typings.generated.sqlalchemy.ext.asyncio.engine import AsyncConnection
from oracledb import AsyncConnection
from oracledb.connection import AsyncConnection
from psycopg.connection_async import AsyncConnection
from sqlalchemy.engine.interfaces import CoreExecuteOptionsParameter
from sqlalchemy.orm.session import _BindArguments
from sqlalchemy.ext.asyncio import AsyncSessionTransaction
from typings.generated.sqlalchemy.ext.asyncio.session import AsyncSessionTransaction
from sqlalchemy.ext.asyncio.session import AsyncSessionTransaction
import typing
from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import Any, ClassVar

from _typeshed import Incomplete
from sqlalchemy.ext.asyncio.session import _AS, async_sessionmaker
from sqlalchemy.orm.session import Session

TYPE_CHECKING: bool

class async_scoped_session(typing.Generic):
    _support_async: ClassVar[bool] = ...
    __orig_bases__: ClassVar[tuple] = ...
    __parameters__: ClassVar[tuple] = ...
    bind: Incomplete
    identity_map: Incomplete
    autoflush: Incomplete
    def __init__(self, session_factory: async_sessionmaker[_AS], scopefunc: Callable[[], Any]) -> None: ...
    def __call__(self, **kw: Any) -> _AS: ...
    def configure(self, **kwargs: Any) -> None: ...
    def remove(self) -> None: ...
    def __contains__(self, instance: object) -> bool: ...
    def __iter__(self) -> Iterator[object]: ...
    def aclose(self) -> None: ...
    def add(self, instance: object, _warn: bool = ...) -> None: ...
    def add_all(self, instances: Iterable[object]) -> None: ...
    def begin(self) -> AsyncSessionTransaction: ...
    def begin_nested(self) -> AsyncSessionTransaction: ...
    def close(self) -> None: ...
    def reset(self) -> None: ...
    def commit(self) -> None: ...
    def connection(self, bind_arguments: _BindArguments | None = ..., execution_options: CoreExecuteOptionsParameter | None = ..., **kw: Any) -> AsyncConnection: ...
    def delete(self, instance: object) -> None: ...
    def execute(self, statement: Executable, params: _CoreAnyExecuteParams | None = ..., *, execution_options: OrmExecuteOptionsParameter = ..., bind_arguments: _BindArguments | None = ..., **kw: Any) -> Result[Any]: ...
    def expire(self, instance: object, attribute_names: Iterable[str] | None = ...) -> None: ...
    def expire_all(self) -> None: ...
    def expunge(self, instance: object) -> None: ...
    def expunge_all(self) -> None: ...
    def flush(self, objects: Sequence[Any] | None = ...) -> None: ...
    def get_bind(self, mapper: _EntityBindKey[_O] | None = ..., clause: ClauseElement | None = ..., bind: _SessionBind | None = ..., **kw: Any) -> Engine | Connection: ...
    def is_modified(self, instance: object, include_collections: bool = ...) -> bool: ...
    def invalidate(self) -> None: ...
    def merge(self, instance: _O, *, load: bool = ..., options: Sequence[ORMOption] | None = ...) -> _O: ...
    def refresh(self, instance: object, attribute_names: Iterable[str] | None = ..., with_for_update: ForUpdateParameter = ...) -> None: ...
    def rollback(self) -> None: ...
    def scalar(self, statement: Executable, params: _CoreAnyExecuteParams | None = ..., *, execution_options: OrmExecuteOptionsParameter = ..., bind_arguments: _BindArguments | None = ..., **kw: Any) -> Any: ...
    def scalars(self, statement: Executable, params: _CoreAnyExecuteParams | None = ..., *, execution_options: OrmExecuteOptionsParameter = ..., bind_arguments: _BindArguments | None = ..., **kw: Any) -> ScalarResult[Any]: ...
    def get(self, entity: _EntityBindKey[_O], ident: _PKIdentityArgument, *, options: Sequence[ORMOption] | None = ..., populate_existing: bool = ..., with_for_update: ForUpdateParameter = ..., identity_token: Any | None = ..., execution_options: OrmExecuteOptionsParameter = ...) -> _O | None: ...
    def get_one(self, entity: _EntityBindKey[_O], ident: _PKIdentityArgument, *, options: Sequence[ORMOption] | None = ..., populate_existing: bool = ..., with_for_update: ForUpdateParameter = ..., identity_token: Any | None = ..., execution_options: OrmExecuteOptionsParameter = ...) -> _O: ...
    def stream(self, statement: Executable, params: _CoreAnyExecuteParams | None = ..., *, execution_options: OrmExecuteOptionsParameter = ..., bind_arguments: _BindArguments | None = ..., **kw: Any) -> AsyncResult[Any]: ...
    def stream_scalars(self, statement: Executable, params: _CoreAnyExecuteParams | None = ..., *, execution_options: OrmExecuteOptionsParameter = ..., bind_arguments: _BindArguments | None = ..., **kw: Any) -> AsyncScalarResult[Any]: ...
    @classmethod
    def close_all(cls) -> None: ...
    @classmethod
    def object_session(cls, instance: object) -> Session | None: ...
    @classmethod
    def identity_key(cls, class_: type[Any] | None = ..., ident: Any | tuple[Any, ...] = ..., *, instance: Any | None = ..., row: Row[Any] | RowMapping | None = ..., identity_token: Any | None = ...) -> _IdentityKeyType[Any]: ...
    @property
    def dirty(self): ...
    @property
    def deleted(self): ...
    @property
    def new(self): ...
    @property
    def is_active(self): ...
    @property
    def no_autoflush(self): ...
    @property
    def info(self): ...
