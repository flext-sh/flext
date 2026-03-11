from multiprocessing import Pool
from sqlalchemy.pool import Pool
from typings.generated.sqlalchemy.pool.base import Pool
from sqlalchemy import Pool
from multiprocessing.pool import Pool
from sqlalchemy.pool.base import Pool
from sqlalchemy.engine import URL
from cairosvg.url import URL
from sqlalchemy import URL
from mdurl import URL
from httpx import URL
from mdurl._url import URL
from fastapi.datastructures import URL
from werkzeug.urls import URL
from typings.ldif3.mdurl import URL
from starlette.datastructures import URL
from sqlalchemy.engine.url import URL
from yarl import URL
from httpx._urls import URL
from yarl._url import URL
from httpcore import URL
from httpcore._models import URL
from sqlalchemy.engine import Engine
from sqlalchemy import Engine
from sqlalchemy.future import Engine
from django.template.engine import Engine
from sqlalchemy.future.engine import Engine
from typings.generated.sqlalchemy.engine.base import Engine
from sqlalchemy.engine.base import Engine
from typing import Any

import _url as _url

def create_engine(url: str | _url.URL, **kwargs: Any) -> Engine: ...
def engine_from_config(configuration: dict[str, Any], prefix: str = ..., **kwargs: Any) -> Engine: ...
def create_pool_from_url(url: str | URL, **kwargs: Any) -> Pool: ...
