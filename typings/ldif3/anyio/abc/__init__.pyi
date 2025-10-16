import types
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Callable, Coroutine, Iterable
from typing import Any, Self, TypeVar

_T = TypeVar("_T")

class TestRunner(ABC):
    def __enter__(self) -> Self: ...
    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> bool | None: ...
    @abstractmethod
    def run_asyncgen_fixture(
        self,
        fixture_func: Callable[..., AsyncGenerator[_T, Any]],
        kwargs: dict[str, Any],
    ) -> Iterable[_T]: ...
    @abstractmethod
    def run_fixture(
        self,
        fixture_func: Callable[..., Coroutine[Any, Any, _T]],
        kwargs: dict[str, Any],
    ) -> _T: ...
    @abstractmethod
    def run_test(
        self, test_func: Callable[..., Coroutine[Any, Any, Any]], kwargs: dict[str, Any]
    ) -> None: ...
