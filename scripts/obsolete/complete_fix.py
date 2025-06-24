#!/usr/bin/env python3
"""Complete fix for dc-api-x pydantic compatibility issues."""

import os
import shutil
import subprocess
import venv
from pathlib import Path


def run_command(cmd, cwd=None) -> bool:
    """Run a command and return its output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"Error: {result.stderr}")
        return False
    return True


def main() -> None:
    """Set up an isolated environment for dc-api-x."""
    # Paths
    base_dir = Path("/home/marlonsc/pyauto")
    venv_path = base_dir / ".venv_completely_isolated"
    dc_api_x_dir = base_dir / "dc-api-x"

    # Clear any existing venv
    if venv_path.exists():
        print(f"Removing existing virtual environment at {venv_path}")
        shutil.rmtree(venv_path)

    # Create a truly isolated virtual environment
    print(f"Creating a new virtual environment at {venv_path}")
    venv.create(venv_path, with_pip=True, system_site_packages=False)

    # Determine Python executable path
    python_path = venv_path / "bin" / "python"
    pip_path = venv_path / "bin" / "pip"

    # Verify pip is installed
    if not (venv_path / "bin" / "pip").exists():
        print("Pip not found in the virtual environment. Installing...")
        run_command([str(python_path), "-m", "ensurepip", "--upgrade"])

    # Upgrade pip
    run_command([str(pip_path), "install", "--upgrade", "pip"])

    # Install dependencies one by one in the correct order
    # First install essential dependencies
    packages = [
        "typing-extensions==4.8.0",
        "annotated-types==0.5.0",
        "pydantic-core==2.10.1",
        "pydantic==2.4.2",
        "pydantic-settings==2.0.3",
        "python-dotenv==0.1.0",
        "click==8.1.3",
        "typer==0.9.0",
    ]

    # Install packages
    for package in packages:
        run_command([str(pip_path), "install", package])

    # Install dc-api-x in development mode
    print("Installing dc-api-x...")
    run_command([str(pip_path), "install", "-e", str(dc_api_x_dir)])

    # Create activation script wrapper
    wrapper_path = base_dir / "use_dcapix.sh"
    with open(wrapper_path, "w", encoding="utf-8") as f:
        f.write(f"""#!/bin/bash
source {venv_path}/bin/activate
dcapix "$@"
""")

    # Make it executable
    os.chmod(wrapper_path, 0o755)

    print("\nInstallation complete!")
    print(f"To use dcapix, run: {wrapper_path}")
    print("This will activate the isolated environment and run the command.")


if __name__ == "__main__":
    main()
