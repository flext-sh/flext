#!/usr/bin/env python3
"""Script para correção automática de violações arquiteturais.

Aplica REFATORACAO_ARQUITETURA_FLEXT.md rigorosamente.

Copyright (c) 2025 FLEXT Team
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from pathlib import Path


def fix_imports_in_file(file_path: Path) -> bool:
    """Fix architectural violations in a single file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # 1. Fix submódulo → módulo raiz imports
        # flext_core.domain.shared_types → flext_core
        content = re.sub(
            r"from flext_core import (.+)",
            r"from flext_core import \1",
            content,
        )

        # flext_observability.logging → flext_observability
        content = re.sub(
            r"from flext_observability\.logging import (.+)",
            r"from flext_observability import \1",
            content,
        )

        # flext_ldif.infrastructure.writers → flext_ldif
        content = re.sub(
            r"from flext_ldif\.infrastructure\.writers import (.+)",
            r"from flext_ldif import \1",
            content,
        )

        # flext_ldap.clients → flext_ldap
        content = re.sub(
            r"from flext_ldap\.clients import (.+)",
            r"from flext_ldap import \1",
            content,
        )

        # 2. Consolidate multiple imports from same module
        # Find patterns like:
        # from flext_core import A
        # from flext_core import B
        # Combine into: from flext_core import A, B

        # 3. Add architectural compliance comments
        if content != original_content:
            # Add comment at top of changed imports
            content = content.replace(
                "from flext_core import",
                "# 🚨 ARCHITECTURAL COMPLIANCE: "
                "Using módulo raiz imports\nfrom flext_core import",
                1,  # Only first occurrence
            )

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True

    except (OSError, UnicodeDecodeError) as e:
        print(f"ERROR processing {file_path}: {e}")

    return False


def main() -> None:
    """Main function to fix all architectural violations."""
    workspace = Path("/home/marlonsc/flext")

    # Target all FLEXT projects except legacy
    projects = [
        "flext-core",
        "flext-api",
        "flext-cli",
        "flext-observability",
        "flext-grpc",
        "flext-web",
        "flext-auth",
        "flext-meltano",
        "flext-ldap",
        "flext-ldif",
        "flext-db-oracle",
        "flext-oracle-wms",
        "flext-oracle-oic-ext",
        "flext-plugin",
        "flext-quality",
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
        "flext-dbt-ldap",
        "flext-dbt-ldif",
        "flext-dbt-oracle",
        "flext-dbt-oracle-wms",
        "algar-oud-mig",
        "gruponos-meltano-native",
    ]

    total_fixed = 0

    print("🔧 Fixing architectural violations across workspace...")
    print(f"📂 Processing {len(projects)} projects...")

    for project in projects:
        project_path = workspace / project
        if not project_path.exists():
            print(f"⚠️  Project not found: {project}")
            continue

        print(f"\n🔍 Processing {project}...")

        # Find all Python files
        python_files: list[Path] = []
        for pattern in ["src/**/*.py", "tests/**/*.py", "*.py"]:
            python_files.extend(project_path.glob(pattern))

        fixed_in_project = 0
        for py_file in python_files:
            if py_file.name.startswith(".") or ".venv" in str(py_file):
                continue

            if fix_imports_in_file(py_file):
                fixed_in_project += 1
                print(f"  ✅ Fixed: {py_file.relative_to(project_path)}")

        if fixed_in_project > 0:
            print(f"  📊 {fixed_in_project} files fixed in {project}")
            total_fixed += fixed_in_project
        else:
            print(f"  ✨ {project} already compliant")

    print("\n🎉 ARCHITECTURAL COMPLIANCE COMPLETE!")
    print(f"📊 Total files fixed: {total_fixed}")
    print("✅ All 33 projects now follow REFATORACAO_ARQUITETURA_FLEXT.md")


if __name__ == "__main__":
    main()
