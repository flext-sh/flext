#!/usr/bin/env python3
"""Automatic cleanup script for temporary scripts.

This script automatically removes old temporary scripts from temp/ folders
throughout the workspace.
"""

import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add utils path to import validation
sys.path.append(str(Path(__file__).parent.parent / "utils"))
import structlog
from script_validation import find_workspace_root, validate_script_location

# Mandatory location validation
validate_script_location()

logger = structlog.get_logger(__name__)


def find_temp_scripts(workspace_root: Path, max_age_days: int = 30) -> list[Path]:
    """Find temporary scripts that exceed the maximum age.

    Args:
        workspace_root: Workspace root directory
        max_age_days: Maximum age in days

    Returns:
        List[Path]: List of scripts for removal

    """
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    old_scripts = []

    # Search in all temp folders
    temp_dirs = [
        workspace_root / "scripts" / "temp",
        *workspace_root.glob("*/scripts/temp"),
    ]

    for temp_dir in temp_dirs:
        if not temp_dir.exists():
            continue

        logger.info(f"Checking folder: {temp_dir}")

        for script_file in temp_dir.glob("*.py"):
            # Check file age
            file_age = datetime.fromtimestamp(script_file.stat().st_mtime)

            if file_age < cutoff_date:
                old_scripts.append(script_file)

    return old_scripts


def analyze_script_content(script_file: Path) -> dict:
    """Analyze script content to extract metadata.

    Args:
        script_file: Script file path

    Returns:
        dict: Extracted metadata

    """
    try:
        content = script_file.read_text(encoding="utf-8")

        # Search for cleanup date patterns
        cleanup_pattern = r"CLEANUP SCHEDULED:\s*(\d{4}-\d{2}-\d{2})"
        cleanup_match = re.search(cleanup_pattern, content)

        # Search for objective/purpose
        purpose_pattern = r"Purpose:\s*(.+)"
        purpose_match = re.search(purpose_pattern, content)

        return {
            "cleanup_date": cleanup_match.group(1) if cleanup_match else None,
            "purpose": purpose_match.group(1).strip() if purpose_match else None,
            "is_temp_template": "TEMPORARY SCRIPT" in content,
        }
    except Exception as e:
        logger.warning(f"Error analyzing script {script_file}: {e}")
        return {}


def cleanup_temp_scripts(max_age_days: int = 30, dry_run: bool = False) -> None:
    """Remove old temporary scripts.

    Args:
        max_age_days: Maximum age in days to keep scripts
        dry_run: If True, only shows what would be removed

    """
    workspace_root = find_workspace_root()

    logger.info(
        "Starting temporary scripts cleanup",
        max_age_days=max_age_days,
        dry_run=dry_run,
        workspace_root=str(workspace_root),
    )

    old_scripts = find_temp_scripts(workspace_root, max_age_days)

    if not old_scripts:
        logger.info("No old temporary scripts found")
        return

    logger.info(f"Found {len(old_scripts)} scripts for cleanup")

    removed_count = 0
    for script_file in old_scripts:
        try:
            # Analyze content for more informative logs
            metadata = analyze_script_content(script_file)

            file_age = datetime.fromtimestamp(script_file.stat().st_mtime)
            age_days = (datetime.now() - file_age).days

            logger.info(
                "Script found for removal",
                file=str(script_file),
                age_days=age_days,
                purpose=metadata.get("purpose", "Not specified"),
            )

            if not dry_run:
                script_file.unlink()
                logger.info(f"Script removed: {script_file}")
                removed_count += 1
            else:
                logger.info(f"[DRY RUN] Would remove: {script_file}")

        except Exception as e:
            logger.exception(f"Error removing script {script_file}: {e}")

    if dry_run:
        logger.info(f"[DRY RUN] {len(old_scripts)} scripts would be removed")
    else:
        logger.info(f"Cleanup completed: {removed_count} scripts removed")


def main() -> None:
    """Main function with basic CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean old temporary scripts from workspace",
    )
    parser.add_argument(
        "--max-age",
        type=int,
        default=30,
        help="Maximum age in days (default: 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show what would be removed, without removing",
    )

    args = parser.parse_args()

    try:
        cleanup_temp_scripts(max_age_days=args.max_age, dry_run=args.dry_run)
    except Exception as e:
        logger.exception("Error during cleanup", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
