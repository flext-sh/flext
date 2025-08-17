import argparse
from abc import ABC, abstractmethod
from collections.abc import Callable as Callable
from dataclasses import dataclass
from typing import ParamSpec

from _typeshed import Incomplete
from flext_core import FlextResult, FlextValue

from flext_tools.quality.gateway import (
    QualityCheckConfig as QualityCheckConfig,
    QualityGateway as QualityGateway,
    all_quality_checks_passed as all_quality_checks_passed,
    get_quality_failure_summary as get_quality_failure_summary,
)
from flext_tools.utils.colors import Colors as Colors, print_colored as print_colored

P_main_func = ParamSpec("P_main_func")
logger: Incomplete

class ScriptMetadata(FlextValue):
    name: str
    description: str
    category: str
    version: str
    requires_confirmation: bool
    dry_run_supported: bool
    def validate_business_rules(self) -> FlextResult[None]: ...

class FlextScript(ABC):
    logger: Incomplete
    start_time: Incomplete
    container: Incomplete
    def __init__(self) -> None: ...
    @property
    @abstractmethod
    def metadata(self) -> ScriptMetadata: ...
    @abstractmethod
    def validate_preconditions(self) -> FlextResult[None]: ...
    @abstractmethod
    def execute_main_logic(self, **kwargs: object) -> FlextResult[object]: ...
    def cleanup(self) -> FlextResult[None]: ...
    def setup(self) -> FlextResult[None]: ...
    def run(self, **kwargs: object) -> int: ...
    def create_parser(self) -> argparse.ArgumentParser: ...
    def main(self) -> int: ...

@dataclass
class ScriptConfig[**P_main_func]:
    name: str
    description: str
    category: str
    main_func: Callable[P_main_func, FlextResult[object]]
    setup_func: Callable[[], FlextResult[None]] | None = ...
    validate_func: Callable[[], FlextResult[None]] | None = ...

def create_simple_script[**P_main_func](
    config: ScriptConfig[P_main_func],
) -> type[FlextScript]: ...
