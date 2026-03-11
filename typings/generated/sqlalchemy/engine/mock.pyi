from sqlalchemy.engine import URL
from cairosvg.url import URL
from typings.ldif3.mdurl import URL
from yarl import URL
from sqlalchemy import URL
from fastapi.datastructures import URL
from werkzeug.urls import URL
from httpcore import URL
from starlette.datastructures import URL
from mdurl import URL
from httpcore._models import URL
from httpx import URL
from sqlalchemy.engine.url import URL
from httpx._urls import URL
from yarl._url import URL
from mdurl._url import URL
from sqlalchemy.engine.interfaces import CoreExecuteOptionsParameter
from sqlalchemy.engine.interfaces import _CoreAnyExecuteParams
from sqlalchemy.sql.expression import Executable
from sqlalchemy import Executable
from sqlalchemy.sql import Executable
from sqlalchemy.sql.base import Executable
from typings.generated.sqlalchemy.sql.schema import HasSchemaAttr
from sqlalchemy.sql.schema import HasSchemaAttr
from sqlalchemy.engine import Dialect
from typings.generated.sqlalchemy.engine.interfaces import Dialect
from _csv import Dialect
from sqlalchemy import Dialect
from csv import Dialect
from sqlalchemy.engine.interfaces import Dialect
from collections.abc import Callable
from typing import Any

class MockConnection:
    def __init__(self, dialect: Dialect, execute: Callable[..., Any]) -> None: ...
    def connect(self, **kwargs: Any) -> MockConnection: ...
    def schema_for_object(self, obj: HasSchemaAttr) -> str | None: ...
    def execution_options(self, **kw: Any) -> MockConnection: ...
    def execute(self, obj: Executable, parameters: _CoreAnyExecuteParams | None = ..., execution_options: CoreExecuteOptionsParameter | None = ...) -> Any: ...
    @property
    def engine(self): ...
    @property
    def dialect(self): ...
    @property
    def name(self): ...
def create_mock_engine(url: str | URL, executor: Any, **kw: Any) -> MockConnection: ...
