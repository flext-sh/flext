#!/usr/bin/env python3
"""Update VSCode settings to exclude files not tracked by git.

This script dynamically generates VSCode exclusion patterns based on:
1. Files currently tracked by git
2. Standard exclusions from .gitignore patterns

Usage:
    python scripts/update_vscode_git_exclusions.py

This will update .vscode/settings.json with appropriate exclusions.
"""

import json
import subprocess
import sys
from pathlib import Path


def get_git_tracked_files() -> set[str]:
    """Get all files currently tracked by git."""
    try:
        result = subprocess.run(
            ["/usr/bin/env", "git", "ls-files"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent
        )
        return set(result.stdout.strip().split('\n'))
    except subprocess.CalledProcessError as e:
        print(f"Error getting git tracked files: {e}", file=sys.stderr)
        return set()


def get_git_untracked_files() -> set[str]:
    """Get all files not tracked by git (including untracked and ignored)."""
    try:
        # Use git ls-files --others to get untracked files
        result = subprocess.run(
            ["/usr/bin/env", "git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent
        )
        untracked_files = set(result.stdout.strip().split('\n'))
        untracked_files.discard('')  # Remove empty strings
        return untracked_files
    except subprocess.CalledProcessError as e:
        print(f"Error getting untracked files: {e}", file=sys.stderr)
        # Fallback: return common untracked patterns
        return {
            "*.tmp", "*.temp", "*.bak", "*.backup", "*.swp", "*.swo", "*~",
            ".DS_Store", "Thumbs.db", "*.log", ".env", ".internal.invalid"
        }


def generate_exclusion_patterns(untracked_files: set[str]) -> list[str]:
    """Generate glob patterns for untracked files."""
    patterns = []

    # Add standard exclusions that are commonly not in git
    standard_exclusions = [
        "**/node_modules",
        "**/__pycache__",
        "**/.mypy_cache",
        "**/.ruff_cache",
        "**/.pytest_cache",
        "**/.pylance_cache",
        "**/build",
        "**/dist",
        "**/*.egg-info",
        "**/.venv",
        "**/venv",
        "**/*.pb2.py",
        "**/*.pb2_grpc.py",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/.git",
        "**/.svn",
        "**/.hg",
        "**/CVS",
        "**/.DS_Store",
        "**/Thumbs.db",
        "**/*.tmp",
        "**/*.temp",
        "**/*.bak",
        "**/*.backup",
        "**/*.swp",
        "**/*.swo",
        "**/*~",
        "**/.vscode/test-results",
        "**/.vscode/settings.json.bak",
        "**/*.log",
        "**/logs",
        "**/tmp",
        "**/temp",
        "**/.meltano",
        "**/vectorbt.pro",
        "**/external-docs"
    ]

    patterns.extend(standard_exclusions)

    # Add patterns for untracked files (grouped by directory)
    dirs_with_untracked = set()
    for file_path in untracked_files:
        if file_path:
            path_parts = Path(file_path).parts
            if len(path_parts) > 1:
                # Add directory pattern
                dirs_with_untracked.add(f"**/{path_parts[0]}")
            else:
                # Add file pattern
                patterns.append(f"**/{file_path}")

    # Add unique directory patterns
    patterns.extend(sorted(dirs_with_untracked))

    return sorted(set(patterns))


def update_vscode_settings(exclusion_patterns: list[str]) -> None:
    """Update .vscode/settings.json with exclusion patterns."""
    vscode_dir = Path(__file__).parent.parent / ".vscode"
    settings_file = vscode_dir / "settings.json"

    # Ensure .vscode directory exists
    vscode_dir.mkdir(exist_ok=True)

    # Load existing settings
    if settings_file.exists():
        with Path(settings_file).open('r', encoding='utf-8') as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                print("Warning: Could not parse existing settings.json, creating new one")
                settings = {}
    else:
        settings = {}

    # Update exclusion settings
    settings["python.analysis.exclude"] = exclusion_patterns
    settings["ruff.exclude"] = exclusion_patterns

    # Also update file watching exclusions
    file_watcher_exclude = {}
    for pattern in exclusion_patterns:
        if pattern.startswith("**/"):
            file_watcher_exclude[pattern[3:]] = True
        else:
            file_watcher_exclude[pattern] = True

    settings["files.watcherExclude"] = file_watcher_exclude

    # Write updated settings
    with Path(settings_file).open('w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)

    print(f"Updated {settings_file} with {len(exclusion_patterns)} exclusion patterns")


def main() -> None:
    """Main function."""
    print("🔍 Analyzing git repository for VSCode exclusions...")

    # Get untracked files
    untracked_files = get_git_untracked_files()
    print(f"Found {len(untracked_files)} untracked files")

    # Generate exclusion patterns
    exclusion_patterns = generate_exclusion_patterns(untracked_files)
    print(f"Generated {len(exclusion_patterns)} exclusion patterns")

    # Update VSCode settings
    update_vscode_settings(exclusion_patterns)

    print("✅ VSCode settings updated successfully!")
    print("Restart VSCode to apply the new exclusion settings.")


if __name__ == "__main__":
    main()
