from django.test.utils import _C
from alembic.ddl._autogen import _C
from alembic.util.langhelpers import _C
from django.template.library import _C
from attr import _C
from attrs import _C
from _weakref import _C
from typings.ldif3.attrs import _C
from alembic.op import _C
from django.core.checks.registry import _C
from typings.ldif3.django-stubs.utils import _C
from joblib.externals.loky.backend.reduction import _C
from alembic.autogenerate.compare.constraints import _C
from django.db.transaction import _C
from alembic.operations.base import _C
from concurrent.futures.thread import _C
from sqlalchemy.engine.util import _C
from django.utils.functional import _C
from typings.ldif3.django-stubs.db import _C
from fastmcp.server.providers.local_provider.local_provider import _C
from django.utils.safestring import _C
from singer_sdk.sql.sink import _C
import _abc
import typing
from collections.abc import Callable
from typing import Any, ClassVar, Self

HAS_CYEXTENSION: bool
def connection_memoize(key: str) -> Callable[[_C], _C]: ...

class _TConsSubject(typing.Protocol):
    __parameters__: ClassVar[tuple] = ...
    _is_protocol: ClassVar[bool] = ...
    __abstractmethods__: ClassVar[frozenset] = ...
    _abc_impl: ClassVar[_abc._abc_data] = ...
    __protocol_attrs__: ClassVar[set] = ...
    @classmethod
    def __subclasshook__(cls, other): ...
    def __init__(self, *args, **kwargs) -> None: ...

class TransactionalContext:
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def close(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, type_: Any, value: Any, traceback: Any) -> None: ...
