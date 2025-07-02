#!/usr/bin/env python3
"""
Simple FLEXT MyPy Issues Fix Script

This script fixes the most common MyPy issues with simple string replacements.
"""

from pathlib import Path


def fix_common_issues():
    """Fix common MyPy issues across FLEXT projects."""
    workspace_root = Path("/home/marlonsc/flext")
    fixes_applied = []

    # Find all Python files in flext-* projects
    for project_dir in workspace_root.glob("flext-*"):
        if not project_dir.is_dir() or project_dir.name.endswith(".bak"):
            continue

        src_dir = project_dir / "src"
        if not src_dir.exists():
            continue

        for py_file in src_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                original_content = content

                # Fix 1: Missing generic type parameters
                content = content.replace(": dict = {}", ": dict[str, Any] = {}")
                content = content.replace(": dict = None", ": dict[str, Any] = None")
                content = content.replace(": list = []", ": list[Any] = []")
                content = content.replace(": list = None", ": list[Any] = None")

                # Fix 2: __post_init__ return annotations
                content = content.replace(
                    "def __post_init__(self):", "def __post_init__(self) -> None:"
                )

                # Fix 3: Remove unused type ignores
                content = content.replace("  # type: ignore[no-untyped-call]", "")
                content = content.replace("  # type: ignore[unused-ignore]", "")

                # Fix 4: Missing Any import where needed
                if ": dict[str, Any]" in content or ": list[Any]" in content:
                    if "from typing import" in content and "Any" not in content:
                        # Simple addition of Any to existing typing import
                        lines = content.split("\n")
                        for i, line in enumerate(lines):
                            if (
                                line.strip().startswith("from typing import")
                                and "Any" not in line
                            ):
                                if line.endswith(")"):
                                    # Multi-line import
                                    lines[i] = line.replace(")", ", Any)")
                                else:
                                    # Single-line import
                                    lines[i] = line + ", Any"
                                break
                        content = "\n".join(lines)

                # Write back if changed
                if content != original_content:
                    py_file.write_text(content)
                    fixes_applied.append(f"Fixed {py_file}")

            except Exception:
                pass

    for _fix in fixes_applied[:10]:  # Show first 10
        pass
    if len(fixes_applied) > 10:
        pass


if __name__ == "__main__":
    fix_common_issues()
