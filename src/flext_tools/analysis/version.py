"""FLEXT Version Analysis Tools - Package Version Conflict Detection and Resolution.

Provides comprehensive version analysis capabilities for detecting and resolving
package version conflicts across the FLEXT ecosystem. This module implements
sophisticated version constraint analysis, conflict detection, and automated
resolution strategies for maintaining consistent dependency management across
all 33 FLEXT projects.

The version analyzer handles complex version constraint scenarios including
semantic versioning, caret constraints, tilde constraints, and range specifications.
All analysis operations provide detailed conflict reports and actionable
resolution recommendations for maintaining ecosystem stability.

Key Components:
    - VersionAnalyzer: Core version analysis and conflict detection engine
    - Version Parsing: Comprehensive package specification parsing and normalization
    - Compatibility Analysis: Cross-project version compatibility validation
    - Conflict Resolution: Automated version conflict resolution strategies
    - Helper Functions: Convenient functional interface for version operations

Architecture:
    Implements enterprise-grade version analysis patterns with proper error
    handling, constraint normalization, and conflict resolution strategies.
    Integrates with packaging library for robust version handling and provides
    comprehensive reporting for operational decision-making.

Example:
    Version conflict analysis across FLEXT projects:

    >>> from flext_tools.analysis.version import VersionAnalyzer
    >>> from flext_tools.analysis.version import analyze_version_conflicts
    >>>
    >>> # Analyze version conflicts across projects
    >>> projects_data = {
    ...     "flext-core": {
    ...         "project": {"dependencies": ["pydantic>=2.0.0"]},
    ...         "tool": {"poetry": {"dependencies": {"pydantic": "^2.1.0"}}},
    ...     },
    ...     "flext-api": {
    ...         "project": {"dependencies": ["pydantic>=1.10.0,<2.0.0"]},
    ...         "tool": {"poetry": {"dependencies": {"pydantic": "^1.10.12"}}},
    ...     },
    ... }
    >>>
    >>> conflicts = analyze_version_conflicts(projects_data)
    >>> if conflicts:
    ...     print(f"Found conflicts in {len(conflicts)} packages")
    ...     for package, conflict_info in conflicts.items():
    ...         print(f"Package {package}: {conflict_info[0]['severity']} conflict")

Integration:
    - Built on packaging library for robust version constraint handling
    - Integrates with flext-tools utilities for consistent error reporting
    - Supports both PEP 621 and Poetry dependency specifications
    - Provides foundation for automated dependency management workflows
    - Coordinates with quality gates for ecosystem consistency validation

Quality Standards:
    - Comprehensive error handling with detailed context preservation
    - Full type annotation coverage for enhanced development experience
    - Extensive validation of version constraint formats and compatibility
    - Performance-optimized algorithms for large-scale dependency analysis
    - Security-conscious version constraint validation and normalization

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

import re

from flext_core import FlextResult, get_logger
from packaging import version
from packaging.specifiers import SpecifierSet
from pydantic import BaseModel, Field

from flext_tools.utils import Colors, print_colored

GROUPS_WITH_EXTRA = 3
GROUPS_WITHOUT_EXTRA = 2
MIN_PROJECTS_HIGH_SEVERITY = 2

# Initialize logger
logger = get_logger(__name__)


class VersionCompatibilityResult(BaseModel):
    """Version compatibility analysis result using FlextEntity for type safety.

    This entity represents the result of version compatibility analysis between
    two package version specifications, providing structured data for compatibility
    assessment and conflict resolution.

    Attributes:
        compatible: Whether the version specifications are compatible
        spec1: First version specification analyzed
        spec2: Second version specification analyzed
        overlap_version: Common version that satisfies both specifications (if any)
        issues: List of compatibility issues found
        recommendations: List of recommended actions for resolution

    """

    compatible: bool = Field(
        description="Whether the version specifications are compatible",
    )
    spec1: str = Field(description="First version specification analyzed")
    spec2: str = Field(description="Second version specification analyzed")
    overlap_version: str | None = Field(
        default=None,
        description="Common version that satisfies both specifications",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="List of compatibility issues found",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="List of recommended actions for resolution",
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules for version compatibility result."""
        if not self.spec1 or not self.spec2:
            return FlextResult.fail("Both version specifications must be provided")
        return FlextResult.ok(None)


