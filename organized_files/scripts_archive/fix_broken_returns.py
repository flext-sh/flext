#!/usr/bin/env python3
"""Fix broken return statements that were incorrectly added."""

import os
import re
from pathlib import Path


class BrokenReturnsFixer:
    """Fix incorrectly placed return statements."""

    def __init__(self):
        self.fixed_files = 0

    def fix_project(self, project_path: str) -> None:
        """Fix all files in a project."""
        print(f"🔧 Fixing broken returns in {project_path}")

        py_files = list(Path(project_path).rglob("*.py"))

        for py_file in py_files:
            if self.fix_file(str(py_file)):
                self.fixed_files += 1

    def fix_file(self, file_path: str) -> bool:
        """Fix broken returns in a single file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix incorrectly placed return statements
            content = self.fix_broken_returns(content)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return False

    def fix_broken_returns(self, content: str) -> str:
        """Remove incorrectly placed return statements."""
        lines = content.split("\n")
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for pattern: function definition followed by return, then docstring
            if (i + 2 < len(lines) and
                "def " in line and ":" in line and
                lines[i + 1].strip() == "return" and
                '"""' in lines[i + 2]):

                # Keep function definition
                fixed_lines.append(line)
                # Skip the incorrect return
                i += 1
                # Keep the docstring and rest
                i += 1
                fixed_lines.append(lines[i])

            # Check for pattern: function definition followed by return, then implementation
            elif (i + 1 < len(lines) and
                  "def " in line and ":" in line and
                  lines[i + 1].strip() == "return" and
                  i + 2 < len(lines) and
                  '"""' not in lines[i + 2]):

                # Keep function definition
                fixed_lines.append(line)
                # Skip the incorrect return
                i += 1

            else:
                fixed_lines.append(line)

            i += 1

        return "\n".join(fixed_lines)


def main():
    """Main execution function."""
    fixer = BrokenReturnsFixer()

    projects = [
        "/home/marlonsc/flext/flext-tap-oracle-wms",
        "/home/marlonsc/flext/flext-target-oracle",
        "/home/marlonsc/flext/gruponos-meltano-native"
    ]

    for project in projects:
        if os.path.exists(project):
            fixer.fix_project(project)
            print(f"  Fixed {fixer.fixed_files} files")
            fixer.fixed_files = 0

    print("\n✅ Fixed broken return statements!")


if __name__ == "__main__":
    main()
