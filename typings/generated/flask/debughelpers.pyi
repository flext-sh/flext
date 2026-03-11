from flask.sansio.scaffold import Scaffold
from h11 import Request
from flask import Request
from typings.generated.starlette.requests import Request
from werkzeug.sansio.request import Request
from werkzeug import Request
from fastapi.requests import Request
from websockets import Request
from httpcore import Request
from requests import Request
from requests.models import Request
from typings.generated.flask.wrappers import Request
from flask.wrappers import Request
from mcp.types import Request
from aiohttp.web import Request
from aiohttp.web_request import Request
from requests.sessions import Request
from werkzeug.wrappers import Request
from h11._events import Request
from httpcore._models import Request
from httpx import Request
from httpx._models import Request
from werkzeug.wrappers.request import Request
from urllib.request import Request
from fastapi import Request
from starlette.requests import Request
from websockets.http11 import Request
import t
from flask.sansio.app import App
from jinja2.loaders import BaseLoader

class UnexpectedUnicodeError(AssertionError, UnicodeError): ...

class DebugFilesKeyError(KeyError, AssertionError):
    def __init__(self, request: Request, key: str) -> None: ...

class FormDataRoutingRedirect(AssertionError):
    def __init__(self, request: Request) -> None: ...
def attach_enctype_error_multidict(request: Request) -> None: ...
def explain_template_loading_attempts(app: App, template: str, attempts: list[tuple[BaseLoader, Scaffold, tuple[str, str | None, t.Callable[[], bool] | None] | None]]) -> None: ...
