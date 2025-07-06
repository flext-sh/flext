#!/usr/bin/env python3
"""Fix ALL indentation issues across Python files - enterprise grade."""

import ast
from pathlib import Path


def fix_python_indentation(content: str) -> str:
    """Fix common indentation issues in Python code."""
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            fixed_lines.append(line)
            continue

        # Common patterns to fix:

        # 1. Docstrings after function definitions with wrong indentation
        if line.strip().startswith('"""') and i > 0:
            prev_line = lines[i - 1].strip()
            if prev_line.endswith((") -> None:", "):")):
                # Find proper indentation from def/class line
                for j in range(i - 1, -1, -1):
                    if lines[j].strip().startswith(("def ", "class ", "async def ")):
                        base_indent = len(lines[j]) - len(lines[j].lstrip())
                        proper_indent = " " * (base_indent + 4)
                        line = proper_indent + line.strip()
                        break

        # 2. Code after docstrings with wrong indentation
        elif i > 0 and lines[i - 1].strip().endswith('"""'):
            # Find the function/class this belongs to
            for j in range(i - 1, -1, -1):
                if lines[j].strip().startswith(("def ", "class ", "async def ")):
                    base_indent = len(lines[j]) - len(lines[j].lstrip())
                    proper_indent = " " * (base_indent + 4)
                    if line.strip() and not line.startswith(proper_indent):
                        line = proper_indent + line.strip()
                    break

        # 3. Fix elif/else/except/finally with wrong indentation
        elif line.strip().startswith(("elif ", "else:", "except", "finally:")):
            # Find matching if/try statement
            for j in range(i - 1, -1, -1):
                prev = lines[j].strip()
                if prev.startswith(("if ", "try:", "for ", "while ", "with ")):
                    target_indent = len(lines[j]) - len(lines[j].lstrip())
                    line = " " * target_indent + line.strip()
                    break

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def validate_python_syntax(content: str) -> list[str]:
    """Validate Python syntax and return error descriptions."""
    try:
        ast.parse(content)
        return []
    except SyntaxError as e:
        return [f"Line {e.lineno}: {e.msg}"]


def fix_file_indentation(file_path: Path) -> tuple[bool, list[str]]:
    """Fix indentation issues in a single Python file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Apply fixes
        fixed_content = fix_python_indentation(content)

        # Validate result
        errors = validate_python_syntax(fixed_content)

        if not errors and fixed_content != original_content:
            file_path.write_text(fixed_content, encoding="utf-8")
            return True, []
        if errors:
            return False, errors
        return False, []  # No changes needed

    except Exception as e:
        return False, [f"Error processing file: {e}"]


def main() -> None:
    """Main function to fix indentation across projects."""
    projects = [
        "flext-auth/src",
        "flext-core/src",
        "flext-ldap/src",
        "flext-api/src",
        "flext-grpc/src",
        "flext-observability/src",
    ]

    total_fixed = 0
    total_errors = 0

    print("🔧 FIXING ALL INDENTATION ISSUES - ENTERPRISE MODE")
    print("=" * 60)

    for project in projects:
        project_path = Path(project)
        if not project_path.exists():
            continue

        print(f"\n📁 Processing {project}...")
        project_fixed = 0
        project_errors = 0

        for py_file in project_path.rglob("*.py"):
            fixed, errors = fix_file_indentation(py_file)

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
    print(f"🎯 SUMMARY: {total_fixed} files fixed, {total_errors} files with errors")

    if total_errors == 0:
        print("✅ ALL INDENTATION ISSUES RESOLVED!")
    else:
        print(f"⚠️  {total_errors} files still have issues - manual review needed")


if __name__ == "__main__":
    main()
