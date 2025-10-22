#!/usr/bin/env python3
"""Pre-commit hook: Block Pydantic v1 patterns from being committed.

This hook prevents Pydantic v1 patterns from entering the codebase.
It runs automatically before commits when pre-commit is installed.

Usage:
    # Install hooks (one-time setup)
    pre-commit install

    # Run manually on all files
    pre-commit run --all-files

    # Run on specific files
    pre-commit run check-pydantic-v2 -- src/module.py

Copyright (c) 2025 FLEXT Team. All rights reserved.
"""

import re
import sys
from pathlib import Path

# CRITICAL: Pydantic v1 patterns that MUST NOT be committed
FORBIDDEN_PATTERNS = [
    (r"class\s+\w+.*:\s*\n\s*class\s+Config:", "Use model_config = ConfigDict()"),
    (r"\.dict\(\)", "Use .model_dump()"),
    (r"\.json\(\)", "Use .model_dump_json()"),
    (r"parse_obj\(", "Use .model_validate()"),
    (r"@validator\(", "Use @field_validator()"),
    (r"@root_validator", "Use @model_validator()"),
]

# Validators that were removed in Phase 3 (regression prevention)
REMOVED_VALIDATORS = [
    "validate_port",
    "validate_email",
    "validate_url",
    "validate_positive_integer",
    "validate_non_negative_integer",
    "validate_string_length",
    "validate_string_pattern",
    "validate_file_path",
    "validate_directory_path",
    "validate_timeout_seconds",
    "validate_retry_count",
    "validate_log_level",
    "validate_string_not_none",
    "validate_string_not_empty",
    "validate_string",
    "validate_host",
]


def check_file(filepath: str) -> bool:
    """Check file for forbidden Pydantic v1 patterns.

    Args:
        filepath: Path to Python file to check

    Returns:
        True if file is valid, False if violations found

    """
    try:
        with Path(filepath).open(encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️  Could not read {filepath}: {e}")
        return True  # Don't block on read errors

    passed = True
    lines = content.split("\n")

    # Check critical patterns
    for pattern, message in FORBIDDEN_PATTERNS:
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line):
                print(f"❌ {filepath}:{line_num}: {message}")
                print(f"   {line.strip()}")
                passed = False

    # Check for removed validators (regression prevention)
    for validator_name in REMOVED_VALIDATORS:
        pattern = rf"def {validator_name}\("
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line):
                print(
                    f"❌ {filepath}:{line_num}: REGRESSION - Removed validator reappeared: {validator_name}"
                )
                print(f"   {line.strip()}")
                print(
                    "   This validator was removed in Phase 3. Use Pydantic v2 native types instead."
                )
                passed = False

    return passed


def main() -> int:
    """Main entry point.

    Returns:
        0 if all files pass, 1 if any violations found

    """
    if len(sys.argv) < 2:
        print("❌ No files provided")
        return 1

    all_passed = True
    for filepath in sys.argv[1:]:
        # Skip non-Python files
        if not filepath.endswith(".py"):
            continue

        # Skip test files and fixtures (they may have examples of bad patterns)
        if "test" in filepath or "fixture" in filepath:
            continue

        if not check_file(filepath):
            all_passed = False

    if not all_passed:
        print("\n" + "=" * 70)
        print("❌ COMMIT BLOCKED: Pydantic v1 patterns detected")
        print("=" * 70)
        print("\nFix these patterns before committing:")
        print("  • class Config: → model_config = ConfigDict()")
        print("  • .dict() → .model_dump()")
        print("  • .json() → .model_dump_json()")
        print("  • parse_obj() → .model_validate()")
        print("  • @validator → @field_validator()")
        print("  • @root_validator → @model_validator()")
        print("\nFor details, see: docs/pydantic-v2-modernization/")
        print("=" * 70)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
