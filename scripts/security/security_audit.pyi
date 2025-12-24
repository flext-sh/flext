from flext import t

class SecurityViolation:
    def __init__(self, message: str, risk_level: str = "MEDIUM") -> None: ...
    message: str
    risk_level: str

class ScanConfig:
    def __init__(
        self,
        target_paths: t.StringList,
        *,
        include_dependencies: bool = False,
    ) -> None: ...
    target_paths: t.StringList
    include_dependencies: bool

class AntipatternScanner:
    def __init__(self, config: ScanConfig) -> None: ...
    config: ScanConfig
    def scan_ecosystem(self) -> list[SecurityViolation]: ...

def scan_flext_ecosystem(
    workspace_path: str,
    _output_file: str | None = None,
) -> list[SecurityViolation]: ...
