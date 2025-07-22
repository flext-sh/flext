#!/usr/bin/env python3
"""Decrypt Secrets Vault.

Descriptografa cofre de secrets de produção usando flext_tools.security
para máxima segurança e padronização enterprise.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from flext_tools import Colors, print_colored
from flext_tools.core.script_base import ScriptMetadata
from flext_tools.security import SecretVaultDecryptor

from ._base_security_script import BaseSecurityScript


class SecretsVaultDecryptor(BaseSecurityScript):
    """Decrypt production secrets vault for deployment or rotation."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="decrypt_secrets_vault",
            description="Decrypt production secrets vault securely",
            category="security",
            version="2.0.0",
        )

# validate_preconditions is inherited from BaseSecurityScript

    def execute_main_logic(self, **kwargs: Any) -> bool:
        """Execute vault decryption."""
        try:
            workspace_root = Path.cwd()
            vault_file = kwargs.get("vault_file")
            password = kwargs.get("password")
            mask_secrets = kwargs.get("mask_secrets", True)
            output_format = kwargs.get("format", "text")

            if not vault_file:
                print_colored("❌ Vault file path is required", Colors.RED)
                return False

            vault_path = workspace_root / vault_file
            if not vault_path.exists():
                print_colored(f"❌ Vault file not found: {vault_path}", Colors.RED)
                return False

            print_colored("🔓 SECRETS VAULT DECRYPTOR", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.security for vault decryption
            vault_decryptor = SecretVaultDecryptor(vault_path=vault_path)

            # Decrypt vault
            decrypt_result = vault_decryptor.decrypt_vault(
                password=password,
                mask_secrets=mask_secrets,
            )

            if decrypt_result:
                print_colored("✅ Vault decrypted successfully", Colors.GREEN)

                # Display secrets according to format
                if output_format == "json":
                    import json

                    print(json.dumps(decrypt_result, indent=2))
                elif output_format == "env":
                    for key, value in decrypt_result.items():
                        if key != "details":
                            display_value = "***MASKED***" if mask_secrets else value
                            print(f"{key}={display_value}")
                else:
                    # Text format
                    print_colored("🔑 Decrypted Secrets:", Colors.BLUE)
                    for key, value in decrypt_result.items():
                        if key != "details":
                            display_value = "***MASKED***" if mask_secrets else value
                            print(f"  {key}: {display_value}")

                # Security warnings
                print_colored("\n⚠️ Security Warnings:", Colors.RED)
                print("• Clear terminal history after viewing secrets")
                print("• Never share or log decrypted secrets")
                print("• Re-encrypt vault immediately after use")

                return True
            print_colored("❌ Failed to decrypt vault", Colors.RED)
            return False

        except Exception as e:
            print_colored(f"❌ Error during vault decryption: {e}", Colors.RED)
            return False

    def create_parser(self) -> Any:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument("vault_file", help="Path to encrypted secrets vault file")

        parser.add_argument(
            "--password",
            help="Vault password (will prompt if not provided)",
        )

        parser.add_argument(
            "--no-mask",
            action="store_true",
            help="Show secrets in clear text (DANGEROUS)",
        )

        parser.add_argument(
            "--format",
            choices=["text", "json", "env"],
            default="text",
            help="Output format (default: text)",
        )

        return parser

    def _process_kwargs(self, args: Any) -> dict[str, Any]:
        """Process arguments into kwargs."""
        kwargs: dict[str, Any] = {}
        kwargs["mask_secrets"] = not getattr(args, "no_mask", False)
        return kwargs

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = SecretsVaultDecryptor()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
