#!/usr/bin/env python3
"""Final ServiceResult Syntax Fix Script.

This script fixes all remaining ServiceResult syntax errors across the FLEXT workspace.
"""

import os
import re
import sys
from pathlib import Path


def find_python_files(root_dir: Path) -> list[Path]:
    """Find all Python files in the workspace."""
    python_files = []
    skip_dirs = {".git", ".mypy_cache", "__pycache__", ".pytest_cache", "node_modules", ".ruff_cache", ".venv"}

    for path in root_dir.rglob("*.py"):
        if any(part in skip_dirs for part in path.parts):
            continue
        python_files.append(path)

    return python_files

def fix_service_result_content(content: str) -> tuple[str, int]:
    """Fix ServiceResult syntax in content."""
    changes = 0

    # Pattern 1: ServiceResult.ok(X) -> ServiceResult.ok(X)
    pattern1 = re.compile(
        r"ServiceResult\s*\(\s*success\s*=\s*True\s*,\s*data\s*=\s*([^)]+)\s*\)",
        re.MULTILINE | re.DOTALL
    )
    content, count1 = pattern1.subn(r"ServiceResult.ok(\1)", content)
    changes += count1

    # Pattern 2: ServiceResult.ok(X) -> ServiceResult.ok(X)
    pattern2 = re.compile(
        r"ServiceResult\s*\(\s*data\s*=\s*([^,]+)\s*,\s*success\s*=\s*True\s*\)",
        re.MULTILINE | re.DOTALL
    )
    content, count2 = pattern2.subn(r"ServiceResult.ok(\1)", content)
    changes += count2

    # Pattern 3: ServiceResult.fail(X) -> ServiceResult.fail(X)
    pattern3 = re.compile(
        r"ServiceResult\s*\(\s*success\s*=\s*False\s*,\s*error\s*=\s*([^)]+)\s*\)",
        re.MULTILINE | re.DOTALL
    )
    content, count3 = pattern3.subn(r"ServiceResult.fail(\1)", content)
    changes += count3

    # Pattern 4: ServiceResult.fail(X) -> ServiceResult.fail(X)
    pattern4 = re.compile(
        r"ServiceResult\s*\(\s*error\s*=\s*([^,]+)\s*,\s*success\s*=\s*False\s*\)",
        re.MULTILINE | re.DOTALL
    )
    content, count4 = pattern4.subn(r"ServiceResult.fail(\1)", content)
    changes += count4

    return content, changes

def process_file(file_path: Path) -> tuple[bool, int]:
    """Process a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            original_content = f.read()

        if "ServiceResult(" not in original_content:
            return False, 0

        fixed_content, changes = fix_service_result_content(original_content)

        if changes > 0:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            return True, changes

        return False, 0

    except Exception:
        return False, 0

def main() -> int:
    """Main execution."""
    workspace_root = Path("/home/marlonsc/flext")


    python_files = find_python_files(workspace_root)

    total_files_fixed = 0
    total_changes = 0
    projects_fixed = set()

    for file_path in python_files:
        was_fixed, changes = process_file(file_path)

        if was_fixed:
            total_files_fixed += 1
            total_changes += changes

            relative_path = file_path.relative_to(workspace_root)
            project_name = relative_path.parts[0]
            projects_fixed.add(project_name)



    if projects_fixed:
        for _project in sorted(projects_fixed):
            pass

    # Verification
    remaining_count = 0
    for file_path in python_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            if re.search(r"ServiceResult\s*\(\s*success\s*=", content):
                remaining_count += 1
                relative_path = file_path.relative_to(workspace_root)
        except:
            pass

    if remaining_count == 0:
        pass
    else:
        pass

    return 0 if remaining_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
