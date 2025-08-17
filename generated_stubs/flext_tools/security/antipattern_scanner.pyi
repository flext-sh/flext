from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

from _typeshed import Incomplete
from flext_core import FlextResult, FlextValue

from flext_tools.utils.colors import Colors as Colors, print_colored as print_colored

logger: Incomplete

class ViolationType(Enum):
    SILENT_FAILURE = "silent_failure"
    EXCEPTION_SWALLOWING = "exception_swallowing"
    FAKE_DATA_GENERATION = "fake_data_generation"

class RiskLevel(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass(frozen=True)
class SecurityViolation:
    file_path: str
    line_number: int
    violation_type: ViolationType
    risk_level: RiskLevel
    code_snippet: str
    description: str
    suggested_fix: str
    def to_dict(self) -> dict[str, object]: ...

class ScanConfig(FlextValue):
    target_paths: list[str]
    exclude_patterns: ClassVar[list[str]]
    include_dependencies: bool
    output_format: str
    risk_threshold: str
    max_workers: int
    def validate_business_rules(self) -> FlextResult[None]: ...

class AntipatternScanner:
    config: Incomplete
    logger: Incomplete
    def __init__(self, config: ScanConfig) -> None: ...
    def scan_ecosystem(self) -> FlextResult[list[SecurityViolation]]: ...
    def generate_report(
        self, violations: list[SecurityViolation], output_file: str
    ) -> FlextResult[None]: ...

def create_security_scanner(
    target_paths: list[str],
    *,
    exclude_dependencies: bool = True,
    output_format: str = "summary",
    risk_threshold: str = "MEDIUM",
) -> FlextResult[AntipatternScanner]: ...
def scan_flext_ecosystem(
    workspace_path: str = ".", output_file: str | None = None
) -> FlextResult[list[SecurityViolation]]: ...
