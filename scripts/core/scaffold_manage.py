#!/usr/bin/env python3
"""Scaffold Management Script.

Manages flx_project templates and scaffolds for the pyauto workspace.

This script handles:
1. Updating scaffold templates from existing projects
2. Syncing projects with latest scaffold
3. Propagating scaffold changes to all projects
4. Creating new projects from scaffolds
5. Scaffold status reporting

Usage:
    python scaffold_manage.py [command] [options]
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Absolute paths
WORKSPACE_ROOT = Path("/home/marlonsc/pyauto")
SCAFFOLD_DIR = WORKSPACE_ROOT / "scaffold"
PYTHON_TEMPLATE_DIR = SCAFFOLD_DIR / "python-flx_project"

# Tracking directory for scaffold updates
SCAFFOLD_TRACKING_DIR = WORKSPACE_ROOT / ".scaffold-tracking"
PYTHON_TRACKING_FILE = SCAFFOLD_TRACKING_DIR / "python-template.json"

# Important files to sync across projects
IMPORTANT_FILES = [
    "pyproject.toml",
    "Makefile",
    "README.md",
    ".gitignore",
    ".pre-commit-config.yaml",
]

# Source files in flx_project structure
PYTHON_SRC_FILES = ["src/__init__.py", "src/module.py"]

# Test files in flx_project structure
PYTHON_TEST_FILES = ["tests/__init__.py", "tests/test_module.py"]

# Projects to be managed
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


def ensure_tracking_dir() -> None:
    """Ensure scaffold tracking directory exists."""
    if not SCAFFOLD_TRACKING_DIR.exists():
        SCAFFOLD_TRACKING_DIR.mkdir(parents=True)
        print(f"Created tracking directory: {SCAFFOLD_TRACKING_DIR}")


def initialize_tracking_file() -> None:
    """Initialize tracking file if it doesn't exist."""
    ensure_tracking_dir()

    if not PYTHON_TRACKING_FILE.exists():
        tracking_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "source_project": "initial",
            "files": {},
        }

        with open(PYTHON_TRACKING_FILE, "w", encoding="utf-8") as f:
            json.dump(tracking_data, f, indent=2)

        print(f"Initialized tracking file: {PYTHON_TRACKING_FILE}")


