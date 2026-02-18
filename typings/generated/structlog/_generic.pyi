import structlog._base
from typing import Any

class BoundLogger(structlog._base.BoundLoggerBase):
    def __getattr__(self, method_name: str) -> Any: ...
