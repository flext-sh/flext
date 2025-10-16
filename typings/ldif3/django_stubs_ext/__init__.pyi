from pathlib import Path
from typing import Any, NotRequired, TypedDict, type_check_only

@type_check_only
class TemplatesSetting(TypedDict):
    BACKEND: str
    NAME: NotRequired[str]
    DIRS: NotRequired[list[str | Path]]
    APP_DIRS: NotRequired[bool]
    OPTIONS: NotRequired[dict[str, Any]]

__all__ = ["TemplatesSetting"]
