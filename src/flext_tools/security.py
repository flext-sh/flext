"""Unified security service for FLEXT platform.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextDomainService, FlextResult


class FlextSecurityService(FlextDomainService[dict[str, str]]):
    """Unified security service with nested helpers.

    Single responsibility: Security operations including vault decryption and antipattern scanning.
    """

    class _VaultHelper:
        """Nested helper for vault operations."""

        @staticmethod
        def decrypt_secrets(vault_path: str) -> FlextResult[dict[str, str]]:
            """Decrypt secrets from vault."""
            _ = vault_path  # Placeholder implementation
            return FlextResult[dict[str, str]].ok({})

    class _ScanHelper:
        """Nested helper for scanning operations."""

        @staticmethod
        def scan_directory(
            directory: str, config: dict[str, str] | None = None,
        ) -> FlextResult[list[str]]:
            """Scan directory for antipatterns."""
            _ = directory, config  # Placeholder implementation
            return FlextResult[list[str]].ok([])

    def execute(self) -> FlextResult[dict[str, str]]:
        """Execute security service - FlextDomainService interface."""
        return FlextResult[dict[str, str]].ok({})

    def decrypt_vault(self, vault_path: str) -> FlextResult[dict[str, str]]:
        """Decrypt secrets from vault using nested helper."""
        return self._VaultHelper.decrypt_secrets(vault_path)

    def scan_antipatterns(
        self, directory: str, config: dict[str, str] | None = None,
    ) -> FlextResult[list[str]]:
        """Scan for antipatterns using nested helper."""
        return self._ScanHelper.scan_directory(directory, config)


# LEGACY ALIASES ELIMINATED - Use FlextSecurityService directly:
# Use: FlextSecurityService instead of AntipatternScanner
# Use: FlextSecurityService instead of SecretVaultDecryptor
# Use: dict[str, object] instead of ScanConfig

__all__ = [
    "FlextSecurityService",
]
