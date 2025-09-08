#!/usr/bin/env python3
"""Add copyright headers to all Python files in FLEXT projects."""

import sys
from pathlib import Path


def get_copyright_for_project(project_name: str) -> str:
    """Get the appropriate copyright header based on project name."""
    # client-a projects use Portuguese copyright
    if any(name in project_name.lower() for name in ["client-a", "oud", "ldap", "ldif"]):
        return '''"""
Copyright (c) 2025 client-a Telecom. Todos os direitos reservados.
SPDX-License-Identifier: Proprietário
"""'''

    # DataCosmos projects
    if "datacosmos" in project_name.lower():
        return '''"""
Copyright (c) 2025 DataCosmos. All rights reserved.
SPDX-License-Identifier: Proprietary
"""'''

    # Default FLEXT Team copyright
    return '''"""
Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""'''


def add_copyright_to_file(filepath: Path, copyright_header: str) -> bool:
    """Add copyright header to a Python file if missing."""
    with filepath.open(encoding="utf-8") as f:
        content = f.read()

    # Skip if already has copyright
    if "Copyright (c)" in content[:500]:
        return False

    lines = content.split("\n")

    # Find where to insert copyright
    insert_index = 0
    in_docstring = False
    docstring_char = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track docstring state
        if not in_docstring:
            if stripped.startswith(('"""', "'''")):
                in_docstring = True
                docstring_char = '"""' if stripped.startswith('"""') else "'''"
                if stripped.count(docstring_char) >= 2:
                    # Single line docstring
                    in_docstring = False
                    insert_index = i + 1
                    break
        elif docstring_char in line:
            in_docstring = False
            insert_index = i + 1
            break

    # Insert copyright after module docstring
    if insert_index > 0:
        # Add blank line if needed
        if insert_index < len(lines) and lines[insert_index].strip():
            lines.insert(insert_index, "")
            insert_index += 1

        # Insert copyright
        for line in reversed(copyright_header.split("\n")):
            lines.insert(insert_index, line)
    else:
        # No module docstring, add at beginning
        lines.insert(0, copyright_header)
        lines.insert(1, "")

    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return True


def main() -> int:
    """Main function to add copyright to all files."""
    base_path = Path("/home/marlonsc/flext")

    # All FLEXT projects
    projects = list(base_path.glob("flext-*")) + list(base_path.glob("singer-*"))

    total_updated = 0

    for project_path in sorted(projects):
        if not project_path.is_dir():
            continue

        project_name = project_path.name
        copyright_header = get_copyright_for_project(project_name)

        src_path = project_path / "src"
        if not src_path.exists():
            continue

        project_updated = 0

        for py_file in src_path.rglob("*.py"):
            # Skip __pycache__ and other generated files
            if "__pycache__" in str(py_file):
                continue

            if add_copyright_to_file(py_file, copyright_header):
                project_updated += 1

        if project_updated:
            total_updated += project_updated

    return 0


if __name__ == "__main__":
    sys.exit(main())
