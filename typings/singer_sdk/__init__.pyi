"""Minimal stub for singer_sdk so type checkers resolve Sink/Target without install.

See: https://sdk.meltano.com/
"""

from collections.abc import Sequence
from typing import Any

class Sink:
    stream_name: str
    config: dict[str, Any]
    authenticator: Any
    def __init__(
        self,
        target: Target,
        stream_name: str,
        schema: dict[str, Any],
        key_properties: Sequence[str] | None = None,
    ) -> None: ...

class Target:
    name: str
    config: dict[str, Any]
    default_sink_class: type[Sink]
    config_jsonschema: dict[str, Any]
    def __init__(self, config: dict[str, Any] | None = None) -> None: ...
    def listen(self, file_input: Any = None, *args: Any, **kwargs: Any) -> None: ...

__all__ = ["Sink", "Target"]
