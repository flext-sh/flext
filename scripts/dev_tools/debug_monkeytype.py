#!/usr/bin/env python3
"""Simple debug script for MonkeyType."""

import subprocess
from pathlib import Path


def main() -> None:
    """Test MonkeyType on a specific module."""
    module_path = "dc_api_x.exceptions"

    print(f"Testing MonkeyType apply on module: {module_path}")

    # Find the file path
    module_parts = module_path.split(".")
    print(f"Module parts: {module_parts}")

    workspace_root = Path.cwd()
    print(f"Workspace root: {workspace_root}")

    if module_parts[0] == "dc_api_x":
        # Check the structure
        module_file = (
            workspace_root / "src" / module_parts[0] / "/".join(module_parts[1:])
        ).with_suffix(".py")
        print(f"Checking file path: {module_file}")
        print(f"File exists: {module_file.exists()}")

    # Apply types
    cmd = ["monkeytype", "apply", module_path]
    print(f"Running command: {' '.join(cmd)}")

    result = subprocess.run(cmd, check=False)
    print(f"Command result: {result.returncode}")


if __name__ == "__main__":
    main()
