#!/usr/bin/env python3
"""Remove tracked files that are now ignored by .gitignore.

Untrack files from git that should be ignored according to the new aggressive
.gitignore, but keep them locally (uses git rm --cached).

Copyright (c) 2025 client-a Telecom. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

import subprocess
from pathlib import Path

FLEXT_ROOT = Path("/home/marlonsc/flext")


def get_tracked_files(project_dir: Path) -> list[str]:
    """Get list of all tracked files in git.

    Args:
        project_dir: Project directory path

    Returns:
        List of tracked file paths

    """
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return [f.strip() for f in result.stdout.split('\n') if f.strip()]
    except subprocess.CalledProcessError:
        return []


def check_if_ignored(project_dir: Path, file_path: str) -> bool:
    """Check if a file is ignored by .gitignore.

    Args:
        project_dir: Project directory path
        file_path: Relative file path to check

    Returns:
        True if file is ignored, False otherwise

    """
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", file_path],
            cwd=project_dir,
            capture_output=True,
            check=False,
        )
        # Exit code 0 means file is ignored
        return result.returncode == 0
    except Exception:
        return False


def untrack_file(project_dir: Path, file_path: str) -> bool:
    """Untrack a file from git (keep local copy).

    Args:
        project_dir: Project directory path
        file_path: Relative file path to untrack

    Returns:
        True if successful, False otherwise

    """
    try:
        subprocess.run(
            ["git", "rm", "--cached", file_path],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"      ⚠️  Failed to untrack {file_path}: {e.stderr}")
        return False


def clean_project(project_dir: Path, dry_run: bool = True) -> dict[str, list[str]]:
    """Clean tracked files that should be ignored.

    Args:
        project_dir: Project directory path
        dry_run: If True, only report what would be removed

    Returns:
        Dictionary with results

    """
    results = {
        "to_remove": [],
        "removed": [],
        "failed": [],
    }

    # Get all tracked files
    tracked_files = get_tracked_files(project_dir)

    if not tracked_files:
        return results

    # Check which tracked files are now ignored
    for file_path in tracked_files:
        if check_if_ignored(project_dir, file_path):
            results["to_remove"].append(file_path)

    if not results["to_remove"]:
        return results

    # Show what will be removed
    if results["to_remove"]:
        print(f"   📋 Found {len(results['to_remove'])} tracked files now ignored:")
        for file_path in results["to_remove"][:10]:  # Show first 10
            print(f"      • {file_path}")
        if len(results["to_remove"]) > 10:
            print(f"      ... and {len(results['to_remove']) - 10} more")

    if dry_run:
        return results

    # Actually untrack files
    print(f"   🗑️  Untracking files from git...")
    for file_path in results["to_remove"]:
        if untrack_file(project_dir, file_path):
            results["removed"].append(file_path)
        else:
            results["failed"].append(file_path)

    return results


def main() -> None:
    """Clean all FLEXT projects."""
    import sys

    # Check if dry-run or execute
    dry_run = "--execute" not in sys.argv

    print("=" * 80)
    if dry_run:
        print("🔍 DRY RUN: Checking Tracked Files Now Ignored by .gitignore")
    else:
        print("🗑️  EXECUTE: Removing Tracked Files Now Ignored by .gitignore")
    print("=" * 80)
    print("\nStrategy:")
    print("  • Find files tracked in git")
    print("  • Check against new .gitignore")
    print("  • Untrack ignored files (git rm --cached)")
    print("  • Keep local files (only remove from git tracking)")
    if dry_run:
        print("\n⚠️  DRY RUN MODE: No changes will be made")
        print("   Run with --execute to actually untrack files")
    print("\n" + "=" * 80 + "\n")

    # Find all projects with git repos
    projects = []
    for project_dir in sorted(FLEXT_ROOT.iterdir()):
        if not project_dir.is_dir():
            continue

        git_dir = project_dir / ".git"
        pyproject = project_dir / "pyproject.toml"

        if git_dir.exists() and pyproject.exists():
            projects.append(project_dir)

    print(f"Found {len(projects)} FLEXT projects with git repos\n")

    total_to_remove = 0
    total_removed = 0
    total_failed = 0
    projects_with_changes = 0

    for project_dir in projects:
        print(f"🔧 {project_dir.name}")

        results = clean_project(project_dir, dry_run=dry_run)

        if results["to_remove"]:
            projects_with_changes += 1
            total_to_remove += len(results["to_remove"])

            if not dry_run:
                total_removed += len(results["removed"])
                total_failed += len(results["failed"])

                if results["removed"]:
                    print(f"   ✅ Untracked {len(results['removed'])} files")
                if results["failed"]:
                    print(f"   ⚠️  Failed to untrack {len(results['failed'])} files")
        else:
            print(f"   ✨ No tracked files to remove")

    print("\n" + "=" * 80)
    if dry_run:
        print(f"📊 DRY RUN Summary:")
        print(f"   Projects with files to untrack: {projects_with_changes}")
        print(f"   Total files would be untracked: {total_to_remove}")
        print("\n💡 To execute: python {} --execute".format(__file__))
    else:
        print(f"📊 Execution Summary:")
        print(f"   Projects cleaned: {projects_with_changes}")
        print(f"   Files untracked: {total_removed}")
        if total_failed:
            print(f"   Files failed: {total_failed}")
        print("\n✅ Files removed from git tracking (kept locally)")
        print("   Run 'git status' in each project to see changes")
    print("=" * 80)

    print("\n📋 Next Steps:")
    if dry_run:
        print("  1. Review the list above")
        print("  2. Run with --execute to untrack files")
        print("  3. Review with: git status")
    else:
        print("  1. Review: cd <project> && git status")
        print("  2. Commit: git add .gitignore && git commit -m 'chore: untrack ignored files'")
        print("  3. The untracked files are still on disk (not deleted)")


if __name__ == "__main__":
    main()
