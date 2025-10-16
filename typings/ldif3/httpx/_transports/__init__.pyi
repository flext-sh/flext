import typing

from _typeshed.wsgi import WSGIApplication

from .._models import Request, Response
from .._types import SyncByteStream
from .base import BaseTransport

if typing.TYPE_CHECKING: ...
__all__ = ["WSGITransport"]

class WSGIByteStream(SyncByteStream):
    def __init__(self, result: typing.Iterable[bytes]) -> None: ...
    def __iter__(self) -> typing.Iterator[bytes]: ...
    def close(self) -> None: ...

class WSGITransport(BaseTransport):
    def __init__(
        self,
        app: WSGIApplication,
        raise_app_exceptions: bool = ...,
        script_name: str = ...,
        remote_addr: str = ...,
        wsgi_errors: typing.TextIO | None = ...,
    ) -> None: ...
    def handle_request(self, request: Request) -> Response: ...