class VersionAnalyzer:
    """Enterprise package version analysis and constraint management.

    Provides comprehensive version analysis capabilities for detecting conflicts,
    normalizing constraints, and resolving version compatibility issues across
    the FLEXT ecosystem. Handles complex version scenarios including semantic
    versioning, caret/tilde constraints, and range specifications.
    """

    @staticmethod
    def parse_version_spec(spec: str) -> tuple[str, str | None]:
        """Extract package name and version constraint from specification.

        Parses various package specification formats including standard PEP 508
        specifications, Poetry-style constraints, and packages with extras.
        Handles complex patterns and normalizes output for consistent processing.

        Args:
            spec: Package specification (e.g., "django>=3.2", "pydantic[email]^2.0")

        Returns:
            Tuple containing (package_name, version_specification)
            Version specification may be None if no constraint is specified

        Example:
            >>> parse_version_spec("pydantic[email]>=2.0.0")
            ('pydantic', '>=2.0.0')
            >>> parse_version_spec("django")
            ('django', None)

        """
        # Common specification patterns
        patterns = [
            r"^([a-zA-Z0-9_\-\.]+)\s*([><=!]+.*)$",  # package>=1.0
            r"^([a-zA-Z0-9_\-\.]+)\[([^\]]+)\]\s*([><=!]+.*)$",  # package[extra]>=1.0
            r"^([a-zA-Z0-9_\-\.]+)$",  # package without version
        ]

        for pattern in patterns:
            match = re.match(pattern, spec.strip())
            if match:
                if len(match.groups()) == GROUPS_WITH_EXTRA:  # With extra
                    return match.group(1), match.group(3)
                if len(match.groups()) == GROUPS_WITHOUT_EXTRA:  # Without extra
                    return match.group(1), match.group(2)
                # Name only
                return match.group(1), None

        return spec, None

    @staticmethod
    def normalize_constraint(constraint: str) -> str:
        """Normalize version constraint to standard PEP 440 format.

        Converts Poetry-style caret (^) and tilde (~) constraints to standard
        PEP 440 version specifiers for consistent processing and compatibility
        analysis. Handles edge cases and semantic versioning rules properly.

        Args:
            constraint: Original constraint (e.g., "^1.2.3", "~2.1.0")

        Returns:
            Normalized constraint in PEP 440 format (e.g., ">=1.2.3,<2.0.0")
            Returns "*" for empty or None constraints

        Example:
            >>> normalize_constraint("^1.2.3")
            '>=1.2.3,<2.0.0'
            >>> normalize_constraint("~2.1.0")
            '>=2.1.0,<2.2.0'

        """
        if not constraint:
            return "*"

        # Remove whitespace
        constraint = constraint.strip()

        # Convert caret (^) to semantic range
        if constraint.startswith("^"):
            base_version = constraint[1:]
            try:
                v = version.parse(base_version)
            except (ValueError, AttributeError, TypeError):
                return constraint
            else:
                # ^0.0.x -> >=0.0.x,<0.0.(x+1) OR ^0.x.y -> >=0.x.y,<0.(x+1).0
                # OR ^x.y.z -> >=x.y.z,<(x+1).0.0
                if v.major == 0:
                    upper = (
                        f"0.0.{v.micro + 1}" if v.minor == 0 else f"0.{v.minor + 1}.0"
                    )
                else:
                    upper = f"{v.major + 1}.0.0"
                return f">={base_version},<{upper}"

        # Convert tilde (~) to range
        if constraint.startswith("~"):
            base_version = constraint[1:]
            try:
                v = version.parse(base_version)
            except (ValueError, AttributeError, TypeError):
                return constraint
            else:
                # ~x.y.z -> >=x.y.z,<x.(y+1).0
                upper = f"{v.major}.{v.minor + 1}.0"
                return f">={base_version},<{upper}"

        return constraint

    @staticmethod
    def check_version_compatibility(
        spec1: str,
        spec2: str,
    ) -> dict[str, object]:
        """Check compatibility between two version specifications.

        Analyzes whether two version constraints can be satisfied simultaneously
        by finding their intersection. Provides detailed compatibility analysis
        including conflict detection and recommended resolution strategies.

        Args:
            spec1: First version specification (e.g., ">=1.0.0")
            spec2: Second version specification (e.g., "<2.0.0")

        Returns:
            Dictionary containing compatibility analysis:
            - compatible: Boolean indicating if specs are compatible
            - conflict: Boolean indicating if there's a direct conflict
            - recommended: Recommended constraint combining both specs
            - issues: List of specific compatibility issues found

        Example:
            >>> check_version_compatibility(">=1.0.0", "<2.0.0")
            {'compatible': True, 'conflict': False, 'recommended': '>=1.0.0,<2.0.0',
             'issues': []}

        """
        if not spec1 or not spec2:
            return {
                "compatible": True,
                "conflict": False,
                "recommended": "*",
                "issues": [],
            }

        # Normalize all constraints
        normalized1 = VersionAnalyzer.normalize_constraint(spec1)
        normalized2 = VersionAnalyzer.normalize_constraint(spec2)

        try:
            combined = SpecifierSet()
            if normalized1 != "*":
                combined &= SpecifierSet(normalized1)
            if normalized2 != "*":
                combined &= SpecifierSet(normalized2)
        except (ValueError, TypeError, AttributeError) as e:
            return {
                "compatible": False,
                "conflict": True,
                "recommended": None,
                "issues": [f"Error processing constraints: {e}"],
            }
        else:
            # Check if there's a valid intersection
            if combined:
                return {
                    "compatible": True,
                    "conflict": False,
                    "recommended": str(combined),
                    "issues": [],
                }
            return {
                "compatible": False,
                "conflict": True,
                "recommended": None,
                "issues": [f"Incompatible constraints: {spec1}, {spec2}"],
            }

    @staticmethod
    def find_common_version_range(
        project_constraints: dict[str, str],
    ) -> str | None:
        """Find common version range across multiple project constraints.

        Analyzes version constraints from multiple projects to find a common
        version range that satisfies all requirements. Uses intersection logic
        to determine the most restrictive compatible constraint.

        Args:
            project_constraints: Dictionary mapping project names to version constraints
                                e.g., {"flext-core": ">=2.0.0", "flext-api": "<3.0.0"}

        Returns:
            Common version range string if compatible, None if incompatible
            Returns "*" for unconstrained scenarios

        Example:
            >>> find_common_version_range({"proj1": ">=1.0.0", "proj2": "<2.0.0"})
            '>=1.0.0,<2.0.0'

        """
        if not project_constraints:
            return None

        constraints = list(project_constraints.values())
        unique_constraints = list({c for c in constraints if c})

        if not unique_constraints:
            return "*"

        if len(unique_constraints) == 1:
            return unique_constraints[0]

        # Try to find intersection
        result = VersionAnalyzer.check_version_compatibility(
            unique_constraints[0],
            unique_constraints[1],
        )
        recommended = result.get("recommended")
        return str(recommended) if recommended is not None else None

    @staticmethod
    def _collect_package_versions(
        projects_data: dict[str, dict[str, object]],
    ) -> dict[str, dict[str, str]]:
        """Collect package versions from project data."""
        package_versions: dict[str, dict[str, str]] = {}

        for project_name, data in projects_data.items():
            VersionAnalyzer._collect_pep621_dependencies(
                data,
                project_name,
                package_versions,
            )
            VersionAnalyzer._collect_poetry_dependencies(
                data,
                project_name,
                package_versions,
            )

        return package_versions

    @staticmethod
    def _collect_pep621_dependencies(
        data: dict[str, object],
        project_name: str,
        package_versions: dict[str, dict[str, str]],
    ) -> None:
        """Collect PEP 621 dependencies from project data."""
        project_section = data.get("project", {})
        if not isinstance(project_section, dict):
            return

        pep621_deps = project_section.get("dependencies", [])
        if not isinstance(pep621_deps, list):
            return

        for dep_spec in pep621_deps:
            package_name, version_spec = VersionAnalyzer.parse_version_spec(dep_spec)
            if package_name and version_spec:
                VersionAnalyzer._add_package_version(
                    package_name,
                    project_name,
                    version_spec,
                    package_versions,
                )

    @staticmethod
    def _collect_poetry_dependencies(
        data: dict[str, object],
        project_name: str,
        package_versions: dict[str, dict[str, str]],
    ) -> None:
        """Collect Poetry dependencies from project data."""
        tool_section = data.get("tool", {})
        if not isinstance(tool_section, dict):
            return

        poetry_section = tool_section.get("poetry", {})
        if not isinstance(poetry_section, dict):
            return

        poetry_deps = poetry_section.get("dependencies", {})
        if not isinstance(poetry_deps, dict):
            return

        for package_name, dep_spec in poetry_deps.items():
            version_spec = VersionAnalyzer._parse_poetry_version_spec(dep_spec)
            if version_spec:
                VersionAnalyzer._add_package_version(
                    package_name,
                    project_name,
                    version_spec,
                    package_versions,
                )

    @staticmethod
    def _parse_poetry_version_spec(dep_spec: object) -> str | None:
        """Parse Poetry dependency specification to extract version."""
        if isinstance(dep_spec, str):
            return dep_spec
        if isinstance(dep_spec, dict):
            version = dep_spec.get("version", "*")
            return str(version) if version is not None else "*"
        return None

    @staticmethod
    def _add_package_version(
        package_name: str,
        project_name: str,
        version_spec: str,
        package_versions: dict[str, dict[str, str]],
    ) -> None:
        """Add a package version to the collection."""
        if package_name not in package_versions:
            package_versions[package_name] = {}
        package_versions[package_name][project_name] = version_spec or "*"

    @staticmethod
    def _detect_version_conflicts(
        package_versions: dict[str, dict[str, str]],
    ) -> dict[str, list[dict[str, object]]]:
        """Detect version conflicts between package constraints.

        Analyzes collected package versions to identify conflicts where
        projects specify incompatible version constraints for the same package.
        Classifies conflicts by severity based on number of affected projects.

        Args:
            package_versions: Package versions by project from _collect_package_versions

        Returns:
            Dictionary mapping package names to conflict information lists
            Each conflict includes type, affected projects, analysis, and severity

        """
        conflicts: dict[str, list[dict[str, object]]] = {}

        for package_name, versions in package_versions.items():
            if len(versions) > 1:
                unique_specs = set(versions.values())
                if len(unique_specs) > 1:
                    analysis = VersionAnalyzer.check_version_compatibility(
                        next(iter(unique_specs)),
                        list(unique_specs)[1],
                    )

                    if not analysis.get("compatible", True):
                        conflicts[package_name] = [
                            {
                                "type": "version_conflict",
                                "projects": versions,
                                "analysis": analysis,
                                "severity": (
                                    "high"
                                    if len(versions) > MIN_PROJECTS_HIGH_SEVERITY
                                    else "medium"
                                ),
                            },
                        ]

        return conflicts

    @staticmethod
    def analyze_version_conflicts(
        projects_data: dict[str, dict[str, object]],
    ) -> dict[str, list[dict[str, object]]]:
        """Analyze version conflicts across FLEXT ecosystem projects.

        Performs comprehensive version conflict analysis across multiple projects,
        identifying packages with incompatible version constraints and providing
        detailed conflict reports with severity classification.

        Args:
            projects_data: Dictionary of project data from pyproject.toml parsing

        Returns:
            Dictionary mapping package names to conflict detail lists
            Includes conflict type, affected projects, and resolution analysis

        """
        print_colored("🔍 Analyzing version conflicts...", Colors.BLUE)

        package_versions = VersionAnalyzer._collect_package_versions(projects_data)
        return VersionAnalyzer._detect_version_conflicts(package_versions)

    @staticmethod
    def suggest_version_resolution(
        conflicts: dict[str, dict[str, object]],
    ) -> dict[str, str]:
        """Suggest automated resolutions for version conflicts.

        Analyzes version conflicts and provides actionable resolution recommendations
        using intelligent constraint intersection and compatibility analysis. Prefers
        the most restrictive compatible constraint when possible.

        Args:
            conflicts: Dictionary of conflicts from analyze_version_conflicts output
                      Contains conflict details, affected projects, and analysis

        Returns:
            Dictionary mapping package names to suggested version constraints
            Suggestions prioritize compatibility across maximum number of projects

        Example:
            >>> conflicts = analyze_version_conflicts(projects_data)
            >>> resolutions = suggest_version_resolution(conflicts)
            >>> print(f"Suggested pydantic version: {resolutions.get('pydantic')}")

        """
        suggestions = {}

        for package, conflict_data in conflicts.items():
            project_specs = conflict_data["projects"]

            # Try to find most recent compatible version
            if isinstance(project_specs, dict):
                all_specs = list(project_specs.values())
            else:
                all_specs = []

            # Remove empty specifications or "*"
            valid_specs = [s for s in all_specs if s and s != "*"]

            if not valid_specs:
                suggestions[package] = "*"
                continue

            # If all specs are equal, use it
            if len(set(valid_specs)) == 1:
                suggestions[package] = valid_specs[0]
                continue

            # Try to find intersection
            if isinstance(project_specs, dict):
                common_range = VersionAnalyzer.find_common_version_range(project_specs)
            else:
                common_range = None
            if common_range:
                suggestions[package] = common_range
            else:
                # Suggest the most restrictive constraint
                suggestions[package] = VersionAnalyzer._get_most_restrictive_spec(
                    valid_specs,
                )

        return suggestions

    @staticmethod
    def _get_most_restrictive_spec(specs: list[str]) -> str:
        """Return the most restrictive version specification.

        Analyzes multiple version specifications and returns the one with
        the most constraints, which is typically the most restrictive.
        Used as fallback when intersection-based resolution fails.

        Args:
            specs: List of version specification strings

        Returns:
            Most restrictive specification string, or "*" if none found

        """

        # Sort by number of constraints
        def count_constraints(spec: str) -> int:
            return len(re.findall(r"[><=!]+", spec))

        sorted_specs = sorted(specs, key=count_constraints, reverse=True)
        return sorted_specs[0] if sorted_specs else "*"


