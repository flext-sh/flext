import ssl

from .._backends.base import NetworkBackend
from .._models import URL, Origin, Request, Response
from .connection_pool import ConnectionPool
from .interfaces import ConnectionInterface

logger = ...
AUTH_METHODS = ...
REPLY_CODES = ...

class SOCKSProxy(ConnectionPool):
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
        network_backend: NetworkBackend | None = ...,
    ) -> None: ...
    def create_connection(self, origin: Origin) -> ConnectionInterface: ...

class Socks5Connection(ConnectionInterface):
    def __init__(
        self,
        proxy_origin: Origin,
        remote_origin: Origin,
        proxy_auth: tuple[bytes, bytes] | None = ...,
        ssl_context: ssl.SSLContext | None = ...,
        keepalive_expiry: float | None = ...,
        http1: bool = ...,
        http2: bool = ...,
        network_backend: NetworkBackend | None = ...,
    ) -> None: ...
    def handle_request(self, request: Request) -> Response: ...
    def can_handle_request(self, origin: Origin) -> bool: ...
    def close(self) -> None: ...
    def is_available(self) -> bool: ...
    def has_expired(self) -> bool: ...
    def is_idle(self) -> bool: ...
    def is_closed(self) -> bool: ...
    def info(self) -> str: ...
