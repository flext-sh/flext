import logging
import types
import typing

from ._models import Request

class Trace:
    def __init__(
        self,
        name: str,
        logger: logging.Logger,
        request: Request | None = ...,
        kwargs: dict[str, typing.Any] | None = ...,
    ) -> None: ...
    def trace(self, name: str, info: dict[str, typing.Any]) -> None: ...
    def __enter__(self) -> typing.Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None = ...,
        exc_value: BaseException | None = ...,
        traceback: types.TracebackType | None = ...,
    ) -> None: ...
    async def atrace(self, name: str, info: dict[str, typing.Any]) -> None: ...
    async def __aenter__(self) -> typing.Self: ...
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = ...,
        exc_value: BaseException | None = ...,
        traceback: types.TracebackType | None = ...,
    ) -> None: ...
