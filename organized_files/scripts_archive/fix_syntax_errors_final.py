#!/usr/bin/env python3
"""Fix specific syntax errors introduced by previous fixes."""

import os
import re
from pathlib import Path


class SyntaxErrorFixer:
    """Fix specific syntax errors without introducing new ones."""

    def __init__(self):
        self.fixed_files = 0

    def fix_project(self, project_path: str) -> None:
        """Fix syntax errors in a project."""
        print(f"🔧 Fixing syntax errors in {project_path}")

        py_files = list(Path(project_path).rglob("*.py"))

        for py_file in py_files:
            if self.fix_file(str(py_file)):
                self.fixed_files += 1

        print(f"  Fixed {self.fixed_files} files")
        self.fixed_files = 0

    def fix_file(self, file_path: str) -> bool:
        """Fix syntax errors in a file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix specific syntax errors
            content = self.fix_malformed_type_aliases(content)
            content = self.fix_duplicate_imports(content)
            content = self.fix_malformed_function_signatures(content)
            content = self.fix_arrow_syntax_errors(content)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return False

    def fix_malformed_type_aliases(self, content: str) -> str:
        """Fix malformed type aliases."""
        # Fix: ValueType = object | str, int, float, bool, dict[str, object, list[object], None]
        return re.sub(
            r"ValueType = object \| str, int, float,\s*bool, dict\[str, object, list\[object\], None\]",
            "ValueType = object | str | int | float | bool | dict[str, object] | list[object] | None",
            content
        )

    def fix_duplicate_imports(self, content: str) -> str:
        """Fix duplicate imports."""
        # Fix: from datetime import datetime, timezone, timezone
        content = re.sub(
            r"from datetime import ([^,\n]+), timezone, timezone",
            r"from datetime import \1, timezone",
            content
        )

        # Fix: from datetime import datetime, timezone, timedelta, timezone
        return re.sub(
            r"from datetime import ([^,\n]+), timedelta, timezone",
            r"from datetime import \1, timedelta, timezone",
            content
        )

    def fix_malformed_function_signatures(self, content: str) -> str:
        """Fix malformed function signatures."""
        # Fix: def _send_webhook_alert(self, webhook_url -> None: str, alert: dict[str, Any]) -> None:
        content = re.sub(
            r"def ([^(]+)\([^)]*webhook_url -> None: str",
            r"def \1(self, webhook_url: str",
            content
        )

        # Fix: def create_monitor(config -> None: dict[str, Any], logger: Any = None) -> OracleTargetMonitor:
        return re.sub(
            r"def ([^(]+)\([^)]*config -> None: dict\[str, Any\]",
            r"def \1(config: dict[str, Any]",
            content
        )

    def fix_arrow_syntax_errors(self, content: str) -> str:
        """Fix arrow syntax errors in function definitions."""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Fix lines with malformed arrows like "-> None:"
            if "-> None:" in line and "def " in line:
                # Ensure proper spacing
                line = re.sub(r"\s*->\s*None\s*:", " -> None:", line)

            fixed_lines.append(line)

        return "\n".join(fixed_lines)


def main():
    """Main execution function."""
    fixer = SyntaxErrorFixer()

    projects = [
        "/home/marlonsc/flext/flext-tap-oracle-wms",
        "/home/marlonsc/flext/flext-target-oracle",
        "/home/marlonsc/flext/gruponos-meltano-native"
    ]

    print("🚀 FIXING SYNTAX ERRORS")
    print("=" * 40)

    for project in projects:
        if os.path.exists(project):
            fixer.fix_project(project)

    print("\n✅ Syntax error fixes completed!")


if __name__ == "__main__":
    main()
