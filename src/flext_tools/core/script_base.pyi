from collections.abc import Callable
from dataclasses import dataclass
from typing import ParamSpec

from flext_core import FlextResult, FlextValue

P_main_func = ParamSpec("P_main_func")

class ScriptMetadata(FlextValue):
    name: str
    description: str
    category: str
    version: str
    requires_confirmation: bool
    dry_run_supported: bool

    def validate_business_rules(self) -> FlextResult[None]: ...

class FlextScript:
    logger: object
    start_time: float

    @property
    def metadata(self) -> ScriptMetadata: ...
    def validate_preconditions(self) -> FlextResult[None]: ...
    def execute_main_logic(self, **kwargs: object) -> FlextResult[object]: ...
    def cleanup(self) -> FlextResult[None]: ...
    def setup(self) -> FlextResult[None]: ...
    def run(self, **kwargs: object) -> int: ...

@dataclass
class ScriptConfig[**P_main_func]:
    name: str
    description: str
    category: str
    main_func: Callable[P_main_func, FlextResult[object]]
    setup_func: Callable[[], FlextResult[None]] | None = None
    validate_func: Callable[[], FlextResult[None]] | None = None

def create_simple_script[**P_main_func](
    config: ScriptConfig[P_main_func],
) -> type[FlextScript]: ...
