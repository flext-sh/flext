#!/usr/bin/env python3
"""Fix specific mypy errors in FLX codebase based on error analysis."""

import json
import re
import subprocess
from pathlib import Path


def get_mypy_errors() -> list[dict[str, any]]:
    """Run mypy and parse errors."""
    result = subprocess.run(
        ["mypy", "flx/src/", "--show-error-codes", "--no-error-summary"],
        capture_output=True,
        text=True,
        check=False,
    )

    errors: list = []
    for line in result.stdout.split("\n"):
        if not line.strip():
            continue

        # Parse error format: file:line: error: message [error-code]
        match = re.match(r"^(.+?):(\d+): error: (.+?) \[(.+?)\]$", line)
        if match:
            filepath, line_num, message, error_code = match.groups()

            # Extract suggestion if present
            suggestion = None
            if 'maybe "' in message:
                suggestion_match = re.search(r'maybe "([^"]+)"', message)
                if suggestion_match:
                    suggestion = suggestion_match.group(1)

            errors.append(
                {
                    "file": filepath,
                    "line": int(line_num),
                    "message": message,
                    "code": error_code,
                    "suggestion": suggestion,
                }
            )

    return errors


def fix_attr_defined_errors(errors: list[dict], dry_run: bool = False) -> int:
    """Fix attr-defined errors with suggestions."""
    fixes_by_file: dict[str, list[tuple[int, str, str]]] = {}

    for error in errors:
        if error["code"] == "attr-defined" and error["suggestion"]:
            filepath = error["file"]
            if filepath not in fixes_by_file:
                fixes_by_file[filepath] = []

            # Extract what needs to be replaced
            message = error["message"]

            # Pattern 1: "ClassName" has no attribute "method"; maybe
            # "flx_method"?
            match1 = re.search(
                r'"([^"]+)" has no attribute "([^"]+)"; maybe "([^"]+)"', message
            )
            if match1:
                _class_name, old_attr, new_attr = match1.groups()
                fixes_by_file[filepath].append((error["line"], old_attr, new_attr))
                continue

            # Pattern 2: Module "x" has no attribute "y"; maybe "z"?
            match2 = re.search(
                r'Module "[^"]+" has no attribute "([^"]+)"; maybe "([^"]+)"', message
            )
            if match2:
                old_attr, new_attr = match2.groups()
                fixes_by_file[filepath].append((error["line"], old_attr, new_attr))

    total_fixes = 0
    for filepath, fixes in fixes_by_file.items():
        if dry_run:
            print(f"\nWould fix in {filepath}:")
            for line_num, old, new in fixes:
                print(f"  Line {line_num}: {old} -> {new}")
            total_fixes += len(fixes)
            total_fixes += apply_fixes_to_file(filepath, fixes)

    return total_fixes


def fix_name_defined_errors(
    errors: list[dict], inventory: dict[str, any], dry_run: bool = False
) -> int:
    """Fix name-defined errors using inventory mappings."""
    fixes_by_file: dict[str, set[tuple[str, str]]] = {}

    for error in errors:
        if error["code"] == "name-defined":
            filepath = error["file"]
            if filepath not in fixes_by_file:
                fixes_by_file[filepath] = set()

            # Extract undefined name
            match = re.search(r'Name "([^"]+)" is not defined', error["message"])
            if match:
                undefined_name = match.group(1)

                # Check if we have a mapping
                if undefined_name in inventory["class_name_mapping"]:
                    new_name = inventory["class_name_mapping"][undefined_name]
                    fixes_by_file[filepath].add((undefined_name, new_name))

    total_fixes = 0
    for filepath, fixes in fixes_by_file.items():
        if dry_run:
            print(f"\nWould fix in {filepath}:")
            for old, new in fixes:
                print(f"  {old} -> {new}")
            total_fixes += len(fixes)
            total_fixes += apply_name_fixes_to_file(filepath, list(fixes))

    return total_fixes


