from typings.generated.sqlalchemy.engine.interfaces import ReflectedColumn
from sqlalchemy.engine.interfaces import ReflectedColumn
from fontTools.ttLib.tables.otConverters import Table
from pyarrow import Table
from openpyxl.worksheet.table import Table
from sqlalchemy import Table
from sqlalchemy.schema import Table
from typings.generated.sqlalchemy.sql.schema import Table
from typings.ldif3.django-stubs.db.backends import Table
from django.db.backends.ddl_references import Table
from pyarrow.__lib_pxi.table import Table
from matplotlib.table import Table
from typings.tomlkit.items import Table
from sqlalchemy.sql.schema import Table
from docx.table import Table
from tomlkit.items import Table
from rich.table import Table
from sqlalchemy import Inspector
from sqlalchemy.engine import Inspector
from sqlalchemy.engine.reflection import Inspector
from typings.generated.sqlalchemy.engine.reflection import Inspector
from sqlalchemy.schema import SchemaItem
from typings.generated.sqlalchemy.sql.schema import SchemaItem
from sqlalchemy.sql.schema import SchemaItem
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
from typing import Any, ClassVar

import sqlalchemy.event.base
import sqlalchemy.sql.base
from sqlalchemy.sql.base import SchemaEventTarget

TYPE_CHECKING: bool

class DDLEvents(sqlalchemy.event.base.Events):
    _target_class_doc: ClassVar[str] = ...
    _dispatch_target: ClassVar[type[sqlalchemy.sql.base.SchemaEventTarget]] = ...
    __orig_bases__: ClassVar[tuple] = ...
    dispatch: ClassVar[sqlalchemy.event.base.DDLEventsDispatch] = ...
    def before_create(self, target: SchemaEventTarget, connection: Connection, **kw: Any) -> None: ...
    def after_create(self, target: SchemaEventTarget, connection: Connection, **kw: Any) -> None: ...
    def before_drop(self, target: SchemaEventTarget, connection: Connection, **kw: Any) -> None: ...
    def after_drop(self, target: SchemaEventTarget, connection: Connection, **kw: Any) -> None: ...
    def before_parent_attach(self, target: SchemaEventTarget, parent: SchemaItem) -> None: ...
    def after_parent_attach(self, target: SchemaEventTarget, parent: SchemaItem) -> None: ...
    def column_reflect(self, inspector: Inspector, table: Table, column_info: ReflectedColumn) -> None: ...
