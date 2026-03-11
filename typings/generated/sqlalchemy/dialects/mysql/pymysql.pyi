from typings.generated.sqlalchemy.engine.interfaces import DBAPICursor
from sqlalchemy.engine.interfaces import DBAPICursor
from sqlalchemy.pool import PoolProxiedConnection
from typings.generated.sqlalchemy.pool.base import PoolProxiedConnection
from sqlalchemy import PoolProxiedConnection
from sqlalchemy.engine.interfaces import PoolProxiedConnection
from sqlalchemy.pool.base import PoolProxiedConnection
from sqlalchemy.engine import ConnectArgsType
from sqlalchemy.engine.interfaces import ConnectArgsType
from sqlalchemy.engine import URL
from cairosvg.url import URL
from sqlalchemy import URL
from mdurl import URL
from httpx import URL
from mdurl._url import URL
from fastapi.datastructures import URL
from werkzeug.urls import URL
from typings.ldif3.mdurl import URL
from starlette.datastructures import URL
from sqlalchemy.engine.url import URL
from yarl import URL
from httpx._urls import URL
from yarl._url import URL
from httpcore import URL
from httpcore._models import URL
from typings.generated.sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.engine.interfaces import DBAPIConnection
from typing import Any, ClassVar, Literal

import DBAPIModule
import sqlalchemy.dialects.mysql.mysqldb
from _typeshed import Incomplete

TYPE_CHECKING: bool

class MySQLDialect_pymysql(sqlalchemy.dialects.mysql.mysqldb.MySQLDialect_mysqldb):
    driver: ClassVar[str] = ...
    supports_statement_cache: ClassVar[bool] = ...
    description_encoding: ClassVar[None] = ...
    supports_server_side_cursors: Incomplete
    @classmethod
    def import_dbapi(cls) -> DBAPIModule: ...
    def do_ping(self, dbapi_connection: DBAPIConnection) -> Literal[True]: ...
    def create_connect_args(self, url: URL, _translate_args: dict[str, Any] | None = ...) -> ConnectArgsType: ...
    def is_disconnect(self, e: DBAPIModule.Error, connection: PoolProxiedConnection | DBAPIConnection | None, cursor: DBAPICursor | None) -> bool: ...

class dialect(sqlalchemy.dialects.mysql.mysqldb.MySQLDialect_mysqldb):
    driver: ClassVar[str] = ...
    supports_statement_cache: ClassVar[bool] = ...
    description_encoding: ClassVar[None] = ...
    supports_server_side_cursors: Incomplete
    @classmethod
    def import_dbapi(cls) -> DBAPIModule: ...
    def do_ping(self, dbapi_connection: DBAPIConnection) -> Literal[True]: ...
    def create_connect_args(self, url: URL, _translate_args: dict[str, Any] | None = ...) -> ConnectArgsType: ...
    def is_disconnect(self, e: DBAPIModule.Error, connection: PoolProxiedConnection | DBAPIConnection | None, cursor: DBAPICursor | None) -> bool: ...
