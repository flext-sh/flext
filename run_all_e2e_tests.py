#!/usr/bin/env python3
"""Run all E2E tests for tap-oracle-wms, target-oracle-wms, and flx-oracle-wms."""

import os
import subprocess
import sys
from pathlib import Path

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def run_project_tests(project_name: str, test_file: str) -> tuple[bool, str]:
    """Run E2E tests for a specific project."""
    project_path = Path(project_name)
    test_path = project_path / test_file

    if not test_path.exists():
        return False, f"Test file not found: {test_path}"

    # First, ensure dependencies are installed
    if (project_path / "pyproject.toml").exists():
        install_result = subprocess.run(
            ["poetry", "install", "--no-interaction"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False,
        )

        if install_result.returncode != 0:
            pass

    # Run the E2E tests
    result = subprocess.run(
        [sys.executable, str(test_path)],
        cwd=project_path,
        capture_output=True,  # Capture output for processing
        text=True,
        check=False,
    )

    # Print the output
    if result.stdout:
        pass
    if result.stderr:
        pass

    success = result.returncode == 0
    status = "PASSED" if success else "FAILED"

    return success, status


def check_environment() -> Any:
    """Check that .env file exists with required variables."""
    env_file = Path(".env")
    if not env_file.exists():
        return False

    # Check for required variables
    required_vars = ["WMS_BASE_URL", "WMS_USERNAME", "WMS_PASSWORD"]

    with open(env_file, encoding="utf-8") as f:
        env_content = f.read()

    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in env_content:
            missing_vars.append(var)

    if missing_vars:
        pass

    return True


def main() -> None:
    """Run all E2E tests."""

    # Check environment
    if not check_environment():
        pass

    # Define test suite
    test_suite = [
        ("tap-oracle-wms", "tests/e2e/test_tap_e2e.py"),
        ("target-oracle-wms", "tests/e2e/test_target_e2e.py"),
        ("flx-oracle-wms", "tests/e2e/test_flx_e2e.py"),
    ]

    results = []

    # Run tests for each project
    for project, test_file in test_suite:
        success, status = run_project_tests(project, test_file)
        results.append((project, success, status))

    # Print summary

    all_passed = True
    for project, success, status in results:
        if not success:
            all_passed = False

    if all_passed:
        return 0
    return 1


if __name__ == "__main__":
    # Change to pyauto directory
    pyauto_dir = Path(__file__).parent
    os.chdir(pyauto_dir)

    # Run tests
    sys.exit(main())