def update_python_scaffold(source_project: str) -> None:
    """Update Python scaffold template from a flx_project."""
    initialize_tracking_file()

    source_path = WORKSPACE_ROOT / source_project

    if not source_path.exists() or not source_path.is_dir():
        print(colorize(f"Error: Project {source_project} does not exist!", "RED"))
        sys.exit(1)

    print(colorize(f"Updating Python scaffold from {source_project}...", "YELLOW"))

    # Create template directory if it doesn't exist
    if not PYTHON_TEMPLATE_DIR.exists():
        PYTHON_TEMPLATE_DIR.mkdir(parents=True)

    # Copy important files
    updated_files = {}
    for file in IMPORTANT_FILES:
        source_file = source_path / file
        target_file = PYTHON_TEMPLATE_DIR / file

        if source_file.exists():
            print(f"Copying {file}...")
            shutil.copy2(source_file, target_file)
            updated_files[file] = True

    # Copy source files
    for file in PYTHON_SRC_FILES:
        source_file = source_path / file
        target_file = PYTHON_TEMPLATE_DIR / file

        if source_file.exists():
            print(f"Copying {file}...")
            # Ensure parent directory exists
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
            updated_files[file] = True

    # Copy test files
    for file in PYTHON_TEST_FILES:
        source_file = source_path / file
        target_file = PYTHON_TEMPLATE_DIR / file

        if source_file.exists():
            print(f"Copying {file}...")
            # Ensure parent directory exists
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
            updated_files[file] = True

    # Update pyproject.toml with generic name
    pyproject_path = PYTHON_TEMPLATE_DIR / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path, encoding="utf-8") as f:
            content = f.read()

        # Replace flx_project name with generic placeholder
        content = content.replace(source_project, "project_name")

        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(content)

    # Update tracking file
    tracking_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "source_project": source_project,
        "files": updated_files,
    }

    with open(PYTHON_TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(tracking_data, f, indent=2)

    print(colorize(f"Python scaffold updated from {source_project}!", "GREEN"))


def sync_project_with_scaffold(flx_project: str, direction: str) -> None:
    """Sync a flx_project with the Python scaffold template."""
    initialize_tracking_file()

    project_path = WORKSPACE_ROOT / flx_project

    if not project_path.exists() or not project_path.is_dir():
        print(colorize(f"Error: Project {flx_project} does not exist!", "RED"))
        sys.exit(1)

    print(colorize(f"Syncing {flx_project} with Python scaffold...", "YELLOW"))

    # Scaffold to flx_project
    if direction in {"s", "b"}:
        print("Applying scaffold to flx_project...")

        for file in IMPORTANT_FILES:
            source_file = PYTHON_TEMPLATE_DIR / file
            target_file = project_path / file

            if source_file.exists() and target_file.exists():
                print(f"  Updating {file}...")

                # Read the file
                with open(source_file, encoding="utf-8") as f:
                    content = f.read()

                # Replace placeholder with flx_project name
                content = content.replace("project_name", flx_project)

                # Write to target
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(content)

    # Project to scaffold
    if direction in {"p", "b"}:
        print("Updating scaffold from flx_project...")

        updated_files = {}
        for file in IMPORTANT_FILES:
            source_file = project_path / file
            target_file = PYTHON_TEMPLATE_DIR / file

            if source_file.exists():
                print(f"  Updating scaffold {file}...")

                # Read the file
                with open(source_file, encoding="utf-8") as f:
                    content = f.read()

                # Replace flx_project name with placeholder
                content = content.replace(flx_project, "project_name")

                # Write to target
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(content)

                updated_files[file] = True

        # Update tracking file
        tracking_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "source_project": flx_project,
            "files": updated_files,
        }

        with open(PYTHON_TRACKING_FILE, "w", encoding="utf-8") as f:
            json.dump(tracking_data, f, indent=2)

    print(colorize("Sync completed!", "GREEN"))


def propagate_scaffold(projects: list[str], confirm: bool = False) -> None:
    """Apply Python scaffold to all specified projects."""
    initialize_tracking_file()

    if not confirm:
        print(
            colorize(
                "Propagating Python scaffold to projects requires confirmation.",
                "YELLOW",
            ),
        )
        print("Run with --confirm to update all projects with the current scaffold.")
        return

    print(colorize("Propagating Python scaffold to all projects...", "YELLOW"))

    for flx_project in projects:
        project_path = WORKSPACE_ROOT / flx_project

        if not project_path.exists():
            print(colorize(f"⚠ Directory {flx_project} does not exist, skipping", "YELLOW"))
            continue

        if not (project_path / "pyproject.toml").exists():
            print(colorize("⚠ Not a Python flx_project, skipping", "YELLOW"))
            continue

        print(f"Updating {flx_project}...")

        for file in IMPORTANT_FILES:
            source_file = PYTHON_TEMPLATE_DIR / file
            target_file = project_path / file

            if source_file.exists() and target_file.exists():
                print(f"  Updating {file}...")

                # Read the file
                with open(source_file, encoding="utf-8") as f:
                    content = f.read()

                # Replace placeholder with flx_project name
                content = content.replace("project_name", flx_project)

                # Write to target
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(content)

        print(colorize(f"✓ {flx_project} updated", "GREEN"))

    print(colorize("All projects updated with the latest Python scaffold!", "GREEN"))


