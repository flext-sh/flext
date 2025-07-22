#!/usr/bin/env python3
"""ARCHITECTURAL FIX: ServiceResult[Any] Standardization Across FLEXT Workspace.

This script fixes the ServiceResult duplicate/inconsistent usage across all 33 projects:

1. Remove duplicated ServiceResult definitions
2. Standardize all imports to use flext_core.domain.shared_types.ServiceResult
3. Convert old syntax ServiceResult.ok(...) to ServiceResult.ok(...)
4. Convert old syntax ServiceResult.fail(...) to ServiceResult.fail(...)
5. Ensure consistent typing ServiceResult[T] usage

ZERO TOLERANCE: Every ServiceResult usage must be correct and consistent.
"""

import os
import re
import sys
from pathlib import Path


def find_python_files(root_path: Path) -> list[Path]:
    """Find all Python files in the workspace, excluding .venv and __pycache__."""
    python_files = []
    for root, dirs, files in os.walk(root_path):
        # Skip virtual environments and cache directories
        dirs[:] = [d for d in dirs if not d.startswith(".venv") and d != "__pycache__"]
        python_files.extend(Path(root) / file for file in files if file.endswith(".py"))
    return python_files


def fix_service_result_imports(content: str, file_path: Path) -> tuple[str, bool]:
    """Fix ServiceResult import statements."""
    modified = False

    # Pattern 1: Wrong root import
    wrong_import = r"^from flext_core import ServiceResult\s*$"
    if re.search(wrong_import, content, re.MULTILINE):
        content = re.sub(
            wrong_import,
            "from flext_core.domain.shared_types import ServiceResult",
            content,
            flags=re.MULTILINE,
        )
        modified = True

    # Pattern 2: Wrong shared_models import (should be shared_types)
    wrong_models_import = r"^from flext_core\.domain\.shared_models import.*ServiceResult.*$"
    if re.search(wrong_models_import, content, re.MULTILINE):
        content = re.sub(
            wrong_models_import,
            "from flext_core.domain.shared_types import ServiceResult",
            content,
            flags=re.MULTILINE,
        )
        modified = True

    return content, modified


def fix_service_result_syntax(content: str, file_path: Path) -> tuple[str, bool]:
    """Fix ServiceResult syntax from old constructor to factory methods."""
    modified = False

    # Pattern 1: ServiceResult[Any].ok(X) -> ServiceResult[Any].ok(X)
    success_pattern = r"ServiceResult\(success=True,\s*data=([^,)]+)(?:,\s*[^)]+)?\)"
    success_matches = re.findall(success_pattern, content)
    if success_matches:
        content = re.sub(
            success_pattern,
            r"ServiceResult.ok(\1)",
            content,
        )
        modified = True

    # Pattern 2: ServiceResult[Any].fail(X) -> ServiceResult[Any].fail(X)
    fail_pattern = r"ServiceResult\(success=False,\s*error=([^,)]+)(?:,\s*[^)]+)?\)"
    fail_matches = re.findall(fail_pattern, content)
    if fail_matches:
        content = re.sub(
            fail_pattern,
            r"ServiceResult.fail(\1)",
            content,
        )
        modified = True

    # Pattern 3: ServiceResult[Any].ok() -> ServiceResult[Any].ok()
    success_no_data_pattern = r"ServiceResult\(success=True\)"
    if re.search(success_no_data_pattern, content):
        content = re.sub(success_no_data_pattern, "ServiceResult.ok()", content)
        modified = True

    # Pattern 4: ServiceResult[Any].fail("Unknown error") -> ServiceResult[Any].fail("Unknown error")
    fail_no_error_pattern = r"ServiceResult\(success=False\)"
    if re.search(fail_no_error_pattern, content):
        content = re.sub(
            fail_no_error_pattern,
            'ServiceResult.fail("Unknown error")',
            content,
        )
        modified = True

    return content, modified


def remove_duplicate_service_result_definitions(content: str, file_path: Path) -> tuple[str, bool]:
    """Remove duplicate ServiceResult class definitions."""
    modified = False

    # Look for class ServiceResult definitions (but not in shared_types.py)
    if file_path.name != "shared_types.py":
        service_result_class_pattern = r"^class ServiceResult.*?(?=^class|\Z)"
        if re.search(service_result_class_pattern, content, re.MULTILINE | re.DOTALL):
            # Remove the duplicate class definition
            content = re.sub(
                service_result_class_pattern,
                "",
                content,
                flags=re.MULTILINE | re.DOTALL,
            )
            modified = True

    return content, modified


def fix_service_result_file(file_path: Path) -> bool:
    """Fix a single Python file for ServiceResult issues."""
    try:
        with open(file_path, encoding="utf-8") as f:
            original_content = f.read()

        content = original_content
        file_modified = False

        # Step 1: Fix imports
        content, imports_modified = fix_service_result_imports(content, file_path)
        file_modified = file_modified or imports_modified

        # Step 2: Fix syntax
        content, syntax_modified = fix_service_result_syntax(content, file_path)
        file_modified = file_modified or syntax_modified

        # Step 3: Remove duplicates (but not in shared_types.py)
        content, duplicates_modified = remove_duplicate_service_result_definitions(content, file_path)
        file_modified = file_modified or duplicates_modified

        # Write back if modified
        if file_modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception:
        return False


def main() -> None:
    """Main function to fix ServiceResult across the entire workspace."""
    workspace_root = Path("/home/marlonsc/flext")

    if not workspace_root.exists():
        sys.exit(1)

    # Find all Python files
    python_files = find_python_files(workspace_root)

    # Process each file
    modified_files = []
    for file_path in python_files:
        # Skip if file doesn't contain ServiceResult
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            if "ServiceResult" not in content:
                continue
        except:
            continue

        if fix_service_result_file(file_path):
            modified_files.append(file_path)

    # Summary

    if modified_files:
        for file_path in modified_files[:10]:  # Show first 10
            pass
        if len(modified_files) > 10:
            pass


if __name__ == "__main__":
    main()
