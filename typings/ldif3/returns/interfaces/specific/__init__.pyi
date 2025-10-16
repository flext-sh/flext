from abc import abstractmethod
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, ClassVar, TypeVar, final

from returns.context import Reader, ReaderResult
from returns.interfaces.specific import reader, result
from returns.primitives.hkt import KindN
from returns.primitives.laws import Law, Lawful, LawSpecDef, law_definition

if TYPE_CHECKING: ...
_FirstType = TypeVar("_FirstType")
_SecondType = TypeVar("_SecondType")
_ThirdType = TypeVar("_ThirdType")
_UpdatedType = TypeVar("_UpdatedType")
_ValueType = TypeVar("_ValueType")
_ErrorType = TypeVar("_ErrorType")
_EnvType = TypeVar("_EnvType")
_ReaderResultLikeType = TypeVar("_ReaderResultLikeType", bound=ReaderResultLikeN)

class ReaderResultLikeN(
    reader.ReaderLike3[_FirstType, _SecondType, _ThirdType],
    result.ResultLikeN[_FirstType, _SecondType, _ThirdType],
):
    __slots__ = ...
    @abstractmethod
    def bind_context_result(
        self: _ReaderResultLikeType,
        function: Callable[
            [_FirstType], ReaderResult[_UpdatedType, _SecondType, _ThirdType]
        ],
    ) -> KindN[_ReaderResultLikeType, _UpdatedType, _SecondType, _ThirdType]: ...
    @classmethod
    @abstractmethod
    def from_failed_context(
        cls: type[_ReaderResultLikeType], inner_value: Reader[_ErrorType, _EnvType]
    ) -> KindN[_ReaderResultLikeType, _FirstType, _ErrorType, _EnvType]: ...
    @classmethod
    @abstractmethod
    def from_result_context(
        cls: type[_ReaderResultLikeType],
        inner_value: ReaderResult[_ValueType, _ErrorType, _EnvType],
    ) -> KindN[_ReaderResultLikeType, _ValueType, _ErrorType, _EnvType]: ...

type ReaderResultLike3[_FirstType, _SecondType, _ThirdType] = ReaderResultLikeN[
    _FirstType, _SecondType, _ThirdType
]

@final
class _LawSpec(LawSpecDef):
    __slots__ = ...
    @law_definition
    def purity_law(
        self: ReaderResultBasedN[_FirstType, _SecondType, _ThirdType], env: _ThirdType
    ) -> None: ...
    @law_definition
    def asking_law(
        self: ReaderResultBasedN[_FirstType, _SecondType, _ThirdType], env: _ThirdType
    ) -> None: ...

class ReaderResultBasedN(
    ReaderResultLikeN[_FirstType, _SecondType, _ThirdType],
    reader.CallableReader3[
        _FirstType,
        _SecondType,
        _ThirdType,
        "Result[_FirstType, _SecondType]",
        _ThirdType,
    ],
    Lawful[...],
):
    __slots__ = ...
    _laws: ClassVar[Sequence[Law]] = ...

type ReaderResultBased3[_FirstType, _SecondType, _ThirdType] = ReaderResultBasedN[
    _FirstType, _SecondType, _ThirdType
]
