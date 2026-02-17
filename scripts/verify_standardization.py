#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-validation/SKILL.md
"""FLEXT Version Standardization Verification Service.

Unified class implementation with flext-core patterns for verifying __version__.py
standardization across the entire FLEXT ecosystem. Railway-oriented error handling
and single responsibility principle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from flext_core import FlextLogger, FlextResult, FlextService
from pydantic import BaseModel

VerificationResult = dict[str, bool]
ProjectVerification = dict[str, object]


class FlextVersionVerificationService(FlextService[dict[str, object]]):
    """Unified version verification service with flext-core integration.

    Railway-oriented implementation providing comprehensive verification of
    __version__.py standardization across the FLEXT ecosystem.
    """

    class VerificationConfig(BaseModel):
        """Immutable verification configuration."""

        flext_root: Path = Path("/home/marlonsc/flext")
        required_version_exports: frozenset[str] = frozenset({
            "__version__",
            "__version_info__",
            "__title__",
            "__description__",
            "__author__",
            "__author_email__",
            "__license__",
            "__url__",
        })

    class _VersionFileVerifier:
        """Advanced version file verification with functional composition."""

        @staticmethod
        def verify(project_dir: Path, package_name: str) -> VerificationResult:
            """Functional version file verification."""
            version_file = project_dir / "src" / package_name / "__version__.py"

            if not version_file.exists():
                return {
                    "has_version_file": False,
                    "uses_importlib": False,
                    "no_hardcoded_version": False,
                    "exports_all_metadata": False,
                }

            content = version_file.read_text()
            return {
                "has_version_file": True,
                "uses_importlib": "from importlib.metadata import metadata" in content,
                "no_hardcoded_version": not bool(
                    re.search(r'__version__\s*=\s*["\'][\d.]+["\']', content),
                ),
                "exports_all_metadata": all(
                    export in content
                    for export in FlextVersionVerificationService.VerificationConfig.required_version_exports
                ),
            }

    class _InitFileVerifier:
        """Advanced init file verification with functional composition."""

        @staticmethod
        def verify(project_dir: Path, package_name: str) -> VerificationResult:
            """Functional init file verification."""
            init_file = project_dir / "src" / package_name / "__init__.py"

            if not init_file.exists():
                return {
                    "imports_from_version": False,
                    "no_hardcoded_version": False,
                }

            content = init_file.read_text()
            return {
                "imports_from_version": f"from {package_name}.__version__ import"
                in content,
                "no_hardcoded_version": not bool(
                    re.search(r'__version__\s*=\s*["\'][\d.]+["\']', content),
                ),
            }

    class _ConstantsFileVerifier:
        """Advanced constants file verification with functional composition."""

        _HARDCODED_PATTERNS = (
            (r'^\s*VERSION\s*=\s*["\'][\d.]+["\']', "VERSION"),
            (r'^\s*AUTHOR\s*=\s*["\']', "AUTHOR"),
            (r'^\s*DESCRIPTION\s*=\s*["\']', "DESCRIPTION"),
            (r'^\s*LICENSE\s*=\s*["\']', "LICENSE"),
        )

        @classmethod
        def verify(cls, project_dir: Path, package_name: str) -> VerificationResult:
            """Functional constants file verification."""
            constants_file = project_dir / "src" / package_name / "constants.py"

            if not constants_file.exists():
                return {"no_hardcoded_metadata": True}

            content = constants_file.read_text()
            has_hardcoded = any(
                re.search(pattern, content, re.MULTILINE)
                and "VERSION = __version__" not in content
                for pattern, _ in cls._HARDCODED_PATTERNS
            )

            return {"no_hardcoded_metadata": not has_hardcoded}

    def __init__(self, config: VerificationConfig | None = None) -> None:
        """Initialize version verification service with configuration."""
        super().__init__()
        self._config = config or self.VerificationConfig()
        self._logger = FlextLogger(__name__)

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute version verification with railway pattern."""
        projects_result = self._discover_projects()
        if projects_result.is_failure:
            error_msg = projects_result.error or "Project discovery failed"
            return FlextResult[dict[str, object]].fail(error_msg)

        verifications_result = self._verify_all_projects(projects_result.value)
        if verifications_result.is_failure:
            error_msg = verifications_result.error or "Project verification failed"
            return FlextResult[dict[str, object]].fail(error_msg)

        return self._generate_summary(verifications_result.value)

    def _discover_projects(self) -> FlextResult[list[Path]]:
        """Railway-oriented project discovery."""
        try:
            projects = [
                project_dir
                for project_dir in sorted(self._config.flext_root.iterdir())
                if project_dir.is_dir() and (project_dir / "pyproject.toml").exists()
            ]
            self._logger.info(f"🔍 Discovered {len(projects)} FLEXT projects")
            return FlextResult[list[Path]].ok(projects)
        except Exception as e:
            return FlextResult[list[Path]].fail(f"Project discovery failed: {e}")

    def _verify_all_projects(
        self,
        projects: list[Path],
    ) -> FlextResult[list[ProjectVerification]]:
        """Railway-oriented bulk project verification."""
        try:
            results = [
                verification
                for project_dir in projects
                if (verification := self._verify_single_project(project_dir))
            ]
            return FlextResult[list[ProjectVerification]].ok(results)
        except Exception as e:
            return FlextResult[list[ProjectVerification]].fail(
                f"Project verification failed: {e}",
            )

    def _verify_single_project(self, project_dir: Path) -> ProjectVerification | None:
        """Railway-oriented single project verification."""
        try:
            package_name = self._resolve_package_name(project_dir)
            if not package_name:
                return {"project": project_dir.name, "error": "No package directory"}

            verification: ProjectVerification = {
                "project": project_dir.name,
                "package": package_name,
                "version_file": self._VersionFileVerifier.verify(
                    project_dir,
                    package_name,
                ),
                "init_file": self._InitFileVerifier.verify(project_dir, package_name),
                "constants_file": self._ConstantsFileVerifier.verify(
                    project_dir,
                    package_name,
                ),
            }

            # Calculate overall status
            version_file_result = verification["version_file"]
            init_file_result = verification["init_file"]
            constants_file_result = verification["constants_file"]

            if isinstance(version_file_result, dict) and all(
                isinstance(v, bool) for v in version_file_result.values()
            ):
                version_ok = all(version_file_result.values())
            else:
                version_ok = False

            if isinstance(init_file_result, dict) and all(
                isinstance(v, bool) for v in init_file_result.values()
            ):
                init_ok = all(init_file_result.values())
            else:
                init_ok = False

            if (
                isinstance(constants_file_result, dict)
                and "no_hardcoded_metadata" in constants_file_result
            ):
                constants_ok = bool(constants_file_result["no_hardcoded_metadata"])
            else:
                constants_ok = False
            verification["status"] = (
                "✅" if (version_ok and init_ok and constants_ok) else "⚠️"
            )

            return verification
        except Exception:
            return None

    def _resolve_package_name(self, project_dir: Path) -> str | None:
        """Advanced package name resolution."""
        src_dir = project_dir / "src"
        if not src_dir.exists():
            return None

        package_name = project_dir.name.replace("-", "_")
        package_dir = src_dir / package_name

        if package_dir.exists():
            return package_name

        # Find any package directory
        package_dirs = [
            d for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
        ]
        return package_dirs[0].name if package_dirs else None

    def _generate_summary(
        self,
        verifications: list[ProjectVerification],
    ) -> FlextResult[dict[str, object]]:
        """Railway-oriented summary generation."""
        try:
            success_count = sum(1 for v in verifications if v.get("status") == "✅")
            warning_count = sum(1 for v in verifications if v.get("status") == "⚠️")
            error_count = sum(1 for v in verifications if "error" in v)

            issues = self._collect_issues(verifications)

            summary = {
                "total_projects": len(verifications),
                "success_count": success_count,
                "warning_count": warning_count,
                "error_count": error_count,
                "issues": issues,
                "verifications": verifications,
            }

            self._print_summary(summary)
            return FlextResult[dict[str, object]].ok(summary)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Summary generation failed: {e}",
            )

    def _collect_issues(self, verifications: list[ProjectVerification]) -> list[str]:
        """Functional issue collection."""
        issues = []
        for verification in verifications:
            if verification.get("status") != "⚠️":
                continue

            project_obj = verification.get("project")
            if not isinstance(project_obj, str):
                continue
            project = project_obj

            version_file_obj = verification.get("version_file")
            init_file_obj = verification.get("init_file")
            constants_file_obj = verification.get("constants_file")

            if isinstance(version_file_obj, dict):
                version_file = version_file_obj
                if not version_file.get("has_version_file", False):
                    issues.append(f"  • {project}: Missing __version__.py")
                elif not version_file.get("uses_importlib", False):
                    issues.append(
                        f"  • {project}: __version__.py doesn't use importlib.metadata",
                    )
                elif not version_file.get("no_hardcoded_version", False):
                    issues.append(
                        f"  • {project}: __version__.py has hardcoded version",
                    )

            if isinstance(init_file_obj, dict):
                init_file = init_file_obj
                if not init_file.get("imports_from_version", False):
                    issues.append(
                        f"  • {project}: __init__.py doesn't import from __version__",
                    )
                if not init_file.get("no_hardcoded_version", False):
                    issues.append(f"  • {project}: __init__.py has hardcoded version")

            if isinstance(constants_file_obj, dict):
                constants_file = constants_file_obj
                if not constants_file.get("no_hardcoded_metadata", False):
                    issues.append(f"  • {project}: constants.py has hardcoded metadata")

        return issues

    def _print_summary(self, summary: dict[str, object]) -> None:
        """Functional summary printing."""
        print("\n" + "=" * 80)
        print("📊 Verification Summary")
        print("=" * 80)
        print(f"\nTotal projects: {summary['total_projects']}")
        print(f"✅ Fully standardized: {summary['success_count']}")
        print(f"⚠️  Need attention: {summary['warning_count']}")
        print(f"❌ Errors: {summary['error_count']}")

        issues_obj = summary.get("issues")
        if isinstance(issues_obj, list):
            issues = issues_obj
            if issues:
                print(f"\n⚠️  Issues Found ({len(issues)}):")
                for issue in issues:
                    if isinstance(issue, str):
                        print(issue)

        print("\n" + "=" * 80)

        warning_count_obj = summary.get("warning_count")
        error_count_obj = summary.get("error_count")
        warning_count = (
            int(warning_count_obj) if isinstance(warning_count_obj, (int, float)) else 0
        )
        error_count = (
            int(error_count_obj) if isinstance(error_count_obj, (int, float)) else 0
        )

        if warning_count == 0 and error_count == 0:
            print("✅ ALL PROJECTS FULLY STANDARDIZED!")
            sys.exit(0)
        else:
            print(f"⚠️  {warning_count + error_count} projects need attention")
            sys.exit(1)


def create_verification_service() -> FlextVersionVerificationService:
    """Factory function for version verification service."""
    return FlextVersionVerificationService()


def main() -> None:
    """Railway-oriented main entry point."""
    print("=" * 80)
    print("🔍 FLEXT Version Standardization Verification Service")
    print("=" * 80)

    service = create_verification_service()
    result = service.execute()

    if result.is_failure:
        print(f"❌ Verification failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
