#!/usr/bin/env python
"""
Fix all Poetry lock files across workspace.

Following CLAUDE.md RULE 4: Complete Delivery
"""

import subprocess
from pathlib import Path


def fix_poetry_locks() -> None:
    """Fix poetry.lock files for all projects."""
    workspace_root = Path("/home/marlonsc/pyauto")
    submodules = [
        "client-a-oud-mig",
        "dbt-ldap",
        "dc-code-analyzer",
        "flx",
        "flx-adapter-example",
        "flx-database-oracle",
        "flx-http-oracle-oic",
        "flx-http-oracle-wms",
        "flx-ldap",
        "flx-meltano-enterprise",
        "flx-oracle-oic",
        "flx-oracle-wms",
        "client-b-poc-oic-wms",
        "ldap-core-shared",
        "oracle-oic-ext",
        "tap-ldap",
        "tap-oracle-oic",
        "tap-oracle-wms",
        "target-ldap",
        "target-oracle-oic",
        "target-oracle-wms",
    ]

    fixed = 0
    failed = 0

    for project in submodules:
        project_path = workspace_root / project

        if not project_path.exists():
            continue

        # Remove old lock file
        lock_file = project_path / "poetry.lock"
        if lock_file.exists():
            lock_file.unlink()

        # Generate new lock file
        try:
            result = subprocess.run(
                ["poetry", "lock"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                fixed += 1
                failed += 1
        except subprocess.TimeoutExpired:
            failed += 1
        except Exception:
            failed += 1

    # Log to token
    with open(workspace_root / ".token", "a") as f:
        f.write(f"POETRY-LOCK-FIX-001: {fixed}/21 locks fixed\n")

    return failed == 0


if __name__ == "__main__":
    success = fix_poetry_locks()
    exit(0 if success else 1)
