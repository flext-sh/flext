#!/usr/bin/env python
"""
Fix the 4 broken projects with specific syntax errors.

Per CLAUDE.md RULE 4: Complete delivery with zero tolerance for violations.
Fix: flx-oracle-oic, gruponos-poc-oic-wms, tap-oracle-oic, target-ldap
"""

import re
from pathlib import Path


def fix_corrupted_imports(file_path: Path) -> bool:
    """Fix corrupted import statements."""
    if not file_path.exists():
        return False

    content = file_path.read_text()
    original_content = content

    # Fix pattern: "from typing import ... from typing import ..."
    content = re.sub(
        r"from typing import [^,\n]+(?:, [^,\n]+)* from typing import [^,\n]+(?:, [^,\n]+)*",
        "from typing import Any, Dict, List, Optional",
        content,
    )

    # Fix constants that got mixed with imports
    content = re.sub(
        r"from typing import [^,\n]+(?:, [^,\n]+)* ([A-Z_]+(?:, [A-Z_]+)*)",
        r"from typing import Any, Dict, List, Optional\n\nfrom .constants import \1",
        content,
    )

    # Fix missing quotes in strings
    content = re.sub(r'env_path"\)', 'env_path")', content)

    if content != original_content:
        file_path.write_text(content)
        return True
    return False


def fix_missing_imports(file_path: Path) -> bool:
    """Fix missing import statements."""
    if not file_path.exists():
        return False

    content = file_path.read_text()
    original_content = content

    # Fix missing HttpClientAdapter import
    if (
        "HttpClientAdapter" in content
        and "from " not in content.split("HttpClientAdapter")[0].split("\n")[-1]
    ):
        # Add the missing import
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("from typing") or line.strip().startswith(
                "import "
            ):
                # Add import after typing imports
                lines.insert(
                    i + 1, "from flx.adapters.outbound.http import HttpClientAdapter"
                )
                break
        content = "\n".join(lines)

    if content != original_content:
        file_path.write_text(content)
        return True
    return False


def fix_project(project_name: str) -> bool:
    """Fix specific project."""
    project_path = Path(f"/home/marlonsc/pyauto/{project_name}")
    fixed_files = []

    if project_name == "flx-oracle-oic":
        # Fix missing HttpClientAdapter import
        adapter_file = project_path / "src/flx_oracle_oic/adapter.py"
        if fix_missing_imports(adapter_file):
            fixed_files.append("adapter.py")

    elif project_name == "tap-oracle-oic":
        # Fix corrupted imports in streams.py
        streams_file = project_path / "src/tap_oracle_oic/streams.py"
        if fix_corrupted_imports(streams_file):
            fixed_files.append("streams.py")

    elif project_name == "target-ldap":
        # Fix corrupted imports in client.py
        client_file = project_path / "src/target_ldap/client.py"
        if fix_corrupted_imports(client_file):
            fixed_files.append("client.py")

    # Test if fix worked
    module_name = project_name.replace("-", "_")
    import subprocess

    try:
        result = subprocess.run(
            [
                "python",
                "-c",
                f"import sys; sys.path.insert(0, '{project_path}/src'); import {module_name}; print('✅ Success')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            return True
        return False
    except Exception:
        return False


def main():
    """Fix all 4 broken projects."""

    broken_projects = [
        "flx-oracle-oic",
        "gruponos-poc-oic-wms",  # Already fixed by linter
        "tap-oracle-oic",
        "target-ldap",
    ]

    fixed_count = 0

    for project in broken_projects:
        if fix_project(project):
            fixed_count += 1

    # Log to token
    with open("/home/marlonsc/pyauto/.token", "a") as f:
        f.write(
            f"FIX-4-BROKEN-PROJECTS-004: Fixed {fixed_count}/{len(broken_projects)} projects\n"
        )

    return fixed_count == len(broken_projects)


if __name__ == "__main__":
    success = main()
    if success:
        pass
    else:
        pass
