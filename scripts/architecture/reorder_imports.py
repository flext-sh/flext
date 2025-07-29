#!/usr/bin/env python3
"""Fix import order violations (E402) in FLEXT API files.

This script systematically fixes import ordering violations by moving
DI container initialization after all other imports.
"""

import re
import sys
from pathlib import Path


def fix_import_order(file_path: Path) -> bool:
    """Fix import order in a Python file.

    Args:
        file_path: Path to the Python file to fix

    Returns:
        True if file was modified, False otherwise

    """
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Pattern to match DI container imports and initialization
        di_pattern = r"(# 🚨 ARCHITECTURAL COMPLIANCE:.*?from flext_.*?infrastructure\.di_container import.*?\n\n# Initialize types via DI container\n.*? = get_.*?\(\)\n)"

        # Find DI imports block
        di_match = re.search(di_pattern, content, re.DOTALL)
        if not di_match:
            return False

        di_block = di_match.group(1)

        # Remove DI block from current position
        content = content.replace(di_block, "")

        # Find position after all imports (before if TYPE_CHECKING or class definitions)
        type_checking_pos = content.find("if TYPE_CHECKING:")
        class_pos = content.find("\nclass ")

        # Find the best insertion point
        insert_pos = -1
        if type_checking_pos != -1:
            insert_pos = type_checking_pos
        elif class_pos != -1:
            insert_pos = class_pos + 1
        else:
            # Find last import line
            lines = content.split("\n")
            for line in lines:
                if line.strip().startswith(
                    ("from ", "import "),
                ) and not line.strip().startswith("#"):
                    insert_pos = content.find("\n", content.find(line)) + 1

        if insert_pos == -1:
            print(f"Could not find insertion point for {file_path}")
            return False

        # Insert DI block at the correct position
        content = (
            content[:insert_pos]
            + "\n"
            + di_block.rstrip()
            + "\n"
            + content[insert_pos:]
        )

        # Clean up extra blank lines
        content = re.sub(r"\n{3,}", "\n\n", content)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            print(f"Fixed import order in {file_path}")
            return True

    except (OSError, ValueError, TypeError) as e:
        print(f"Error processing {file_path}: {e}")
        return False

    return False


def main() -> None:
    """Main function to fix import order in all Python files."""
    base_dir = Path("/home/marlonsc/flext/flext-api")

    if not base_dir.exists():
        print(f"Directory {base_dir} does not exist")
        sys.exit(1)

    # Find all Python files with potential import order issues
    python_files = list(base_dir.rglob("*.py"))

    files_fixed = 0
    for py_file in python_files:
        if fix_import_order(py_file):
            files_fixed += 1

    print(f"\nFixed import order in {files_fixed} files")


if __name__ == "__main__":
    main()
