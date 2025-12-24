#!/usr/bin/env python3
"""Convert class aliases to real inheritance in all modules.

Converts patterns like:
    ClassName = Parent.ClassName
to:
    class ClassName(Parent.ClassName):
        \"\"\"ClassName - real inheritance.\"\"\"

Handles:
- Classes (normal inheritance)
- Protocols (with @runtime_checkable)
- Skips enum values (.value)
- Skips Literal type aliases
"""

import re
import sys
from pathlib import Path
from re import Match

# Pattern to match class aliases: ClassName = Parent.ClassName (not .value, not in type alias)
ALIAS_PATTERN = re.compile(
    r"^(\s*)([A-Z][a-zA-Z0-9_]*)\s*=\s*([A-Z][a-zA-Z0-9_]*\.[A-Z][a-zA-Z0-9_]*)(?!\.value)\s*$",
)

# Pattern to detect if we're in a type alias context (PEP 695)
TYPE_ALIAS_PATTERN = re.compile(r"^\s*type\s+[A-Z]")


def is_protocol_file(filepath: Path) -> bool:
    """Check if file is a protocols.py file."""
    return filepath.name == "protocols.py"


def convert_alias_to_inheritance(
    match: Match[str], line_num: int, lines: list[str], filepath: Path,
) -> str:
    """Convert alias to inheritance class."""
    indent = match.group(1)
    class_name = match.group(2)
    parent_class = match.group(3)

    # Check if next line is a comment or docstring
    next_line_idx = line_num
    if next_line_idx < len(lines):
        next_line = lines[next_line_idx].strip()
        if next_line.startswith(('"""', "'''", "#")):
            # Keep existing docstring/comment
            if is_protocol_file(filepath):
                return f'{indent}@runtime_checkable\n{indent}class {class_name}({parent_class}, Protocol):\n{indent}    """{class_name} - real inheritance."""'
            return f'{indent}class {class_name}({parent_class}):\n{indent}    """{class_name} - real inheritance."""'

    # Check if parent is a Protocol
    is_protocol = "Protocol" in parent_class or is_protocol_file(filepath)

    if is_protocol:
        return f'{indent}@runtime_checkable\n{indent}class {class_name}({parent_class}, Protocol):\n{indent}    """{class_name} - real inheritance."""'

    return f'{indent}class {class_name}({parent_class}):\n{indent}    """{class_name} - real inheritance."""'


def process_file(filepath: Path, *, dry_run: bool = False) -> tuple[int, bool]:
    """Process a single file, converting aliases to inheritance.

    Returns:
        Tuple of (number of conversions, file_was_modified)

    """
    try:
        content = Path(filepath).read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return 0, False

    original_content = content
    lines = content.split("\n")
    modified_lines = []
    conversions = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        match = ALIAS_PATTERN.match(line)

        # Skip if in type alias context
        if TYPE_ALIAS_PATTERN.match(line):
            modified_lines.append(line)
            i += 1
            continue

        if match:
            # Check if this is a type alias (next line might have type keyword)
            if i + 1 < len(lines) and "type " in lines[i + 1]:
                modified_lines.append(line)
                i += 1
                continue

            # Convert to inheritance
            converted = convert_alias_to_inheritance(match, i + 1, lines, filepath)
            modified_lines.extend(converted.split("\n"))
            conversions += 1
        else:
            modified_lines.append(line)
        i += 1

    if conversions > 0:
        new_content = "\n".join(modified_lines)
        if new_content != original_content:
            if not dry_run:
                try:
                    Path(filepath).write_text(new_content, encoding="utf-8")
                    return conversions, True
                except Exception as e:
                    print(f"Error writing {filepath}: {e}", file=sys.stderr)
                    return conversions, False
            else:
                return conversions, True

    return conversions, False


def main() -> None:
    """Main entry point."""
    dry_run = "--dry-run" in sys.argv

    if len(sys.argv) > 1 and not dry_run:
        target_files = [Path(p) for p in sys.argv[1:] if p != "--dry-run"]
    else:
        # Find all target files
        target_files = []
        target_names = {
            "models.py",
            "typings.py",
            "utilities.py",
            "constants.py",
            "protocols.py",
        }
        for root in Path().rglob("*"):
            if (
                "__pycache__" in str(root)
                or ".venv" in str(root)
                or ".git" in str(root)
            ):
                continue
            if root.name in target_names and (
                "src" in str(root) or "tests/helpers" in str(root)
            ):
                target_files.append(root)

    total_conversions = 0
    files_modified = 0

    for filepath in sorted(target_files):
        conversions, modified = process_file(filepath, dry_run=dry_run)
        if conversions > 0:
            status = "[DRY RUN] " if dry_run else ""
            print(f"{status}{filepath}: {conversions} conversion(s)")
            total_conversions += conversions
            if modified:
                files_modified += 1

    print(f"\nTotal: {total_conversions} conversions in {files_modified} files")
    return 0 if total_conversions == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
