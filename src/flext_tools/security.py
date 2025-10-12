"""Unified security service for FLEXT platform.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self

from flext_core import FlextCore


class FlextSecurityService(FlextCore.Service[FlextCore.Types.StringDict]):
    """Unified security service with nested helpers.

    Single responsibility: Security operations including vault decryption and antipattern scanning.
    """

    class _VaultHelper:
        """Nested helper for vault operations."""

        @staticmethod
        def decrypt_secrets(
            vault_path: str,
        ) -> FlextCore.Result[FlextCore.Types.StringDict]:
            """Decrypt secrets from vault."""
            _ = vault_path  # Placeholder implementation
            return FlextCore.Result[FlextCore.Types.StringDict].ok({})

    class _ScanHelper:
        """Nested helper for scanning operations."""

        @staticmethod
        def scan_directory(
            directory: str,
            config: FlextCore.Types.StringDict | None = None,
        ) -> FlextCore.Result[FlextCore.Types.StringList]:
            """Scan directory for antipatterns."""
            _ = directory, config  # Placeholder implementation
            return FlextCore.Result[FlextCore.Types.StringList].ok([])

    def execute(self: Self) -> FlextCore.Result[FlextCore.Types.StringDict]:
        """Execute security service - FlextCore.Service interface."""
        return FlextCore.Result[FlextCore.Types.StringDict].ok({})

    def decrypt_vault(
        self, vault_path: str
    ) -> FlextCore.Result[FlextCore.Types.StringDict]:
        """Decrypt secrets from vault using nested helper."""
        return self._VaultHelper.decrypt_secrets(vault_path)

    def scan_antipatterns(
        self,
        directory: str,
        config: FlextCore.Types.StringDict | None = None,
    ) -> FlextCore.Result[FlextCore.Types.StringList]:
        """Scan for antipatterns using nested helper."""
        return self._ScanHelper.scan_directory(directory, config)


# LEGACY ALIASES ELIMINATED - Use FlextSecurityService directly:
# Use: FlextSecurityService instead of AntipatternScanner
# Use: FlextSecurityService instead of SecretVaultDecryptor
# Use: FlextCore.Types.Dict instead of ScanConfig

__all__ = [
    "FlextSecurityService",
]
