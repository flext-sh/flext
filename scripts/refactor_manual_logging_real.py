#!/usr/bin/env python3
"""Real script to refactor ALL manual logging setups in FLEXT ecosystem.

This script finds and replaces ALL instances of:
- import logging
- logger = get_logger(__name__)
- logging.getLogger() calls

With the standardized FLEXT pattern:
- from flext_core import get_logger
- logger = get_logger(__name__)

ZERO TOLERANCE - No partial fixes, all manual logging must be eliminated.
"""

import re
from pathlib import Path


def find_python_files(root_dir: Path) -> list[Path]:
    """Find all Python files to process."""
    python_files = []

    # Skip these directories completely
    skip_dirs = {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".git",
        ".venv",
        "venv",
        "node_modules",
        ".flext_backups",
    }

    for file_path in root_dir.rglob("*.py"):
        # Skip if any parent directory is in skip_dirs
        if any(part in skip_dirs for part in file_path.parts):
            continue

        # Skip the logging module itself - it's allowed to import logging
        if "patterns/logging.py" in str(file_path):
            print(f"⏭️  Skipping logging module: {file_path}")
            continue

        python_files.append(file_path)

    return python_files


def analyze_file(file_path: Path) -> tuple[bool, list[str]]:
    """Analyze a file for manual logging patterns."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return False, []

    issues = []
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()

        # Check for import logging
        if re.match(r"^import\s+logging\s*$", line_stripped):
            issues.append(f"Line {i}: import logging")

        # Check for from logging import
        if re.match(r"^from\s+logging\s+import", line_stripped):
            issues.append(f"Line {i}: from logging import ...")

        # Check for logging.getLogger() calls
        if "FlextLoggerFactory.get_logger(" in line:
            issues.append(f"Line {i}: FlextLoggerFactory.get_logger() call")

    return len(issues) > 0, issues


def refactor_file(file_path: Path) -> tuple[bool, list[str]]:
    """Refactor a single file to use FlextLoggerFactory."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError) as e:
        return False, [f"Failed to read file: {e}"]

    original_content = content
    changes = []

    # Pattern 1: Replace 'import logging' with FlextLoggerFactory import
    if re.search(r"^import\s+logging\s*$", content, re.MULTILINE):
        # Remove standalone 'import logging'
        content = re.sub(r"^import\s+logging\s*$\n?", "", content, flags=re.MULTILINE)

        # Add FlextLoggerFactory import if not present
        if (
            "from flext_core import get_logger" not in content
            and "FlextLoggerFactory" not in content
        ):
            # Find import section and add the import
            lines = content.split("\n")
            import_insert_index = 0

            # Find the best place to insert the import
            for i, line in enumerate(lines):
                if line.strip().startswith("from __future__"):
                    import_insert_index = i + 2  # After future imports + blank line
                elif line.strip().startswith('"""') or line.strip().startswith("'''"):
                    # Skip docstrings
                    continue
                elif line.strip().startswith("import ") or line.strip().startswith(
                    "from ",
                ):
                    import_insert_index = max(import_insert_index, i + 1)

            # Insert the import
            if import_insert_index < len(lines):
                lines.insert(import_insert_index, "")
                lines.insert(
                    import_insert_index + 1, "from flext_core import get_logger",
                )
            else:
                lines.append("")
                lines.append("from flext_core import get_logger")

            content = "\n".join(lines)

        changes.append("Replaced 'import logging' with FlextLoggerFactory import")

    # Pattern 2: Replace FlextLoggerFactory.get_logger(__name__) calls
    if "FlextLoggerFactory.get_logger(" in content:
        content = re.sub(
            r"logging\.getLogger\(__name__\)",
            "FlextLoggerFactory.get_logger(__name__)",
            content,
        )
        content = re.sub(
            r"logging\.getLogger\([^)]+\)",
            lambda m: m.group(0).replace(
                "logging.getLogger", "FlextLoggerFactory.get_logger",
            ),
            content,
        )
        changes.append(
            "Replaced logging.getLogger() calls with FlextLoggerFactory.get_logger()",
        )

    # Pattern 3: Handle logger = FlextLoggerFactory.get_logger() patterns
    content = re.sub(
        r"(\w+)\s*=\s*logging\.getLogger\(",
        r"\1 = FlextLoggerFactory.get_logger(",
        content,
    )

    # Only write if content changed
    if content != original_content:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, changes
        except PermissionError as e:
            return False, [f"Failed to write file: {e}"]

    return False, []


