import threading
from collections.abc import Callable, Hashable, MutableMapping
from logging import Logger
from typing import Any, TypeVar

NONE_ID: int
NO_RECEIVERS: Any
logger: Logger

class Signal:
    receivers: list[Any]
    lock: threading.Lock
    use_caching: bool
    sender_receivers_cache: MutableMapping[Any, Any]
    def __init__(self, use_caching: bool = ...) -> None: ...
    def connect(
        self,
        receiver: Callable,
        sender: object | None = ...,
        weak: bool = ...,
        dispatch_uid: Hashable | None = ...,
    ) -> None: ...
    def disconnect(
        self,
        receiver: Callable | None = ...,
        sender: object | None = ...,
        dispatch_uid: str | None = ...,
    ) -> bool: ...
    def has_listeners(self, sender: Any | None = ...) -> bool: ...
    def send(self, sender: Any, **named: Any) -> list[tuple[Callable, str | None]]: ...
    async def asend(
        self, sender: Any, **named: Any
    ) -> list[tuple[Callable, str | None]]: ...
    def send_robust(
        self, sender: Any, **named: Any
    ) -> list[tuple[Callable, Exception | Any]]: ...
    async def asend_robust(
        self, sender: Any, **named: Any
    ) -> list[tuple[Callable, Exception | Any]]: ...

_F = TypeVar("_F", bound=Callable[..., Any])

def receiver(
    signal: list[Signal] | tuple[Signal, ...] | Signal,
    *,
    sender: object | None = ...,
    weak: bool = ...,
    dispatch_uid: Hashable | None = ...,
    **named: Any,
) -> Callable[[_F], _F]: ...
