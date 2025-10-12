from collections.abc import Callable
from typing import TypeVar

from flext_core import FlextCore

_T = TypeVar("_T")

class BenchmarkFixture:
    group: str
    name: str | None
    extra_info: FlextCore.Types.Dict

    def __call__(
        self,
        func: Callable[[], _T],
        /,
        *args: object,
        **kwargs: object,
    ) -> _T: ...
    def pedantic(
        self,
        func: Callable[[], _T],
        /,
        *args: object,
        **kwargs: object,
    ) -> _T: ...
    def timer(
        self, func: Callable[[], _T], /, *args: object, **kwargs: object
    ) -> _T: ...
