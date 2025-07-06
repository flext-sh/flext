#!/usr/bin/env python3
"""Super-aggressive syntax error fixer for FLEXT projects."""

import re
from pathlib import Path


def fix_aggressive_syntax_errors(content: str) -> str:
    """Apply aggressive syntax error fixes."""

    # Fix 1: Remove duplicate type ignore comments
    content = re.sub(
        r"# type: ignore\[misc\]\s*# type: ignore\[misc\]",
        "# type: ignore[misc]",
        content,
    )

    # Fix 2: Fix malformed hasattr syntax with type ignore
    content = re.sub(
        r"if hasattr\([^)]+\)\s*# type: ignore\[misc\]\s*# type: ignore\[misc\]:",
        lambda m: m.group(0).replace(
            "# type: ignore[misc]  # type: ignore[misc]:", ":"
        ),
        content,
    )

    # Fix 3: Fix hasattr with missing colon
    content = re.sub(
        r"if hasattr\([^)]+\)\s*# type: ignore\[misc\]\s*# type: ignore\[misc\]$",
        lambda m: m.group(0).rstrip() + ":",
        content,
        flags=re.MULTILINE,
    )

    # Fix 4: Fix docstring indentation issues more aggressively
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        # Fix docstrings that start with wrong indentation after function definitions
        if '"""' in line and i > 0:
            prev_line = lines[i - 1].strip()
            if prev_line.endswith((") -> None:", "):", "-> None:")):
                # Find the function definition
                for j in range(i - 1, max(0, i - 10), -1):
                    if lines[j].strip().startswith(("def ", "class ", "async def ")):
                        base_indent = len(lines[j]) - len(lines[j].lstrip())
                        proper_indent = " " * (base_indent + 4)
                        if line.strip().startswith('"""'):
                            line = proper_indent + line.strip()
                        break

        # Fix indentation after docstrings
        if i > 0 and lines[i - 1].strip().endswith('"""') and line.strip():
            # Find the function this belongs to
            for j in range(i - 2, max(0, i - 10), -1):
                if lines[j].strip().startswith(("def ", "class ", "async def ")):
                    base_indent = len(lines[j]) - len(lines[j].lstrip())
                    proper_indent = " " * (base_indent + 4)
                    if not line.startswith(proper_indent) and line.strip():
                        line = proper_indent + line.strip()
                    break

        # Fix else/elif/except/finally indentation
        if line.strip().startswith(("else:", "elif ", "except", "finally:")):
            # Find matching control structure
            for j in range(i - 1, max(0, i - 20), -1):
                prev = lines[j].strip()
                if prev.startswith(("if ", "try:", "for ", "while ", "with ", "elif ")):
                    target_indent = len(lines[j]) - len(lines[j].lstrip())
                    line = " " * target_indent + line.strip()
                    break

        fixed_lines.append(line)

    content = "\n".join(fixed_lines)

    # Fix 5: Add missing colons to if/else statements
    content = re.sub(r"(if [^:]+)\s*$", r"\1:", content, flags=re.MULTILINE)
    content = re.sub(r"(else)\s*$", r"\1:", content, flags=re.MULTILINE)
    content = re.sub(r"(elif [^:]+)\s*$", r"\1:", content, flags=re.MULTILINE)

    # Fix 6: Fix try/except blocks
    content = re.sub(r"(try)\s*$", r"\1:", content, flags=re.MULTILINE)
    content = re.sub(r"(except [^:]*)\s*$", r"\1:", content, flags=re.MULTILINE)
    content = re.sub(r"(finally)\s*$", r"\1:", content, flags=re.MULTILINE)

    # Fix 7: Remove trailing colons on imports and other statements that don't need them
    content = re.sub(r"^(import [^:]+):$", r"\1", content, flags=re.MULTILINE)
    return re.sub(r"^(from [^:]+):$", r"\1", content, flags=re.MULTILINE)


def process_file_aggressive(file_path: Path) -> tuple[bool, list[str]]:
    """Process a single file with aggressive error fixing."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Apply aggressive fixes
        fixed_content = fix_aggressive_syntax_errors(content)

        if fixed_content != original_content:
            # Backup original
            backup_path = file_path.with_suffix(".py.aggressive_backup")
            backup_path.write_text(original_content, encoding="utf-8")

            # Write fixed content
            file_path.write_text(fixed_content, encoding="utf-8")
            return True, []

        return False, []

    except Exception as e:
        return False, [f"Error processing file: {e}"]


def main() -> None:
    """Main function to apply aggressive fixes."""
    projects = [
        "flext-auth/src",
        "flext-core/src",
        "flext-api/src",
        "flext-grpc/src",
        "flext-observability/src",
        "flext-ldap/src",  # Attack the big one too
    ]

    total_fixed = 0
    total_errors = 0

    print("🔥 AGGRESSIVE SYNTAX ERROR FIXING - NUCLEAR MODE")
    print("=" * 60)

    for project in projects:
        project_path = Path(project)
        if not project_path.exists():
            continue

        print(f"\n💥 Attacking {project}...")
        project_fixed = 0
        project_errors = 0

        for py_file in project_path.rglob("*.py"):
            fixed, errors = process_file_aggressive(py_file)

            if fixed:
                print(f"  ✅ Fixed: {py_file.relative_to(project_path)}")
                project_fixed += 1
            elif errors:
                print(f"  ❌ Errors in {py_file.relative_to(project_path)}:")
                for error in errors:
                    print(f"     {error}")
                project_errors += 1

        print(f"  📊 {project}: {project_fixed} fixed, {project_errors} errors")
        total_fixed += project_fixed
        total_errors += project_errors

    print("\n" + "=" * 60)
    print(f"🎯 NUCLEAR SUMMARY: {total_fixed} files attacked, {total_errors} failures")

    if total_fixed > 0:
        print("🔥 AGGRESSIVE FIXES APPLIED - CHECK RESULTS!")
    else:
        print("💣 NO CHANGES NEEDED OR POSSIBLE")


if __name__ == "__main__":
    main()
