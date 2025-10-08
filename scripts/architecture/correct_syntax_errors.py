#!/usr/bin/env python3
"""Script de correção de erros de sintaxe introduzidos pelo fix_imports.py.

Aplica correções RIGOROSAS seguindo REFATORACAO_ARQUITETURA_FLEXT.md
REGRA ABSOLUTA: Camadas 2,3,5 APENAS lógica de negócio -
generalizações APENAS em camada 1

Copyright (c) 2025 FLEXT Team
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from pathlib import Path

from flext_core import FlextTypes


def fix_indentation_errors(content: str) -> str:
    """Fix indentation errors caused by import fixes."""
    # Fix pattern: if TYPE_CHECKING:\n# comment\nfrom module import
    content = re.sub(
        r"(if TYPE_CHECKING:)\n(\s*# [^\n]+)\nfrom (\w+) import",
        r"\1\n\2\n    from \3 import",
        content,
    )

    # Fix dangling imports after if blocks
    return re.sub(
        r"(if TYPE_CHECKING:[^\n]*\n(?:\s*#[^\n]*\n)*)\n"
        r"from (\w+) import([^\n]+)\n\n(\s+from \w+)",
        r"\1    from \2 import\3\n\n\4",
        content,
    )


def fix_syntax_errors_in_file(file_path: Path) -> bool:
    """Fix architectural violations and syntax errors in a single file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Fix indentation issues
        content = fix_indentation_errors(content)

        # Fix specific patterns that break syntax
        fixes = [
            # Pattern 1: TYPE_CHECKING block with misplaced imports
            (
                r"(if TYPE_CHECKING:)\s*\n\s*# [^\n]+\nfrom (\w+) import",
                r"\1\n    # 🚨 ARCHITECTURAL COMPLIANCE: "
                r"Using módulo raiz imports\n    from \2 import",
            ),
            # Pattern 2: Dangling imports after TYPE_CHECKING
            (
                r"(# 🚨 ARCHITECTURAL COMPLIANCE[^\n]*)\n"
                r"from (\w+) import([^\n]+)\n\n(\s+from)",
                r"\1\n    from \2 import\3\n\n\4",
            ),
            # Pattern 3: Missing indentation in TYPE_CHECKING blocks
            (
                r"if TYPE_CHECKING:\n(\s*# [^\n]+)\n([^\s].*from \w+ import)",
                r"if TYPE_CHECKING:\n\1\n    \2",
            ),
        ]

        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        # Ensure proper indentation in TYPE_CHECKING blocks
        lines = content.split("\n")
        fixed_lines: FlextTypes.StringList = []
        in_type_checking = False

        for line in lines:
            if "if TYPE_CHECKING:" in line:
                in_type_checking = True
                fixed_lines.append(line)
            elif in_type_checking and (line.startswith(("from ", "import "))):
                # Ensure imports in TYPE_CHECKING are indented
                fixed_lines.append("    " + line.strip())
            elif in_type_checking and line.strip() and not line.startswith(" "):
                # End of TYPE_CHECKING block
                in_type_checking = False
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        content = "\n".join(fixed_lines)

        # Write back if changed
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True

        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main() -> None:
    """Main function to fix all syntax errors across workspace."""
    workspace = Path("../..")

    # Focus on projects with errors identified
    error_projects = [
        "flext-meltano",
        "flext-api",
        "flext-ldap",
        "flext-auth",
        "flext-grpc",
        "flext-observability",
        "flext-cli",
    ]

    total_fixed = 0

    for project in error_projects:
        project_path = workspace / project
        if not project_path.exists():
            continue

        # Find all Python files
        python_files: list[Path] = []
        for pattern in ["src/**/*.py", "tests/**/*.py"]:
            python_files.extend(project_path.glob(pattern))

        fixed_in_project = 0
        for py_file in python_files:
            if py_file.name.startswith(".") or ".venv" in str(py_file):
                continue

            if fix_syntax_errors_in_file(py_file):
                fixed_in_project += 1

        if fixed_in_project > 0:
            total_fixed += fixed_in_project


if __name__ == "__main__":
    main()
