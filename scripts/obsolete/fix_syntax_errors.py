#!/usr/bin/env python3
"""Fix syntax errors in client.py and adapters.py.

This script specifically targets and fixes:
1. Duplicated "from e" clauses
2. Malformed raise statements
3. Misplaced function definitions in exception blocks
4. Other syntax errors in client.py and adapters.py

Usage:
    python fix_syntax_errors.py
"""

import re
from pathlib import Path


def fix_client_file() -> bool:
    """Fix syntax errors in client.py."""
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

    # Fix the duplicated * separator in line ~177
    content = re.sub(
        r"(\s+)max_retries: int = DEFAULT_MAX_RETRIES,\n\s+retry_backoff: float = DEFAULT_RETRY_BACKOFF,\n\s+\*,\s+debug: bool = False,",
        r"\1max_retries: int = DEFAULT_MAX_RETRIES,\n\1retry_backoff: float = DEFAULT_RETRY_BACKOFF,\n\1*, debug: bool = False,",
        content,
    )

    # Fix the malformed raise statements with duplicated "from e"
    content = re.sub(
        r'raise RequestError\(f"Request error: \{str\(e\)}\"\) from eraise ApiError\(f"API error: \{str\(e\)}\"\) from edef _process_response',
        r'raise RequestError(f"Request error: {str(e)}") from e\n\n    def _process_response',
        content,
    )

    # Fix the AdapterTypeError raise statement around line 822
    content = re.sub(
        r"raise AdapterTypeError\(AdapterTypeError\.DIRECTORY_REQUIRED\) from etry: from e",
        r"raise AdapterTypeError(AdapterTypeError.DIRECTORY_REQUIRED) from e\n        try:",
        content,
    )

    # Fix the MessageQueueAdapter raise statement around line 863
    content = re.sub(
        r"raise AdapterTypeError\(AdapterTypeError\.MESSAGE_QUEUE_REQUIRED\) from etry: from e",
        r"raise AdapterTypeError(AdapterTypeError.MESSAGE_QUEUE_REQUIRED) from e\n        try:",
        content,
    )

    # Check if changes were made
    if content != original_content:
        client_path.write_text(content, encoding="utf-8")
        print(f"Fixed syntax errors in {client_path}")
        return True

    print(f"No syntax errors found in {client_path}")
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
    content = adapters_path.read_text(encoding="utf-8")
    original_content = content

    # Fix the database connection error
    content = re.sub(
        r'raise ConnectionError\(f"Failed to connect to database: \{str\(e\)}\"\) from edef disconnect\(self\) -> None: from e',
        r'raise ConnectionError(f"Failed to connect to database: {str(e)}") from e\n\n    def disconnect(self) -> None:',
        content,
    )

    # Fix the LDAP connection error
    content = re.sub(
        r'raise ConnectionError\(f"Failed to connect to LDAP directory: \{str\(e\)}\"\) from edef disconnect\(self\) -> None: from e',
        r'raise ConnectionError(f"Failed to connect to LDAP directory: {str(e)}") from e\n\n    def disconnect(self) -> None:',
        content,
    )

    # Check if changes were made
    if content != original_content:
        adapters_path.write_text(content, encoding="utf-8")
        print(f"Fixed syntax errors in {adapters_path}")
        return True

    print(f"No syntax errors found in {adapters_path}")
    return False


def main() -> None:
    """Main entry point."""
    fixed_client = fix_client_file()
    fixed_adapters = fix_adapters_file()

    if fixed_client or fixed_adapters:
        print("\nFixed syntax errors in files.")
        print("\nNo syntax errors fixed.")


if __name__ == "__main__":
    main()
