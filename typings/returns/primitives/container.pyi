from abc import ABC
from typing import Any, TypeVar

from returns.interfaces.equable import Equable
from returns.primitives.hkt import Kind1
from returns.primitives.types import Immutable

_EqualType = TypeVar("_EqualType", bound=Equable)

class BaseContainer(Immutable, ABC):
    """Utility class to provide all needed magic methods to the context."""

    __slots__ = ("_inner_value",)
    _inner_value: Any

    def __init__(self, inner_value: Any) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

def container_equality(
    self: Kind1[_EqualType, Any],
    other: Kind1[_EqualType, Any],
) -> bool: ...
