from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, ParamSpec, TypeVar

if TYPE_CHECKING:
    ArgsT = ParamSpec("ArgsT")
RetT = TypeVar("RetT")

def trio_test[**ArgsT, RetT](
    fn: Callable[ArgsT, Awaitable[RetT]],
) -> Callable[ArgsT, RetT]: ...
