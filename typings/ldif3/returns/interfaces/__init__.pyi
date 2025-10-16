from abc import abstractmethod
from collections.abc import Callable, Sequence
from typing import ClassVar, Never, TypeVar, final

from returns.primitives.hkt import KindN
from returns.primitives.laws import Law, Lawful, LawSpecDef, law_definition

_FirstType = TypeVar("_FirstType")
_SecondType = TypeVar("_SecondType")
_ThirdType = TypeVar("_ThirdType")
_UpdatedType = TypeVar("_UpdatedType")
_AltableType = TypeVar("_AltableType", bound=AltableN)
_NewType1 = TypeVar("_NewType1")
_NewType2 = TypeVar("_NewType2")

@final
class _LawSpec(LawSpecDef):
    __slots__ = ...
    @law_definition
    def identity_law(self: AltableN[_FirstType, _SecondType, _ThirdType]) -> None: ...
    @law_definition
    def associative_law(
        self: AltableN[_FirstType, _SecondType, _ThirdType],
        first: Callable[[_SecondType], _NewType1],
        second: Callable[[_NewType1], _NewType2],
    ) -> None: ...

class AltableN[FirstType, SecondType, ThirdType](
    Lawful["AltableN[_FirstType, _SecondType, _ThirdType]"]
):
    __slots__ = ...
    _laws: ClassVar[Sequence[Law]] = ...
    @abstractmethod
    def alt(
        self: _AltableType, function: Callable[[_SecondType], _UpdatedType]
    ) -> KindN[_AltableType, _FirstType, _UpdatedType, _ThirdType]: ...

type Altable2[_FirstType, _SecondType] = AltableN[_FirstType, _SecondType, Never]
type Altable3[_FirstType, _SecondType, _ThirdType] = AltableN[
    _FirstType, _SecondType, _ThirdType
]
