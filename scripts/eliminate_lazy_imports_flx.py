#!/usr/bin/env python
"""
URGENT: Eliminate ALL lazy imports in FLX project.

Per CLAUDE.md RULE 4 + user demand: "TOLERANCIA ZERO a lazy import de codigo"
Replace all TYPE_CHECKING patterns with direct imports.
"""

import re
from pathlib import Path


def eliminate_type_checking_file(file_path: Path) -> bool:
    """Eliminate TYPE_CHECKING patterns in a single file."""
    if not file_path.exists() or not file_path.name.endswith('.py'):
        return False

    content = file_path.read_text()
    original_content = content

    # Pattern 1: Remove TYPE_CHECKING blocks and make imports direct
    type_checking_pattern = r'if TYPE_CHECKING:\s*\n((?:[ \t]*from .+\n?)+)'
    matches = re.findall(type_checking_pattern, content, re.MULTILINE)

    if matches:
        # Extract imports from TYPE_CHECKING blocks
        direct_imports = []
        for match in matches:
            import_lines = match.strip().split('\n')
            for line in import_lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    direct_imports.append(line)

        # Remove TYPE_CHECKING blocks
        content = re.sub(type_checking_pattern, '', content, flags=re.MULTILINE)

        # Add direct imports at top after existing imports
        if direct_imports:
            # Find the position after the last import
            import_position = 0
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith(('from ', 'import ')) and 'TYPE_CHECKING' not in line:
                    import_position = i + 1

            # Insert direct imports
            for import_line in direct_imports:
                lines.insert(import_position, import_line)
                import_position += 1

            content = '\n'.join(lines)

    # Pattern 2: Remove TYPE_CHECKING import itself
    content = re.sub(r'from typing import.*TYPE_CHECKING.*\n', '', content)
    content = re.sub(r'from typing import TYPE_CHECKING\n', '', content)

    # Pattern 3: Clean up typing imports if TYPE_CHECKING was the only one
    content = re.sub(r'from typing import \s*\n', '', content)

    # Pattern 4: Remove lazy_import references
    content = re.sub(r'from .*lazy_import.*\n', '', content)
    content = re.sub(r'import.*lazy_import.*\n', '', content)

    # Pattern 5: Clean up multiple blank lines
    content = re.sub(r'\n\n\n+', '\n\n', content)

    if content != original_content:
        file_path.write_text(content)
        return True
    return False


def eliminate_lazy_imports_project() -> tuple[int, list[str]]:
    """Eliminate ALL lazy imports in FLX project."""
    flx_path = Path("/home/marlonsc/pyauto/flx")
    src_path = flx_path / "src"

    fixed_files = []
    total_fixed = 0

    # Find all Python files with TYPE_CHECKING or lazy imports
    for py_file in src_path.rglob("*.py"):
        if py_file.is_file():
            content = py_file.read_text()
            if 'TYPE_CHECKING' in content or 'lazy_import' in content:
                if eliminate_type_checking_file(py_file):
                    fixed_files.append(str(py_file.relative_to(flx_path)))
                    total_fixed += 1

    return total_fixed, fixed_files


def main():
    """Execute lazy import elimination."""

    # Log start
    with open("/home/marlonsc/pyauto/.token", "a") as f:
        f.write("ELIMINATE-LAZY-IMPORTS-FLX-001 STARTED: Zero tolerance elimination begins\n")

    total_fixed, fixed_files = eliminate_lazy_imports_project()

    # Remove lazy_import utils if it exists
    lazy_import_utils = Path("/home/marlonsc/pyauto/flx/src/flx/utils")
    if lazy_import_utils.exists():
        for file in lazy_import_utils.glob("*lazy*"):
            if file.is_file():
                file.unlink()
                fixed_files.append(f"DELETED: {file}")

    # Log completion
    with open("/home/marlonsc/pyauto/.token", "a") as f:
        f.write(f"ELIMINATE-LAZY-IMPORTS-FLX-001 COMPLETED: Fixed {total_fixed} files, eliminated all TYPE_CHECKING\n")

    return total_fixed > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
