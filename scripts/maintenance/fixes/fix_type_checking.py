#!/usr/bin/env python3
"""Script to fix TYPE_CHECKING imports in FLX project files."""

import re
import subprocess
from pathlib import Path
from typing import Any


def get_type_checking_errors() -> Any:
    """Get list of files with TYPE_CHECKING undefined errors."""
    result = subprocess.run(
        ["ruff", "check", "flx/", "--select=F821", "--no-fix", "--format=json"],
        capture_output=True,
        text=True,
        cwd="/home/marlonsc/pyauto",
        check=False,
    )

    if result.returncode != 0:
        print("Error running ruff:", result.stderr)
        return []

    import json

    try:
        errors = json.loads(result.stdout)
        type_checking_files: set = set()
        for error in errors:
            if "TYPE_CHECKING" in error.get("message", ""):
                type_checking_files.add(error["filename"])
        return list(type_checking_files)
    except json.JSONDecodeError:
        print("Could not parse ruff output")
        return []


def fix_type_checking_import(file_path) -> bool:
    """Fix TYPE_CHECKING import in a specific file."""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return False

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Check if TYPE_CHECKING is already imported
    if "TYPE_CHECKING" in content:
        # Check if it's imported correctly
        if re.search(r"from typing import.*TYPE_CHECKING", content):
            print(f"✓ {file_path} already has correct TYPE_CHECKING import")
            return True

        # Need to add TYPE_CHECKING to existing typing import
        typing_import_pattern = r"from typing import ([^()\n]+)"
        match = re.search(typing_import_pattern, content)
        if match:
            imports = match.group(1)
            if "TYPE_CHECKING" not in imports:
                new_imports = imports.strip() + ", TYPE_CHECKING"
                new_line = f"from typing import {new_imports}"
                content = re.sub(typing_import_pattern, new_line, content)
                print(f"+ Added TYPE_CHECKING to existing import in {file_path}")
            # Add TYPE_CHECKING import after other typing imports
            # Look for the first import line
            lines = content.split("\n")
            insert_index = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(
                    "from typing import",
                ) or line.strip().startswith("import typing"):
                    insert_index = i + 1
                    break
                if line.strip().startswith("from ") or line.strip().startswith(
                    "import ",
                ):
                    insert_index = i + 1

            if insert_index > 0:
                lines.insert(insert_index, "")
                lines.insert(insert_index + 1, "try:")
                lines.insert(insert_index + 2, "    from typing import TYPE_CHECKING")
                lines.insert(insert_index + 3, "except ImportError:")
                lines.insert(insert_index + 4, "    TYPE_CHECKING = False")
                content = "\n".join(lines)
                print(f"+ Added TYPE_CHECKING import block to {file_path}")

    # Write the modified content back
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return True


def main() -> None:
    """Main function to fix TYPE_CHECKING errors."""
    print("Finding files with TYPE_CHECKING errors...")
    files_with_errors = get_type_checking_errors()

    if not files_with_errors:
        print("No TYPE_CHECKING errors found!")
        return

    print(f"Found {len(files_with_errors)} files with TYPE_CHECKING errors:")
    for file_path in files_with_errors:
        print(f"  - {file_path}")

    print("\nFixing files...")
    fixed_count = 0
    for file_path in files_with_errors:
        if fix_type_checking_import(file_path):
            fixed_count += 1

    print(f"\nFixed {fixed_count}/{len(files_with_errors)} files")

    # Run ruff again to see remaining errors
    print("\nChecking for remaining TYPE_CHECKING errors...")
    result = subprocess.run(
        ["ruff", "check", "flx/", "--select=F821", "--no-fix"],
        capture_output=True,
        text=True,
        cwd="/home/marlonsc/pyauto",
        check=False,
    )

    type_checking_errors = [
        line for line in result.stdout.split("\n") if "TYPE_CHECKING" in line
    ]
    if type_checking_errors:
        print(f"Still {len(type_checking_errors)} TYPE_CHECKING errors remaining:")
        for error in type_checking_errors[:5]:  # Show first 5
            print(f"  {error}")
        print("✓ All TYPE_CHECKING errors fixed!")


if __name__ == "__main__":
    main()
