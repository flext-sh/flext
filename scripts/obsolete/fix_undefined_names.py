#!/usr/bin/env python3
"""Fix undefined name 'e' in client.py.

This script fixes two F821 Undefined name 'e' errors in client.py
where 'from e' is used but 'e' is not defined.

Usage:
    python fix_undefined_names.py
"""

import re
from pathlib import Path


def fix_client_file() -> bool:
    """Fix undefined name 'e' errors in client.py."""
    client_path = (
        Path(__file__).parent.parent /
        "dc-api-x" /
        "src" /
        "dc_api_x" /
        "client.py")

    if not client_path.exists():
        print(f"File not found: {client_path}")
        return False

    print(f"Processing {client_path}")
    content = client_path.read_text(encoding="utf-8")
    original_content = content

    # Fix raise AdapterTypeError in search method
    content = re.sub(
        r"raise AdapterTypeError\(AdapterTypeError\.DIRECTORY_REQUIRED\) from e",
        r"raise AdapterTypeError(AdapterTypeError.DIRECTORY_REQUIRED)",
        content,
    )

    # Fix raise AdapterTypeError in publish_message method
    content = re.sub(
        r"raise AdapterTypeError\(AdapterTypeError\.MESSAGE_QUEUE_REQUIRED\) from e",
        r"raise AdapterTypeError(AdapterTypeError.MESSAGE_QUEUE_REQUIRED)",
        content,
    )

    # Check if changes were made
    if content != original_content:
        client_path.write_text(content, encoding="utf-8")
        print(f"Fixed undefined name 'e' errors in {client_path}")
        return True

    print(f"No undefined name errors found in {client_path}")
    return False


def main() -> None:
    """Main entry point."""
    fix_client_file()


if __name__ == "__main__":
    main()
