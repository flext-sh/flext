#!/usr/bin/env python3
"""Fix remaining __init__.py files that need __version__ imports.

Copyright (c) 2025 client-a Telecom. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

import re
from pathlib import Path

FLEXT_ROOT = Path("/home/marlonsc/flext")

PROJECTS_TO_FIX = [
    "flext-auth",
    "flext-ldif",
    "flext-observability",
    "flext-oracle-wms",
    "flext-quality",
    "flext-tap-ldif",
    "flext-tap-oracle-oic",
    "flext-target-ldap",
    "flext-target-oracle-oic",
    "flext-web",
    "client-b-meltano-native",
]


def fix_init_file(project_name: str) -> bool:
    """Fix __init__.py for a project."""
    package_name = project_name.replace("-", "_")
    package_dir = FLEXT_ROOT / project_name / "src" / package_name
    init_file = package_dir / "__init__.py"

    if not init_file.exists():
        print(f"   ❌ {project_name}: No __init__.py found")
        return False

    content = init_file.read_text()

    # Remove hardcoded __version__
    content = re.sub(
        r'^__version__\s*=\s*["\'].*?["\'].*$', "", content, flags=re.MULTILINE
    )

    # Remove hardcoded __author__
    content = re.sub(
        r'^__author__\s*=\s*["\'].*?["\'].*$', "", content, flags=re.MULTILINE
    )

    # Add import if not present
    if f"from {package_name}.__version__ import" not in content:
        # Add after "from __future__ import annotations"
        if "from __future__ import annotations" in content:
            content = content.replace(
                "from __future__ import annotations",
                f"from __future__ import annotations\n\nfrom {package_name}.__version__ import __version__, __version_info__",
            )
        else:
            # Add at the top after docstring
            lines = content.split("\n")
            insert_index = 0

            # Skip module docstring
            in_docstring = False
            for i, line in enumerate(lines):
                if '"""' in line or "'''" in line:
                    if not in_docstring:
                        in_docstring = True
                    else:
                        insert_index = i + 1
                        break

            if insert_index == 0:
                insert_index = 1

            lines.insert(
                insert_index,
                f"\nfrom {package_name}.__version__ import __version__, __version_info__",
            )
            content = "\n".join(lines)

    # Clean up multiple blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)

    init_file.write_text(content)
    print(f"   ✅ {project_name}: Fixed __init__.py")
    return True


def main() -> None:
    """Fix all remaining __init__.py files."""
    print("=" * 80)
    print("🔧 Fixing remaining __init__.py files")
    print("=" * 80)

    success = 0
    for project in PROJECTS_TO_FIX:
        if fix_init_file(project):
            success += 1

    print("\n" + "=" * 80)
    print(f"✅ Fixed {success}/{len(PROJECTS_TO_FIX)} __init__.py files")
    print("=" * 80)


if __name__ == "__main__":
    main()
