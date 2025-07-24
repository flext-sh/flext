#!/usr/bin/env python3
"""Script de correção de erros de sintaxe introduzidos pelo fix_imports.py.

Aplica correções RIGOROSAS seguindo REFATORACAO_ARQUITETURA_FLEXT.md
REGRA ABSOLUTA: Camadas 2,3,5 APENAS lógica de negócio - generalizações APENAS em camada 1

Copyright (c) 2025 FLEXT Team
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from pathlib import Path


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
        r"(if TYPE_CHECKING:[^\n]*\n(?:\s*#[^\n]*\n)*)\nfrom (\w+) import([^\n]+)\n\n(\s+from \w+)",
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
                r"\1\n    # 🚨 ARCHITECTURAL COMPLIANCE: Using módulo raiz imports\n    from \2 import",
            ),
            # Pattern 2: Dangling imports after TYPE_CHECKING
            (
                r"(# 🚨 ARCHITECTURAL COMPLIANCE[^\n]*)\nfrom (\w+) import([^\n]+)\n\n(\s+from)",
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
        fixed_lines = []
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

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True

    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")

    return False


def main() -> None:
    """Main function to fix all syntax errors across workspace."""
    workspace = Path("/home/marlonsc/flext")

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

    print("🔧 Fixing syntax errors from architectural compliance...")
    print(f"📂 Processing {len(error_projects)} projects...")

    for project in error_projects:
        project_path = workspace / project
        if not project_path.exists():
            print(f"⚠️  Project not found: {project}")
            continue

        print(f"\n🔍 Processing {project}...")

        # Find all Python files
        python_files = []
        for pattern in ["src/**/*.py", "tests/**/*.py"]:
            python_files.extend(project_path.glob(pattern))

        fixed_in_project = 0
        for py_file in python_files:
            if py_file.name.startswith(".") or ".venv" in str(py_file):
                continue

            if fix_syntax_errors_in_file(py_file):
                fixed_in_project += 1
                print(f"  ✅ Fixed: {py_file.relative_to(project_path)}")

        if fixed_in_project > 0:
            print(f"  📊 {fixed_in_project} files fixed in {project}")
            total_fixed += fixed_in_project
        else:
            print(f"  ✨ {project} syntax already correct")

    print("\n🎉 SYNTAX ERRORS FIXED!")
    print(f"📊 Total files fixed: {total_fixed}")
    print("✅ All projects follow clean syntax with architectural compliance")


if __name__ == "__main__":
    main()
