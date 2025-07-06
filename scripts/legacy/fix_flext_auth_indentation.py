#!/usr/bin/env python3
"""Fix indentation issues in flext-auth specifically."""

import re
from pathlib import Path


def fix_docstring_indentation(file_path: Path) -> bool:
    """Fix docstring indentation issues."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Fix common indentation patterns
        patterns = [
            # Fix docstrings that start with wrong indentation
            (r'(\n    def [^:\n]+:\n)       """([^"]+)"""', r'\1        """\2"""'),
            # Fix other indentation issues
            (r'(\n       )"""([^"]+)"""', r'\1        """\2"""'),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            print(f"✅ Fixed indentation in {file_path}")
            return True
        return False

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main() -> None:
    """Main function."""
    flext_auth_path = Path("flext-auth/src")

    if not flext_auth_path.exists():
        print("❌ flext-auth/src directory not found")
        return

    fixed_count = 0
    for py_file in flext_auth_path.rglob("*.py"):
        if fix_docstring_indentation(py_file):
            fixed_count += 1

    print(f"🎯 Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
