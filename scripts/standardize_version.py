#!/usr/bin/env python3
"""Standardize __version__.py across all FLEXT ecosystem projects.

This script implements the flext-core __version__.py pattern across all 32 FLEXT
projects, ensuring pyproject.toml is the single source of truth for all metadata.

Usage:
    # Dry run (safe - no changes)
    python scripts/standardize_version.py --dry-run

    # Dry run with verbose output
    python scripts/standardize_version.py --dry-run --verbose

    # Apply changes to specific project
    python scripts/standardize_version.py --project flext-ldif

    # Apply to all projects (DANGER!)
    python scripts/standardize_version.py --all --yes-i-am-sure

Copyright (c) 2025 client-a Telecom. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from flext_core import FlextTypes

# FLEXT ecosystem root directory
FLEXT_ROOT: Final[Path] = Path("/home/marlonsc/flext")

# Standard __version__.py template following flext-core pattern
VERSION_TEMPLATE = '''"""Version and package metadata using importlib.metadata.

Single source of truth pattern following flext-core standards.
All metadata comes from pyproject.toml via importlib.metadata.

Copyright (c) 2025 client-a Telecom. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations
from flext_core import FlextBus

from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

from importlib.metadata import metadata

_metadata = metadata("{package_name}")

__version__ = _metadata["Version"]
__version_info__ = tuple(
    int(part) if part.isdigit() else part for part in __version__.split(".")
)
__title__ = _metadata["Name"]
__description__ = _metadata["Summary"]
__author__ = _metadata.get("Author")
__author_email__ = _metadata.get("Author-Email")
__license__ = _metadata.get("License")
__url__ = _metadata.get("Home-Page")

