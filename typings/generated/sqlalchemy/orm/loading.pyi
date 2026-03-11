from sqlalchemy.engine.interfaces import _ExecuteOptions
from sqlalchemy.orm import InstanceState
from sqlalchemy.orm.state import InstanceState
from typings.generated.sqlalchemy.orm.state import InstanceState
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.sql import Select
from sqlalchemy import Select
from django.forms import Select
from django.forms.widgets import Select
from sqlalchemy.sql.expression import Select
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import LoaderCallableStatus
from sqlalchemy.orm.base import LoaderCallableStatus
from typings.generated.sqlalchemy.orm.base import LoaderCallableStatus
from sqlalchemy.orm._typing import _IdentityKeyType
from sqlalchemy.orm.identity import _O
from sqlalchemy.orm.bulk_persistence import _O
from sqlalchemy.orm.scoping import _O
from sqlalchemy.sql.type_api import _O
from sqlalchemy.orm._typing import _O
from sqlalchemy.orm.loading import _O
from sqlalchemy.orm.base import _O
from sqlalchemy.orm import Mapper
from typings.generated.sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.mapper import Mapper
from typings.generated.sqlalchemy.orm.session import Session
from requests import Session
from sqlalchemy.orm import Session
from requests.sessions import Session
from _pytest.main import Session
from sqlalchemy.orm.session import Session
from typings.generated.sqlalchemy.orm.query import Query
from sqlalchemy.orm import Query
from redis.commands.search.query import Query
from openpyxl.pivot.cache import Query
from fastapi import Query
from aiohttp.typedefs import Query
from django.db.models.sql import Query
from fastapi.param_functions import Query
from psycopg.abc import Query
from yarl import Query
from fastapi.params import Query
from sqlalchemy.orm.query import Query
from yarl._query import Query
from django.db.models.sql.query import Query
from sqlalchemy.engine import Result
from sqlalchemy import Result
from flext_core.result import Result
from typings.generated.sqlalchemy.engine.result import Result
from redis.commands.search.result import Result
from pluggy import Result
from typings.generated.sqlalchemy.ext.baked import Result
from rich.repr import Result
from pluggy._result import Result
from click.testing import Result
from returns.result import Result
from sqlalchemy.engine.result import Result
from mcp.types import Result
from sqlalchemy import CursorResult
from sqlalchemy.engine import CursorResult
from typings.generated.sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.engine.cursor import CursorResult
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import sqlalchemy.cyextension.immutabledict
from _typeshed import Incomplete
from sqlalchemy.engine.result import FrozenResult
from sqlalchemy.orm.base import PassiveFlag
from sqlalchemy.orm.context import FromStatement, QueryContext
from sqlalchemy.sql.selectable import ForUpdateArg

TYPE_CHECKING: bool
EMPTY_DICT: sqlalchemy.cyextension.immutabledict.immutabledict
def instances(cursor: CursorResult[Any], context: QueryContext) -> Result[Any]: ...
def merge_frozen_result(session, statement, frozen_result, load: bool = ...): ...
def merge_result(query: Query[Any], iterator: FrozenResult | Iterable[Sequence[Any]] | Iterable[object], load: bool = ...) -> FrozenResult | Iterable[Any]: ...
def get_from_identity(session: Session, mapper: Mapper[_O], key: _IdentityKeyType[_O], passive: PassiveFlag) -> LoaderCallableStatus | _O | None: ...
def load_on_ident(session: Session, statement: Select | FromStatement, key: _IdentityKeyType | None, *, load_options: Sequence[ORMOption] | None = ..., refresh_state: InstanceState[Any] | None = ..., with_for_update: ForUpdateArg | None = ..., only_load_props: Iterable[str] | None = ..., no_autoflush: bool = ..., bind_arguments: Mapping[str, Any] = ..., execution_options: _ExecuteOptions = ..., require_pk_cols: bool = ..., is_user_refresh: bool = ...): ...
def load_on_pk_identity(session: Session, statement: Select | FromStatement, primary_key_identity: tuple[Any, ...] | None, *, load_options: Sequence[ORMOption] | None = ..., refresh_state: InstanceState[Any] | None = ..., with_for_update: ForUpdateArg | None = ..., only_load_props: Iterable[str] | None = ..., identity_token: Any | None = ..., no_autoflush: bool = ..., bind_arguments: Mapping[str, Any] = ..., execution_options: _ExecuteOptions = ..., require_pk_cols: bool = ..., is_user_refresh: bool = ...): ...

class PostLoad:
    load_keys: Incomplete
    loaders: Incomplete
    states: Incomplete
    def __init__(self) -> None: ...
    def add_state(self, state, overwrite): ...
    def invoke(self, context, path): ...
    @classmethod
    def for_context(cls, context, path, only_load_props): ...
    def path_exists(self, context, path, key): ...
    @classmethod
    def callable_for_path(cls, context, path, limit_to_mapper, token, loader_callable, *arg, **kw): ...
def load_scalar_attributes(mapper, state, attribute_names, passive): ...
