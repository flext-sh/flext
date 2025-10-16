#!/usr/bin/env python3
"""Decrypt Secrets Vault.

Descriptografa cofre de secrets de produção usando flext_quality.tools.security
para máxima segurança e padronização enterprise.
"""

import argparse
import sys
from pathlib import Path

from flext_core import FlextResult, FlextTypes

from flext_quality.tools import (
    Colors,
    ScriptMetadata,
    SecretVaultDecryptor,
    print_colored,
)

from ._base_security_script import BaseSecurityScript


class SecretsVaultDecryptor(BaseSecurityScript):
    """Decrypt production secrets vault for deployment or rotation."""

    @property
    def metadata(self) -> ScriptMetadata:
        """Get script metadata."""
        return ScriptMetadata(
            name="decrypt_secrets_vault",
            description="Decrypt production secrets vault securely",
            category="security",
            version="2.0.0",
        )

    # validate_preconditions is inherited from BaseSecurityScript

    def execute_main_logic(self, **kwargs: object) -> FlextResult[object]:
        """Execute main script logic."""
        """Execute vault decryption."""
        try:
            workspace_root = Path.cwd()
            vault_file = kwargs.get("vault_file")
            output_format = kwargs.get("format", "text")

            if not vault_file:
                print_colored("❌ Vault file path is required", Colors.RED)
                return FlextResult[object].fail("Vault file path is required")

            vault_path = workspace_root / str(vault_file)
            if not vault_path.exists():
                print_colored(f"❌ Vault file not found: {vault_path}", Colors.RED)
                return FlextResult[object].fail(f"Vault file not found: {vault_path}")

            print_colored("🔓 SECRETS VAULT DECRYPTOR", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_quality.tools.security for vault decryption
            vault_decryptor = SecretVaultDecryptor()

            # Decrypt vault
            decrypt_result = vault_decryptor.decrypt_vault(str(vault_path))

            if decrypt_result:
                print_colored("✅ Vault decrypted successfully", Colors.GREEN)

                # Display secrets according to format
                if output_format == "json":
                    pass
                elif output_format == "env":
                    for key in decrypt_result:
                        if key != "details":
                            pass
                else:
                    # Text format
                    print_colored("🔑 Decrypted Secrets:", Colors.BLUE)
                    for key in decrypt_result:
                        if key != "details":
                            pass

                # Security warnings
                print_colored("\n⚠️ Security Warnings:", Colors.RED)

                return FlextResult[object].ok(
                    {"decrypt_result": decrypt_result, "output_format": output_format},
                )

            print_colored("❌ Failed to decrypt vault", Colors.RED)
            return FlextResult[object].fail("Failed to decrypt vault")

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during vault decryption: {e}", Colors.RED)
            return FlextResult[object].fail(f"Vault decryption error: {e}")

    def create_parser(self) -> argparse.ArgumentParser:
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

    def _process_kwargs(self, args: object) -> FlextTypes.Dict:
        """Process arguments into kwargs."""
        kwargs: FlextTypes.Dict = {}
        kwargs["mask_secrets"] = not getattr(args, "no_mask", False)
        return kwargs

    def cleanup(self) -> FlextResult[None]:
        """Limpeza após execução."""
        return FlextResult[None].ok(None)


def main() -> int:
    """Main function."""
    script = SecretsVaultDecryptor()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
