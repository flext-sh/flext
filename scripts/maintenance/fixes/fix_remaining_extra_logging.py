#!/usr/bin/env python3
"""
Script para corrigir todas as ocorrências restantes de extra= em logging do projeto FLX.
"""

import re
from pathlib import Path


def fix_logging_extra(file_path):
    """Fix logging calls with extra= parameter in a file."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Pattern 1: Simple extra= with single dict items
    pattern1 = r'logger\.(\w+)\(\s*"([^"]+)",\s*extra=\{([^}]+)\}\s*\)'

    def replace_simple_extra(match):
        method = match.group(1)
        message = match.group(2)
        extra_content = match.group(3)

        # Extract key-value pairs from extra dict
        pairs = re.findall(r'"([^"]+)":\s*([^,}]+)', extra_content)
        if not pairs:
            return f'logger.{method}("{message}")'

        # Create formatted message with placeholders
        placeholders = []
        values = []
        for key, value in pairs:
            placeholders.append(f"{key}: %s")
            values.append(value.strip())

        new_message = f"{message} - {', '.join(placeholders)}"
        new_values = ", ".join(values)

        return f'logger.{method}("{new_message}", {new_values})'

    content = re.sub(pattern1, replace_simple_extra, content)

    # Pattern 2: Simple single line extra= without complex nesting
    pattern2 = r'logger\.(\w+)\(\s*"([^"]+)",\s*extra=([^)]+)\)'

    def replace_simple_single_line(match):
        method = match.group(1)
        message = match.group(2)
        extra_param = match.group(3).strip()

        if extra_param.startswith("{") and extra_param.endswith("}"):
            # It's a dict literal, try to parse simple cases
            inner = extra_param[1:-1].strip()
            if '"' in inner and ":" in inner:
                # Extract simple key-value pairs
                pairs = re.findall(r'"([^"]+)":\s*([^,}]+)', inner)
                if pairs:
                    placeholders = []
                    values = []
                    for key, value in pairs:
                        placeholders.append(f"{key}: %s")
                        values.append(value.strip())

                    new_message = f"{message} - {', '.join(placeholders)}"
                    new_values = ", ".join(values)

                    return f'logger.{method}("{new_message}", {new_values})'

        # For complex cases or variables, just pass the variable
        if not extra_param.startswith("{"):
            # It's likely a variable
            return f'logger.{method}("{message} - Data: %s", {extra_param})'

        return f'logger.{method}("{message}")'

    content = re.sub(pattern2, replace_simple_single_line, content)

    # Pattern 3: Multi-line logging with extra=
    # This is more complex, we'll handle specific known patterns

    # Fix exception logging with extra
    exception_pattern = (
        r'logger\.exception\(\s*"([^"]+)",\s*extra=\{[^}]*"error_type"[^}]*\}[^)]*\)'
    )
    content = re.sub(exception_pattern, r'logger.exception("\1")', content)

    # Fix multi-line extra= patterns (simple approach)
    multiline_pattern = r'(\s+logger\.\w+\(\s*"[^"]+",)\s*extra=\{[^}]*\}([^)]*\))'
    content = re.sub(multiline_pattern, r"\1\2", content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed logging in {file_path}")
        return True

    return False


def main():
    """Main function to fix all files."""
    flx_dir = Path("/home/marlonsc/pyauto/flx")

    # Files to fix
    files_to_fix = [
        "examples/advanced/declarative_example.py",
    ]

    fixed_files = []

    for file_path in files_to_fix:
        full_path = flx_dir / file_path
        if full_path.exists() and fix_logging_extra(full_path):
            fixed_files.append(str(full_path))

    print(f"\nFixed {len(fixed_files)} files:")
    for file_path in fixed_files:
        print(f"  - {file_path}")


if __name__ == "__main__":
    main()