def fix_call_arg_errors(
    errors: list[dict], inventory: dict[str, any], dry_run: bool = False
) -> int:
    """Fix call-arg errors by adding missing arguments."""
    fixes_by_file: dict[str, list[dict]] = {}

    for error in errors:
        if error["code"] == "call-arg" and "Missing named argument" in error["message"]:
            filepath = error["file"]
            if filepath not in fixes_by_file:
                fixes_by_file[filepath] = []

            # Extract missing argument and class
            match = re.search(
                r'Missing named argument "([^"]+)" for "([^"]+)"', error["message"]
            )
            if match:
                arg_name, class_name = match.groups()

                # Get class info from inventory
                if class_name in inventory["classes"]:
                    class_info = inventory["classes"][class_name]
                    # Find the argument info
                    for arg in class_info["init_args"]:
                        if arg["name"] == arg_name:
                            fixes_by_file[filepath].append(
                                {
                                    "line": error["line"],
                                    "class": class_name,
                                    "arg": arg_name,
                                    "has_default": arg.get("has_default", False),
                                    "default": arg.get("default", None),
                                    "type": arg.get("annotation", None),
                                }
                            )
                            break

    total_fixes = 0
    for filepath, fixes in fixes_by_file.items():
        if dry_run:
            print(f"\nWould fix in {filepath}:")
            for fix in fixes:
                print(f"  Line {fix['line']}: Add {fix['arg']} to {fix['class']} call")
            total_fixes += len(fixes)
            # This is complex and needs careful handling
            print(f"Call-arg fixes for {filepath} need manual review")
            for fix in fixes:
                print(f"  Line {fix['line']}: {fix['class']} needs {fix['arg']}")

    return total_fixes


def apply_fixes_to_file(filepath: str, fixes: list[tuple[int, str, str]]) -> int:
    """Apply attribute fixes to a file."""
    try:
        path = Path(filepath)
        lines = path.read_text().splitlines()

        # Sort fixes by line number (descending) to avoid offset issues
        fixes.sort(key=lambda x: x[0], reverse=True)

        applied = 0
        for line_num, old_attr, new_attr in fixes:
            # Line numbers are 1-based
            idx = line_num - 1
            if 0 <= idx < len(lines):
                line = lines[idx]
                # Use word boundaries to avoid partial replacements
                new_line = re.sub(r"\b" + re.escape(old_attr) + r"\b", new_attr, line)
                if new_line != line:
                    lines[idx] = new_line
                    applied += 1

        if applied > 0:
            path.write_text("\n".join(lines) + "\n")

        return applied

    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return 0


def apply_name_fixes_to_file(filepath: str, fixes: list[tuple[str, str]]) -> int:
    """Apply name fixes to a file."""
    try:
        path = Path(filepath)
        content = path.read_text()

        applied = 0
        for old_name, new_name in fixes:
            # Use word boundaries for accurate replacement
            pattern = r"\b" + re.escape(old_name) + r"\b"
            new_content = re.sub(pattern, new_name, content)
            if new_content != content:
                content = new_content
                applied += 1

        if applied > 0:
            path.write_text(content)

        return applied

    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return 0


def main() -> None:
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix mypy errors in FLX codebase")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed"
    )
    parser.add_argument(
        "--type",
        choices=["attr", "name", "call", "all"],
        default="all",
        help="Type of errors to fix",
    )
    args = parser.parse_args()

    # Load inventory
    inventory_file = Path("/home/marlonsc/pyauto/flx_inventory.json")
    with open(inventory_file, encoding="utf-8") as f:
        inventory = json.load(f)

    print("Analyzing mypy errors...")
    errors = get_mypy_errors()

    # Count errors by type
    error_counts: dict = {}
    for error in errors:
        error_counts[error["code"]] = error_counts.get(error["code"], 0) + 1

    print(f"\nFound {len(errors)} total errors:")
    for code, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {code}: {count}")

    print(f"\nMode: {'DRY RUN' if args.dry_run else 'APPLYING FIXES'}")

    total_fixes = 0

    if args.type in {"attr", "all"}:
        print("\n--- Fixing attr-defined errors ---")
        attr_errors = [e for e in errors if e["code"] == "attr-defined"]
        fixes = fix_attr_defined_errors(attr_errors, args.dry_run)
        total_fixes += fixes
        print(f"Fixed {fixes} attr-defined errors")

    if args.type in {"name", "all"}:
        print("\n--- Fixing name-defined errors ---")
        name_errors = [e for e in errors if e["code"] == "name-defined"]
        fixes = fix_name_defined_errors(name_errors, inventory, args.dry_run)
        total_fixes += fixes
        print(f"Fixed {fixes} name-defined errors")

    if args.type in {"call", "all"}:
        print("\n--- Analyzing call-arg errors ---")
        call_errors = [e for e in errors if e["code"] == "call-arg"]
        fixes = fix_call_arg_errors(call_errors, inventory, args.dry_run)
        print(f"Identified {fixes} call-arg errors needing manual review")

    print(f"\nTotal fixes applied: {total_fixes}")

    if args.dry_run:
        print("\nThis was a dry run. Use without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
