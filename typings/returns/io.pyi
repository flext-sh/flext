"""Type stubs for returns.io - Generated for pyrefly compatibility."""

from typing import Any, Generic, TypeVar

T_co = TypeVar("T_co", covariant=True)
E_co = TypeVar("E_co", covariant=True)


class IOResult(Generic[T_co, E_co]):
    """IO Result base type - union of IOSuccess and IOFailure."""

    def unwrap(self) -> T_co: ...
    def failure(self) -> E_co: ...


class IOSuccess(IOResult[T_co, Any]):
    """IO Success wrapper."""

    def __init__(self, inner_value: T_co) -> None:
        """IOSuccess constructor."""

    @property
    def value(self) -> T_co: ...

    def unwrap(self) -> T_co: ...

    def failure(self) -> None: ...


class IOFailure(IOResult[Any, E_co]):
    """IO Failure wrapper."""

    def __init__(self, inner_value: E_co) -> None:
        """IOFailure constructor."""

    @property
    def value(self) -> E_co: ...

    def unwrap(self) -> E_co: ...

    def failure(self) -> E_co: ...


class IO(Generic[T_co]):
    """IO monad wrapper."""

    def __init__(self, inner_value: T_co) -> None:
        """IO constructor."""

    @property
    def value(self) -> T_co: ...
