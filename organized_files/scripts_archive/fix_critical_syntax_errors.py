#!/usr/bin/env python3
"""Fix critical syntax errors introduced by the automated fix script."""

import os
import re
from pathlib import Path


def fix_syntax_errors(file_path: str) -> bool:
    """Fix critical syntax errors in Python files."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return False

    original_content = content

    # Fix invalid class inheritance (Union without imports)
    content = re.sub(r"class (\w+)\([^)]+, Union\):", r"class \1(\2):", content)
    content = re.sub(r"class (\w+)\(Union\):", r"class \1:", content)

    # Fix logger with Union parameter
    content = re.sub(r"logger = logging\.getLogger\([^)]+, Union\)", r"logger = logging.getLogger(__name__)", content)

    # Fix function definitions with Union parameter
    content = re.sub(r"def __init__\([^)]+, Union\) -> None:", r"def __init__(self, config: dict[str, Any], logger: Any = None) -> None:", content)

    # Fix broken import lines
    content = re.sub(r"from \.discovery import \([^)]+, Union\)", r"from .discovery import (\n    AuthenticationError,\n    EntityDescriptionError,\n    EntityDiscovery,\n    EntityDiscoveryError,\n    NetworkError,\n    SchemaGenerationError,\n    SchemaGenerator,\n)", content)

    # Fix broken import lines with comma-Union
    content = re.sub(r"(\w+),\s*Union\)", r"\1)", content)

    # Fix broken tuple assignment with Union
    content = re.sub(r"(\w+): Union\[([^\]]+)\]", r"\1: \2", content)

    # Fix malformed docstring placement
    content = re.sub(r'def (\w+)\(\s*"""TODO: Add docstring\."""\s*self,', r"def \1(\n        self,", content)
    content = re.sub(r'def (\w+)\(\s*"""TODO: Add docstring\."""', r"def \1(", content)

    # Fix invalid parameter definitions
    content = re.sub(r'def (\w+)\(\s*"""TODO: Add docstring\."""\s*([^)]+)\)', r"def \1(\2)", content)

    # Fix misplaced docstrings in function signatures
    lines = content.split("\n")
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Look for function definitions followed by misplaced docstrings
        if re.match(r"\s*def\s+\w+\(", line) and '"""TODO: Add docstring."""' in line:
            # Extract the function definition part
            func_def = re.sub(r'\s*"""TODO: Add docstring\."""\s*', "", line)
            new_lines.append(func_def)

            # Add proper docstring after function definition
            if i + 1 < len(lines) and lines[i + 1].strip() != '"""TODO: Add docstring."""':
                new_lines.append('        """TODO: Add docstring."""')
        else:
            new_lines.append(line)

        i += 1

    content = "\n".join(new_lines)

    # Fix broken type hints
    content = re.sub(r"Union\[([^,\]]+),\s*None\]", r"\1 | None", content)
    content = re.sub(r"Union\[([^,\]]+),\s*([^,\]]+)\]", r"\1 | \2", content)

    # Add missing Union import if needed
    if "Union[" in content and "from typing import" in content and "Union" not in content:
        content = re.sub(
            r"(from typing import[^)]*)",
            r"\1, Union",
            content
        )

    if content != original_content:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception:
            return False

    return False


def main():
    """Fix critical syntax errors in all Python files."""
    projects = [
        "/home/marlonsc/flext/flext-tap-oracle-wms",
        "/home/marlonsc/flext/flext-target-oracle",
        "/home/marlonsc/flext/gruponos-meltano-native"
    ]

    total_fixed = 0

    for project in projects:
        if os.path.exists(project):
            print(f"\n🔧 Fixing syntax errors in {project}")

            python_files = list(Path(project).rglob("*.py"))
            fixed_count = 0

            for py_file in python_files:
                if "backup" in str(py_file) or ".venv" in str(py_file):
                    continue

                if fix_syntax_errors(str(py_file)):
                    fixed_count += 1
                    if fixed_count % 10 == 0:
                        print(f"  Fixed {fixed_count} files...")

            print(f"✅ Fixed {fixed_count} files in {os.path.basename(project)}")
            total_fixed += fixed_count

    print(f"\n📊 Total files fixed: {total_fixed}")


if __name__ == "__main__":
    main()
