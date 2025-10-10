#!/usr/bin/env python3
"""Remove redundant version imports and assignments.

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
    "flext-web",
    "client-b-meltano-native",
]


def fix_init_file(project_name: str) -> bool:
    """Fix __init__.py by removing redundant version code."""
    package_name = project_name.replace("-", "_")
    init_file = FLEXT_ROOT / project_name / "src" / package_name / "__init__.py"

    if not init_file.exists():
        print(f"   ❌ {project_name}: No __init__.py found")
        return False

    content = init_file.read_text()

    # Remove old version.py import
    content = re.sub(
        r"^from\s+\w+\.version\s+import.*$", "", content, flags=re.MULTILINE
    )

    # Remove try/except block for importlib.metadata.version
    content = re.sub(
        r'try:\s*\n\s*__version__\s*=\s*importlib\.metadata\.version\(["\'].*?["\']\)\s*\n.*?except.*?:\s*\n\s*__version__\s*=\s*["\'].*?["\']\s*\n',
        "",
        content,
        flags=re.DOTALL,
    )

    # Remove PROJECT_VERSION assignment
    content = re.sub(
        r"^PROJECT_VERSION:.*?=.*?VERSION.*$", "", content, flags=re.MULTILINE
    )

    # Remove redundant __version__ assignments
    content = re.sub(
        r"^__version__:\s*str\s*=\s*VERSION\.version.*$",
        "",
        content,
        flags=re.MULTILINE,
    )

    # Remove redundant __version_info__ assignments
    content = re.sub(
        r"^__version_info__:.*?=\s*VERSION\.version_info.*$",
        "",
        content,
        flags=re.MULTILINE,
    )

    # Clean up multiple blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)

    # Remove PROJECT_VERSION and VERSION from __all__
    version_exports = [
        "PROJECT_VERSION",
        "VERSION",
        "FlextTargetLdapVersion",
        "FlextMeltanoTapOracleOicVersion",
        "FlextTargetOracleOicVersion",
        "FlextAuthVersion",
        "FlextLdifVersion",
        "FlextObservabilityVersion",
        "FlextOracleWmsVersion",
        "FlextQualityVersion",
        "FlextWebVersion",
        "client-bMeltanoNativeVersion",
    ]

    for export in version_exports:
        content = re.sub(rf'^\s*"{export}",\s*\n', "", content, flags=re.MULTILINE)

    init_file.write_text(content)
    print(f"   ✅ {project_name}: Fixed __init__.py")
    return True


def main() -> None:
    """Fix all __init__.py files."""
    print("=" * 80)
    print("🔧 Removing redundant version imports and assignments")
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
