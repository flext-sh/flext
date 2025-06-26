#!/usr/bin/env python
"""Fix systematic syntax errors in FLX project.

Per CLAUDE.md RULE 4: Complete delivery with zero tolerance for violations.
Fixing import sys issues and other syntax problems systematically.
"""

import re
import subprocess
from pathlib import Path


class FlxSyntaxFixer:
    """Fix syntax errors in FLX project systematically."""

    def __init__(self):
        """Initialize fixer."""
        self.flx_root = Path("/home/marlonsc/pyauto/flx")
        self.fixed_files = []
        self.errors = []

    def find_syntax_error_files(self) -> list[Path]:
        """Find all Python files with syntax errors."""
        try:
            result = subprocess.run(
                [
                    "find",
                    str(self.flx_root),
                    "-name",
                    "*.py",
                    "-not",
                    "-path",
                    "*/.venv/*",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return [Path(f) for f in result.stdout.strip().split("\n") if f]
        except subprocess.CalledProcessError:
            return []

    def fix_import_syntax_errors(self, file_path: Path) -> bool:
        """Fix import syntax errors in a single file."""
        if not file_path.exists():
            return False

        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # Fix patterns that cause syntax errors

            # 1. Remove isolated "import sys" lines that create syntax errors
            lines = content.split("\n")
            fixed_lines = []

            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # Skip isolated "import sys" that doesn't belong
                if line == "import sys" and i > 0:
                    # Check if this is in proper import section
                    prev_line = lines[i - 1].strip() if i > 0 else ""
                    next_line = lines[i + 1].strip() if i < len(lines) - 1 else ""

                    # If it's isolated (not part of proper import block), skip it
                    if (
                        not prev_line.startswith('"""')
                        and not prev_line.startswith("from __future__")
                        and not prev_line.startswith("import ")
                        and not prev_line.startswith("from ")
                        and not next_line.startswith("from ")
                        and not next_line.startswith("import ")
                    ):
                        i += 1
                        continue

                # Fix duplicate import lines
                if line.startswith("from typing import") and any(
                    prev_line.startswith("from typing import")
                    for prev_line in fixed_lines[-3:]
                ):
                    i += 1
                    continue

                fixed_lines.append(lines[i])
                i += 1

            # Fix docstring syntax issues
            content = "\n".join(fixed_lines)

            # Fix broken docstrings that don't close properly
            content = re.sub(r'"""[^"]*\n\nThis module', r'"""\n\nThis module', content)

            # Fix multiple duplicate imports in one line
            content = re.sub(
                r"from typing import ([^,\n]+(?:, [^,\n]+)*)(, [^,\n]+)*\nfrom typing import.*",
                r"from typing import \1",
                content,
                flags=re.MULTILINE,
            )

            # Clean up any remaining syntax issues
            # Remove lines that are just standalone keywords
            content = re.sub(
                r"^\s*from __future__ import annotations\s*$\n^\s*import sys\s*$\n^\s*from typing.*$\n^\s*from typing.*$\n",
                "from __future__ import annotations\n\nfrom typing import Any, Dict, List, Optional\n",
                content,
                flags=re.MULTILINE,
            )

            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                return True
            return False

        except Exception as e:
            self.errors.append(f"{file_path}: {e}")
            return False

    def validate_python_syntax(self, file_path: Path) -> bool:
        """Validate that file has correct Python syntax."""
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", str(file_path)],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    def fix_all_syntax_errors(self) -> None:
        """Fix all syntax errors in FLX project."""
        files_to_fix = self.find_syntax_error_files()

        if not files_to_fix:
            return

        for file_path in files_to_fix:
            # Skip if already valid
            if self.validate_python_syntax(file_path):
                continue

            # Try to fix
            if self.fix_import_syntax_errors(file_path):
                if self.validate_python_syntax(file_path):
                    self.fixed_files.append(file_path)
                else:
                    pass

        # Summary

        if self.errors:
            for _error in self.errors[:5]:  # Show first 5 errors
                pass

        # Log to token
        with open(self.flx_root.parent / ".token", "a") as f:
            f.write(
                f"FLX-SYNTAX-FIX-002 PROGRESS: Fixed {len(self.fixed_files)} syntax errors\n",
            )


if __name__ == "__main__":
    fixer = FlxSyntaxFixer()
    fixer.fix_all_syntax_errors()
