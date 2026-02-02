"""Type stubs for returns.result - Generated for pyrefly compatibility."""

from typing import Any, Generic, TypeVar

# TypeVars matching returns library conventions
_ValueType_co = TypeVar("_ValueType_co", covariant=True)
_ErrorType_co = TypeVar("_ErrorType_co", covariant=True)
_NewValueType = TypeVar("_NewValueType")

class Result(Generic[_ValueType_co, _ErrorType_co]):
    """Result base type - union of Success and Failure."""

    def unwrap(self) -> _ValueType_co: ...
    def failure(self) -> _ErrorType_co: ...


class Success(Result[_ValueType_co, Any]):
    """Success result wrapper."""

    def __init__(self, inner_value: _ValueType_co) -> None:
        """Success constructor."""

    @property
    def value(self) -> _ValueType_co: ...

    def unwrap(self) -> _ValueType_co: ...

    def failure(self) -> None: ...


class Failure(Result[Any, _ErrorType_co]):
    """Failure result wrapper."""

    def __init__(self, inner_value: _ErrorType_co) -> None:
        """Failure constructor."""

    @property
    def value(self) -> _ErrorType_co: ...

    def unwrap(self) -> _ErrorType_co: ...

    def failure(self) -> _ErrorType_co: ...
