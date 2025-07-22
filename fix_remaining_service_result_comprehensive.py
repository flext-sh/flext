#!/usr/bin/env python3
"""Comprehensive ServiceResult Syntax Fix Script - Final Cleanup.

This script handles all remaining ServiceResult syntax errors across the FLEXT workspace.
Focus areas:
1. Complex ServiceResult constructor patterns
2. Integration test complex scenarios
3. Edge cases from previous automated fixes
4. Ensure 100% ServiceResult API compliance across all 33 projects

Copyright (c) 2025 FLEXT Team
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def find_all_python_files(root_dir: Path) -> list[Path]:
    """Find all Python files in the workspace."""
    python_files = []

    # Skip these directories entirely
    skip_dirs = {".git", ".mypy_cache", "__pycache__", ".pytest_cache", "node_modules", ".ruff_cache", ".venv"}

    for path in root_dir.rglob("*.py"):
        # Check if any parent directory should be skipped
        if any(part in skip_dirs for part in path.parts):
            continue
        python_files.append(path)

    return python_files

def analyze_service_result_patterns(content: str) -> list[tuple[str, int, str]]:
    """Find all problematic ServiceResult patterns in file content."""
    issues = []
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        # Pattern 1: ServiceResult.ok(...)
        if re.search(r"ServiceResult\s*\(\s*success\s*=\s*True\s*,\s*data\s*=", line):
            issues.append(("old_success_true", i, line.strip()))

        # Pattern 2: ServiceResult.fail(...)
        elif re.search(r"ServiceResult\s*\(\s*success\s*=\s*False\s*,\s*error\s*=", line):
            issues.append(("old_success_false", i, line.strip()))

        # Pattern 3: ServiceResult.ok(...)
        elif re.search(r"ServiceResult\s*\(\s*data\s*=.*,\s*success\s*=\s*True", line):
            issues.append(("old_data_success_true", i, line.strip()))

        # Pattern 4: ServiceResult.fail(...)
        elif re.search(r"ServiceResult\s*\(\s*error\s*=.*,\s*success\s*=\s*False", line):
            issues.append(("old_error_success_false", i, line.strip()))

        # Pattern 5: Complex nested ServiceResult constructors
        elif re.search(r"ServiceResult\s*\(\s*success\s*=.*,.*=.*,.*\)", line):
            issues.append(("complex_constructor", i, line.strip()))

        # Pattern 6: ServiceResult with multiple parameters
        elif "ServiceResult(" in line and ("success=" in line or ("data=" in line and "error=" in line)):
            issues.append(("multi_param_constructor", i, line.strip()))

    return issues

def fix_service_result_line(line: str) -> str:
    """Fix ServiceResult syntax on a single line."""
    # Pattern 1: ServiceResult.ok(X) -> ServiceResult.ok(X)
    line = re.sub(
        r"ServiceResult\s*\(\s*success\s*=\s*True\s*,\s*data\s*=\s*([^)]+)\s*\)",
        r"ServiceResult.ok(\1)",
        line
    )

    # Pattern 2: ServiceResult.ok(X) -> ServiceResult.ok(X)
    line = re.sub(
        r"ServiceResult\s*\(\s*data\s*=\s*([^,]+)\s*,\s*success\s*=\s*True\s*\)",
        r"ServiceResult.ok(\1)",
        line
    )

    # Pattern 3: ServiceResult.fail(X) -> ServiceResult.fail(X)
    line = re.sub(
        r"ServiceResult\s*\(\s*success\s*=\s*False\s*,\s*error\s*=\s*([^)]+)\s*\)",
        r"ServiceResult.fail(\1)",
        line
    )

    # Pattern 4: ServiceResult.fail(X) -> ServiceResult.fail(X)
    line = re.sub(
        r"ServiceResult\s*\(\s*error\s*=\s*([^,]+)\s*,\s*success\s*=\s*False\s*\)",
        r"ServiceResult.fail(\1)",
        line
    )

    # Pattern 5: Handle complex multi-line cases - extract just the data/error part
    # ServiceResult.ok({...}) -> ServiceResult.ok({...})
    complex_success_match = re.search(r"ServiceResult\s*\(\s*success\s*=\s*True\s*,\s*data\s*=\s*(.+)\s*\)$", line)
    if complex_success_match:
        data_part = complex_success_match.group(1)
        line = re.sub(
            r"ServiceResult\s*\(\s*success\s*=\s*True\s*,\s*data\s*=\s*.+\s*\)$",
            f"ServiceResult.ok({data_part})",
            line
        )

    # ServiceResult.fail(X) -> ServiceResult.fail(X) for complex cases
    complex_error_match = re.search(r"ServiceResult\s*\(\s*success\s*=\s*False\s*,\s*error\s*=\s*(.+)\s*\)$", line)
    if complex_error_match:
        error_part = complex_error_match.group(1)
        line = re.sub(
            r"ServiceResult\s*\(\s*success\s*=\s*False\s*,\s*error\s*=\s*.+\s*\)$",
            f"ServiceResult.fail({error_part})",
            line
        )

    return line

def fix_multiline_service_result(content: str) -> str:
    """Fix multiline ServiceResult constructors."""
    # Pattern 1: Multiline ServiceResult.ok(...)
    pattern1 = re.compile(
        r"ServiceResult\s*\(\s*success\s*=\s*True\s*,\s*data\s*=\s*([^)]*(?:\([^)]*\)[^)]*)*)\s*\)",
        re.MULTILINE | re.DOTALL
    )

    def replace1(match) -> str:
        data_content = match.group(1).strip()
        # Remove trailing comma if present
        data_content = re.sub(r",\s*$", "", data_content)
        return f"ServiceResult.ok({data_content})"

    content = pattern1.sub(replace1, content)

    # Pattern 2: Multiline ServiceResult.fail(...)
    pattern2 = re.compile(
        r"ServiceResult\s*\(\s*success\s*=\s*False\s*,\s*error\s*=\s*([^)]*(?:\([^)]*\)[^)]*)*)\s*\)",
        re.MULTILINE | re.DOTALL
    )

    def replace2(match) -> str:
        error_content = match.group(1).strip()
        # Remove trailing comma if present
        error_content = re.sub(r",\s*$", "", error_content)
        return f"ServiceResult.fail({error_content})"

    content = pattern2.sub(replace2, content)

    # Pattern 3: Handle data-first patterns - ServiceResult.ok(X)
    pattern3 = re.compile(
        r"ServiceResult\s*\(\s*data\s*=\s*([^,]*(?:\([^)]*\)[^,]*)*)\s*,\s*success\s*=\s*True\s*\)",
        re.MULTILINE | re.DOTALL
    )

    def replace3(match) -> str:
        data_content = match.group(1).strip()
        return f"ServiceResult.ok({data_content})"

    content = pattern3.sub(replace3, content)

    # Pattern 4: Handle error-first patterns - ServiceResult.fail(X)
    pattern4 = re.compile(
        r"ServiceResult\s*\(\s*error\s*=\s*([^,]*(?:\([^)]*\)[^,]*)*)\s*,\s*success\s*=\s*False\s*\)",
        re.MULTILINE | re.DOTALL
    )

    def replace4(match) -> str:
        error_content = match.group(1).strip()
        return f"ServiceResult.fail({error_content})"

    return pattern4.sub(replace4, content)


def process_file(file_path: Path) -> tuple[bool, list[str]]:
    """Process a single file and fix ServiceResult syntax."""
    try:
        with open(file_path, encoding="utf-8") as f:
            original_content = f.read()

        # Skip if no ServiceResult usage
        if "ServiceResult(" not in original_content:
            return False, []

        # Analyze issues before fixing
        issues = analyze_service_result_patterns(original_content)
        if not issues:
            return False, []

        # Apply fixes
        content = original_content

        # Fix multiline patterns first
        content = fix_multiline_service_result(content)

        # Fix line by line
        lines = content.split("\n")
        fixed_lines = []
        changes = []

        for i, line in enumerate(lines):
            if "ServiceResult(" in line and ("success=" in line or ("data=" in line and "error=" in line)):
                fixed_line = fix_service_result_line(line)
                if fixed_line != line:
                    changes.append(f"Line {i+1}: {line.strip()} -> {fixed_line.strip()}")
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        final_content = "\n".join(fixed_lines)

        # Only write if content changed
        if final_content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_content)
            return True, changes

        return False, []

    except Exception as e:
        return False, [f"Error processing {file_path}: {e}"]

def main() -> int:
    """Main execution function."""
    workspace_root = Path("/home/marlonsc/flext")

    if not workspace_root.exists():
        sys.exit(1)


    # Find all Python files
    python_files = find_all_python_files(workspace_root)

    # Process files
    total_files_processed = 0
    total_changes = 0
    errors = []
    projects_with_fixes = set()

    for file_path in python_files:
        was_modified, changes = process_file(file_path)

        if was_modified:
            total_files_processed += 1
            total_changes += len(changes)

            # Extract project name
            relative_path = file_path.relative_to(workspace_root)
            project_name = relative_path.parts[0]
            projects_with_fixes.add(project_name)

            for _change in changes[:3]:  # Show first 3 changes
                pass
            if len(changes) > 3:
                pass

        elif changes:  # Errors
            errors.extend(changes)

    # Summary

    if projects_with_fixes:
        for _project in sorted(projects_with_fixes):
            pass

    if errors:
        for _error in errors[:10]:  # Show first 10 errors
            pass
        if len(errors) > 10:
            pass

    # Verification
    remaining_count = 0
    for file_path in python_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check for problematic patterns
            if re.search(r"ServiceResult\s*\(\s*success\s*=", content):
                remaining_count += 1
        except:
            pass

    if remaining_count == 0:
        pass
    else:
        pass

    return 0 if remaining_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
