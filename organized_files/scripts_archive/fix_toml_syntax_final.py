#!/usr/bin/env python3
"""Fix TOML syntax errors in all pyproject.toml files."""

import glob
import re
from pathlib import Path


def fix_toml_syntax(file_path):
    """Fix common TOML syntax errors."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix the specific "]select = ["ALL"]" pattern
        content = re.sub(r'\]select = \["ALL"\]', ']\nselect = ["ALL"]', content)

        # Fix any other malformed array endings
        content = re.sub(r"\](\w+) = ", r"]\n\1 = ", content)

        # Fix incomplete sections
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Skip empty lines at start of processing
            if not fixed_lines and not line.strip():
                continue

            # Handle lines that look like they got merged incorrectly
            if "]" in line and " = " in line and not line.strip().startswith("["):
                # Split at the first ']'
                parts = line.split("]", 1)
                if len(parts) == 2:
                    fixed_lines.append(parts[0] + "]")
                    remaining = parts[1].strip()
                    if remaining:
                        fixed_lines.append(remaining)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        # Remove excessive empty lines
        final_lines = []
        prev_empty = False
        for line in fixed_lines:
            is_empty = not line.strip()
            if is_empty and prev_empty:
                continue
            final_lines.append(line)
            prev_empty = is_empty

        # Ensure file ends with single newline
        while final_lines and not final_lines[-1].strip():
            final_lines.pop()

        content = "\n".join(final_lines) + "\n"

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Fix all problematic TOML files."""
    problem_files = [
        "legacy/flx-meltano-enterprise/pyproject.toml",
        "legacy/flx/pyproject.toml",
        "legacy/flx-database-oracle/pyproject.toml",
        "flext-tap-ldap/pyproject.toml",
        "flext-tap-oracle-oic/pyproject.toml",
        "flext-target-ldap/pyproject.toml",
        "flext-target-oracle-oic/pyproject.toml",
        "flext-dbt-ldap/pyproject.toml",
        "flext-oracle-oic-ext/pyproject.toml",
        "gruponos-poc-oic-wms/pyproject.toml",
        "flext-quality/pyproject.toml"
    ]

    fixed_count = 0
    for file_path in problem_files:
        if Path(file_path).exists():
            print(f"🔧 Fixing {file_path}...")
            if fix_toml_syntax(file_path):
                fixed_count += 1
                print("   ✅ Fixed")
            else:
                print("   ℹ️  No changes needed")
        else:
            print("   ⚠️  File not found")

    print(f"\n📊 Summary: {fixed_count} files modified")


if __name__ == "__main__":
    main()
