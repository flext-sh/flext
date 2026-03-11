from contextlib import _T_co
from sqlalchemy.sql.elements import _T_co
from _operator import _T_co
from optype.io import _T_co
from pandas._typing import _T_co
from _typeshed import _T_co
from scipy._lib._util import _T_co
from numpy.lib._npyio_impl import _T_co
from docker.types.daemon import _T_co
from concurrent.futures._base import _T_co
from lxml.etree._saxparser import _T_co
from typing_extensions import _T_co
from sqlalchemy.ext.hybrid import _T_co
from typing import _T_co
from numpy.lib._function_base_impl import _T_co
from itertools import _T_co
from math import _T_co
from sqlalchemy.sql._typing import _T_co
from sqlalchemy.orm.interfaces import _T_co
from sqlalchemy.util.langhelpers import _T_co
from numpy._core._internal import _T_co
from operator import _T_co
from sqlalchemy.orm._typing import _T_co
from sqlalchemy.sql.roles import _T_co
from psycopg2._range import _T_co
from optype._core._can import _T_co
from asyncio import _T_co
from _asyncio import _T_co
from numpy._typing._nested_sequence import _T_co
from sqlalchemy.util.compat import _T_co
from functools import _T_co
from numpy import _T_co
from sqlalchemy.orm.attributes import _T_co
from dataclasses import _T_co
from optype.copy import _T_co
from numpy.lib._type_check_impl import _T_co
from sqlalchemy.orm.base import _T_co
from optype.numpy._ufunc import _T_co
from optype.numpy._any_array import _T_co
from openpyxl.xml._functions_overloads import _T_co
from sqlalchemy.util._collections import _T_co
from psycopg2._psycopg import _T_co
from scipy.sparse._base import _T_co
from PIL._typing import _T_co
from asyncio.tasks import _T_co
from importlib.metadata._meta import _T_co
from builtins import _T_co
from sqlalchemy.sql.type_api import _T_co
from lxml.etree._iterparse import _T_co
from sqlalchemy.ext.asyncio.base import _T_co
from sqlalchemy.util._concurrency_py3k import _T_co
from anyio._core._contextmanagers import _T_co
from io import _T_co
import _abc
import abc
import collections.abc
import typing
from collections.abc import AsyncIterator, Callable, Generator
from typing import Any, ClassVar as _ClassVar

from _typeshed import Incomplete

class ReversibleProxy(typing.Generic):
    _proxy_objects: _ClassVar[dict] = ...
    __orig_bases__: _ClassVar[tuple] = ...
    __parameters__: _ClassVar[tuple] = ...

class StartableContext(collections.abc.Awaitable, typing.Generic, abc.ABC):
    __orig_bases__: _ClassVar[tuple] = ...
    __parameters__: _ClassVar[tuple] = ...
    __abstractmethods__: _ClassVar[frozenset] = ...
    _abc_impl: _ClassVar[_abc._abc_data] = ...
    def start(self, is_ctxmanager: bool = ...) -> _T_co: ...
    def __await__(self) -> Generator[Any, Any, _T_co]: ...
    def __aenter__(self) -> _T_co: ...
    def __aexit__(self, type_: Any, value: Any, traceback: Any) -> bool | None: ...

class GeneratorStartableContext(StartableContext):
    __orig_bases__: _ClassVar[tuple] = ...
    __parameters__: _ClassVar[tuple] = ...
    __abstractmethods__: _ClassVar[frozenset] = ...
    _abc_impl: _ClassVar[_abc._abc_data] = ...
    gen: Incomplete
    def __init__(self, func: Callable[..., AsyncIterator[_T_co]], args: tuple[Any, ...], kwds: dict[str, Any]) -> None: ...
    def start(self, is_ctxmanager: bool = ...) -> _T_co: ...
    def __aexit__(self, typ: Any, value: Any, traceback: Any) -> bool | None: ...
def asyncstartablecontext(func: Callable[..., AsyncIterator[_T_co]]) -> Callable[..., GeneratorStartableContext[_T_co]]: ...

class ProxyComparable(ReversibleProxy):
    __orig_bases__: _ClassVar[tuple] = ...
    __parameters__: _ClassVar[tuple] = ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
