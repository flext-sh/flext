import typing

from .base import SOCKET_OPTION, AsyncNetworkBackend, AsyncNetworkStream

class AutoBackend(AsyncNetworkBackend):
    async def connect_tcp(
        self,
        host: str,
        port: int,
        timeout: float | None = ...,
        local_address: str | None = ...,
        socket_options: typing.Iterable[SOCKET_OPTION] | None = ...,
    ) -> AsyncNetworkStream: ...
    async def connect_unix_socket(
        self,
        path: str,
        timeout: float | None = ...,
        socket_options: typing.Iterable[SOCKET_OPTION] | None = ...,
    ) -> AsyncNetworkStream: ...
    async def sleep(self, seconds: float) -> None: ...
