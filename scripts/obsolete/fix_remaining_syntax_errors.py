#!/usr/bin/env python3
"""Fix remaining syntax errors in client.py and adapters.py.

This script fixes the remaining syntax errors that weren't caught by the previous scripts:
1. Malformed code in client.py around the _process_response method
2. Malformed code in adapters.py that mixes function definitions with exception handling

Usage:
    python fix_remaining_syntax_errors.py
"""

from pathlib import Path


def fix_client_file() -> bool:
    """Fix syntax errors in client.py."""
    client_path = (
        Path(__file__).parent.parent / "dc-api-x" / "src" / "dc_api_x" / "client.py"
    )

    if not client_path.exists():
        print(f"File not found: {client_path}")
        return False

    print(f"Processing {client_path}")

    # Read the file directly
    with open(client_path, encoding="utf-8") as f:
        lines = f.readlines()

    lines.copy()
    fixed_content = False

    # Look for the problematic line with "from edef"
    for i in range(len(lines)):
        if "from edef" in lines[i]:
            if "_process_response" in lines[i]:
                # Split the 'from e' from the method definition
                parts = lines[i].split("from e")
                if len(parts) > 1:
                    # Fix the first part to include proper 'from e'
                    lines[i] = parts[0] + "from e\n"

                    # Add the method definition as a new line
                    next_line = "\n    def _process_response(self, response: requests.Response) -> FlxResponse:\n"
                    lines.insert(i + 1, next_line)
                    fixed_content = True
                    break

    # Only write the file if changes were made
    if fixed_content:
        with open(client_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"Fixed syntax errors in {client_path}")
        return True

    print(f"No syntax errors found to fix in {client_path}")
    return False


def fix_adapters_file() -> bool:
    """Fix syntax errors in adapters.py."""
    adapters_path = (
        Path(__file__).parent.parent
        / "dc-api-x"
        / "src"
        / "dc_api_x"
        / "utils"
        / "adapters.py"
    )

    if not adapters_path.exists():
        print(f"File not found: {adapters_path}")
        return False

    print(f"Processing {adapters_path}")

    # Read the file directly
    with open(adapters_path, encoding="utf-8") as f:
        lines = f.readlines()

    lines.copy()
    fixed_content = False

    # Look for the problematic lines with "from edef"
    for i in range(len(lines)):
        if "from edef" in lines[i]:
            # Database connection
            if "Failed to connect to database" in lines[i]:
                # Split the 'from e' from the method definition
                parts = lines[i].split("from e")
                if len(parts) > 1:
                    # Fix the first part to include proper 'from e'
                    lines[i] = parts[0] + "from e\n"

                    # Add method definition as a new line
                    lines.insert(i + 1, "\n    def disconnect(self) -> None:\n")
                    fixed_content = True

            # LDAP connection
            if "Failed to connect to LDAP directory" in lines[i]:
                # Split the 'from e' from the method definition
                parts = lines[i].split("from e")
                if len(parts) > 1:
                    # Fix the first part to include proper 'from e'
                    lines[i] = parts[0] + "from e\n"

                    # Add method definition as a new line
                    lines.insert(i + 1, "\n    def disconnect(self) -> None:\n")
                    fixed_content = True

    # Only write the file if changes were made
    if fixed_content:
        with open(adapters_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"Fixed syntax errors in {adapters_path}")
        return True
    print(f"No syntax errors found to fix in {adapters_path}")
    return False


def main() -> None:
    """Main entry point."""
    client_fixed = fix_client_file()
    adapters_fixed = fix_adapters_file()

    if client_fixed or adapters_fixed:
        print("\nFixed remaining syntax errors.")
    else:
        print("\nNo remaining syntax errors found or fixed.")


if __name__ == "__main__":
    main()
