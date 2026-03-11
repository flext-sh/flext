from openapi_pydantic.v3.v3_0 import Response
from h11 import Response
from typings.generated.starlette.responses import Response
from flask import Response
from fastapi.openapi.models import Response
from fastapi.responses import Response
from openapi_pydantic.v3 import Response
from openapi_pydantic import Response
from aiohttp.web import Response
from aiohttp.web_response import Response
from requests.adapters import Response
from requests import Response
from h11._events import Response
from typings.generated.flask.wrappers import Response
from httpx import Response
from werkzeug.wrappers.response import Response
from fastapi import Response
from werkzeug.wrappers import Response
from werkzeug.sansio.response import Response
from flask.wrappers import Response
from openapi_pydantic.v3.v3_0.response import Response
from websockets import Response
from websockets.http11 import Response
from httpcore import Response
from requests.models import Response
from werkzeug import Response
from httpx._models import Response
from openapi_pydantic.v3.v3_1 import Response
from openapi_pydantic.v3.v3_1.response import Response
from starlette.responses import Response
from httpcore._models import Response
from flask.sansio.app import App
from typing import ClassVar

import t

class JSONProvider:
    def __init__(self, app: App) -> None: ...
    def dumps(self, obj: t.Any, **kwargs: t.Any) -> str: ...
    def dump(self, obj: t.Any, fp: t.IO[str], **kwargs: t.Any) -> None: ...
    def loads(self, s: str | bytes, **kwargs: t.Any) -> t.Any: ...
    def load(self, fp: t.IO[t.AnyStr], **kwargs: t.Any) -> t.Any: ...
    def response(self, *args: t.Any, **kwargs: t.Any) -> Response: ...

class DefaultJSONProvider(JSONProvider):
    ensure_ascii: ClassVar[bool] = ...
    sort_keys: ClassVar[bool] = ...
    compact: ClassVar[None] = ...
    mimetype: ClassVar[str] = ...
    @staticmethod
    def default(o: t.Any) -> t.Any: ...
    def dumps(self, obj: t.Any, **kwargs: t.Any) -> str: ...
    def loads(self, s: str | bytes, **kwargs: t.Any) -> t.Any: ...
    def response(self, *args: t.Any, **kwargs: t.Any) -> Response: ...
