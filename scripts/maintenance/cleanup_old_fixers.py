#!/usr/bin/env python3
"""
Cleanup script to archive old maintenance scripts.

This script identifies obsolete maintenance scripts and moves them to an archive
directory, keeping only the unified maintenance system and essential scripts.
"""

import shutil
from datetime import datetime
from pathlib import Path


def main() -> None:
    """Archive old maintenance scripts."""
    # Scripts to keep
    keep_scripts = {
        "unified_maintenance_system.py",
        "cleanup_old_fixers.py",
        "README.md",
        "emergency_lint_fixer.py",  # Keep for emergencies
    }

    # Directories to process
    dirs_to_clean = [
        Path("scripts/maintenance"),
        Path("scripts/maintenance/fixes"),
        Path("scripts/utilities"),
        Path("scripts/obsolete"),
    ]

    # Create archive directory
    archive_dir = Path("archive/maintenance_scripts")
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Archive timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    moved_count = 0

    for dir_path in dirs_to_clean:
        if not dir_path.exists():
            continue

        # Find fix/lint scripts
        patterns = ["fix_*.py", "lint_*.py", "*_fixer*.py", "*_fix.py"]

        for pattern in patterns:
            for script in dir_path.glob(pattern):
                # Skip if in keep list
                if script.name in keep_scripts:
                    continue

                # Create archive path
                relative_path = script.relative_to(Path("."))
                archive_path = archive_dir / timestamp / relative_path
                archive_path.parent.mkdir(parents=True, exist_ok=True)

                # Move file
                print(f"Archiving: {script} -> {archive_path}")
                shutil.move(str(script), str(archive_path))
                moved_count += 1

    print(
        f"\nArchived {moved_count} obsolete scripts to {
            archive_dir /
            timestamp}")
    print("\nRemaining maintenance structure:")
    print("- scripts/maintenance/unified_maintenance_system.py (main system)")
    print("- scripts/maintenance/emergency_lint_fixer.py (emergency use)")
    print("- scripts/maintenance/README.md (documentation)")
    print("- config/maintenance*.yaml (configuration files)")


if __name__ == "__main__":
    main()
