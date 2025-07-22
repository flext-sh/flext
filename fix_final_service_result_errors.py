#!/usr/bin/env python3
"""Final fix for remaining ServiceResult syntax errors.

This script addresses the remaining complex ServiceResult constructor patterns
that weren't caught by previous fixes.
"""

import os
import re
from pathlib import Path


def fix_remaining_service_result_patterns(content: str) -> str:
    """Fix remaining ServiceResult patterns."""
    # Fix pattern: ServiceResult[Any](success=False, \n    "error message",
    pattern1 = re.compile(
        r"ServiceResult\(success=False,\s*\n\s*([^,)]+),\s*\n\s*\)",
        re.MULTILINE | re.DOTALL
    )
    content = pattern1.sub(r"ServiceResult.fail(\1)", content)

    # Fix pattern: ServiceResult[Any](success=True, data)
    pattern2 = re.compile(
        r"ServiceResult\(success=True,\s+([^)]+)\)",
        re.MULTILINE
    )
    content = pattern2.sub(r"ServiceResult.ok(\1)", content)

    # Fix pattern: ServiceResult[Any](success=False, error)
    pattern3 = re.compile(
        r"ServiceResult\(success=False,\s+([^)]+)\)",
        re.MULTILINE
    )
    content = pattern3.sub(r"ServiceResult.fail(\1)", content)

    # Fix specific pattern: return_value=ServiceResult(success=True, 5)
    pattern4 = re.compile(
        r"ServiceResult\(success=True,\s*(\d+)\)",
        re.MULTILINE
    )
    content = pattern4.sub(r"ServiceResult.ok(\1)", content)

    # Fix import error: from flext_core.domain.shared_types EntityId, LogLevel
    # Should be: from flext_core.domain.shared_types import EntityId, LogLevel
    import_pattern = re.compile(
        r"from flext_core\.domain\.shared_types\s+([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)",
        re.MULTILINE
    )
    return import_pattern.sub(r"from flext_core.domain.shared_types import \1", content)



def fix_file(file_path: Path) -> bool:
    """Fix ServiceResult issues in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            original_content = f.read()

        # Only process files with ServiceResult constructor patterns or import issues
        if "ServiceResult(" not in original_content and "from flext_core.domain.shared_types " not in original_content:
            return False

        content = fix_remaining_service_result_patterns(original_content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False
    except Exception:
        return False


def main() -> None:
    """Main function to fix final ServiceResult errors."""
    workspace_root = Path("/home/marlonsc/flext")

    # Focus on projects that commonly have remaining issues
    project_patterns = [
        "client-a-oud-mig/**/*.py",
        "client-b-meltano-native/**/*.py",
        "flext-db-oracle/**/*.py",
        "flext-meltano/**/*.py",
    ]

    files_to_fix = []
    for pattern in project_patterns:
        files_to_fix.extend(workspace_root.glob(pattern))


    fixed_count = 0
    for file_path in files_to_fix:
        if fix_file(file_path):
            fixed_count += 1



if __name__ == "__main__":
    main()
