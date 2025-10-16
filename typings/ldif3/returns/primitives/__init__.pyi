from collections.abc import Awaitable, Callable, Generator
from typing import NewType, ParamSpec, TypeVar, final

_ValueType = TypeVar("_ValueType")
_AwaitableT = TypeVar("_AwaitableT", bound=Awaitable)
_Ps = ParamSpec("_Ps")
_Sentinel = NewType("_Sentinel", object)
_sentinel: _Sentinel = ...

@final
class ReAwaitable:
    __slots__ = ...
    def __init__(self, coro: Awaitable[_ValueType]) -> None: ...
    def __await__(self) -> Generator[None, None, _ValueType]: ...

def reawaitable[**Ps, AwaitableT: Awaitable](
    coro: Callable[_Ps, _AwaitableT],
) -> Callable[_Ps, _AwaitableT]: ...
