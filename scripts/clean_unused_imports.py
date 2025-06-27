#!/usr/bin/env python
"""Clean unused typing imports from flx-meltano-enterprise."""

from pathlib import Path


def clean_unused_imports(file_path: Path) -> bool:
    """Clean unused typing imports from a file."""
    if not file_path.exists() or file_path.suffix != ".py":
        return False

    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Remove specific unused imports
        lines = content.split("\n")
        new_lines: list = []

        for line in lines:
            # Skip these specific unused import lines
            if line.strip() in [
                "from typing import Optional",
                "from typing import Dict",
                "from typing import List",
            ]:
                continue
            new_lines.append(line)

        new_content = "\n".join(new_lines)

        if new_content != original_content:
            file_path.write_text(new_content, encoding="utf-8")
            return True

        return False

    except Exception:
        return False


def main() -> None:
    """Clean all files in flx-meltano-enterprise."""
    project_root = Path("/home/marlonsc/pyauto/flx-meltano-enterprise")

    cleaned_files = 0
    total_files = 0

    for py_file in project_root.rglob("*.py"):
        if ".venv" in str(py_file) or "__pycache__" in str(py_file):
            continue

        total_files += 1
        if clean_unused_imports(py_file):
            cleaned_files += 1


if __name__ == "__main__":
    main()
