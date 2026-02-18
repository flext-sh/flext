from typing import Any, EventDict

CRITICAL: int
FATAL: int
ERROR: int
WARNING: int
WARN: int
INFO: int
DEBUG: int
NOTSET: int
NAME_TO_LEVEL: dict
LEVEL_TO_NAME: dict
def map_method_name(method_name: str) -> str: ...
def add_log_level(logger: Any, method_name: str, event_dict: EventDict) -> EventDict: ...