def main() -> None:
    """Main refactoring process."""
    print("🚀 Starting REAL manual logging refactoring across FLEXT ecosystem...")

    # Find all FLEXT project directories
    flext_root = Path("/home/marlonsc/flext")

    if not flext_root.exists():
        print(f"❌ FLEXT root directory not found: {flext_root}")
        return

    # Find all Python files in the ecosystem
    print("🔍 Finding Python files to analyze...")
    python_files = find_python_files(flext_root)
    print(f"📁 Found {len(python_files)} Python files to analyze")

    # Analyze files for manual logging patterns
    print("\n🔍 PHASE 1: Analyzing files for manual logging patterns...")
    files_with_issues = []
    total_issues = 0

    for file_path in python_files:
        has_issues, issues = analyze_file(file_path)
        if has_issues:
            files_with_issues.append((file_path, issues))
            total_issues += len(issues)

    print("\n📊 ANALYSIS RESULTS:")
    print(f"   Files with manual logging: {len(files_with_issues)}")
    print(f"   Total logging issues: {total_issues}")

    if not files_with_issues:
        print("✅ No manual logging patterns found!")
        return

    # Show first 10 files with issues
    print("\n📋 Files with manual logging (showing first 10):")
    for i, (file_path, issues) in enumerate(files_with_issues[:10]):
        rel_path = file_path.relative_to(flext_root)
        print(f"   📄 {rel_path}")
        for issue in issues[:3]:  # Show first 3 issues per file
            print(f"      🔸 {issue}")
        if len(issues) > 3:
            print(f"      ... and {len(issues) - 3} more issues")
        if i == 9 and len(files_with_issues) > 10:
            print(f"   ... and {len(files_with_issues) - 10} more files")

    # Refactor files
    print(f"\n🔧 PHASE 2: Refactoring {len(files_with_issues)} files...")
    refactored_count = 0
    failed_count = 0

    for file_path, _ in files_with_issues:
        rel_path = file_path.relative_to(flext_root)
        success, changes = refactor_file(file_path)

        if success:
            refactored_count += 1
            print(f"✅ {rel_path}")
            for change in changes:
                print(f"   🔸 {change}")
        else:
            failed_count += 1
            print(f"❌ {rel_path}")
            if changes:  # Error messages
                for error in changes:
                    print(f"   🔸 {error}")

    # Final verification
    print("\n🔍 PHASE 3: Final verification...")
    remaining_files = []

    for file_path in python_files:
        has_issues, issues = analyze_file(file_path)
        if has_issues:
            remaining_files.append((file_path, issues))

    print("\n📊 FINAL RESULTS:")
    print(f"   ✅ Files refactored: {refactored_count}")
    print(f"   ❌ Files failed: {failed_count}")
    print(f"   🔍 Files still with issues: {len(remaining_files)}")

    if remaining_files:
        print("\n⚠️  REMAINING ISSUES:")
        for file_path, issues in remaining_files[:5]:
            rel_path = file_path.relative_to(flext_root)
            print(f"   📄 {rel_path}")
            for issue in issues:
                print(f"      🔸 {issue}")

    if len(remaining_files) == 0:
        print("\n🎉 SUCCESS! All manual logging patterns eliminated!")
    else:
        print(f"\n⚠️  {len(remaining_files)} files still need manual attention")


if __name__ == "__main__":
    main()
