import math
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import tzinfo
from types import EllipsisType
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
    Protocol,
    Self,
    SupportsFloat,
    SupportsIndex,
    TypeVar,
    runtime_checkable,
)

from typing_extensions import DocInfo, doc

KW_ONLY = ...
SLOTS = ...
__all__ = (
    "BaseMetadata",
    "DocInfo",
    "Ge",
    "GroupedMetadata",
    "Gt",
    "Interval",
    "IsDigits",
    "IsFinite",
    "IsInfinite",
    "IsNan",
    "IsNotFinite",
    "IsNotInfinite",
    "IsNotNan",
    "Le",
    "Len",
    "LowerCase",
    "Lt",
    "MaxLen",
    "MinLen",
    "MultipleOf",
    "Predicate",
    "Timezone",
    "UpperCase",
    "__version__",
    "doc",
)
__version__ = ...
T = TypeVar("T")

class SupportsGt(Protocol):
    def __gt__(self, __other: Self) -> bool: ...

class SupportsGe(Protocol):
    def __ge__(self, __other: Self) -> bool: ...

class SupportsLt(Protocol):
    def __lt__(self, __other: Self) -> bool: ...

class SupportsLe(Protocol):
    def __le__(self, __other: Self) -> bool: ...

class SupportsMod(Protocol):
    def __mod__(self, __other: Self) -> Self: ...

class SupportsDiv(Protocol):
    def __div__(self, __other: Self) -> Self: ...

class BaseMetadata:
    __slots__ = ...

@dataclass(frozen=True, **SLOTS)
class Gt(BaseMetadata):
    gt: SupportsGt

@dataclass(frozen=True, **SLOTS)
class Ge(BaseMetadata):
    ge: SupportsGe

@dataclass(frozen=True, **SLOTS)
class Lt(BaseMetadata):
    lt: SupportsLt

@dataclass(frozen=True, **SLOTS)
class Le(BaseMetadata):
    le: SupportsLe

@runtime_checkable
class GroupedMetadata(Protocol):
    @property
    def __is_annotated_types_grouped_metadata__(self) -> Literal[True]: ...
    def __iter__(self) -> Iterator[object]: ...

    if not TYPE_CHECKING: ...

@dataclass(frozen=True, **KW_ONLY, **SLOTS)
class Interval(GroupedMetadata):
    gt: SupportsGt | None = ...
    ge: SupportsGe | None = ...
    lt: SupportsLt | None = ...
    le: SupportsLe | None = ...
    def __iter__(self) -> Iterator[BaseMetadata]: ...

@dataclass(frozen=True, **SLOTS)
class MultipleOf(BaseMetadata):
    multiple_of: SupportsDiv | SupportsMod

@dataclass(frozen=True, **SLOTS)
class MinLen(BaseMetadata):
    min_length: Annotated[int, Ge(0)]

@dataclass(frozen=True, **SLOTS)
class MaxLen(BaseMetadata):
    max_length: Annotated[int, Ge(0)]

@dataclass(frozen=True, **SLOTS)
class Len(GroupedMetadata):
    min_length: Annotated[int, Ge(0)] = ...
    max_length: Annotated[int, Ge(0)] | None = ...
    def __iter__(self) -> Iterator[BaseMetadata]: ...

@dataclass(frozen=True, **SLOTS)
class Timezone(BaseMetadata):
    tz: str | tzinfo | EllipsisType | None

@dataclass(frozen=True, **SLOTS)
class Unit(BaseMetadata):
    unit: str

@dataclass(frozen=True, **SLOTS)
class Predicate(BaseMetadata):
    func: Callable[[Any], bool]

@dataclass
class Not:
    func: Callable[[Any], bool]
    def __call__(self, __v: Any) -> bool: ...

type LowerCase[_StrType: str] = Annotated[_StrType, Predicate(str.islower)]
type UpperCase[_StrType: str] = Annotated[_StrType, Predicate(str.isupper)]
type IsDigit[_StrType: str] = Annotated[_StrType, Predicate(str.isdigit)]
IsDigits = IsDigit
type IsAscii[_StrType: str] = Annotated[_StrType, Predicate(str.isascii)]
type IsFinite[_NumericType: SupportsFloat | SupportsIndex] = Annotated[
    _NumericType, Predicate(math.isfinite)
]
type IsNotFinite[_NumericType: SupportsFloat | SupportsIndex] = Annotated[
    _NumericType, Predicate(Not(math.isfinite))
]
type IsNan[_NumericType: SupportsFloat | SupportsIndex] = Annotated[
    _NumericType, Predicate(math.isnan)
]
type IsNotNan[_NumericType: SupportsFloat | SupportsIndex] = Annotated[
    _NumericType, Predicate(Not(math.isnan))
]
type IsInfinite[_NumericType: SupportsFloat | SupportsIndex] = Annotated[
    _NumericType, Predicate(math.isinf)
]
type IsNotInfinite[_NumericType: SupportsFloat | SupportsIndex] = Annotated[
    _NumericType, Predicate(Not(math.isinf))
]
