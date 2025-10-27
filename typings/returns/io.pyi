"""Type stubs for returns.io module with complete IO interface.

PEP 561 compliant type stubs for the returns library IO types.
"""

from typing import Any, Callable, TypeVar

from returns.result import Failure, Success

_ValueType = TypeVar("_ValueType")
_NewValueType = TypeVar("_NewValueType")
_ErrorType = TypeVar("_ErrorType")
_NewErrorType = TypeVar("_NewErrorType")

class IO[_ValueType]:
    """IO container that represents computation with IO side effects.

    This is the base IO type for pure IO operations without error handling.
    """

    def __init__(self, inner_value: _ValueType) -> None:
        """Public constructor for IO type."""
        ...

    def map(
        self, function: Callable[[_ValueType], _NewValueType]
    ) -> IO[_NewValueType]:
        """Map a function over the success value."""
        ...

    def bind(
        self, function: Callable[[_ValueType], IO[_NewValueType]]
    ) -> IO[_NewValueType]:
        """Monadic bind operation."""
        ...

class IOResult[_ValueType, _ErrorType]:
    """IO container with error handling capabilities.

    Similar to Result but for IO operations. Has both map() and alt() methods.
    IOSuccess and IOFailure are concrete implementations of IOResult.
    """

    def map(
        self, function: Callable[[_ValueType], _NewValueType]
    ) -> IOResult[_NewValueType, _ErrorType]:
        """Map a function over the success value."""
        ...

    def alt(
        self, function: Callable[[_ErrorType], _NewErrorType]
    ) -> IOResult[_ValueType, _NewErrorType]:
        """Map a function over the failure value."""
        ...

    def bind(
        self, function: Callable[[_ValueType], IOResult[_NewValueType, _ErrorType]]
    ) -> IOResult[_NewValueType, _ErrorType]:
        """Monadic bind operation."""
        ...

class IOSuccess[_ValueType](IOResult[_ValueType, Any]):
    """IO container representing successful computation.

    Inherits from IOResult[T, Any] where error type is Any.
    """

    def __init__(self, value: _ValueType) -> None: ...

class IOFailure[_ErrorType](IOResult[Any, _ErrorType]):
    """IO container representing failed computation.

    Inherits from IOResult[Any, E] where value type is Any.
    """

    def __init__(self, error: _ErrorType) -> None: ...

__all__ = ["IO", "IOResult", "IOSuccess", "IOFailure"]
