#!/usr/bin/env python3
"""Script to refactor manual logging setups to use FLEXT patterns.

This script finds all Python files that use manual logging setup
(logger = FlextLoggerFactory.get_logger(__name__)) and refactors them to use
FlextLoggerFactory from flext-core.
"""

import re
import subprocess


def find_files_with_manual_logging():
    """Find all Python files with manual logging setup."""
    cmd = [
        "find", ".",
        "-name", "*.py",
        "-exec", "grep", "-l", "logger = logging\\.getLogger", "{}", ";",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return [line.strip() for line in result.stdout.split("\n") if line.strip()]
    except subprocess.CalledProcessError:
        return []


def refactor_file(file_path: str) -> bool:
    """Refactor a single file to use FLEXT logging patterns."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Replace import logging with FlextLoggerFactory import
        content = re.sub(
            r"^import logging\n",
            "",
            content,
            flags=re.MULTILINE,
        )

        # Add FlextLoggerFactory import if not present
        if "FlextLoggerFactory" not in content:
            # Find the from flext_core import line and add to it
            if "from flext_core import" in content:
                content = re.sub(
                    r"(from flext_core import [^)]*?)(FlextResult)",
                    r"\1FlextLoggerFactory, \2",
                    content,
                )
            else:
                # Add new import line after other imports
                import_pattern = r"(from __future__ import annotations\n\n)(.*?)(from [^f].*?\n)"
                match = re.search(import_pattern, content, re.DOTALL)
                if match:
                    content = content.replace(
                        match.group(0),
                        f"{match.group(1)}{match.group(2)}from flext_core import FlextLoggerFactory\n{match.group(3)}",
                    )

        # Replace logger = FlextLoggerFactory.get_logger(__name__)
        content = re.sub(
            r"logger = logging\.getLogger\(__name__\)",
            "logger = FlextLoggerFactory.get_logger(__name__)",
            content,
        )

        # Remove unused logging import lines
        content = re.sub(r"^import logging\n", "", content, flags=re.MULTILINE)
        content = re.sub(r"^from logging import .*?\n", "", content, flags=re.MULTILINE)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Refactored: {file_path}")
            return True
        print(f"⏭️ No changes needed: {file_path}")
        return False

    except Exception as e:
        print(f"❌ Error refactoring {file_path}: {e}")
        return False


def main():
    """Main refactoring function."""
    print("🔍 Finding files with manual logging setup...")
    files = find_files_with_manual_logging()

    if not files:
        print("✅ No files found with manual logging setup!")
        return

    print(f"📄 Found {len(files)} files to refactor")

    refactored_count = 0
    for file_path in files:
        if refactor_file(file_path):
            refactored_count += 1

    print("\n✅ Refactoring complete!")
    print(f"📊 Refactored {refactored_count} out of {len(files)} files")


if __name__ == "__main__":
    main()
