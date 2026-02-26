from collections.abc import Callable

TYPE_CHECKING: bool

class _ModuleRegistry:
    def __init__(self, prefix: str = ...) -> None: ...
    def preload_module(self, *deps: str) -> Callable[[_FN], _FN]: ...
    def import_prefix(self, path: str) -> None: ...
preload_module: method
import_prefix: method
