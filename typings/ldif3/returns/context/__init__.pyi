from collections.abc import Callable
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar, final

from returns.context import NoDeps
from returns.context.requires_context import RequiresContext
from returns.interfaces.specific import reader_result
from returns.primitives.container import BaseContainer
from returns.primitives.hkt import Kind3, SupportsKind3
from returns.result import Result

if TYPE_CHECKING: ...
_EnvType_contra = TypeVar("_EnvType_contra", contravariant=True)
_NewEnvType = TypeVar("_NewEnvType")
_ValueType_co = TypeVar("_ValueType_co", covariant=True)
_NewValueType = TypeVar("_NewValueType")
_ErrorType_co = TypeVar("_ErrorType_co", covariant=True)
_NewErrorType = TypeVar("_NewErrorType")
_FirstType = TypeVar("_FirstType")

@final
class RequiresContextResult(
    BaseContainer,
    SupportsKind3[
        "RequiresContextResult", _ValueType_co, _ErrorType_co, _EnvType_contra
    ],
    reader_result.ReaderResultBasedN[_ValueType_co, _ErrorType_co, _EnvType_contra],
):
    __slots__ = ...
    _inner_value: Callable[[_EnvType_contra], Result[_ValueType_co, _ErrorType_co]]
    no_args: ClassVar[NoDeps] = ...
    def __init__(
        self,
        inner_value: Callable[[_EnvType_contra], Result[_ValueType_co, _ErrorType_co]],
    ) -> None: ...
    def __call__(
        self, deps: _EnvType_contra
    ) -> Result[_ValueType_co, _ErrorType_co]: ...
    def swap(
        self,
    ) -> RequiresContextResult[_ErrorType_co, _ValueType_co, _EnvType_contra]: ...
    def map(
        self, function: Callable[[_ValueType_co], _NewValueType]
    ) -> RequiresContextResult[_NewValueType, _ErrorType_co, _EnvType_contra]: ...
    def apply(
        self,
        container: Kind3[
            RequiresContextResult,
            Callable[[_ValueType_co], _NewValueType],
            _ErrorType_co,
            _EnvType_contra,
        ],
    ) -> RequiresContextResult[_NewValueType, _ErrorType_co, _EnvType_contra]: ...
    def bind(
        self,
        function: Callable[
            [_ValueType_co],
            Kind3[RequiresContextResult, _NewValueType, _ErrorType_co, _EnvType_contra],
        ],
    ) -> RequiresContextResult[_NewValueType, _ErrorType_co, _EnvType_contra]: ...

    bind_context_result = ...
    def bind_result(
        self, function: Callable[[_ValueType_co], Result[_NewValueType, _ErrorType_co]]
    ) -> RequiresContextResult[_NewValueType, _ErrorType_co, _EnvType_contra]: ...
    def bind_context(
        self,
        function: Callable[
            [_ValueType_co], RequiresContext[_NewValueType, _EnvType_contra]
        ],
    ) -> RequiresContextResult[_NewValueType, _ErrorType_co, _EnvType_contra]: ...
    def alt(
        self, function: Callable[[_ErrorType_co], _NewErrorType]
    ) -> RequiresContextResult[_ValueType_co, _NewErrorType, _EnvType_contra]: ...
    def lash(
        self,
        function: Callable[
            [_ErrorType_co],
            Kind3[RequiresContextResult, _ValueType_co, _NewErrorType, _EnvType_contra],
        ],
    ) -> RequiresContextResult[_ValueType_co, _NewErrorType, _EnvType_contra]: ...
    def modify_env(
        self, function: Callable[[_NewEnvType], _EnvType_contra]
    ) -> RequiresContextResult[_ValueType_co, _ErrorType_co, _NewEnvType]: ...
    @classmethod
    def ask(
        cls,
    ) -> RequiresContextResult[_EnvType_contra, _ErrorType_co, _EnvType_contra]: ...
    @classmethod
    def from_result(
        cls, inner_value: Result[_NewValueType, _NewErrorType]
    ) -> RequiresContextResult[_NewValueType, _NewErrorType, NoDeps]: ...
    @classmethod
    def from_typecast(
        cls,
        inner_value: RequiresContext[
            Result[_NewValueType, _NewErrorType], _EnvType_contra
        ],
    ) -> RequiresContextResult[_NewValueType, _NewErrorType, _EnvType_contra]: ...
    @classmethod
    def from_context(
        cls, inner_value: RequiresContext[_NewValueType, _NewEnvType]
    ) -> RequiresContextResult[_NewValueType, Any, _NewEnvType]: ...
    @classmethod
    def from_failed_context(
        cls, inner_value: RequiresContext[_NewValueType, _NewEnvType]
    ) -> RequiresContextResult[Any, _NewValueType, _NewEnvType]: ...
    @classmethod
    def from_result_context(
        cls,
        inner_value: RequiresContextResult[_NewValueType, _NewErrorType, _NewEnvType],
    ) -> RequiresContextResult[_NewValueType, _NewErrorType, _NewEnvType]: ...
    @classmethod
    def from_value(
        cls, inner_value: _FirstType
    ) -> RequiresContextResult[_FirstType, Any, NoDeps]: ...
    @classmethod
    def from_failure(
        cls, inner_value: _FirstType
    ) -> RequiresContextResult[Any, _FirstType, NoDeps]: ...

type RequiresContextResultE[_ValueType_co, _EnvType_contra] = RequiresContextResult[
    _ValueType_co, Exception, _EnvType_contra
]
type ReaderResult = RequiresContextResult
type ReaderResultE[_ValueType_co, _EnvType_contra] = RequiresContextResult[
    _ValueType_co, Exception, _EnvType_contra
]
