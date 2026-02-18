"""Type stubs for returns.maybe - Generated for pyrefly compatibility."""

from typing import Any, Generic, TypeVar

T_co = TypeVar("T_co", covariant=True)


class Maybe(Generic[T_co]):
    """Maybe base type - union of Some and Nothing."""

    def unwrap(self) -> T_co: ...


class Some(Maybe[T_co]):
    """Some value wrapper."""

    def __init__(self, inner_value: T_co) -> None:
        """Some constructor."""

    @property
    def value(self) -> T_co: ...

    def unwrap(self) -> T_co: ...


class _Nothing(Maybe[Any]):
    """Nothing/None value wrapper - singleton type."""

    @property
    def value(self) -> None: ...

    def unwrap(self) -> None: ...


Nothing: _Nothing
