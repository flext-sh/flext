#!/usr/bin/env python3
"""Project Management Script.

Provides consolidated functionality for managing multiple Python projects
in the pyauto workspace.

This script handles:
1. Environment setup (venv, Poetry)
2. Dependency installation and management
3. Testing, linting, and formatting
4. Project standardization
5. Status reporting

Usage:
    python project_manage.py [command] [options]
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Absolute paths
WORKSPACE_ROOT = Path("/home/marlonsc/pyauto")
VENV_DIR = WORKSPACE_ROOT / ".venv"
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"

# Configuration
PYTHON_VERSION = "3.13"
PYTHON_CONSTRAINT = "^3.13"
PY_TARGET_VERSION = "py313"
MYPY_PY_VERSION = "3.13"
LINE_LENGTH = 88

# Projects to manage
DEFAULT_PROJECTS = [
    "dc-automatic",
    "dc-auto",
    "dc-meltano-plugins",
    "dc-oracle-oic",
    "dc-oracle-wms",
    "project-algar-oud",
    "project-gruponos-poc-oic-wms",
    "scripts",
]

# Cache files to track changes
POETRY_INSTALL_CHECK = WORKSPACE_ROOT / ".poetry_install_complete"
VENV_CHECK = WORKSPACE_ROOT / ".venv_complete"
LOCK_UPDATED_CHECK = WORKSPACE_ROOT / ".lock_updated"

# Colors for terminal output
COLORS = {
    "GREEN": "\033[0;32m",
    "YELLOW": "\033[0;33m",
    "RED": "\033[0;31m",
    "NC": "\033[0m",  # No Color
}


def colorize(text: str, color: str) -> str:
    """Add color to terminal output."""
    return f"{COLORS.get(color, '')}{text}{COLORS['NC']}"


def run_command(
    cmd: list[str],
    cwd: Path | None = None,
    capture_output: bool = False,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Run a shell command."""
    try:
        return subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=capture_output,
            text=True,
            check=check,
            env=env,
        )
    except subprocess.CalledProcessError as e:
        print(f"{colorize('Error:', 'RED')} {e}")
        if capture_output and e.stderr:
            print(e.stderr)
        if check:
            sys.exit(1)
        return e


def ensure_venv() -> None:
    """Ensure virtual environment exists and is up to date."""
    print("Checking virtual environment...")

    # Check if virtualenv exists and is valid
    pip_path = VENV_DIR / "bin" / "pip"
    poetry_path = VENV_DIR / "bin" / "poetry"
    venv_broken = False

    if VENV_DIR.exists():
        if not pip_path.exists():
            print(colorize("Virtual environment is broken, recreating...", "YELLOW"))
            venv_broken = True
            shutil.rmtree(VENV_DIR)
            try:
                # Check if the virtualenv is working
                run_command([str(pip_path), "--version"], capture_output=True)
            except Exception:
                print(
                    colorize(
                        "Virtual environment is not working, recreating...",
                        "YELLOW",
                    ),
                )
                venv_broken = True
                shutil.rmtree(VENV_DIR)

    if not VENV_DIR.exists() or venv_broken:
        # Find Python interpreter
        py_version = PYTHON_VERSION
        try:
            # Try to find the system Python with the required version
            which_result = run_command(
                ["which", f"python{py_version}"],
                capture_output=True,
            )
            python_path = which_result.stdout.strip()
            print(f"Using Python interpreter: {python_path}")
        except Exception:
            # Fallback to the generic command
            python_path = f"python{py_version}"
            print(f"Using default Python command: {python_path}")

        print(f"Creating virtual environment in {VENV_DIR}...")
        run_command([python_path, "-m", "venv", str(VENV_DIR)])

    # Verify the virtualenv is functional
    try:
        # Upgrade pip
        run_command([str(pip_path), "install", "--upgrade", "pip"])

        # Install Poetry in virtualenv if it doesn't exist
        if not poetry_path.exists():
            print("Installing Poetry inside virtualenv...")
            run_command([str(pip_path), "install", "poetry"])

        # Mark venv as complete
        VENV_CHECK.touch()
        print(colorize("Virtual environment is ready", "GREEN"))
    except Exception as e:
        print(colorize(f"Error setting up virtual environment: {e}", "RED"))
        print(
            colorize(
                "Try running 'make fix-venv' to rebuild the virtualenv",
                "YELLOW",
            ),
        )
        sys.exit(1)