def show_scaffold_status() -> None:
    """Show status of scaffold templates."""
    initialize_tracking_file()

    print(colorize("=========================================", "YELLOW"))
    print(colorize("         SCAFFOLD STATUS REPORT          ", "YELLOW"))
    print(colorize("=========================================", "YELLOW"))
    print("Python scaffold:")

    # Read tracking data
    try:
        with open(PYTHON_TRACKING_FILE, encoding="utf-8") as f:
            tracking_data = json.load(f)

        last_updated = tracking_data.get("last_updated", "Unknown")
        source_project = tracking_data.get("source_project", "Unknown")

        print(f"  Last updated: {last_updated}")
        print(f"  Source flx_project: {source_project}")
        print("  Template files:")

        for file in IMPORTANT_FILES:
            template_file = PYTHON_TEMPLATE_DIR / file
            if template_file.exists():
                print(f"    {colorize('✓', 'GREEN')} {file}")
            else:
                print(f"    {colorize('✗', 'RED')} {file} (missing)")

        # Source and test files
        for file in PYTHON_SRC_FILES + PYTHON_TEST_FILES:
            template_file = PYTHON_TEMPLATE_DIR / file
            if template_file.exists():
                print(f"    {colorize('✓', 'GREEN')} {file}")
            else:
                print(f"    {colorize('✗', 'RED')} {file} (missing)")

    except (FileNotFoundError, json.JSONDecodeError):
        print(f"  {colorize('No tracking information available', 'RED')}")

    print(colorize("=========================================", "YELLOW"))


def create_new_project(project_name: str) -> None:
    """Create a new flx_project from Python scaffold template."""
    initialize_tracking_file()

    project_path = WORKSPACE_ROOT / project_name

    if project_path.exists():
        print(colorize(f"Error: Project {project_name} already exists!", "RED"))
        sys.exit(1)

    if not PYTHON_TEMPLATE_DIR.exists():
        print(
            colorize(
                f"Error: Scaffold template {PYTHON_TEMPLATE_DIR} does not exist!",
                "RED",
            ),
        )
        sys.exit(1)

    print(colorize(f"Creating new flx_project: {project_name}", "YELLOW"))

    # Copy template directory
    shutil.copytree(PYTHON_TEMPLATE_DIR, project_path)

    # Update flx_project name in files
    for root, _, files in os.walk(project_path):
        for file in files:
            file_path = Path(root) / file

            # Skip binary files
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Replace placeholder with flx_project name
                if "project_name" in content:
                    content = content.replace("project_name", project_name)

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
            except UnicodeDecodeError:
                # Skip binary files
                pass

    print(colorize(f"Project {project_name} created successfully!", "GREEN"))


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Scaffold management utilities")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Update scaffold command
    update_parser = subparsers.add_parser(
        "update",
        help="Update scaffold from a flx_project",
    )
    update_parser.add_argument("source", help="Source flx_project name")

    # Sync flx_project command
    sync_parser = subparsers.add_parser("sync", help="Sync a flx_project with scaffold")
    sync_parser.add_argument("flx_project", help="Project name to sync")
    sync_parser.add_argument(
        "--direction",
        choices=["s", "p", "b"],
        default="b",
        help="Direction: scaffold->flx_project (s), flx_project->scaffold (p), bidirectional (b)",
    )

    # Propagate scaffold command
    propagate_parser = subparsers.add_parser(
        "propagate",
        help="Apply scaffold to all projects",
    )
    propagate_parser.add_argument(
        "--projects",
        nargs="+",
        default=DEFAULT_PROJECTS,
        help="Projects to update",
    )
    propagate_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm propagation",
    )

    # Status command
    subparsers.add_parser("status", help="Show scaffold status")

    # Create flx_project command
    create_parser = subparsers.add_parser(
        "create",
        help="Create a new flx_project from scaffold",
    )
    create_parser.add_argument("name", help="New flx_project name")

    args = parser.parse_args()

    # Process commands
    if args.command == "update":
        update_python_scaffold(args.source)

    elif args.command == "sync":
        sync_project_with_scaffold(args.flx_project, args.direction)

    elif args.command == "propagate":
        propagate_scaffold(args.projects, args.confirm)

    elif args.command == "status":
        show_scaffold_status()

    elif args.command == "create":
        create_new_project(args.name)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
