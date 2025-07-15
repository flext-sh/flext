#!/usr/bin/env python3
"""Decrypt production secrets vault for deployment or rotation."""

import base64
import getpass
import json
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def decrypt_secrets_vault(vault_file: Path, password: str) -> dict:
    """Decrypt the production secrets vault."""

    # Load vault data
    with open(vault_file, encoding="utf-8") as f:
        vault_data = json.load(f)

    # Recreate encryption key from password
    password_bytes = password.encode("utf-8")
    salt = base64.b64decode(vault_data["salt"])
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
    fernet = Fernet(key)

    # Decrypt secrets
    encrypted_data = base64.b64decode(vault_data["encrypted_secrets"])
    decrypted_json = fernet.decrypt(encrypted_data).decode("utf-8")
    return json.loads(decrypted_json)


def display_secrets(secrets_data: dict, mask_secrets: bool = True) -> None:
    """Display secrets with optional masking."""
    print("🔓 DECRYPTED PRODUCTION SECRETS:")
    print("=" * 50)

    for key, value in secrets_data.items():
        if key == "created_at":
            print(f"  📅 {key}: {value}")
        elif mask_secrets and len(str(value)) > 8:
            print(f"  🔑 {key}: {str(value)[:4]}...{str(value)[-4:]}")
        else:
            print(f"  🔑 {key}: {value}")


def export_secrets_to_env(secrets_data: dict, output_file: Path) -> None:
    """Export secrets as environment variables script."""
    env_content = "#!/bin/bash\n"
    env_content += (
        "# Production secrets - source this file to set environment variables\n"
    )
    env_content += "# WARNING: Contains production secrets - keep secure!\n\n"

    for key, value in secrets_data.items():
        if key != "created_at":
            env_var_name = f"FLEXT_SECRET_{key.upper()}"
            env_content += f'export {env_var_name}="{value}"\n'

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(env_content)

    # Make executable
    output_file.chmod(0o700)

    print(f"✅ Secrets exported to: {output_file}")


def main():
    """Main secrets vault management interface."""
    print("🔐 FLEXT PRODUCTION SECRETS VAULT MANAGER")
    print("=" * 50)

    project_root = Path(__file__).parent.parent
    vault_file = project_root / "secrets" / "production_secrets.vault"

    if not vault_file.exists():
        print(f"❌ Secrets vault not found: {vault_file}")
        print("Run generate_production_secrets.py first to create the vault.")
        return

    # Get vault password
    password = getpass.getpass("Enter vault master password: ")

    try:
        # Decrypt secrets
        print("\n🔓 Decrypting secrets vault...")
        secrets_data = decrypt_secrets_vault(vault_file, password)

        print(f"✅ Successfully decrypted {len(secrets_data)} secrets")

        # Display options
        while True:
            print("\n📋 VAULT OPERATIONS:")
            print("  1. View secrets (masked)")
            print("  2. View secrets (full)")
            print("  3. Export to environment script")
            print("  4. View specific secret")
            print("  5. Exit")

            choice = input("\nSelect operation (1-5): ").strip()

            if choice == "1":
                display_secrets(secrets_data, mask_secrets=True)
            elif choice == "2":
                confirm = input(
                    "Show full secrets? This will display sensitive data (y/N): "
                )
                if confirm.lower() == "y":
                    display_secrets(secrets_data, mask_secrets=False)
                else:
                    print("Operation cancelled.")
            elif choice == "3":
                output_file = project_root / "secrets" / "production_secrets.sh"
                export_secrets_to_env(secrets_data, output_file)
            elif choice == "4":
                available_keys = [k for k in secrets_data if k != "created_at"]
                print(f"Available secrets: {', '.join(available_keys)}")
                secret_name = input("Enter secret name: ").strip()
                if secret_name in available_keys:
                    print(f"🔑 {secret_name}: {secrets_data[secret_name]}")
                else:
                    print("❌ Secret not found")
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice")

    except Exception as e:
        print(f"❌ Failed to decrypt vault: {e}")
        print("Check your password and try again.")


if __name__ == "__main__":
    main()
