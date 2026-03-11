from fastapi.responses import Response
from openapi_pydantic.v3 import Response
from openapi_pydantic import Response
from openapi_pydantic.v3.v3_0 import Response
from h11 import Response
from typings.generated.starlette.responses import Response
from flask import Response
from httpx import Response
from fastapi import Response
from fastapi.openapi.models import Response
from requests.adapters import Response
from requests import Response
from werkzeug.wrappers.response import Response
from typings.generated.flask.wrappers import Response
from websockets import Response
from httpcore import Response
from werkzeug import Response
from openapi_pydantic.v3.v3_1 import Response
from openapi_pydantic.v3.v3_0.response import Response
from werkzeug.sansio.response import Response
from flask.wrappers import Response
from aiohttp.web import Response
from starlette.responses import Response
from websockets.http11 import Response
from h11._events import Response
from httpcore._models import Response
from aiohttp.web_response import Response
from openapi_pydantic.v3.v3_1.response import Response
from werkzeug.wrappers import Response
from requests.models import Response
from httpx._models import Response
import os

import flask
import t

class Blueprint(flask.sansio.blueprints.Blueprint):
    def __init__(self, name: str, import_name: str, static_folder: str | os.PathLike[str] | None = ..., static_url_path: str | None = ..., template_folder: str | os.PathLike[str] | None = ..., url_prefix: str | None = ..., subdomain: str | None = ..., url_defaults: dict[str, t.Any] | None = ..., root_path: str | None = ..., cli_group: str | None = ...) -> None: ...
    def get_send_file_max_age(self, filename: str | None) -> int | None: ...
    def send_static_file(self, filename: str) -> Response: ...
    def open_resource(self, resource: str, mode: str = ..., encoding: str | None = ...) -> t.IO[t.AnyStr]: ...
