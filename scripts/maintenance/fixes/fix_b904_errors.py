#!/usr/bin/env python3
"""Script para corrigir automaticamente problemas B904 restantes."""

import re
from pathlib import Path


def fix_b904_exceptions(content: str) -> str:
    """Fix B904 errors - missing exception chaining."""
    lines = content.split("\n")

    # Track exception variables in except blocks
    in_except_block = False
    except_variable = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        indentation = line[: len(line) - len(line.lstrip())]

        # Check if we're entering an except block
        if stripped.startswith("except ") and " as " in stripped:
            # Extract the exception variable name
            match = re.search(r"except .+ as (\w+):", stripped)
            if match:
                except_variable = match.group(1)
                in_except_block = True
                in_except_block = False
                except_variable = None
        elif stripped.startswith("except "):
            in_except_block = True
            except_variable = None
        elif (
            stripped
            and not stripped.startswith(" ")
            and not stripped.startswith("\t")
            and "except" not in stripped
        ):
            # We've left the except block
            in_except_block = False
            except_variable = None

        # If we're in an except block and find a raise statement
        if in_except_block and stripped.startswith(
                "raise ") and except_variable:
            # Check if it already has 'from'
            if " from " not in stripped:
                # Add exception chaining
                if stripped.endswith(")"):
                    lines[i] = (
                        f"{indentation}raise {stripped[6:]} from {except_variable}"
                    )
                    # For cases like: raise Exception("message")
                    lines[i] = (
                        f"{indentation}raise {stripped[6:]} from {except_variable}"
                    )

    return "\n".join(lines)


def fix_remaining_syntax_errors(content: str) -> str:
    """Fix remaining syntax errors from incomplete f-string conversions."""
    # Fix cases where f-strings weren't properly converted
    content = re.sub(
        r'(\s+logger\.\w+\s*\(\s*)"([^"]*?)", ([^,]+)\s+f"([^"]*?)"',
        r'\1"\2 \4", \3',
        content,
    )

    # Fix cases with multiple f-string fragments
    return re.sub(
        r'(\s+logger\.\w+\s*\(\s*)"([^"]*?)", ([^,]+)\s*\n\s*f"([^"]*?)"',
        r'\1"\2 \4", \3',
        content,
    )


def fix_lint_file(file_path: Path) -> bool:
    """Fix lint issues in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply fixes
        content = fix_b904_exceptions(content)
        content = fix_remaining_syntax_errors(content)

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
    """Main function to fix remaining lint issues."""
    # Target directories
    target_dirs = [
        Path("project-algar-oud/src"),
        Path("project-algar-oud/scripts"),
        Path("project-algar-oud/examples"),
        Path("project-gruponos-oic-wms/src"),
        Path("project-gruponos-oic-wms/scripts"),
    ]

    files_fixed = 0
    total_files = 0

    for target_dir in target_dirs:
        if target_dir.exists():
            # Directory - find all Python files
            for py_file in target_dir.rglob("*.py"):
                total_files += 1
                if fix_lint_file(py_file):
                    files_fixed += 1
            print(f"Skipping non-existent path: {target_dir}")

    print(f"\nSummary: Fixed {files_fixed} out of {total_files} files")


if __name__ == "__main__":
    main()
