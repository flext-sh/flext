#!/usr/bin/env python3
"""
FLEXT Syntax Error Fixer
========================

Fixes specific syntax errors identified in quality pipeline.
"""

import re
from pathlib import Path

from rich.console import Console

console = Console()


def fix_double_docstrings(file_path: Path) -> bool:
    """Fix files with double docstrings causing syntax errors."""
    if not file_path.exists():
        return False

    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Pattern: def __init__(...): \n    """Initialize instance.""" \n    """Real docstring...
        # Fix: Remove the auto-added generic docstring
        pattern = r'(def __init__\([^)]*\) -> None:)\n(\s*)"""Initialize instance\."""\n(\s*)"""([^"]+)"""'
        content = re.sub(pattern, r'\1\n\2"""\4"""', content)

        # Pattern: class ClassName: \n    """Initialize instance.""" \n    """Real docstring...
        pattern = (
            r'(class \w+[^:]*:)\n(\s*)"""Initialize instance\."""\n(\s*)"""([^"]+)"""'
        )
        content = re.sub(pattern, r'\1\n\2"""\4"""', content)

        # Fix indentation issues where """Initialize instance.""" is wrongly indented
        pattern = r'(\s+)"""Initialize instance\."""\n(\s+)"""([^"]+)"""'
        content = re.sub(pattern, r'\2"""\3"""', content)

        # Remove orphaned "Initialize instance." docstrings
        content = re.sub(
            r'^\s*"""Initialize instance\."""\s*\n', "", content, flags=re.MULTILINE
        )

        if content != original_content:
            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + ".syntax_backup")
            backup_path.write_text(original_content, encoding="utf-8")

            # Write fixed content
            file_path.write_text(content, encoding="utf-8")
            console.print(f"[green]✓ Fixed syntax errors in {file_path}[/green]")
            return True

    except Exception as e:
        console.print(f"[red]❌ Error fixing {file_path}: {e}[/red]")
        return False

    return False


def main() -> None:
    """Fix syntax errors in flext-auth."""
    workspace_root = Path.cwd()
    auth_project = workspace_root / "flext-auth"

    if not auth_project.exists():
        console.print("[red]❌ flext-auth directory not found[/red]")
        return

    console.print("[cyan]🔧 Fixing syntax errors in flext-auth...[/cyan]")

    fixed_count = 0

    # Fix all Python files in flext-auth
    for py_file in auth_project.rglob("*.py"):
        if fix_double_docstrings(py_file):
            fixed_count += 1

    console.print(f"[green]✅ Fixed syntax errors in {fixed_count} files[/green]")


if __name__ == "__main__":
    main()
