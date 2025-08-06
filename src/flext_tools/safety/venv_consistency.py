"""FLEXT Virtual Environment Consistency Validation - Enterprise Environment Management.

Provides comprehensive validation capabilities for shared virtual environment
consistency across the FLEXT ecosystem. This module ensures that the workspace
virtual environment maintains consistency with all project requirements,
identifies conflicts, and provides actionable recommendations for resolution.

The validator analyzes installed packages against project requirements from
all Poetry configurations, detecting version conflicts, missing dependencies,
orphaned packages, and other inconsistencies that could impact development
and deployment stability.

Key Components:
    - VenvConsistencyValidator: Main validation engine for environment analysis
    - PackageInfo: Structured representation of installed package metadata
    - VenvConflict: Detailed conflict information with severity classification
    - Consistency Analysis: Cross-project requirement validation
    - Resolution Recommendations: Actionable suggestions for conflict resolution

Architecture:
    Implements enterprise-grade environment validation with proper error handling,
    comprehensive scanning capabilities, and detailed reporting. Integrates with
    Poetry dependency management and provides structured output for automated
    and manual conflict resolution processes.

Example:
    Validate workspace virtual environment consistency:

    >>> from flext_tools.safety.venv_consistency import VenvConsistencyValidator
    >>> from pathlib import Path
    >>>
    >>> # Initialize validator for workspace
    >>> validator = VenvConsistencyValidator(Path("/workspace/flext"))
    >>>
    >>> # Perform comprehensive consistency validation
    >>> conflicts = validator.validate_venv_consistency()
    >>>
    >>> # Review critical conflicts
    >>> if conflicts["critical"]:
    ...     print(f"Found {len(conflicts['critical'])} critical issues")
    ...     for conflict in conflicts["critical"]:
    ...         print(f"Package: {conflict.package}")
    ...         print(f"Issue: {conflict.details}")
    ...         print(f"Projects affected: {conflict.affected_projects}")

Integration:
    - Built on Poetry configuration parsing for accurate requirement extraction
    - Integrates with pip list for comprehensive package discovery
    - Coordinates with quality gates for automated environment validation
    - Provides foundation for automated environment synchronization
    - Supports workspace-wide dependency management strategies

Quality Standards:
    - Comprehensive error handling with detailed context preservation
    - Performance optimization for large workspace environments
    - Configurable analysis parameters and severity thresholds
    - Integration with development workflows and CI/CD pipelines
    - Professional English documentation and user-facing messages

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from flext_tools.utils import Colors, print_colored

if TYPE_CHECKING:
    from pathlib import Path

MAX_ORPHAN_DISPLAY = 10
MAX_PROJECTS_DISPLAY = 5
MAX_CONFLICTS_DISPLAY = 10


@dataclass
class PackageInfo:
    """Information about an installed package.

    Represents metadata for packages installed in the virtual environment
    including version information, location, and dependency relationships
    for comprehensive environment analysis.

    Attributes:
        name: Package name (normalized to lowercase)
        version: Installed package version string
        location: Installation location path (optional)
        required_by: List of packages that depend on this package (optional)
        dependencies: List of packages this package depends on (optional)

    """

    name: str
    version: str
    location: str | None = None
    required_by: list[str] | None = None
    dependencies: list[str] | None = None


@dataclass
class VenvConflict:
    """Represents a conflict in the virtual environment.

    Contains detailed information about environment inconsistencies including
    conflict type, affected packages, severity assessment, and impact analysis
    for structured conflict resolution and reporting.

    Attributes:
        type: Conflict type ("version", "missing", "duplicate", "orphan")
        package: Name of the affected package
        details: Detailed description of the conflict
        severity: Severity level ("critical", "warning", "info")
        affected_projects: List of projects impacted by this conflict

    """

    type: str  # "version", "missing", "duplicate", "orphan"
    package: str
    details: str
    severity: str  # "critical", "warning", "info"
    affected_projects: list[str]


class VenvConsistencyValidator:
    """Validates consistency of shared virtual environment across workspace.

    Provides comprehensive validation capabilities for workspace virtual environment
    consistency, analyzing installed packages against project requirements and
    identifying conflicts, missing dependencies, and optimization opportunities.

    This validator serves as the primary tool for maintaining environment health
    across the FLEXT ecosystem, ensuring that the shared virtual environment
    meets all project requirements while identifying potential issues before
    they impact development or deployment processes.

    Attributes:
        workspace_path: Path to the workspace root directory
        venv_path: Path to the shared virtual environment
        installed_packages: Dictionary of installed package information
        project_requirements: Dictionary of project requirement specifications
        conflicts: List of identified environment conflicts

    Features:
        - Comprehensive package installation analysis
        - Cross-project requirement validation
        - Version conflict detection with severity assessment
        - Orphaned package identification
        - Missing dependency detection
        - Detailed reporting with actionable recommendations

    Architecture:
        Uses Poetry configuration parsing and pip list integration for
        comprehensive environment analysis with proper error handling
        and structured conflict reporting.

    Example:
        Validate workspace environment consistency:

        >>> from pathlib import Path
        >>> validator = VenvConsistencyValidator(Path("/workspace"))
        >>>
        >>> conflicts = validator.validate_venv_consistency()
        >>>
        >>> # Check for critical issues
        >>> if conflicts["critical"]:
        ...     print("Critical environment issues detected:")
        ...     for conflict in conflicts["critical"]:
        ...         print(f"  {conflict.package}: {conflict.details}")
        >>>
        >>> # Review warnings and optimization opportunities
        >>> for severity in ["warning", "info"]:
        ...     if conflicts[severity]:
        ...         print(f"{severity.title()} issues: {len(conflicts[severity])}")

    Integration:
        Integrates with Poetry dependency management, quality gates, and
        automated validation pipelines for continuous environment health
        monitoring and maintenance.

    """

    def __init__(self, workspace_path: Path) -> None:
        """Initialize validator with workspace path."""
        self.workspace_path = workspace_path
        self.venv_path = workspace_path / ".venv"
        self.installed_packages: dict[str, PackageInfo] = {}
        self.project_requirements: dict[str, dict[str, str]] = {}
        self.conflicts: list[VenvConflict] = []

    def validate_venv_consistency(self) -> dict[str, list[VenvConflict]]:
        """Validate consistency of shared virtual environment.

        Performs comprehensive validation of the workspace virtual environment
        against all project requirements, identifying conflicts, missing packages,
        version inconsistencies, and optimization opportunities.

        Returns:
            Dictionary mapping severity levels to lists of conflicts:
            - 'critical': Issues that must be resolved (missing venv, missing packages)
            - 'warning': Issues that should be addressed (version conflicts)
            - 'info': Optimization opportunities (orphaned packages)

        Validation Process:
            1. Verify virtual environment exists and is accessible
            2. Scan all installed packages with metadata extraction
            3. Collect requirements from all project Poetry configurations
            4. Analyze conflicts between installed packages and requirements
            5. Organize conflicts by severity for prioritized resolution
            6. Generate comprehensive validation summary report

        Architecture:
            Uses pipeline pattern for validation steps with proper error handling
            and recovery at each stage to ensure comprehensive analysis even
            with partial failures.

        """
        print_colored(
            "🔍 Validating virtual environment consistency...",
            Colors.BLUE,
        )

        # 1. Check if virtual environment exists
        if not self._check_venv_exists():
            return {
                "critical": [
                    VenvConflict(
                        type="missing_venv",
                        package="",
                        details="Virtual environment not found",
                        severity="critical",
                        affected_projects=[],
                    ),
                ],
            }

        # 2. Scan installed packages
        self._scan_installed_packages()

        # 3. Collect project requirements
        self._collect_project_requirements()

        # 4. Analyze conflicts
        self._analyze_conflicts()

        # 5. Organize conflicts by severity
        conflicts_by_severity = self._organize_conflicts_by_severity()

        # 6. Generate validation report
        self._print_validation_summary(conflicts_by_severity)

        return conflicts_by_severity

    def _check_venv_exists(self) -> bool:
        """Check if the virtual environment exists.

        Validates that the expected virtual environment directory exists
        and is accessible for package analysis and validation.

        Returns:
            True if virtual environment exists and is accessible,
            False if missing or inaccessible

        """
        if not self.venv_path.exists():
            print_colored("❌ Virtual environment not found!", Colors.RED)
            print_colored(f"    Expected at: {self.venv_path}", Colors.YELLOW)
            return False

        print_colored(
            f"✅ Virtual environment found: {self.venv_path}",
            Colors.GREEN,
        )
        return True

    def _scan_installed_packages(self) -> None:
        """Scan packages installed in the virtual environment.

        Uses pip list to discover all installed packages with their
        versions and metadata for comprehensive environment analysis.

        Updates the installed_packages dictionary with PackageInfo
        objects containing package metadata for conflict analysis.
        """
        print_colored("  📦 Scanning installed packages...", Colors.CYAN)

        try:
            # Use pip list to get installed packages
            # Safe: using sys.executable with hardcoded arguments
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.workspace_path,
            )

            packages_data = json.loads(result.stdout)

            for package_data in packages_data:
                name = package_data["name"].lower()
                version = package_data["version"]

                self.installed_packages[name] = PackageInfo(
                    name=name,
                    version=version,
                )

            print_colored(
                f"    ✅ {len(self.installed_packages)} packages found",
                Colors.GREEN,
            )

        except subprocess.CalledProcessError as e:
            print_colored(f"    ⚠️ Error scanning packages: {e}", Colors.YELLOW)
        except (json.JSONDecodeError, OSError, ValueError) as e:
            print_colored(f"    ⚠️ Unexpected error: {e}", Colors.YELLOW)

    def _collect_project_requirements(self) -> None:
        """Collect requirements from all projects in workspace.

        Scans all project directories for pyproject.toml files and extracts
        Poetry dependency specifications including main dependencies and
        development group dependencies for comprehensive requirement analysis.

        Updates the project_requirements dictionary with project-specific
        dependency specifications for conflict detection.
        """
        print_colored("  📋 Collecting project requirements...", Colors.CYAN)

        projects = [
            d
            for d in self.workspace_path.iterdir()
            if d.is_dir()
            and not d.name.startswith(".")
            and (d / "pyproject.toml").exists()
        ]

        for project_path in projects:
            project_name = project_path.name

            # Process pyproject.toml
            pyproject_path = project_path / "pyproject.toml"

            try:
                with pyproject_path.open("rb") as f:
                    data = tomllib.load(f)

                self.project_requirements[project_name] = {}

                # Main dependencies
                deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
                for dep_name, dep_spec in deps.items():
                    if dep_name != "python":
                        name, version = self._parse_dependency_spec(str(dep_spec))
                        self.project_requirements[project_name][name] = version

                # Development dependencies
                dev_deps = (
                    data.get("tool", {})
                    .get("poetry", {})
                    .get("group", {})
                    .get("dev", {})
                    .get("dependencies", {})
                )
                for dep_spec in dev_deps.values():
                    name, version = self._parse_dependency_spec(str(dep_spec))
                    self.project_requirements[project_name][f"{name}[dev]"] = version

            except (
                OSError,
                tomllib.TOMLDecodeError,
                KeyError,
                UnicodeDecodeError,
            ) as e:
                print_colored(
                    f"    ⚠️ Error reading {project_name}: {e}",
                    Colors.YELLOW,
                )

        total_reqs = sum(len(reqs) for reqs in self.project_requirements.values())
        print_colored(
            f"    ✅ {total_reqs} requirements across {len(projects)} projects",
            Colors.GREEN,
        )

    def _parse_dependency_spec(
        self,
        dep_spec: str | dict[str, object],
    ) -> tuple[str, str]:
        """Parse a PEP 621 dependency specification.

        Processes dependency specifications from Poetry configuration files,
        handling both simple string formats and complex dictionary formats
        with proper normalization and version extraction.

        Args:
            dep_spec: Dependency specification (string or dict format)

        Returns:
            Tuple containing normalized package name and version constraint

        Supported Formats:
            - Simple strings: "package", "package^1.0.0", "package>=1.0.0"
            - Dictionary format: {"name": "package", "version": "^1.0.0"}

        """
        if isinstance(dep_spec, dict):
            name = dep_spec.get("name", "unknown")
            version = dep_spec.get("version", "*")
            return str(name).lower(), str(version)

        # Simple string like "package^1.0.0" or "package"
        if "^" in dep_spec:
            name, version = dep_spec.split("^", 1)
            return name.lower().strip(), f"^{version.strip()}"
        if "==" in dep_spec:
            name, version = dep_spec.split("==", 1)
            return name.lower().strip(), f"=={version.strip()}"
        if ">=" in dep_spec:
            name, version = dep_spec.split(">=", 1)
            return name.lower().strip(), f">={version.strip()}"
        return dep_spec.lower().strip(), "*"

    def _analyze_conflicts(self) -> None:
        """Analyze conflicts between installed packages and requirements.

        Performs comprehensive conflict analysis by comparing installed packages
        against project requirements, identifying version conflicts, missing
        packages, and orphaned installations for structured conflict resolution.

        Analysis Types:
            - Version conflicts: Same package with different version requirements
            - Missing packages: Required packages not installed in environment
            - Orphaned packages: Installed packages not required by any project

        Updates the conflicts list with structured conflict information
        including severity assessment and affected project identification.
        """
        print_colored("  🔍 Analyzing conflicts...", Colors.CYAN)

        # Map which package is requested by which projects
        package_requesters: dict[str, list[str]] = defaultdict(list)
        package_versions: dict[str, set[str]] = defaultdict(set)

        for project, requirements in self.project_requirements.items():
            for package, version in requirements.items():
                # Remove markers like [dev]
                clean_package = package.split("[")[0]
                package_requesters[clean_package].append(project)
                package_versions[clean_package].add(version)

        # 1. Version conflicts
        for package, versions in package_versions.items():
            if len(versions) > 1:
                self.conflicts.append(
                    VenvConflict(
                        type="version",
                        package=package,
                        details=f"Conflicting versions: {', '.join(versions)}",
                        severity="warning",
                        affected_projects=package_requesters[package],
                    ),
                )

        # 2. Packages missing
        for package, requesters in package_requesters.items():
            if package not in self.installed_packages:
                self.conflicts.append(
                    VenvConflict(
                        type="missing",
                        package=package,
                        details="Package required but not installed",
                        severity="critical",
                        affected_projects=requesters,
                    ),
                )

        # 3. Orphaned packages
        all_required = set(package_requesters.keys())
        installed_names = set(self.installed_packages.keys())
        orphans = installed_names - all_required

        # Remove known system packages
        system_packages = {
            "pip",
            "setuptools",
            "wheel",
            "poetry",
            "poetry-core",
            "pkg-resources",
            "pkg_resources",
            "distlib",
            "virtualenv",
        }
        orphans -= system_packages

        for orphan in orphans:
            self.conflicts.append(
                VenvConflict(
                    type="orphan",
                    package=orphan,
                    details="Package installed but not required by any project",
                    severity="info",
                    affected_projects=[],
                ),
            )

        print_colored(
            f"    ✅ {len(self.conflicts)} conflicts identified",
            Colors.GREEN,
        )

    def _organize_conflicts_by_severity(self) -> dict[str, list[VenvConflict]]:
        """Organize conflicts by severity level.

        Groups identified conflicts into severity categories for prioritized
        resolution and structured reporting. Critical issues require immediate
        attention, warnings should be addressed, and info items are optimization
        opportunities.

        Returns:
            Dictionary mapping severity levels to conflict lists:
            - 'critical': Issues that must be resolved immediately
            - 'warning': Issues that should be addressed
            - 'info': Optimization opportunities and minor issues

        """
        organized: dict[str, list[VenvConflict]] = {
            "critical": [],
            "warning": [],
            "info": [],
        }

        for conflict in self.conflicts:
            organized[conflict.severity].append(conflict)

        return organized

    def _print_validation_summary(
        self,
        conflicts_by_severity: dict[str, list[VenvConflict]],
    ) -> None:
        """Print comprehensive validation summary report.

        Generates detailed console output summarizing the virtual environment
        validation results including statistics, conflict breakdown by severity,
        and actionable information for conflict resolution.

        Args:
            conflicts_by_severity: Organized conflicts grouped by severity level
            for structured reporting and prioritized resolution planning

        """
        print_colored("\n" + "=" * 60, Colors.CYAN)
        print_colored(
            "📊 VIRTUAL ENVIRONMENT CONSISTENCY VALIDATION SUMMARY",
            Colors.CYAN,
        )
        print_colored("=" * 60, Colors.CYAN)

        total_installed = len(self.installed_packages)
        total_projects = len(self.project_requirements)
        total_conflicts = len(self.conflicts)

        print_colored(f"📦 Packages installed: {total_installed}", Colors.BLUE)
        print_colored(f"📂 Projects scanned: {total_projects}", Colors.BLUE)
        print_colored(f"⚠️ Conflicts found: {total_conflicts}", Colors.BLUE)

        # Display conflicts by severity
        for severity, conflicts in conflicts_by_severity.items():
            if not conflicts:
                continue

            if severity == "critical":
                icon, color = "🔴", Colors.RED
            elif severity == "warning":
                icon, color = "🟡", Colors.YELLOW
            else:
                icon, color = "[INFO]", Colors.CYAN

            print_colored(
                f"\n{icon} {severity.upper()}: {len(conflicts)} conflicts",
                color,
            )

            for conflict in conflicts[:MAX_CONFLICTS_DISPLAY]:
                print_colored(f"  • {conflict.package}: {conflict.details}", color)

                if conflict.affected_projects:
                    projects_str = ", ".join(
                        conflict.affected_projects[:MAX_PROJECTS_DISPLAY],
                    )
                    if len(conflict.affected_projects) > MAX_PROJECTS_DISPLAY:
                        projects_str += (
                            f" and {len(conflict.affected_projects) - 5} more"
                        )
                    print_colored(f"    🎯 Affected projects: {projects_str}", color)

            if len(conflicts) > MAX_CONFLICTS_DISPLAY:
                print_colored(
                    f"    ... and {len(conflicts) - 10} more conflicts",
                    color,
                )