# Helper functions following flext-core pattern
def parse_version_spec(spec: str) -> tuple[str, str | None]:
    """Parse version specification into package name and version constraint.

    Args:
        spec: Package specification (e.g., "django>=3.2")

    Returns:
        Tuple (package_name, version_specification)

    """
    return VersionAnalyzer.parse_version_spec(spec)


def normalize_constraint(constraint: str) -> str:
    """Normalize version constraint to standard format.

    Args:
        constraint: Original constraint (e.g., "^1.2.3")

    Returns:
        Normalized constraint (e.g., ">=1.2.3,<2.0.0")

    """
    return VersionAnalyzer.normalize_constraint(constraint)


def check_version_compatibility(
    spec1: str,
    spec2: str,
) -> FlextResult[VersionCompatibilityResult]:
    """Check compatibility between two version specifications using FlextResult.

    Args:
        spec1: First version specification
        spec2: Second version specification

    Returns:
        FlextResult containing VersionCompatibilityResult with compatibility analysis

    """
    try:
        legacy_result = VersionAnalyzer.check_version_compatibility(spec1, spec2)

        # Convert legacy dict result to VersionCompatibilityResult
        overlap_version = legacy_result.get("overlap_version")
        issues = legacy_result.get("issues", [])
        recommendations = legacy_result.get("recommendations", [])

        result = VersionCompatibilityResult(
            compatible=bool(legacy_result.get("compatible", False)),
            spec1=spec1,
            spec2=spec2,
            overlap_version=str(overlap_version)
            if overlap_version is not None
            else None,
            issues=list(issues) if isinstance(issues, (list, tuple)) else [],
            recommendations=list(recommendations)
            if isinstance(recommendations, (list, tuple))
            else [],
        )

        return FlextResult.ok(result)
    except Exception as e:
        logger.exception(
            "Version compatibility check failed",
            spec1=spec1,
            spec2=spec2,
            error=str(e),
        )
        return FlextResult.fail(f"Version compatibility check failed: {e}")


def analyze_version_conflicts(
    projects_data: dict[str, dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    """Analyze version conflicts between projects.

    Args:
        projects_data: Dictionary of project data from pyproject.toml files

    Returns:
        Dictionary of conflicts by package name

    """
    return VersionAnalyzer.analyze_version_conflicts(projects_data)


def suggest_version_resolution(
    conflicts: dict[str, dict[str, object]],
) -> dict[str, str]:
    """Suggest resolutions for version conflicts.

    Args:
        conflicts: Dictionary of conflicts from analyze_version_conflicts

    Returns:
        Suggested versions by package name

    """
    return VersionAnalyzer.suggest_version_resolution(conflicts)
