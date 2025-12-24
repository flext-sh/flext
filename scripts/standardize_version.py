#!/usr/bin/env python3
"""FLEXT Version Standardization Service.

Unified class implementation with flext-core patterns for __version__.py standardization
across the entire FLEXT ecosystem. Railway-oriented error handling, single responsibility
principle, and zero-tolerance quality gates.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from flext import FlextLogger, FlextModels, FlextResult, FlextService


class FlextVersionStandardizationService(FlextService[dict[str, object]]):
    """Unified version standardization service with flext-core integration.

    Railway-oriented implementation providing comprehensive __version__.py standardization
    across the FLEXT ecosystem using advanced patterns and minimal line count.
    """

    class ProjectAnalysis(FlextModels.Value):
        """Immutable project analysis data."""

        name: str
        path: Path
        src_path: Path
        package_name: str
        pyproject_toml: Path
        current_version_file: Path | None
        needs_update: bool
        has_pyproject: bool
        issues: frozenset[str]  # Immutable set for thread safety

    class StandardizationConfig(FlextModels.Value):
        """Immutable standardization configuration."""

        dry_run: bool
        verbose: bool
        flext_root: Path = Path("/home/marlonsc/flext")

    class _VersionTemplate:
        """Advanced template composition using nested class pattern."""

        TEMPLATE = '''"""Version and package metadata using importlib.metadata.

Single source of truth pattern following flext-core standards.
All metadata comes from pyproject.toml via importlib.metadata.

Copyright (c) 2025 client-a Telecom. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations
from flext import FlextBus, FlextSettings, FlextConstants, FlextContainer, FlextContext,
    FlextDecorators, FlextDispatcher, FlextExceptions, h,
    FlextLogger, x, FlextModels, FlextProcessors, p,
    FlextRegistry, FlextResult, FlextRuntime, FlextService, t,
    u
from importlib.metadata import metadata

_metadata = metadata("{package_name}")

__version__ = _metadata["Version"]
__version_info__ = tuple(int(part) if part.isdigit() else part for part in __version__.split("."))
__title__ = _metadata["Name"]
__description__ = _metadata["Summary"]
__author__ = _metadata.get("Author")
__author_email__ = _metadata.get("Author-Email")
__license__ = _metadata.get("License")
__url__ = _metadata.get("Home-Page")

