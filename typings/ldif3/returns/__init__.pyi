from collections.abc import (
    AsyncGenerator,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
)
from typing import Any, ParamSpec, TypeVar, final, overload

from returns.interfaces.specific.future import FutureBased1
from returns.interfaces.specific.future_result import FutureResultBased2
from returns.io import IO, IOResult
from returns.primitives.container import BaseContainer
from returns.primitives.hkt import Kind1, Kind2, SupportsKind1, SupportsKind2
from returns.result import Result

_ValueType_co = TypeVar("_ValueType_co", covariant=True)
_NewValueType = TypeVar("_NewValueType")
_ErrorType_co = TypeVar("_ErrorType_co", covariant=True)
_NewErrorType = TypeVar("_NewErrorType")
_FuncParams = ParamSpec("_FuncParams")
_FirstType = TypeVar("_FirstType")
_SecondType = TypeVar("_SecondType")

async def async_identity[FirstType](instance: _FirstType) -> _FirstType: ...

@final
class Future(
    BaseContainer, SupportsKind1["Future", _ValueType_co], FutureBased1[_ValueType_co]
):
    __slots__ = ...
    _inner_value: Awaitable[_ValueType_co]
    def __init__(self, inner_value: Awaitable[_ValueType_co]) -> None: ...
    def __await__(self) -> Generator[None, None, IO[_ValueType_co]]: ...
    async def awaitable(self) -> IO[_ValueType_co]: ...
    def map(
        self, function: Callable[[_ValueType_co], _NewValueType]
    ) -> Future[_NewValueType]: ...
    def apply(
        self, container: Kind1[Future, Callable[[_ValueType_co], _NewValueType]]
    ) -> Future[_NewValueType]: ...
    def bind(
        self, function: Callable[[_ValueType_co], Kind1[Future, _NewValueType]]
    ) -> Future[_NewValueType]: ...

    bind_future = ...
    def bind_async(
        self,
        function: Callable[[_ValueType_co], Awaitable[Kind1[Future, _NewValueType]]],
    ) -> Future[_NewValueType]: ...

    bind_async_future = ...
    def bind_awaitable(
        self, function: Callable[[_ValueType_co], Awaitable[_NewValueType]]
    ) -> Future[_NewValueType]: ...
    def bind_io(
        self, function: Callable[[_ValueType_co], IO[_NewValueType]]
    ) -> Future[_NewValueType]: ...
    def __aiter__(self) -> AsyncIterator[_ValueType_co]: ...
    @classmethod
    def do(cls, expr: AsyncGenerator[_NewValueType]) -> Future[_NewValueType]: ...
    @classmethod
    def from_value(cls, inner_value: _NewValueType) -> Future[_NewValueType]: ...
    @classmethod
    def from_future(
        cls, inner_value: Future[_NewValueType]
    ) -> Future[_NewValueType]: ...
    @classmethod
    def from_io(cls, inner_value: IO[_NewValueType]) -> Future[_NewValueType]: ...
    @classmethod
    def from_future_result(
        cls, inner_value: FutureResult[_NewValueType, _NewErrorType]
    ) -> Future[Result[_NewValueType, _NewErrorType]]: ...

def future[**FuncParams, FirstType, SecondType, ValueType_co](
    function: Callable[_FuncParams, Coroutine[_FirstType, _SecondType, _ValueType_co]],
) -> Callable[_FuncParams, Future[_ValueType_co]]: ...
def asyncify[**FuncParams, ValueType_co](
    function: Callable[_FuncParams, _ValueType_co],
) -> Callable[_FuncParams, Coroutine[Any, Any, _ValueType_co]]: ...

