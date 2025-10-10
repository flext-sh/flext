#!/usr/bin/env python3
"""Update __init__.py files to import from __version__.py.

This script automates updating all __init__.py files across FLEXT ecosystem projects
to import version metadata from __version__.py instead of using hardcoded values.

Copyright (c) 2025 client-a Telecom. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

FLEXT_ROOT: Final[Path] = Path("/home/marlonsc/flext")

# Projects that need __init__.py updates (from standardization report)
PROJECTS_TO_UPDATE = [
    "flexcore",
    "flext-cli",
    "flext-db-oracle",
    "flext-dbt-ldap",
    "flext-dbt-ldif",
    "flext-dbt-oracle",
    "flext-dbt-oracle-wms",
    "flext-grpc",
    "flext-ldap",
    "flext-meltano",
    "flext-oracle-oic",
    "flext-plugin",
    "flext-tap-ldap",
    "flext-tap-ldif",
    "flext-tap-oracle",
    "flext-tap-oracle-oic",
    "flext-tap-oracle-wms",
    "flext-target-ldap",
    "flext-target-ldif",
    "flext-target-oracle",
    "flext-target-oracle-oic",
    "flext-target-oracle-wms",
]


def update_init_file(project_name: str) -> bool:
    """Update __init__.py to import from __version__.

    Args:
        project_name: Name of the project directory

    Returns:
        True if updated successfully, False otherwise

    """
    # Find the package directory
    project_dir = FLEXT_ROOT / project_name
    src_dir = project_dir / "src"

    if not src_dir.exists():
        print(f"   ❌ No src/ directory in {project_name}")
        return False

    # Find package directory
    package_name = project_name.replace("-", "_")
    package_dir = src_dir / package_name

    if not package_dir.exists():
        # Try to find any package directory
        package_dirs = [
            d for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
        ]
        if not package_dirs:
            print(f"   ❌ No package directory in {project_name}/src/")
            return False
        package_dir = package_dirs[0]
        package_name = package_dir.name

    init_file = package_dir / "__init__.py"

    if not init_file.exists():
        print(f"   ⚠️  No __init__.py in {package_name}")
        return False

    # Read current content
    content = init_file.read_text()

    # Check if already imports from __version__
    if f"from {package_name}.__version__ import" in content:
        print(f"   ℹ️  {project_name}: Already imports from __version__")
        return True

    # Remove hardcoded version metadata
    new_content = content

    # Remove hardcoded __version__ (but keep imports)
    new_content = re.sub(
        r'^__version__\s*=\s*["\'].*?["\'].*$', "", new_content, flags=re.MULTILINE
    )

    # Remove hardcoded __author__
    new_content = re.sub(
        r'^__author__\s*=\s*["\'].*?["\'].*$', "", new_content, flags=re.MULTILINE
    )

    # Remove hardcoded __email__
    new_content = re.sub(
        r'^__email__\s*=\s*["\'].*?["\'].*$', "", new_content, flags=re.MULTILINE
    )

    # Remove hardcoded __description__
    new_content = re.sub(
        r'^__description__\s*=\s*["\'].*?["\'].*$', "", new_content, flags=re.MULTILINE
    )

    # Add import from __version__ after "from __future__ import annotations"
    if "from __future__ import annotations" in new_content:
        new_content = new_content.replace(
            "from __future__ import annotations",
            f"from __future__ import annotations\n\nfrom {package_name}.__version__ import __version__, __version_info__",
        )
    else:
        # Add at the top after docstring
        lines = new_content.split("\n")
        insert_index = 0

        # Skip module docstring
        in_docstring = False
        for i, line in enumerate(lines):
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                elif in_docstring:
                    insert_index = i + 1
                    break

        if insert_index == 0:
            insert_index = 1  # After first line

        lines.insert(
            insert_index,
            f"\nfrom {package_name}.__version__ import __version__, __version_info__",
        )
        new_content = "\n".join(lines)

    # Clean up multiple blank lines
    new_content = re.sub(r"\n{3,}", "\n\n", new_content)

    # Write updated content
    init_file.write_text(new_content)

    print(f"   ✅ {project_name}: Updated __init__.py")
    return True


def main() -> None:
    """Update all __init__.py files."""
    print("=" * 80)
    print("🔧 Updating __init__.py files to import from __version__.py")
    print("=" * 80)

    success_count = 0
    for project in PROJECTS_TO_UPDATE:
        if update_init_file(project):
            success_count += 1

    print("\n" + "=" * 80)
    print(f"✅ Updated {success_count}/{len(PROJECTS_TO_UPDATE)} __init__.py files")
    print("=" * 80)


if __name__ == "__main__":
    main()
