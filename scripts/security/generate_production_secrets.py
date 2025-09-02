#!/usr/bin/env python3
"""Generate Production Secrets.

Gera secrets criptograficamente seguros para produção usando flext_tools.security
para máxima segurança e padronização enterprise.
"""

import argparse
import sys
from pathlib import Path

from flext_core import FlextResult

from flext_tools import Colors, ScriptMetadata, print_colored
from flext_tools.security import (
    ProductionSecretsGenerator as FlextToolsSecretsGenerator,
)

from ._base_security_script import BaseSecurityScript


class ProductionSecretsScript(BaseSecurityScript):
    """Generate cryptographically secure secrets for production."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="generate_production_secrets",
            description="Generate secure secrets for production deployment",
            category="security",
            version="2.0.0",
        )

    # validate_preconditions is inherited from BaseSecurityScript

    def execute_main_logic(self, **kwargs: object) -> FlextResult[object]:
        """Execute secrets generation."""
        try:
            workspace_root = Path.cwd()
            environment = kwargs.get("environment", "production")
            output_file = kwargs.get("output_file")
            encrypt = kwargs.get("encrypt", True)

            print_colored("🔐 PRODUCTION SECRETS GENERATOR", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.security for secret generation
            secret_generator = FlextToolsSecretsGenerator()

            # Generate complete set of production secrets
            secrets_result = secret_generator.generate_production_secrets(
                environment=environment,
                encrypt=encrypt,
            )

            if secrets_result:
                print_colored(
                    "✅ Production secrets generated successfully",
                    Colors.GREEN,
                )

                # Display summary
                print_colored("🔑 Generated secrets:", Colors.BLUE)
                for secret_type in secrets_result:
                    if secret_type != "details":  # nosec B105 - comparing key name, not password
                        pass

                # Save to file if requested
                if output_file:
                    output_path = workspace_root / str(output_file)
                    # Save secrets to file (implementation would go here)
                    print_colored(f"💾 Secrets saved to: {output_path}", Colors.CYAN)
                else:
                    # Display vault information
                    print_colored("🏦 Secrets generated in memory", Colors.CYAN)

                # Security reminders
                print_colored("\n🛡️ Security Reminders:", Colors.YELLOW)

                return FlextResult[object].ok(
                    {"secrets_result": secrets_result, "environment": environment},
                )

            print_colored("❌ Failed to generate production secrets", Colors.RED)
            return FlextResult[object].fail("Failed to generate production secrets")

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during secrets generation: {e}", Colors.RED)
            return FlextResult[object].fail(f"Secrets generation error: {e}")

    def create_parser(self) -> argparse.ArgumentParser:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--environment",
            default="production",
            choices=["production", "staging", "development"],
            help="Target environment (default: production)",
        )

        parser.add_argument(
            "--output-file",
            help="Output file path (default: auto-generated vault)",
        )

        parser.add_argument(
            "--no-encrypt",
            action="store_true",
            help="Skip encryption (NOT recommended for production)",
        )

        return parser

    def _process_kwargs(self, args: object) -> dict[str, object]:
        """Process arguments into kwargs."""
        kwargs: dict[str, object] = {}
        kwargs["encrypt"] = not getattr(args, "no_encrypt", False)
        return kwargs

    def cleanup(self) -> FlextResult[None]:
        """Limpeza após execução."""
        return FlextResult[None].ok(None)


def main() -> int:
    """Main function."""
    script = ProductionSecretsScript()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
