from joblib.parallel import method
from h11._abnf import method
from sqlalchemy.util.typing import _FN
from sqlalchemy.orm.strategy_options import _FN
from sqlalchemy.util.preloaded import _FN
from sqlalchemy.sql.operators import _FN
from sqlalchemy.orm.collections import _FN
from collections.abc import Callable

TYPE_CHECKING: bool

class _ModuleRegistry:
    def __init__(self, prefix: str = ...) -> None: ...
    def preload_module(self, *deps: str) -> Callable[[_FN], _FN]: ...
    def import_prefix(self, path: str) -> None: ...
preload_module: method
import_prefix: method
