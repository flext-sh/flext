#!/usr/bin/env python3
"""Fix unbalanced quotes and invalid characters in TOML files."""

import re
from pathlib import Path


def fix_toml_quotes(file_path):
    """Fix quote and syntax issues in TOML files."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix unbalanced quotes in comments
        content = re.sub(r'"T201",\s*log\.error statements \(temporarily\)', '"T201",  # log.error statements (temporarily)', content)
        content = re.sub(r'"(\w+)",\s*([^#][^"]*)\s*$', r'"\1",  # \2', content, flags=re.MULTILINE)

        # Fix unbalanced quotes in multi-line arrays
        lines = content.split("\n")
        fixed_lines = []
        in_array = False

        for line in lines:
            stripped = line.strip()

            # Detect array start
            if "[" in stripped and not stripped.startswith("[tool"):
                in_array = True

            # Fix unbalanced quotes in array items
            if in_array and stripped:
                # Fix comments without quotes
                if ', version = "' in line and "} # " not in line:
                    # This is fine, poetry format
                    pass
                elif '"' in stripped and not stripped.startswith("#"):
                    # Check for unbalanced quotes in comments
                    if stripped.count('"') % 2 != 0:
                        # Try to fix common patterns
                        if "# " in stripped and not stripped.endswith('"'):
                            # Comment without proper quote handling
                            parts = stripped.split("# ", 1)
                            if len(parts) == 2:
                                line = line.replace("# " + parts[1], "  # " + parts[1])

            # Detect array end
            if "]" in stripped and in_array:
                in_array = False

            fixed_lines.append(line)

        content = "\n".join(fixed_lines)

        # Fix specific patterns that cause issues
        content = re.sub(r'bandit = \{ extras = \["toml"\]\n, version = "([^"]+)" \}',
                        r'bandit = { extras = ["toml"], version = "\1" }', content)

        # Fix log.error patterns specifically
        content = re.sub(r'"T201",\s*log\.error statements \([^)]*\)', '"T201",  # log.error statements (temporarily)', content)

        # Fix other unquoted comments
        content = re.sub(r'"([^"]+)",\s*([^#\n][^\n]*?)(?=\n|$)', r'"\1",  # \2', content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Fix all remaining problematic files."""
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
        "client-b-poc-oic-wms/pyproject.toml",
        "flext-quality/pyproject.toml"
    ]

    fixed_count = 0
    for file_path in problem_files:
        if Path(file_path).exists():
            print(f"🔧 Fixing quotes in {file_path}...")
            if fix_toml_quotes(file_path):
                fixed_count += 1
                print("   ✅ Fixed")
            else:
                print("   ℹ️  No changes needed")
        else:
            print("   ⚠️  File not found")

    print(f"\n📊 Summary: {fixed_count} files modified")


if __name__ == "__main__":
    main()
