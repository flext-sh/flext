#!/usr/bin/env python3
"""Update flext_core imports to use centralized flext imports across all FLEXT projects.

This script updates all Python files in FLEXT projects to use the centralized
flext imports instead of importing directly from flext_core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def update_flext_core_imports(file_path: Path) -> bool:
    """Update flext_core imports in a Python file.

    Args:
        file_path: Path to the Python file to update

    Returns:
        True if file was modified, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Pattern to match multi-line flext_core imports
        multiline_pattern = r"from flext_core import \(\s*((?:[^)]+\s*,\s*)*[^)]+)\s*\)"

        def replace_multiline_import(match):
            imports_text = match.group(1)
            # Remove trailing comma and whitespace
            imports_clean = re.sub(r',\s*$', '', imports_text.strip())
            # Replace with single-line import
            return f"from flext import {imports_clean}"

        # Replace multi-line imports
        content = re.sub(multiline_pattern, replace_multiline_import, content, flags=re.MULTILINE | re.DOTALL)

        # Replace single-line imports
        content = re.sub(r"from flext_core import (.+)", r"from flext import \1", content)

        # Handle special case where imports are split across lines with backslashes
        content = re.sub(r"from flext_core import \\\s*\n\s*(.+)", r"from flext import \1", content, flags=re.MULTILINE)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True

    except (OSError, ValueError, TypeError):
        return False

    return False


def main() -> None:
    """Main function to update flext_core imports in all FLEXT projects."""
    project_root = Path(".")

    # Find all Python files in FLEXT projects (excluding flext-core itself since it's the source)
    flext_projects = [
        "flext-api", "flext-auth", "flext-cli", "flext-db-oracle", "flext-dbt-ldap",
        "flext-dbt-ldif", "flext-dbt-oracle", "flext-dbt-oracle-wms", "flext-grpc",
        "flext-ldap", "flext-ldif", "flext-meltano", "flext-observability",
        "flext-oracle-oic", "flext-oracle-wms", "flext-plugin", "flext-quality",
        "flext-tap-ldap", "flext-tap-ldif", "flext-tap-oracle", "flext-tap-oracle-oic",
        "flext-tap-oracle-wms", "flext-target-ldap", "flext-target-ldif",
        "flext-target-oracle", "flext-target-oracle-oic", "flext-target-oracle-wms",
        "flext-web"
    ]

    files_updated = 0

    for project in flext_projects:
        project_path = project_root / project
        if not project_path.exists():
            continue

        # Find all Python files in the project
        python_files = list(project_path.rglob("*.py"))

        for py_file in python_files:
            # Skip __pycache__ and other generated files
            if "__pycache__" in str(py_file) or py_file.name.startswith('.'):
                continue

            if update_flext_core_imports(py_file):
                print(f"Updated: {py_file}")
                files_updated += 1

    print(f"\nTotal files updated: {files_updated}")


if __name__ == "__main__":
    main()