__all__ = ["__version__", "__version_info__", "__title__", "__description__", "__author__", "__author_email__", "__license__", "__url__"]
'''

        @classmethod
        def format(cls, package_name: str) -> str:
            return cls.TEMPLATE.format(package_name=package_name)

    def __init__(self, config: StandardizationConfig) -> None:
        """Initialize version standardization service with configuration."""
        super().__init__()
        self._config = config
        self._logger = FlextLogger(__name__)
        self._projects: list[FlextVersionStandardizationService.ProjectAnalysis] = []

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute version standardization with railway pattern."""
        return (
            self._scan_projects()
            .flat_map(lambda _: self._generate_report())
            .flat_map(self._execute_standardization)
        )

    def _scan_projects(
        self,
    ) -> FlextResult[list[FlextVersionStandardizationService.ProjectAnalysis]]:
        """Railway-oriented project scanning."""
        try:
            self._logger.info(
                f"🔍 Scanning FLEXT ecosystem at: {self._config.flext_root}",
            )
            projects = []
            for project_dir in sorted(self._config.flext_root.iterdir()):
                if not project_dir.is_dir() or project_dir.name in {
                    ".git",
                    ".venv",
                    "node_modules",
                    "__pycache__",
                }:
                    continue
                if not (project_dir / "pyproject.toml").exists():
                    continue
                if (analysis := self._analyze_project(project_dir)) is not None:
                    projects.append(analysis)
            self._projects = projects
            self._logger.info(f"✅ Found {len(projects)} FLEXT projects")
            return FlextResult[
                list[FlextVersionStandardizationService.ProjectAnalysis]
            ].ok(projects)
        except Exception as e:
            return FlextResult[
                list[FlextVersionStandardizationService.ProjectAnalysis]
            ].fail(f"Project scan failed: {e}")

    def _analyze_project(
        self, project_dir: Path,
    ) -> FlextVersionStandardizationService.ProjectAnalysis | None:
        """Advanced project analysis with pattern matching."""
        try:
            pyproject_toml = project_dir / "pyproject.toml"
            src_path = project_dir / "src"
            if not src_path.exists():
                return None

            package_dirs = [
                d
                for d in src_path.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            ]
            if not package_dirs:
                return None

            package_dir = self._resolve_package_dir(project_dir, package_dirs)
            if package_dir is None:
                return None

            current_version_file, needs_update, issues = self._analyze_version_files(
                package_dir,
            )

            return self.ProjectAnalysis(
                name=project_dir.name,
                path=project_dir,
                src_path=src_path,
                package_name=package_dir.name,
                pyproject_toml=pyproject_toml,
                current_version_file=current_version_file,
                needs_update=needs_update,
                has_pyproject=True,
                issues=frozenset(issues),
            )
        except Exception:
            return None

    def _resolve_package_dir(
        self, project_dir: Path, package_dirs: list[Path],
    ) -> Path | None:
        """Advanced package directory resolution with pattern matching."""
        if len(package_dirs) == 1:
            return package_dirs[0]

        project_name_snake = project_dir.name.replace("-", "_")
        if matching := next(
            (d for d in package_dirs if d.name == project_name_snake), None,
        ):
            return matching

        non_test_packages = [d for d in package_dirs if "test" not in d.name.lower()]
        return non_test_packages[0] if non_test_packages else package_dirs[0]

    def _analyze_version_files(
        self, package_dir: Path,
    ) -> tuple[Path | None, bool, list[str]]:
        """Advanced version file analysis with pattern matching."""
        version_py = package_dir / "version.py"
        version_underscore = package_dir / "__version__.py"

        current_file = (
            version_underscore
            if version_underscore.exists()
            else (version_py if version_py.exists() else None)
        )
        if not current_file:
            return None, True, ["No version file found"]

        content = current_file.read_text()
        issues = []

        if "class " in content or "client-aOudMigVersion" in content:
            issues.append("Uses custom version class (non-standard)")
        if "importlib.metadata" not in content:
            issues.append("Doesn't use importlib.metadata")
        if current_file.name == "version.py":
            issues.append("Uses version.py instead of __version__.py")

        needs_update = bool(issues)
        return current_file, needs_update, issues

    def _generate_report(self) -> FlextResult[dict[str, object]]:
        """Advanced report generation with functional composition."""
        stats = self._calculate_stats()
        grouped_projects = self._group_projects_by_status()

        print(f"\n📊 STANDARDIZATION REPORT\n{'=' * 80}")
        self._print_stats(stats)
        self._print_project_groups(grouped_projects)

        return FlextResult[dict[str, object]].ok({
            "stats": stats,
            "projects": grouped_projects,
            "config": self._config,
        })

    def _calculate_stats(self) -> dict[str, int]:
        """Functional statistics calculation."""
        return {
            "total": len(self._projects),
            "ready": sum(
                1 for p in self._projects if not p.needs_update and not p.issues
            ),
            "needs_update": sum(1 for p in self._projects if p.needs_update),
            "has_issues": sum(1 for p in self._projects if p.issues),
        }

    def _group_projects_by_status(
        self,
    ) -> dict[str, list[FlextVersionStandardizationService.ProjectAnalysis]]:
        """Functional project grouping."""
        return {
            "ready": [p for p in self._projects if not p.needs_update and not p.issues],
            "update": [p for p in self._projects if p.needs_update],
            "issues": [p for p in self._projects if p.issues and not p.needs_update],
        }

    def _print_stats(self, stats: dict[str, int]) -> None:
        """Functional statistics printing."""
        print("\n📈 Statistics:")
        print(f"   Total projects: {stats['total']}")
        print(f"   ✅ Already standardized: {stats['ready']}")
        print(f"   🔄 Needs update: {stats['needs_update']}")
        print(f"   ⚠️  Has issues: {stats['has_issues']}")

    def _print_project_groups(
        self,
        groups: dict[str, list[FlextVersionStandardizationService.ProjectAnalysis]],
    ) -> None:
        """Functional project group printing."""
        if groups["ready"]:
            print(f"\n✅ Already Standardized ({len(groups['ready'])}):")
            for p in groups["ready"]:
                print(f"   • {p.name}")

        if groups["update"]:
            print(f"\n🔄 Ready for Update ({len(groups['update'])}):")
            for p in groups["update"]:
                print(f"   • {p.name}")
                if p.current_version_file:
                    print(f"     Current: {p.current_version_file.name}")
                for issue in p.issues:
                    print(f"     ⚠️  {issue}")

        if groups["issues"]:
            print(f"\n⚠️  Needs Manual Review ({len(groups['issues'])}):")
            for p in groups["issues"]:
                print(f"   • {p.name}")
                for issue in p.issues:
                    print(f"     ❌ {issue}")

    def _execute_standardization(
        self, report: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
        """Railway-oriented standardization execution."""
        if self._config.dry_run:
            return FlextResult[dict[str, object]].ok({
                "dry_run": True,
                "report": report,
            })

        update_projects = [p for p in self._projects if p.needs_update]
        if not update_projects:
            print("\n✅ All projects are already standardized!")
            return FlextResult[dict[str, object]].ok({"already_standardized": True})

        print(f"\n🎯 Standardizing {len(update_projects)} projects:")
        for p in update_projects:
            print(f"   • {p.name}")

        # Functional composition of standardization steps
        results = [self._standardize_single_project(p) for p in update_projects]
        success_count = sum(1 for r in results if r.is_success)

        print(
            f"\n✅ Standardization complete: {success_count}/{len(update_projects)} projects updated",
        )
        return FlextResult[dict[str, object]].ok({
            "success_count": success_count,
            "total": len(update_projects),
        })

    def _standardize_single_project(
        self, project: FlextVersionStandardizationService.ProjectAnalysis,
    ) -> FlextResult[bool]:
        """Railway-oriented single project standardization."""
        try:
            print(f"\n🔧 Processing: {project.name} (Package: {project.package_name})")

            # Functional composition of steps
            return (
                self._create_version_file(project)
                .flat_map(lambda _: self._remove_old_version_file(project))
                .flat_map(lambda _: self._update_init_file(project))
                .flat_map(lambda _: self._check_constants_file(project))
                .map(
                    lambda _: (
                        print(f"   ✅ {project.name} processed successfully"),
                        True,
                    )[1],
                )
            )
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to standardize {project.name}: {e}")

    def _create_version_file(
        self, project: FlextVersionStandardizationService.ProjectAnalysis,
    ) -> FlextResult[Path]:
        """Railway-oriented version file creation."""
        version_file = project.src_path / project.package_name / "__version__.py"
        content = self._VersionTemplate.format(project.package_name)

        try:
            version_file.write_text(content)
            print(f"   ✍️  Created: {version_file.relative_to(self._config.flext_root)}")
            return FlextResult[Path].ok(version_file)
        except Exception as e:
            return FlextResult[Path].fail(f"Failed to create version file: {e}")

    def _remove_old_version_file(
        self, project: FlextVersionStandardizationService.ProjectAnalysis,
    ) -> FlextResult[bool]:
        """Railway-oriented old version file removal."""
        old_version = project.src_path / project.package_name / "version.py"
        if old_version.exists():
            try:
                old_version.unlink()
                print(
                    f"   🗑️  Removed: {old_version.relative_to(self._config.flext_root)}",
                )
            except Exception as e:
                return FlextResult[bool].fail(f"Failed to remove old version file: {e}")
        return FlextResult[bool].ok(True)

    def _update_init_file(
        self, project: FlextVersionStandardizationService.ProjectAnalysis,
    ) -> FlextResult[bool]:
        """Railway-oriented init file updates."""
        init_file = project.src_path / project.package_name / "__init__.py"
        if not init_file.exists():
            return FlextResult[bool].ok(True)

        try:
            content = init_file.read_text(encoding="utf-8")
            import_statement = f"from {project.package_name}.__version__ import __version__, __version_info__"

            if import_statement in content:
                print("   ℹ️  __init__.py already imports from __version__")
                return FlextResult[bool].ok(True)

            # Advanced content manipulation - would add import if needed
            print(
                f"   ⚠️  Manual review needed: {init_file.relative_to(self._config.flext_root)}",
            )
            print(f"      Add: {import_statement}")
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to update init file: {e}")

    def _check_constants_file(
        self, project: FlextVersionStandardizationService.ProjectAnalysis,
    ) -> FlextResult[bool]:
        """Railway-oriented constants file checking."""
        constants_file = project.src_path / project.package_name / "constants.py"
        if not constants_file.exists():
            return FlextResult[bool].ok(True)

        try:
            content = constants_file.read_text(encoding="utf-8")
            patterns = [
                ('VERSION = "', "hardcoded VERSION"),
                ('AUTHOR = "', "hardcoded AUTHOR"),
                ('DESCRIPTION = "', "hardcoded DESCRIPTION"),
                ('LICENSE = "', "hardcoded LICENSE"),
            ]

            found_issues = [desc for pattern, desc in patterns if pattern in content]

            if found_issues:
                print("   ⚠️  constants.py has hardcoded metadata:")
                for issue in found_issues:
                    print(f"      • {issue}")
                print(
                    f"      Manual review needed: {constants_file.relative_to(self._config.flext_root)}",
                )

            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Failed to check constants file: {e}")


def create_standardization_service(
    *, dry_run: bool = True, verbose: bool = False,
) -> FlextVersionStandardizationService:
    """Factory function for version standardization service."""
    config = FlextVersionStandardizationService.StandardizationConfig(
        dry_run=dry_run, verbose=verbose,
    )
    return FlextVersionStandardizationService(config)


def main() -> None:
    """Railway-oriented main entry point."""
    parser = argparse.ArgumentParser(
        description="Standardize __version__.py across FLEXT ecosystem",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show changes without making them",
    )
    parser.add_argument("--execute", action="store_true", help="Actually make changes")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output",
    )
    parser.add_argument("--project", type=str, help="Standardize specific project only")
    parser.add_argument("--all", action="store_true", help="Standardize all projects")
    parser.add_argument(
        "--yes-i-am-sure", action="store_true", help="Skip confirmation prompt",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("🚀 FLEXT Ecosystem __version__.py Standardization Service")
    print("=" * 80)
    print(
        f"\nMode: {'🔍 DRY RUN (safe - no changes)' if not args.execute else '⚠️  EXECUTE (will make changes!)'}",
    )

    service = create_standardization_service(
        dry_run=not args.execute, verbose=args.verbose,
    )

    result = service.execute()
    if result.is_failure:
        print(f"❌ Standardization failed: {result.error}")
        sys.exit(1)

    print("✅ Standardization completed successfully")


if __name__ == "__main__":
    main()
