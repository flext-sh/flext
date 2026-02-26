from typing import Any

import structlog._base

class BoundLogger(structlog._base.BoundLoggerBase):
    def __getattr__(self, method_name: str) -> Any: ...
