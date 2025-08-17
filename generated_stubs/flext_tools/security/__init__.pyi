from typing import Any

from _typeshed import Incomplete

from flext_tools.security.antipattern_scanner import (
    AntipatternScanner as AntipatternScanner,
    RiskLevel as RiskLevel,
    ScanConfig as ScanConfig,
    SecurityViolation as SecurityViolation,
    ViolationType as ViolationType,
    create_security_scanner as create_security_scanner,
    scan_flext_ecosystem as scan_flext_ecosystem,
)

__all__ = [
    "AntipatternScanner",
    "RiskLevel",
    "ScanConfig",
    "SecretGenerator",
    "SecretVaultDecryptor",
    "SecurityViolation",
    "ViolationType",
    "create_security_scanner",
    "scan_flext_ecosystem",
]

class SecretGenerator:
    def generate_production_secrets(
        self, *, environment: str, encrypt: bool
    ) -> dict[str, str]: ...

class SecretVaultDecryptor:
    vault_path: Incomplete
    def __init__(self, *, vault_path: Any) -> None: ...
    def decrypt_vault(
        self, *, password: str | None, mask_secrets: bool
    ) -> dict[str, str] | None: ...