def configure_poetry() -> None:
    """Configure Poetry to use the workspace virtual environment."""
    ensure_venv()

    print("Configuring Poetry to use workspace virtual environment...")

    # Use Poetry from the virtualenv if available
    poetry_path = VENV_DIR / "bin" / "poetry"
    poetry_cmd = str(poetry_path) if poetry_path.exists() else "poetry"

    # Get Poetry version
    poetry_version_result = run_command([poetry_cmd, "--version"], capture_output=True)
    poetry_version = (
        poetry_version_result.stdout.strip()
        if hasattr(poetry_version_result, "stdout")
        else "Unknown"
    )
    print(f"Using Poetry version: {poetry_version}")

    # Configure Poetry to NOT create flx_project-specific virtual environments
    run_command(
        [poetry_cmd, "config", "virtualenvs.in-flx_project", "false"],
        check=False,
    )

    # Set the path to the root .venv directory (without trailing slash to
    # avoid ~.venv error)
    absolute_venv_path = str(VENV_DIR.resolve())
    run_command(
        [poetry_cmd, "config", "virtualenvs.path", absolute_venv_path],
        check=False,
    )

    # Try to set create to false to avoid creating new environments
    try:
        run_command([poetry_cmd, "config", "virtualenvs.create", "false"], check=False)
    except Exception as e:
        print(colorize(f"Note: Could not set virtualenvs.create: {e}", "YELLOW"))

    # Try to set prefer-active-python (only in newer Poetry versions)
    try:
        # Check if this setting exists first
        test_result = run_command(
            [poetry_cmd, "config", "--list"],
            capture_output=True,
            check=False,
        )
        if (
            hasattr(test_result, "stdout")
            and "virtualenvs.prefer-active-python" in test_result.stdout
        ):
            run_command(
                [
                    poetry_cmd,
                    "config",
                    "virtualenvs.prefer-active-python",
                    "true",
                ],
                check=False,
            )
    except Exception as e:
        print(
            colorize(
                f"Note: Could not set virtualenvs.prefer-active-python: {e}",
                "YELLOW",
            ),
        )
        print(
            colorize(
                "This is expected in older Poetry versions and can be ignored",
                "YELLOW",
            ),
        )

    print(
        colorize(
            "Poetry configured to use single workspace virtual environment",
            "GREEN",
        ),
    )


def update_lock_file() -> None:
    """Update Poetry lock file if needed."""
    print("Checking if lock file needs updating...")

    # Use Poetry from the virtualenv if available
    poetry_path = VENV_DIR / "bin" / "poetry"
    poetry_cmd = str(poetry_path) if poetry_path.exists() else "poetry"

    poetry_lock = WORKSPACE_ROOT / "poetry.lock"
    pyproject_toml = WORKSPACE_ROOT / "pyproject.toml"

    if not poetry_lock.exists() or os.path.getmtime(poetry_lock) < os.path.getmtime(
        pyproject_toml,
    ):
        try:
            # Try to get Poetry version
            result = run_command([poetry_cmd, "--version"], capture_output=True)
            poetry_version = result.stdout.strip()
            print(f"Using {poetry_version}")

            # Use plain 'lock' command without flags (works in all versions)
            run_command([poetry_cmd, "lock"], cwd=WORKSPACE_ROOT)
            print("Lock file updated")
        except Exception as e:
            print(colorize(f"Error updating lock file: {e}", "RED"))
            print(colorize("Continuing without lock file update", "YELLOW"))

    LOCK_UPDATED_CHECK.touch()


