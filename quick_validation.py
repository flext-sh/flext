#!/usr/bin/env python3
"""Quick validation of all projects."""

import subprocess
import sys
from pathlib import Path


def test_project(name, path) -> Any:
    """Quick test of a project."""

    # Check if project exists
    if not Path(path).exists():
        return False

    # Try to import the module
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            f"import sys; sys.path.insert(0, '{path}/src'); import {name.replace('-', '_')}; print('✅ Import successful')",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    return result.returncode == 0


# Test all projects
projects = [
    ("tap-oracle-wms", "tap-oracle-wms"),
    ("target-oracle-wms", "target-oracle-wms"),
    ("flx-oracle-wms", "flx-oracle-wms"),
]

all_ok = True
for name, path in projects:
    if not test_project(name, path):
        all_ok = False

if all_ok:
    pass

sys.exit(0 if all_ok else 1)
