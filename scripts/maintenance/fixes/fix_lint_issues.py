#!/usr/bin/env python3
"""Script para corrigir automaticamente problemas de lint G004, B904, PERF403."""

import re
from pathlib import Path


def fix_g004_logging_fstrings(content: str) -> str:
    """Fix G004 errors - f-strings in logging statements."""
    # Pattern to match logging statements with f-strings
    patterns = [
        # logger.info("message %s", var")
        (
            r'(\s+(?:logger|self\.logger)\.(?:debug|info|warning|error|exception|critical)\s*\(\s*)f"([^"]*?{[^}]*}[^"]*?)"',
            r'\1"\2", ',
        ),
        (
            r"(\s+(?:logger|self\.logger)\.(?:debug|info|warning|error|exception|critical)\s*\(\s*)f'([^']*?{[^}]*}[^']*?)'",
            r"\1'\2', ",
        ),
    ]

    for pattern, _replacement in patterns:
        # Find all matches
        matches = re.finditer(pattern, content)
        for match in reversed(
            list(matches)
        ):  # Process in reverse to maintain positions
            start, end = match.span()
            prefix = match.group(1)
            message = match.group(2)

            # Convert f-string variables to % formatting
            # Find {variable} patterns and convert them
            variables = re.findall(r"{([^}]+)}", message)
            if variables:
                # Replace {var} with %s
                new_message = re.sub(r"{[^}]+}", "%s", message)
                # Build the replacement with variables
                var_list = ", ".join(variables)
                replacement_text = f'{prefix}"{new_message}", {var_list}'
                content = content[:start] + replacement_text + content[end:]

    return content


def fix_b904_exception_chaining(content: str) -> str:
    """Fix B904 errors - missing exception chaining."""
    # Pattern to match raise statements without proper chaining
    # Look for raise statements within except blocks
    lines = content.split("\n")
    in_except_block = False
    except_variable = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check if we're entering an except block
        if stripped.startswith("except ") and " as " in stripped:
            in_except_block = True
            # Extract the exception variable name
            match = re.search(r"except .+ as (\w+):", stripped)
            if match:
                except_variable = match.group(1)
        elif stripped.startswith("except "):
            in_except_block = True
            except_variable = None
        elif (
            not stripped.startswith(" ") and stripped != "" and "except" not in stripped
        ):
            # We've left the except block
            in_except_block = False
            except_variable = None

        # If we're in an except block and find a raise statement
        if in_except_block and stripped.startswith(
                "raise ") and except_variable:
            # Check if it already has 'from'
            if " from " not in stripped and not stripped.endswith(
                f" from {except_variable}"
            ):
                # Add exception chaining
                if stripped.endswith(")"):
                    lines[i] = line.replace(
                        stripped, f"{stripped} from {except_variable}"
                    )
                    lines[i] = line.replace(
                        stripped, f"{stripped} from {except_variable}"
                    )

    return "\n".join(lines)


def fix_lint_file(file_path: Path) -> bool:
    """Fix lint issues in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply fixes
        content = fix_g004_logging_fstrings(content)
        content = fix_b904_exception_chaining(content)

        # Write back only if changes were made
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main() -> None:
    """Main function to fix lint issues in project directories."""
    # Target directories
    target_dirs = [
        Path("project-algar-oud/src"),
        Path("project-algar-oud/scripts"),
        Path("project-algar-oud/examples"),
        Path("project-gruponos-oic-wms/src"),
        Path("project-gruponos-oic-wms/scripts"),
        Path("project-gruponos-oic-wms/debug_order_hdr_load.py"),
    ]

    files_fixed = 0
    total_files = 0

    for target_dir in target_dirs:
        if target_dir.is_file():
            # Single file
            total_files += 1
            if fix_lint_file(target_dir):
                files_fixed += 1
        elif target_dir.exists():
            # Directory - find all Python files
            for py_file in target_dir.rglob("*.py"):
                total_files += 1
                if fix_lint_file(py_file):
                    files_fixed += 1
            print(f"Skipping non-existent path: {target_dir}")

    print(f"\nSummary: Fixed {files_fixed} out of {total_files} files")


if __name__ == "__main__":
    main()