def install_dependencies(dev: bool = False) -> None:
    """Install Poetry dependencies."""
    ensure_venv()
    update_lock_file()

    print("Installing dependencies...")

    # Use Poetry from the virtualenv if available
    poetry_path = VENV_DIR / "bin" / "poetry"
    poetry_cmd = str(poetry_path) if poetry_path.exists() else "poetry"

    try:
        if dev:
            run_command(
                [poetry_cmd, "install", "--with", "dev", "--no-root"],
                cwd=WORKSPACE_ROOT,
            )
            run_command(
                [poetry_cmd, "install", "--only", "main", "--no-root"],
                cwd=WORKSPACE_ROOT,
            )
    except subprocess.CalledProcessError as e:
        print(colorize(f"Error with standard install: {e}", "YELLOW"))
        print("Trying alternative install method...")
        try:
            # Some Poetry versions might not support --no-root or have
            # different flags
            if dev:
                run_command(
                    [poetry_cmd, "install", "--dev"],
                    cwd=WORKSPACE_ROOT,
                    check=False,
                )
                run_command(
                    [poetry_cmd, "install", "--no-dev"],
                    cwd=WORKSPACE_ROOT,
                    check=False,
                )
        except Exception as e2:
            print(colorize(f"Alternative install failed: {e2}", "RED"))
            print(colorize("Please check your Poetry version and configuration", "RED"))
            return

    POETRY_INSTALL_CHECK.touch()
    print(colorize("Dependencies installed", "GREEN"))


def install_project_deps(projects: list[str], dev: bool = False) -> None:
    """Install dependencies for specified projects."""
    # Use Poetry from the virtualenv if available
    poetry_path = VENV_DIR / "bin" / "poetry"
    poetry_cmd = str(poetry_path) if poetry_path.exists() else "poetry"

    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project

        if not project_path.exists():
            print(
                colorize(
                    f"⚠ Directory {flx_project} does not exist, skipping",
                    "YELLOW",
                ),
            )
            continue

        print(
            f"Installing {'all' if dev else 'main'} dependencies for {flx_project}...",
        )

        try:
            # Try modern Poetry syntax first with --no-root
            dev_flag = "--with" if dev else "--only"
            group = "dev" if dev else "main"

            run_command(
                [
                    poetry_cmd,
                    "install",
                    f"{dev_flag}",
                    f"{group}",
                    "--no-root",
                ],
                cwd=project_path,
                check=False,
            )
            print(colorize(f"✓ {flx_project} installation complete", "GREEN"))
        except Exception as e:
            print(
                colorize(f"Error with modern syntax for {flx_project}: {e}", "YELLOW"),
            )
            try:
                # Try alternative syntax for older Poetry versions
                if dev:
                    run_command(
                        [poetry_cmd, "install", "--dev"],
                        cwd=project_path,
                        check=False,
                    )
                    run_command(
                        [poetry_cmd, "install", "--no-dev"],
                        cwd=project_path,
                        check=False,
                    )
                print(colorize(f"✓ {flx_project} installation complete", "GREEN"))
            except Exception as e2:
                print(colorize(f"Error installing {flx_project}: {e2}", "RED"))


def run_tests(projects: list[str]) -> None:
    """Run tests for specified projects."""
    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project

        if not project_path.exists():
            print(
                colorize(
                    f"⚠ Directory {flx_project} does not exist, skipping",
                    "YELLOW",
                ),
            )
            continue

        print(f"Testing {flx_project}...")

        try:
            run_command(["poetry", "run", "pytest"], cwd=project_path, check=False)
            print(colorize(f"✓ {flx_project} tests complete", "GREEN"))
        except Exception as e:
            print(colorize(f"Error testing {flx_project}: {e}", "RED"))


def run_linting(projects: list[str]) -> None:
    """Run linting for specified projects."""
    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project

        if not project_path.exists():
            print(
                colorize(
                    f"⚠ Directory {flx_project} does not exist, skipping",
                    "YELLOW",
                ),
            )
            continue

        print(f"Linting {flx_project}...")

        try:
            run_command(["make", "lint"], cwd=project_path, check=False)
            print(colorize(f"✓ {flx_project} linting complete", "GREEN"))
        except Exception as e:
            print(colorize(f"Error linting {flx_project}: {e}", "RED"))


