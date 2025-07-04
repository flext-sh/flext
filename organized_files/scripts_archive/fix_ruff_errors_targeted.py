#!/usr/bin/env python3
"""Targeted fix for remaining ruff errors with precision."""

import os
import re
import subprocess
from pathlib import Path


class TargetedRuffFixer:
    """Fix remaining ruff errors with surgical precision."""

    def __init__(self):
        self.fixed_files = 0

    def fix_project(self, project_path: str) -> None:
        """Fix ruff errors in a project with targeted approach."""
        print(f"🎯 TARGETED RUFF FIX: {project_path}")

        # Get Python files
        py_files = list(Path(project_path).rglob("*.py"))

        for py_file in py_files:
            if self.fix_file_targeted(str(py_file)):
                self.fixed_files += 1

        print(f"  Fixed {self.fixed_files} files")
        self.fixed_files = 0

    def fix_file_targeted(self, file_path: str) -> bool:
        """Apply targeted fixes to avoid introducing new errors."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Only apply safe, targeted fixes
            content = self.fix_duplicate_docstrings(content)
            content = self.fix_malformed_todo_comments(content)
            content = self.fix_line_length_safe(content)
            content = self.fix_simple_violations(content)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return False

    def fix_duplicate_docstrings(self, content: str) -> str:
        """Remove duplicate docstrings that were added incorrectly."""
        lines = content.split("\n")
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Remove duplicate TODO docstrings
            if ('"""TODO: Add docstring."""' in line and
                i + 1 < len(lines) and
                '"""' in lines[i + 1] and
                "TODO: Add docstring" not in lines[i + 1]):
                # Skip the duplicate TODO docstring
                i += 1
                continue

            # Remove malformed TODO comments before functions
            if (line.strip().startswith("# TODO(@dev): Refactor") and
                i + 1 < len(lines) and
                '"""TODO: Add docstring."""' in lines[i + 1]):
                # Skip both the TODO comment and malformed docstring
                i += 2
                continue

            fixed_lines.append(line)
            i += 1

        return "\n".join(fixed_lines)

    def fix_malformed_todo_comments(self, content: str) -> str:
        """Fix malformed TODO comments."""
        # Remove TODO comments that are incorrectly placed
        content = re.sub(
            r"# TODO\(@dev\): Consider breaking down this complex function  # Link: https://github\.com/issue/todo\n",
            "",
            content
        )

        # Clean up TODO comments format
        return re.sub(
            r'# TODO\(@dev\): Refactor to reduce complexity\n\s*"""TODO: Add docstring\."""\n',
            "",
            content
        )

    def fix_line_length_safe(self, content: str) -> str:
        """Fix line length violations safely without breaking code."""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            if len(line) > 88:
                # Only break safe patterns
                if " and " in line and len(line) < 120:
                    # Break at logical operators
                    parts = line.split(" and ", 1)
                    if len(parts) == 2:
                        indent = len(line) - len(line.lstrip())
                        fixed_lines.extend((parts[0] + " and", " " * (indent + 4) + parts[1]))
                        continue

                if " or " in line and len(line) < 120:
                    # Break at logical operators
                    parts = line.split(" or ", 1)
                    if len(parts) == 2:
                        indent = len(line) - len(line.lstrip())
                        fixed_lines.extend((parts[0] + " or", " " * (indent + 4) + parts[1]))
                        continue

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_simple_violations(self, content: str) -> str:
        """Fix simple violations that are safe."""
        # Fix DTZ005: Add timezone to datetime.now()
        if "datetime.now()" in content and "timezone" in content:
            content = re.sub(r"datetime\.now\(\)", r"datetime.now(timezone.utc)", content)

        # Add noqa for necessary imports
        return re.sub(
            r"from __future__ import annotations$",
            r"from __future__ import annotations  # noqa: F401",
            content,
            flags=re.MULTILINE
        )


def main():
    """Main execution function."""
    fixer = TargetedRuffFixer()

    projects = [
        "/home/marlonsc/flext/flext-tap-oracle-wms",
        "/home/marlonsc/flext/flext-target-oracle",
        "/home/marlonsc/flext/gruponos-meltano-native"
    ]

    print("🎯 TARGETED RUFF ERROR FIXING")
    print("=" * 40)

    for project in projects:
        if os.path.exists(project):
            # Count errors before
            before_count = count_ruff_errors(project)
            print(f"\n{os.path.basename(project)}: {before_count} errors before")

            # Apply fixes
            fixer.fix_project(project)

            # Count errors after
            after_count = count_ruff_errors(project)
            reduction = before_count - after_count

            print(f"  After: {after_count} errors")
            print(f"  Fixed: {reduction} errors")


def count_ruff_errors(project_path: str) -> int:
    """Count ruff errors in a project."""
    try:
        project_name = os.path.basename(project_path)
        if "gruponos-meltano-native" in project_path:
            src_dir = "src/"
        else:
            src_dir = "src/" if "tap-oracle" in project_path else f'{project_name.replace("-", "_")}/'

        result = subprocess.run(
            ["python", "-m", "ruff", "check", src_dir],
            cwd=project_path,
            capture_output=True,
            text=True, check=False
        )

        if result.stdout.strip():
            errors = [line for line in result.stdout.strip().split("\n")
                     if line.strip() and ":" in line and not line.startswith("Found")]
            return len(errors)

        return 0

    except Exception as e:
        print(f"Error counting ruff errors in {project_path}: {e}")
        return 0


if __name__ == "__main__":
    main()
