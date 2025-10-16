from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, TypeVar

from returns.context import RequiresContextFutureResult
from returns.primitives.hkt import Kind3
from returns.result import Result

if TYPE_CHECKING: ...
_ValueType_co = TypeVar("_ValueType_co", covariant=True)
_NewValueType = TypeVar("_NewValueType")
_ErrorType_co = TypeVar("_ErrorType_co", covariant=True)
_EnvType = TypeVar("_EnvType")

async def async_bind_async(
    function: Callable[
        [_ValueType_co],
        Awaitable[
            Kind3[RequiresContextFutureResult, _NewValueType, _ErrorType_co, _EnvType],
        ],
    ],
    container: RequiresContextFutureResult[_ValueType_co, _ErrorType_co, _EnvType],
    deps: _EnvType,
) -> Result[_NewValueType, _ErrorType_co]: ...
async def async_compose_result(
    function: Callable[
        [Result[_ValueType_co, _ErrorType_co]],
        Kind3[RequiresContextFutureResult, _NewValueType, _ErrorType_co, _EnvType],
    ],
    container: RequiresContextFutureResult[_ValueType_co, _ErrorType_co, _EnvType],
    deps: _EnvType,
) -> Result[_NewValueType, _ErrorType_co]: ...