def run_formatting(projects: list[str]) -> None:
    """Format code for specified projects."""
    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project

        if not project_path.exists():
            print(
                colorize(
                    f"⚠ Directory {flx_project} does not exist, skipping",
                    "YELLOW",
                ),
            )
            continue

        print(f"Formatting {flx_project}...")

        try:
            run_command(["make", "format"], cwd=project_path, check=False)
            print(colorize(f"✓ {flx_project} formatting complete", "GREEN"))
        except Exception as e:
            print(colorize(f"Error formatting {flx_project}: {e}", "RED"))


def update_python_constraints(projects: list[str]) -> None:
    """Update Python version constraints in all pyproject.toml files."""
    print("Updating Python version constraints in all projects...")

    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project
        pyproject_path = project_path / "pyproject.toml"

        if not project_path.exists():
            print(
                colorize(
                    f"⚠ Directory {flx_project} does not exist, skipping",
                    "YELLOW",
                ),
            )
            continue

        if not pyproject_path.exists():
            print(colorize(f"⚠ No pyproject.toml in {flx_project}, skipping", "YELLOW"))
            continue

        print(f"Updating Python constraints in {flx_project}...")

        # Read the file
        with open(pyproject_path, encoding="utf-8") as f:
            content = f.read()

        # Replace Python version constraint
        import re

        content = re.sub(
            r'python = "[^"]*"',
            f'python = "{PYTHON_CONSTRAINT}"',
            content,
        )

        # Write the file
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(colorize(f"✓ Updated {flx_project}/pyproject.toml", "GREEN"))


def standardize_linting(projects: list[str]) -> None:
    """Standardize linting and formatting settings."""
    print("Standardizing linting and formatting settings in all projects...")

    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project
        pyproject_path = project_path / "pyproject.toml"

        if not project_path.exists():
            print(
                colorize(
                    f"⚠ Directory {flx_project} does not exist, skipping",
                    "YELLOW",
                ),
            )
            continue

        if not pyproject_path.exists():
            print(colorize(f"⚠ No pyproject.toml in {flx_project}, skipping", "YELLOW"))
            continue

        print(f"Standardizing linting in {flx_project}...")

        # Read the file
        with open(pyproject_path, encoding="utf-8") as f:
            content = f.read()

        # Update line length
        import re

        content = re.sub(
            r"line-length = [0-9]*",
            f"line-length = {LINE_LENGTH}",
            content,
        )

        # Update target version
        content = content.replace(
            r"target-version = \[(.*)\]",
            f'target-version = ["{PY_TARGET_VERSION}"]',
        )

        # Update mypy python version
        content = re.sub(
            r'python_version = "[0-9.]*"',
            f'python_version = "{MYPY_PY_VERSION}"',
            content,
        )

        # Write the file
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(colorize(f"✓ Updated {flx_project}/pyproject.toml", "GREEN"))


