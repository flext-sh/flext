"""Type stubs for returns.primitives.hkt.

Based on: dry-python/returns v0.24.x
Source: returns/primitives/hkt.py
"""

from collections.abc import Callable
from typing import Any, Generic, Protocol, TypeVar

from typing_extensions import Never, TypeVarTuple, Unpack

_InstanceType_co = TypeVar("_InstanceType_co", covariant=True)
_TypeArgType1_co = TypeVar("_TypeArgType1_co", covariant=True)
_TypeArgType2_co = TypeVar("_TypeArgType2_co", covariant=True)
_TypeArgType3_co = TypeVar("_TypeArgType3_co", covariant=True)

_FunctionDefType_co = TypeVar("_FunctionDefType_co", bound=Callable, covariant=True)
_FunctionType = TypeVar("_FunctionType", bound=Callable)
_UpdatedType = TypeVar("_UpdatedType")
_TypeVars = TypeVarTuple("_TypeVars")

class KindN(Generic[_InstanceType_co, Unpack[_TypeVars]]):
    """Emulation support for Higher Kinded Types."""

    __slots__ = ()

Kind1 = KindN[_InstanceType_co, _TypeArgType1_co, Any, Any]
Kind2 = KindN[_InstanceType_co, _TypeArgType1_co, _TypeArgType2_co, Any]
Kind3 = KindN[_InstanceType_co, _TypeArgType1_co, _TypeArgType2_co, _TypeArgType3_co]

class SupportsKindN(KindN[_InstanceType_co, Unpack[_TypeVars]]):
    """Base class for kinded containers."""

    __slots__ = ()

SupportsKind1 = SupportsKindN[_InstanceType_co, _TypeArgType1_co, Never, Never]
SupportsKind2 = SupportsKindN[
    _InstanceType_co, _TypeArgType1_co, _TypeArgType2_co, Never
]
SupportsKind3 = SupportsKindN[
    _InstanceType_co, _TypeArgType1_co, _TypeArgType2_co, _TypeArgType3_co
]

def dekind(
    kind: KindN[_InstanceType_co, _TypeArgType1_co, _TypeArgType2_co, _TypeArgType3_co],
) -> _InstanceType_co: ...

class Kinded(Protocol[_FunctionDefType_co]):
    """Protocol that tracks kinded functions calls."""

    __slots__ = ()

    __call__: _FunctionDefType_co

    def __get__(
        self, instance: _UpdatedType, type_: type
    ) -> Callable[..., _UpdatedType]: ...

def kinded(function: _FunctionType) -> Kinded[_FunctionType]: ...
