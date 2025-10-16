import ssl

from .._backends.base import AsyncNetworkBackend
from .._models import URL, Origin, Request, Response
from .connection_pool import AsyncConnectionPool
from .interfaces import AsyncConnectionInterface

logger = ...
AUTH_METHODS = ...
REPLY_CODES = ...

class AsyncSOCKSProxy(AsyncConnectionPool):
    def __init__(
        self,
        proxy_url: URL | bytes | str,
        proxy_auth: tuple[bytes | str, bytes | str] | None = ...,
        ssl_context: ssl.SSLContext | None = ...,
        max_connections: int | None = ...,
        max_keepalive_connections: int | None = ...,
        keepalive_expiry: float | None = ...,
        http1: bool = ...,
        http2: bool = ...,
        retries: int = ...,
        network_backend: AsyncNetworkBackend | None = ...,
    ) -> None: ...
    def create_connection(self, origin: Origin) -> AsyncConnectionInterface: ...

class AsyncSocks5Connection(AsyncConnectionInterface):
    def __init__(
        self,
        proxy_origin: Origin,
        remote_origin: Origin,
        proxy_auth: tuple[bytes, bytes] | None = ...,
        ssl_context: ssl.SSLContext | None = ...,
        keepalive_expiry: float | None = ...,
        http1: bool = ...,
        http2: bool = ...,
        network_backend: AsyncNetworkBackend | None = ...,
    ) -> None: ...
    async def handle_async_request(self, request: Request) -> Response: ...
    def can_handle_request(self, origin: Origin) -> bool: ...
    async def aclose(self) -> None: ...
    def is_available(self) -> bool: ...
    def has_expired(self) -> bool: ...
    def is_idle(self) -> bool: ...
    def is_closed(self) -> bool: ...
    def info(self) -> str: ...