@final
class FutureResult(
    BaseContainer,
    SupportsKind2["FutureResult", _ValueType_co, _ErrorType_co],
    FutureResultBased2[_ValueType_co, _ErrorType_co],
):
    __slots__ = ...
    _inner_value: Awaitable[Result[_ValueType_co, _ErrorType_co]]
    def __init__(
        self, inner_value: Awaitable[Result[_ValueType_co, _ErrorType_co]]
    ) -> None: ...
    def __await__(
        self,
    ) -> Generator[None, None, IOResult[_ValueType_co, _ErrorType_co]]: ...
    async def awaitable(self) -> IOResult[_ValueType_co, _ErrorType_co]: ...
    def swap(self) -> FutureResult[_ErrorType_co, _ValueType_co]: ...
    def map(
        self, function: Callable[[_ValueType_co], _NewValueType]
    ) -> FutureResult[_NewValueType, _ErrorType_co]: ...
    def apply(
        self,
        container: Kind2[
            FutureResult, Callable[[_ValueType_co], _NewValueType], _ErrorType_co
        ],
    ) -> FutureResult[_NewValueType, _ErrorType_co]: ...
    def bind(
        self,
        function: Callable[
            [_ValueType_co], Kind2[FutureResult, _NewValueType, _ErrorType_co]
        ],
    ) -> FutureResult[_NewValueType, _ErrorType_co]: ...

    bind_future_result = ...
    def bind_async(
        self,
        function: Callable[
            [_ValueType_co],
            Awaitable[Kind2[FutureResult, _NewValueType, _ErrorType_co]],
        ],
    ) -> FutureResult[_NewValueType, _ErrorType_co]: ...

    bind_async_future_result = ...
    def bind_awaitable(
        self, function: Callable[[_ValueType_co], Awaitable[_NewValueType]]
    ) -> FutureResult[_NewValueType, _ErrorType_co]: ...
    def bind_result(
        self, function: Callable[[_ValueType_co], Result[_NewValueType, _ErrorType_co]]
    ) -> FutureResult[_NewValueType, _ErrorType_co]: ...
    def bind_ioresult(
        self,
        function: Callable[[_ValueType_co], IOResult[_NewValueType, _ErrorType_co]],
    ) -> FutureResult[_NewValueType, _ErrorType_co]: ...
    def bind_io(
        self, function: Callable[[_ValueType_co], IO[_NewValueType]]
    ) -> FutureResult[_NewValueType, _ErrorType_co]: ...
    def bind_future(
        self, function: Callable[[_ValueType_co], Future[_NewValueType]]
    ) -> FutureResult[_NewValueType, _ErrorType_co]: ...
    def bind_async_future(
        self, function: Callable[[_ValueType_co], Awaitable[Future[_NewValueType]]]
    ) -> FutureResult[_NewValueType, _ErrorType_co]: ...
    def alt(
        self, function: Callable[[_ErrorType_co], _NewErrorType]
    ) -> FutureResult[_ValueType_co, _NewErrorType]: ...
    def lash(
        self,
        function: Callable[
            [_ErrorType_co], Kind2[FutureResult, _ValueType_co, _NewErrorType]
        ],
    ) -> FutureResult[_ValueType_co, _NewErrorType]: ...
    def compose_result(
        self,
        function: Callable[
            [Result[_ValueType_co, _ErrorType_co]],
            Kind2[FutureResult, _NewValueType, _ErrorType_co],
        ],
    ) -> FutureResult[_NewValueType, _ErrorType_co]: ...
    def __aiter__(self) -> AsyncIterator[_ValueType_co]: ...
    @classmethod
    def do(
        cls, expr: AsyncGenerator[_NewValueType]
    ) -> FutureResult[_NewValueType, _NewErrorType]: ...
    @classmethod
    def from_typecast(
        cls, inner_value: Future[Result[_NewValueType, _NewErrorType]]
    ) -> FutureResult[_NewValueType, _NewErrorType]: ...
    @classmethod
    def from_future(
        cls, inner_value: Future[_NewValueType]
    ) -> FutureResult[_NewValueType, Any]: ...
    @classmethod
    def from_failed_future(
        cls, inner_value: Future[_NewErrorType]
    ) -> FutureResult[Any, _NewErrorType]: ...
    @classmethod
    def from_future_result(
        cls, inner_value: FutureResult[_NewValueType, _NewErrorType]
    ) -> FutureResult[_NewValueType, _NewErrorType]: ...
    @classmethod
    def from_io(
        cls, inner_value: IO[_NewValueType]
    ) -> FutureResult[_NewValueType, Any]: ...
    @classmethod
    def from_failed_io(
        cls, inner_value: IO[_NewErrorType]
    ) -> FutureResult[Any, _NewErrorType]: ...
    @classmethod
    def from_ioresult(
        cls, inner_value: IOResult[_NewValueType, _NewErrorType]
    ) -> FutureResult[_NewValueType, _NewErrorType]: ...
    @classmethod
    def from_result(
        cls, inner_value: Result[_NewValueType, _NewErrorType]
    ) -> FutureResult[_NewValueType, _NewErrorType]: ...
    @classmethod
    def from_value(
        cls, inner_value: _NewValueType
    ) -> FutureResult[_NewValueType, Any]: ...
    @classmethod
    def from_failure(
        cls, inner_value: _NewErrorType
    ) -> FutureResult[Any, _NewErrorType]: ...

def FutureSuccess[NewValueType](
    inner_value: _NewValueType,
) -> FutureResult[_NewValueType, Any]: ...
def FutureFailure[NewErrorType](
    inner_value: _NewErrorType,
) -> FutureResult[Any, _NewErrorType]: ...

type FutureResultE[_ValueType_co] = FutureResult[_ValueType_co, Exception]
_ExceptionType = TypeVar("_ExceptionType", bound=Exception)

@overload
def future_safe[**FuncParams, FirstType, SecondType, ValueType_co](
    exceptions: Callable[
        _FuncParams, Coroutine[_FirstType, _SecondType, _ValueType_co]
    ],
    /,
) -> Callable[_FuncParams, FutureResultE[_ValueType_co]]: ...
@overload
def future_safe[ExceptionType: Exception](
    exceptions: tuple[type[_ExceptionType], ...],
) -> Callable[
    [Callable[_FuncParams, Coroutine[_FirstType, _SecondType, _ValueType_co]]],
    Callable[_FuncParams, FutureResult[_ValueType_co, _ExceptionType]],
]: ...
def future_safe[
    **FuncParams,
    FirstType,
    SecondType,
    ValueType_co,
    ExceptionType: Exception,
](
    exceptions: (
        Callable[_FuncParams, Coroutine[_FirstType, _SecondType, _ValueType_co]]
        | tuple[type[_ExceptionType], ...]
    ),
) -> (
    Callable[_FuncParams, FutureResultE[_ValueType_co]]
    | Callable[
        [Callable[_FuncParams, Coroutine[_FirstType, _SecondType, _ValueType_co]]],
        Callable[_FuncParams, FutureResult[_ValueType_co, _ExceptionType]],
    ]
): ...