def standardize_makefiles(projects: list[str]) -> None:
    """Standardize Makefiles across projects."""
    print("Standardizing Makefiles across all projects...")

    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project
        makefile_path = project_path / "Makefile"

        if not project_path.exists():
            print(
                colorize(
                    f"⚠ Directory {flx_project} does not exist, skipping",
                    "YELLOW",
                ),
            )
            continue

        if not makefile_path.exists():
            print(colorize(f"⚠ No Makefile in {flx_project}, skipping", "YELLOW"))
            continue

        print(f"Standardizing Makefile for {flx_project}...")

        # Read the file
        with open(makefile_path, encoding="utf-8") as f:
            content = f.read()

        # Update Python version
        content = content.replace(
            r"PYTHON := python3\.[0-9]*",
            f"PYTHON := python{PYTHON_VERSION}",
        )

        # Write the file
        with open(makefile_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(colorize(f"✓ Updated {flx_project}/Makefile", "GREEN"))


def apply_pep8_standards(projects: list[str]) -> None:
    """Apply PEP 8 standards to Python code."""
    print("Applying PEP 8 standards to projects...")

    pep8_script = SCRIPTS_DIR / "pep8_apply.py"

    if not pep8_script.exists():
        print(colorize(f"⚠ Script {pep8_script} not found, skipping", "RED"))
        print(
            colorize(
                "This script may have been removed in the reorganization.",
                "YELLOW",
            ),
        )
        print(
            colorize(
                "PEP 8 formatting is now handled by the 'format' command.",
                "YELLOW",
            ),
        )
        return

    project_paths = [str(WORKSPACE_ROOT / flx_project) for flx_project in projects]

    run_command(
        [str(VENV_DIR / "bin" / "python"), str(pep8_script), *project_paths],
        check=False,
    )


def check_pep8_standards(projects: list[str]) -> None:
    """Check PEP 8 standards in Python code."""
    print("Checking PEP 8 standards for projects...")

    pep8_check_script = SCRIPTS_DIR / "pep8_check.py"

    if not pep8_check_script.exists():
        print(colorize(f"⚠ Script {pep8_check_script} not found, skipping", "RED"))
        print(
            colorize(
                "This script may have been removed in the reorganization.",
                "YELLOW",
            ),
        )
        print(
            colorize(
                "PEP 8 checking is now handled by the 'lint' command.",
                "YELLOW",
            ),
        )
        return

    project_paths = [str(WORKSPACE_ROOT / flx_project) for flx_project in projects]

    run_command(
        [str(VENV_DIR / "bin" / "python"), str(pep8_check_script), *project_paths],
        check=False,
    )


def setup_precommit_hooks() -> None:
    """Set up pre-commit hooks."""
    print("Setting up pre-commit hooks...")

    run_command(
        [str(VENV_DIR / "bin" / "python"), "-m", "pre_commit", "install"],
        cwd=WORKSPACE_ROOT,
    )

    print(colorize("Pre-commit hooks installed!", "GREEN"))


def clean_project(projects: list[str]) -> None:
    """Clean build files from projects."""
    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project

        if not project_path.exists():
            print(
                colorize(
                    f"⚠ Directory {flx_project} does not exist, skipping",
                    "YELLOW",
                ),
            )
            continue

        print(f"Cleaning {flx_project}...")

        try:
            run_command(["make", "clean"], cwd=project_path, check=False)
            print(colorize(f"✓ {flx_project} cleaned", "GREEN"))
        except Exception as e:
            print(colorize(f"Error cleaning {flx_project}: {e}", "RED"))


def clean_venv() -> None:
    """Remove virtual environment."""
    print("Removing workspace virtual environment...")

    if VENV_DIR.exists():
        shutil.rmtree(VENV_DIR)

    for check_file in [VENV_CHECK, POETRY_INSTALL_CHECK, LOCK_UPDATED_CHECK]:
        if check_file.exists():
            check_file.unlink()

    print(colorize("Virtual environment removed!", "GREEN"))


def remove_project_venvs(projects: list[str]) -> None:
    """Remove flx_project-specific virtual environments to use the centralized one."""
    print("Removing flx_project-specific virtual environments...")

    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project
        project_venv = project_path / ".venv"

        if not project_path.exists():
            print(
                colorize(
                    f"⚠ Directory {flx_project} does not exist, skipping",
                    "YELLOW",
                ),
            )
            continue

        if project_venv.exists():
            print(f"Removing virtual environment from {flx_project}...")
            try:
                shutil.rmtree(project_venv)
                print(colorize(f"✓ {flx_project} virtual environment removed", "GREEN"))
            except Exception as e:
                print(colorize(f"Error removing venv in {flx_project}: {e}", "RED"))
            print(colorize(f"✓ No flx_project-specific venv in {flx_project}", "GREEN"))


def remove_lock_files(projects: list[str]) -> None:
    """Remove poetry.lock files from projects."""
    print("Removing poetry.lock files from all projects...")

    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project
        lock_file = project_path / "poetry.lock"

        if not project_path.exists():
            print(
                colorize(
                    f"⚠ Directory {flx_project} does not exist, skipping",
                    "YELLOW",
                ),
            )
            continue

        if lock_file.exists():
            print(f"Removing lock file from {flx_project}...")
            lock_file.unlink()
            print(colorize(f"✓ {flx_project} lock removed", "GREEN"))
            print(colorize(f"✓ No lock file in {flx_project}", "YELLOW"))


def upgrade_dependencies(projects: list[str]) -> None:
    """Upgrade all dependencies to latest versions."""
    remove_lock_files(projects)

    print("Upgrading dependencies to latest versions for all projects...")

    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project

        if not project_path.exists():
            print(
                colorize(
                    f"⚠ Directory {flx_project} does not exist, skipping",
                    "YELLOW",
                ),
            )
            continue

        print(f"Upgrading dependencies in {flx_project}...")

        try:
            run_command(["poetry", "update", "--lock"], cwd=project_path, check=False)
            print(colorize(f"✓ {flx_project} dependencies upgraded", "GREEN"))
        except Exception as e:
            print(colorize(f"Error upgrading {flx_project}: {e}", "RED"))


def build_project(projects: list[str]) -> None:
    """Build projects."""
    print("Building projects...")

    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project

        if not project_path.exists():
            print(
                colorize(
                    f"⚠ Directory {flx_project} does not exist, skipping",
                    "YELLOW",
                ),
            )
            continue

        print(f"Building {flx_project}...")

        try:
            if (project_path / "Makefile").exists():
                # Check if the Makefile has a build target
                try:
                    # Use make -n to do a dry run and see if the build target
                    # exists
                    result = run_command(
                        ["make", "-n", "build"],
                        cwd=project_path,
                        capture_output=True,
                        check=False,
                    )
                    stderr_output = (
                        result.stderr.decode("utf-8", errors="ignore")
                        if isinstance(result.stderr, bytes)
                        else result.stderr
                    )
                    if (
                        result.returncode != 0
                        and "No rule to make target" in stderr_output
                    ):
                        print(
                            colorize(
                                f"⚠ No build target in Makefile for {flx_project}, trying Poetry",
                                "YELLOW",
                            ),
                        )
                        if (project_path / "pyproject.toml").exists():
                            # Explicitly use the root virtualenv
                            env = os.environ.copy()
                            env["VIRTUAL_ENV"] = str(VENV_DIR.resolve())
                            run_command(
                                ["poetry", "build", "--no-interaction"],
                                cwd=project_path,
                                check=False,
                                env=env,
                            )
                            print(
                                colorize(
                                    f"⚠ No pyproject.toml found in {flx_project}, skipping",
                                    "YELLOW",
                                ),
                            )
                            continue
                        run_command(["make", "build"], cwd=project_path, check=False)
                except Exception as e:
                    print(
                        colorize(
                            f"⚠ Error checking build target in {flx_project}: {e}",
                            "YELLOW",
                        ),
                    )
                    if (project_path / "pyproject.toml").exists():
                        # Explicitly use the root virtualenv
                        env = os.environ.copy()
                        env["VIRTUAL_ENV"] = str(VENV_DIR.resolve())
                        run_command(
                            ["poetry", "build", "--no-interaction"],
                            cwd=project_path,
                            check=False,
                            env=env,
                        )
                        continue
            elif (project_path / "pyproject.toml").exists():
                # Explicitly use the root virtualenv
                env = os.environ.copy()
                env["VIRTUAL_ENV"] = str(VENV_DIR.resolve())
                run_command(
                    ["poetry", "build", "--no-interaction"],
                    cwd=project_path,
                    check=False,
                    env=env,
                )
                print(
                    colorize(
                        f"⚠ No build configuration found in {flx_project}, skipping",
                        "YELLOW",
                    ),
                )
                continue

            print(colorize(f"✓ {flx_project} built", "GREEN"))
        except Exception as e:
            print(colorize(f"Error building {flx_project}: {e}", "RED"))


def show_project_status(projects: list[str]) -> None:
    """Show status overview of all projects."""
    print(colorize("======================================", "YELLOW"))
    print(colorize("        PROJECT STATUS OVERVIEW        ", "YELLOW"))
    print(colorize("======================================", "YELLOW"))
    print(f"Python version: {PYTHON_VERSION}")
    print()

    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project

        if not project_path.exists():
            print(colorize(f"{flx_project}: Directory not found", "RED"))
            print()
            continue

        print(colorize(f"{flx_project}:", "YELLOW"))

        # Check pyproject.toml
        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists():
            # Extract Python constraint
            with open(pyproject_path, encoding="utf-8") as f:
                content = f.read()
                import re

                python_ver = re.search(r'python = "([^"]*)"', content)
                if python_ver:
                    print(f"  Python constraint: {python_ver.group(1)}")
                    print("  Python constraint: Not found")
            print(colorize("  No pyproject.toml found", "RED"))

        # Check if using centralized virtual environment
        if (project_path / ".venv").exists():
            print(colorize("  Project-specific venv: Found (will be unused)", "YELLOW"))
            print(colorize("  Using centralized venv", "GREEN"))

        # Check lock file
        if (project_path / "poetry.lock").exists():
            print(colorize("  Lock file: Found", "GREEN"))
            print(colorize("  Lock file: Missing", "YELLOW"))

        print()

    print(colorize("======================================", "YELLOW"))


def rebuild_venv() -> None:
    """Recreate virtual environment from scratch."""
    print("Rebuilding virtual environment from scratch...")

    # Remove existing virtualenv
    if VENV_DIR.exists():
        print("Removing existing virtual environment...")
        shutil.rmtree(VENV_DIR)

    # Remove marker files
    for check_file in [VENV_CHECK, POETRY_INSTALL_CHECK, LOCK_UPDATED_CHECK]:
        if check_file.exists():
            check_file.unlink()

    # Find Python interpreter
    py_version = PYTHON_VERSION
    try:
        # Try to find the system Python with the required version
        which_result = run_command(
            ["which", f"python{py_version}"],
            capture_output=True,
        )
        python_path = which_result.stdout.strip()
        print(f"Using Python interpreter: {python_path}")
    except Exception:
        # Fallback to the generic command
        python_path = f"python{py_version}"
        print(f"Using default Python command: {python_path}")

    # Create new virtualenv
    print(f"Creating fresh virtual environment in {VENV_DIR}...")
    run_command([python_path, "-m", "venv", str(VENV_DIR)])

    # Install core packages
    str(VENV_DIR / "bin" / "python")
    pip_venv = str(VENV_DIR / "bin" / "pip")

    # Check if virtualenv is working
    try:
        # Upgrade pip
        run_command([pip_venv, "install", "--upgrade", "pip"])

        # Install Poetry inside virtualenv
        print("Installing Poetry inside virtualenv...")
        run_command([pip_venv, "install", "poetry"])
    except Exception as e:
        print(colorize(f"Error setting up virtual environment: {e}", "RED"))
        print(colorize("Virtual environment may not be properly set up", "RED"))
        return

    # Mark venv as complete
    VENV_CHECK.touch()
    print(colorize("Virtual environment has been rebuilt", "GREEN"))


def main() -> None:  # noqa: PLR0912, PLR0915
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Project management utilities")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Setup commands
    setup_parser = subparsers.add_parser("setup", help="Set up environment")
    setup_parser.add_argument(
        "--projects",
        nargs="+",
        default=DEFAULT_PROJECTS,
        help="Projects to set up",
    )

    # Fix virtualenv command
    subparsers.add_parser("fix-venv", help="Rebuild virtual environment from scratch")

    # Install commands
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.add_argument(
        "--dev",
        action="store_true",
        help="Install development dependencies",
    )
    install_parser.add_argument(
        "--projects",
        nargs="+",
        default=DEFAULT_PROJECTS,
        help="Projects to install",
    )

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument(
        "--projects",
        nargs="+",
        default=DEFAULT_PROJECTS,
        help="Projects to test",
    )

    # Build command
    build_parser = subparsers.add_parser("build", help="Build projects")
    build_parser.add_argument(
        "--projects",
        nargs="+",
        default=DEFAULT_PROJECTS,
        help="Projects to build",
    )

    # Lint command
    lint_parser = subparsers.add_parser("lint", help="Run linting")
    lint_parser.add_argument(
        "--projects",
        nargs="+",
        default=DEFAULT_PROJECTS,
        help="Projects to lint",
    )

    # Format command
    format_parser = subparsers.add_parser("format", help="Format code")
    format_parser.add_argument(
        "--projects",
        nargs="+",
        default=DEFAULT_PROJECTS,
        help="Projects to format",
    )

    # Clean commands
    clean_parser = subparsers.add_parser("clean", help="Clean build files")
    clean_parser.add_argument(
        "--venv",
        action="store_true",
        help="Also clean virtual environment",
    )
    clean_parser.add_argument(
        "--flx_project-venvs",
        action="store_true",
        help="Remove flx_project-specific virtual environments",
    )
    clean_parser.add_argument(
        "--projects",
        nargs="+",
        default=DEFAULT_PROJECTS,
        help="Projects to clean",
    )

    # Standardize commands
    std_parser = subparsers.add_parser("standardize", help="Standardize projects")
    std_parser.add_argument(
        "--python",
        action="store_true",
        help="Update Python constraints",
    )
    std_parser.add_argument(
        "--lint",
        action="store_true",
        help="Standardize linting settings",
    )
    std_parser.add_argument("--make", action="store_true", help="Standardize Makefiles")
    std_parser.add_argument(
        "--all",
        action="store_true",
        help="Apply all standardizations",
    )
    std_parser.add_argument("--pep8", action="store_true", help="Apply PEP 8 standards")
    std_parser.add_argument(
        "--check",
        action="store_true",
        help="Check PEP 8 standards",
    )
    std_parser.add_argument(
        "--hooks",
        action="store_true",
        help="Set up pre-commit hooks",
    )
    std_parser.add_argument(
        "--projects",
        nargs="+",
        default=DEFAULT_PROJECTS,
        help="Projects to standardize",
    )

    # Dependency commands
    deps_parser = subparsers.add_parser("deps", help="Manage dependencies")
    deps_parser.add_argument(
        "--remove-locks",
        action="store_true",
        help="Remove lock files",
    )
    deps_parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Upgrade dependencies",
    )
    deps_parser.add_argument(
        "--projects",
        nargs="+",
        default=DEFAULT_PROJECTS,
        help="Projects to manage",
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Show flx_project status")
    status_parser.add_argument(
        "--projects",
        nargs="+",
        default=DEFAULT_PROJECTS,
        help="Projects to show",
    )

    args = parser.parse_args()

    # Process commands
    if args.command == "setup":
        # Clean up existing flx_project-specific virtual environments
        remove_project_venvs(args.projects)
        ensure_venv()
        configure_poetry()
        install_dependencies(dev=True)
        install_project_deps(args.projects, dev=True)

    elif args.command == "fix-venv":
        rebuild_venv()
        configure_poetry()
        install_dependencies(dev=True)

    elif args.command == "install":
        install_dependencies(dev=args.dev)
        install_project_deps(args.projects, dev=args.dev)

    elif args.command == "test":
        run_tests(args.projects)

    elif args.command == "build":
        build_project(args.projects)

    elif args.command == "lint":
        run_linting(args.projects)

    elif args.command == "format":
        run_formatting(args.projects)

    elif args.command == "clean":
        clean_project(args.projects)
        if args.venv:
            clean_venv()
        if args.project_venvs:
            remove_project_venvs(args.projects)

    elif args.command == "standardize":
        if args.all or args.python:
            update_python_constraints(args.projects)
        if args.all or args.lint:
            standardize_linting(args.projects)
        if args.all or args.make:
            standardize_makefiles(args.projects)
        if args.all or args.pep8:
            apply_pep8_standards(args.projects)
        if args.all or args.check:
            check_pep8_standards(args.projects)
        if args.all or args.hooks:
            setup_precommit_hooks()

    elif args.command == "deps":
        if args.remove_locks:
            remove_lock_files(args.projects)
        if args.upgrade:
            upgrade_dependencies(args.projects)

    elif args.command == "status":
        show_project_status(args.projects)

        parser.print_help()


if __name__ == "__main__":
    main()
