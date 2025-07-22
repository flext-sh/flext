#!/usr/bin/env python3
"""Fix remaining ServiceResult syntax errors - focused on integration tests.

This script fixes the complex multi-line ServiceResult constructor patterns
that the previous script missed, particularly in integration tests.
"""

import os
import re
from pathlib import Path


def fix_complex_service_result_patterns(content: str) -> str:
    """Fix complex ServiceResult patterns that span multiple lines."""
    # Pattern 1: ServiceResult[Any](success=True, \n    data...)
    pattern1 = re.compile(
        r"ServiceResult\(success=True,\s*\n\s*([^)]+)\)",
        re.MULTILINE | re.DOTALL
    )
    content = pattern1.sub(r"ServiceResult.ok(\1)", content)

    # Pattern 2: ServiceResult[Any](success=False, \n    error...)
    pattern2 = re.compile(
        r"ServiceResult\(success=False,\s*\n\s*([^)]+)\)",
        re.MULTILINE | re.DOTALL
    )
    content = pattern2.sub(r"ServiceResult.fail(\1)", content)

    # Pattern 3: Fix trailing whitespace after success=True/False,
    pattern3 = re.compile(
        r"ServiceResult\(success=(True|False),\s*\n",
        re.MULTILINE
    )

    def replace_pattern3(match) -> str:
        success = match.group(1)
        if success == "True":
            return "ServiceResult.ok("
        return "ServiceResult.fail("

    return pattern3.sub(replace_pattern3, content)



def fix_file(file_path: Path) -> bool:
    """Fix ServiceResult issues in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            original_content = f.read()

        # Only process files with ServiceResult
        if "ServiceResult(" not in original_content:
            return False

        content = fix_complex_service_result_patterns(original_content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False
    except Exception:
        return False


def main() -> None:
    """Main function to fix remaining ServiceResult errors."""
    workspace_root = Path("/home/marlonsc/flext")

    # Focus on integration test files that commonly have complex patterns
    integration_test_patterns = [
        "**/tests/integration/**/*.py",
        "**/tests/unit/**/*.py",
        "**/src/**/sql/*.py",  # SQL modules often have complex ServiceResult usage
        "**/src/**/compare/*.py",  # Comparison modules
    ]

    files_to_fix = []
    for pattern in integration_test_patterns:
        files_to_fix.extend(workspace_root.glob(pattern))


    fixed_count = 0
    for file_path in files_to_fix:
        if fix_file(file_path):
            fixed_count += 1



if __name__ == "__main__":
    main()