__all__ = [
    "__version__",
    "__version_info__",
    "__title__",
    "__description__",
    "__author__",
    "__author_email__",
    "__license__",
    "__url__",
]
'''


@dataclass
class ProjectInfo:
    """Information about a FLEXT project."""

    name: str
    path: Path
    src_path: Path
    package_name: str
    pyproject_toml: Path
    current_version_file: Path | None
    needs_update: bool
    has_pyproject: bool
    issues: FlextTypes.StringList


class VersionStandardizer:
    """Standardize __version__.py across FLEXT projects."""

    def __init__(self, dry_run: bool = True, verbose: bool = False) -> None:
        """Initialize the standardizer.

        Args:
            dry_run: If True, only report changes without making them
            verbose: If True, show detailed output

        """
        self.dry_run = dry_run
        self.verbose = verbose
        self.projects: list[ProjectInfo] = []

    def scan_projects(self) -> None:
        """Scan all FLEXT projects in the ecosystem."""
        print(f"\n🔍 Scanning FLEXT ecosystem at: {FLEXT_ROOT}")
        print("=" * 80)

        # Find all directories with pyproject.toml (Python projects)
        for project_dir in sorted(FLEXT_ROOT.iterdir()):
            if not project_dir.is_dir():
                continue

            # Skip common non-project directories
            if project_dir.name in {".git", ".venv", "node_modules", "__pycache__"}:
                continue

            # Only process directories with pyproject.toml
            pyproject_file = project_dir / "pyproject.toml"
            if not pyproject_file.exists():
                continue

            self._analyze_project(project_dir)

        print(f"\n✅ Found {len(self.projects)} FLEXT projects")
        print("=" * 80)

    def _analyze_project(self, project_dir: Path) -> None:
        """Analyze a single project."""
        issues = []

        # Find pyproject.toml
        pyproject_toml = project_dir / "pyproject.toml"
        has_pyproject = pyproject_toml.exists()

        if not has_pyproject:
            issues.append("Missing pyproject.toml")

        # Find src directory
        src_path = project_dir / "src"
        if not src_path.exists():
            issues.append("Missing src/ directory")
            # Can't analyze further
            return

        # Find package directory (should be only one directory in src/)
        package_dirs = [
            d for d in src_path.iterdir() if d.is_dir() and not d.name.startswith(".")
        ]

        if not package_dirs:
            issues.append("No package found in src/")
            return

        if len(package_dirs) > 1:
            # Multiple packages - use the one matching project name or first non-test package
            project_name_snake = project_dir.name.replace("-", "_")
            matching_package = next(
                (d for d in package_dirs if d.name == project_name_snake), None
            )
            if matching_package:
                package_dir = matching_package
            else:
                # Use first non-test package
                non_test_packages = [
                    d for d in package_dirs if "test" not in d.name.lower()
                ]
                if non_test_packages:
                    package_dir = non_test_packages[0]
                else:
                    package_dir = package_dirs[0]
                issues.append(f"Multiple packages in src/, using: {package_dir.name}")
        else:
            package_dir = package_dirs[0]

        package_name = package_dir.name

        # Check for existing version files
        version_py = package_dir / "version.py"
        version_underscore = package_dir / "__version__.py"

        current_version_file = None
        if version_underscore.exists():
            current_version_file = version_underscore
        elif version_py.exists():
            current_version_file = version_py

        # Determine if update is needed
        needs_update = False
        if current_version_file:
            # Check if it follows the standard pattern
            content = current_version_file.read_text()
            if "class " in content or "client-aOudMigVersion" in content:
                needs_update = True
                issues.append("Uses custom version class (non-standard)")
            elif "importlib.metadata" not in content:
                needs_update = True
                issues.append("Doesn't use importlib.metadata")
            elif current_version_file.name == "version.py":
                needs_update = True
                issues.append("Uses version.py instead of __version__.py")
        else:
            needs_update = True
            issues.append("No version file found")

        project_info = ProjectInfo(
            name=project_dir.name,
            path=project_dir,
            src_path=src_path,
            package_name=package_name,
            pyproject_toml=pyproject_toml,
            current_version_file=current_version_file,
            needs_update=needs_update,
            has_pyproject=has_pyproject,
            issues=issues,
        )

        self.projects.append(project_info)

        if self.verbose:
            print(f"\n📦 {project_dir.name}")
            print(f"   Package: {package_name}")
            print(
                f"   Version file: {current_version_file.name if current_version_file else 'None'}"
            )
            print(f"   Needs update: {needs_update}")
            if issues:
                print(f"   Issues: {', '.join(issues)}")

    def report(self) -> None:
        """Generate detailed report of projects."""
        print("\n" + "=" * 80)
        print("📊 STANDARDIZATION REPORT")
        print("=" * 80)

        # Count statistics
        total = len(self.projects)
        needs_update = sum(1 for p in self.projects if p.needs_update)
        has_issues = sum(1 for p in self.projects if p.issues)
        ready = sum(1 for p in self.projects if not p.needs_update and not p.issues)

        print("\n📈 Statistics:")
        print(f"   Total projects: {total}")
        print(f"   ✅ Already standardized: {ready}")
        print(f"   🔄 Needs update: {needs_update}")
        print(f"   ⚠️  Has issues: {has_issues}")

        # Group projects by status
        ready_projects = [
            p for p in self.projects if not p.needs_update and not p.issues
        ]
        update_projects = [
            p for p in self.projects if p.needs_update and p.has_pyproject
        ]
        issue_projects = [
            p
            for p in self.projects
            if not p.has_pyproject or (p.issues and not p.needs_update)
        ]

        if ready_projects:
            print(f"\n✅ Already Standardized ({len(ready_projects)}):")
            for p in ready_projects:
                print(f"   • {p.name}")

        if update_projects:
            print(f"\n🔄 Ready for Update ({len(update_projects)}):")
            for p in update_projects:
                print(f"   • {p.name}")
                if p.current_version_file:
                    print(f"     Current: {p.current_version_file.name}")
                for issue in p.issues:
                    print(f"     ⚠️  {issue}")

        if issue_projects:
            print(f"\n⚠️  Needs Manual Review ({len(issue_projects)}):")
            for p in issue_projects:
                print(f"   • {p.name}")
                for issue in p.issues:
                    print(f"     ❌ {issue}")

    def standardize_project(self, project: ProjectInfo) -> bool:
        """Standardize a single project.

        Args:
            project: Project information

        Returns:
            True if successful, False otherwise

        """
        if not project.has_pyproject:
            print(f"   ❌ Skipping {project.name}: Missing pyproject.toml")
            return False

        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}🔧 Processing: {project.name}")
        print(f"   Package: {project.package_name}")

        # Step 1: Create new __version__.py
        version_file = project.src_path / project.package_name / "__version__.py"
        version_content = VERSION_TEMPLATE.format(package_name=project.package_name)

        if self.dry_run:
            print(f"   ℹ️  Would create: {version_file.relative_to(FLEXT_ROOT)}")
        else:
            print(f"   ✍️  Creating: {version_file.relative_to(FLEXT_ROOT)}")
            version_file.write_text(version_content)

        # Step 2: Remove old version.py if it exists
        old_version = project.src_path / project.package_name / "version.py"
        if old_version.exists() and old_version != version_file:
            if self.dry_run:
                print(f"   ℹ️  Would remove: {old_version.relative_to(FLEXT_ROOT)}")
            else:
                print(f"   🗑️  Removing: {old_version.relative_to(FLEXT_ROOT)}")
                old_version.unlink()

        # Step 3: Update __init__.py
        init_file = project.src_path / project.package_name / "__init__.py"
        if init_file.exists():
            self._update_init_file(project, init_file)

        # Step 4: Check for hardcoded metadata in constants
        constants_file = project.src_path / project.package_name / "constants.py"
        if constants_file.exists():
            self._check_constants_file(project, constants_file)

        print(f"   ✅ {project.name} processed successfully")
        return True

    def _update_init_file(self, project: ProjectInfo, init_file: Path) -> None:
        """Update __init__.py to import from __version__."""
        content = init_file.read_text(encoding="utf-8")

        # Check if already uses __version__ import
        if f"from {project.package_name}.__version__ import" in content:
            print("   ℹ️  __init__.py already imports from __version__")
            return

        if self.dry_run:
            print(f"   ℹ️  Would update: {init_file.relative_to(FLEXT_ROOT)}")
            print(
                f"      Add: from {project.package_name}.__version__ import __version__, __version_info__"
            )
        else:
            print(f"   ⚠️  Manual review needed: {init_file.relative_to(FLEXT_ROOT)}")
            print(
                f"      Add: from {project.package_name}.__version__ import __version__, __version_info__"
            )

    def _check_constants_file(self, project: ProjectInfo, constants_file: Path) -> None:
        """Check constants.py for hardcoded metadata."""
        content = constants_file.read_text(encoding="utf-8")

        hardcoded_patterns = [
            ('VERSION = "', "hardcoded VERSION"),
            ('AUTHOR = "', "hardcoded AUTHOR"),
            ('DESCRIPTION = "', "hardcoded DESCRIPTION"),
            ('LICENSE = "', "hardcoded LICENSE"),
        ]

        found_issues = []
        for pattern, description in hardcoded_patterns:
            if pattern in content:
                found_issues.append(description)

        if found_issues:
            print("   ⚠️  constants.py has hardcoded metadata:")
            for issue in found_issues:
                print(f"      • {issue}")
            if not self.dry_run:
                print(
                    f"      Manual review needed: {constants_file.relative_to(FLEXT_ROOT)}"
                )

    def standardize_all(self, confirm: bool = False) -> None:
        """Standardize all projects that need updates.

        Args:
            confirm: If True, proceed without confirmation prompt

        """
        update_projects = [
            p for p in self.projects if p.needs_update and p.has_pyproject
        ]

        if not update_projects:
            print("\n✅ All projects are already standardized!")
            return

        print(f"\n🎯 Planning to update {len(update_projects)} projects:")
        for p in update_projects:
            print(f"   • {p.name}")

        if not self.dry_run and not confirm:
            response = input("\n⚠️  This will modify files. Continue? [y/N]: ")
            if response.lower() != "y":
                print("❌ Aborted by user")
                return

        success_count = 0
        for project in update_projects:
            if self.standardize_project(project):
                success_count += 1

        print("\n" + "=" * 80)
        if self.dry_run:
            print(
                f"✅ Dry run complete: {success_count}/{len(update_projects)} projects would be updated"
            )
        else:
            print(
                f"✅ Standardization complete: {success_count}/{len(update_projects)} projects updated"
            )
        print("=" * 80)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Standardize __version__.py across FLEXT ecosystem"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be done without making changes (default)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually make changes (opposite of --dry-run)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output",
    )
    parser.add_argument(
        "--project",
        type=str,
        help="Standardize specific project only",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Standardize all projects",
    )
    parser.add_argument(
        "--yes-i-am-sure",
        action="store_true",
        help="Skip confirmation prompt (DANGER!)",
    )

    args = parser.parse_args()

    # Determine dry-run mode
    dry_run = not args.execute

    print("=" * 80)
    print("🚀 FLEXT Ecosystem __version__.py Standardization Script")
    print("=" * 80)
    print(
        f"\nMode: {'🔍 DRY RUN (safe - no changes)' if dry_run else '⚠️  EXECUTE (will make changes!)'}"
    )

    standardizer = VersionStandardizer(dry_run=dry_run, verbose=args.verbose)

    # Scan all projects
    standardizer.scan_projects()

    # Generate report
    standardizer.report()

    # Execute standardization if requested
    if args.all:
        standardizer.standardize_all(confirm=args.yes_i_am_sure)
    elif args.project:
        project = next(
            (p for p in standardizer.projects if p.name == args.project), None
        )
        if project:
            standardizer.standardize_project(project)
        else:
            print(f"\n❌ Project '{args.project}' not found")
            sys.exit(1)
    else:
        print("\n💡 Next steps:")
        print("   • Review the report above")
        print("   • Run with --all to standardize all projects")
        print("   • Run with --execute to actually make changes")
        print("   • Run with --project <name> to standardize one project")


if __name__ == "__main__":
    main()
