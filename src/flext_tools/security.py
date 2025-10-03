"""Unified security service for FLEXT platform.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self

from flext_core import FlextResult, FlextService, FlextTypes


class FlextSecurityService(FlextService[FlextTypes.StringDict]):
    """Unified security service with nested helpers.

    Single responsibility: Security operations including vault decryption and antipattern scanning.
    """

    class _VaultHelper:
        """Nested helper for vault operations."""

        @staticmethod
        def decrypt_secrets(vault_path: str) -> FlextResult[FlextTypes.StringDict]:
            """Decrypt secrets from vault."""
            _ = vault_path  # Placeholder implementation
            return FlextResult[FlextTypes.StringDict].ok({})

    class _ScanHelper:
        """Nested helper for scanning operations."""

        @staticmethod
        def scan_directory(
            directory: str,
            config: FlextTypes.StringDict | None = None,
        ) -> FlextResult[FlextTypes.StringList]:
            """Scan directory for antipatterns."""
            _ = directory, config  # Placeholder implementation
            return FlextResult[FlextTypes.StringList].ok([])

    def execute(self: Self) -> FlextResult[FlextTypes.StringDict]:
        """Execute security service - FlextService interface."""
        return FlextResult[FlextTypes.StringDict].ok({})

    def decrypt_vault(self, vault_path: str) -> FlextResult[FlextTypes.StringDict]:
        """Decrypt secrets from vault using nested helper."""
        return self._VaultHelper.decrypt_secrets(vault_path)

    def scan_antipatterns(
        self,
        directory: str,
        config: FlextTypes.StringDict | None = None,
    ) -> FlextResult[FlextTypes.StringList]:
        """Scan for antipatterns using nested helper."""
        return self._ScanHelper.scan_directory(directory, config)


# LEGACY ALIASES ELIMINATED - Use FlextSecurityService directly:
# Use: FlextSecurityService instead of AntipatternScanner
# Use: FlextSecurityService instead of SecretVaultDecryptor
# Use: FlextTypes.Dict instead of ScanConfig

__all__ = [
    "FlextSecurityService",
]
