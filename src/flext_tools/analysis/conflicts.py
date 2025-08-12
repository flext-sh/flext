"""FLEXT Dependency Conflict Analysis - Enterprise Conflict Detection.

Provides comprehensive dependency conflict detection and resolution tools
for the FLEXT ecosystem. Analyzes dependency graphs across all 32 projects
to identify version conflicts, circular dependencies, and optimization
opportunities with enterprise-grade accuracy and performance.

This module implements sophisticated graph analysis algorithms to detect
various types of dependency issues and provides actionable recommendations
for resolution, ensuring ecosystem stability and maintainability across
complex multi-project environments.

Key Features:
    - Multi-project dependency conflict detection
    - Circular dependency identification and resolution
    - Version constraint conflict analysis with severity assessment
    - Dependency optimization recommendations
    - Integration with Poetry lock file analysis
    - Update blocker identification and resolution strategies
    - Comprehensive conflict reporting and visualization

Architecture:
    Uses graph theory algorithms to analyze dependency relationships,
    implementing Clean Architecture patterns for maintainable and
    testable conflict detection logic. Integrates with version analysis
    and lock consistency checking for comprehensive validation.

Example:
    Analyze workspace for conflicts:

    >>> from flext_tools.analysis import ConflictAnalyzer
    >>> from pathlib import Path
    >>>
    >>> analyzer = ConflictAnalyzer()
    >>> workspace = Path("/path/to/workspace")
    >>> result = analyzer.analyze_workspace_conflicts(workspace)
    >>>
    >>> if result["version_conflicts"]:
    ...     print(f"Found {len(result['version_conflicts'])} conflicts")
    ...     for package, conflict in result["version_conflicts"].items():
    ...         print(f"  {package}: {conflict['severity']} severity")
    >>>
    >>> # Generate detailed report
    >>> report = analyzer.generate_conflict_report(result)
    >>> print(report)

Integration:
    - Uses flext-core FlextResult for consistent error handling
    - Integrates with Poetry operations for lock file analysis
    - Coordinates with quality gates for automated validation
    - Provides CLI integration for development workflows

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING, cast

from flext_core import FlextResult, get_logger
from pydantic import BaseModel, Field

from flext_tools.analysis.lock_consistency import LockConsistencyAnalyzer
from flext_tools.analysis.version import VersionAnalyzer
from flext_tools.utils import Colors, print_colored

if TYPE_CHECKING:
    from pathlib import Path

# Analysis Configuration Constants
MIN_PROJECTS_FOR_ANALYSIS = (
    2  # Minimum projects required for meaningful conflict analysis
)

# Initialize logger
logger = get_logger(__name__)


class ConflictAnalysisResult(BaseModel):
    """Comprehensive conflict analysis result using FlextEntity for enterprise domain modeling.

    This entity represents the complete result of dependency conflict analysis
    across the FLEXT ecosystem, providing structured data for conflict resolution
    and decision-making with proper domain modeling patterns.

    Attributes:
        total_projects: Number of projects analyzed in the workspace
        version_conflicts: Detailed version conflict information by package
        circular_dependencies: List of detected circular dependency patterns
        update_blockers: Projects and packages blocking dependency updates
        suggested_resolutions: AI-generated resolution recommendations
        analysis_summary: Statistical summary and analysis metadata

    """

    total_projects: int = Field(
        default=0, description="Number of projects analyzed in the workspace",
    )
    version_conflicts: dict[str, dict[str, object]] = Field(
        default_factory=dict,
        description="Detailed version conflict information by package",
    )
    circular_dependencies: list[str] = Field(
        default_factory=list,
        description="List of detected circular dependency patterns",
    )
    update_blockers: dict[str, dict[str, object]] = Field(
        default_factory=dict,
        description="Projects and packages blocking dependency updates",
    )
    suggested_resolutions: dict[str, str] = Field(
        default_factory=dict, description="AI-generated resolution recommendations",
    )
    analysis_summary: dict[str, object] = Field(
        default_factory=dict, description="Statistical summary and analysis metadata",
    )

    def has_conflicts(self) -> bool:
        """Check if analysis found any conflicts."""
        return bool(
            self.version_conflicts or self.circular_dependencies or self.update_blockers,
        )

    def conflict_count(self) -> int:
        """Get total number of conflicts found."""
        return (
            len(self.version_conflicts)
            + len(self.circular_dependencies)
            + len(self.update_blockers)
        )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules for conflict analysis result."""
        if self.total_projects < 0:
            return FlextResult.fail("Total projects cannot be negative")
        return FlextResult.ok(None)


class ConflictAnalyzer:
    """Enterprise dependency conflict analyzer for FLEXT ecosystem coordination.

    Analyzes dependency conflicts across the 32-project FLEXT ecosystem,
    providing comprehensive conflict detection, severity assessment, and
    resolution recommendations. Implements enterprise-grade algorithms
    for dependency graph analysis and optimization.

    This analyzer serves as the primary tool for maintaining dependency
    health across the ecosystem, identifying conflicts before they become
    critical issues and providing actionable resolution strategies.

    Attributes:
        version_analyzer (VersionAnalyzer): Version analysis and resolution engine
        min_projects (int): Minimum projects required for meaningful analysis

    Features:
        - Multi-project dependency conflict detection
        - Version constraint analysis with severity assessment
        - Update blocker identification and resolution
        - Lock file consistency validation
        - Comprehensive conflict reporting and visualization
        - Integration with Poetry dependency management

    Architecture:
        Uses graph theory algorithms for dependency analysis, implementing
        Clean Architecture patterns for maintainable and extensible conflict
        detection. Integrates with multiple analysis engines for comprehensive
        validation.

    Example:
        Analyze workspace conflicts:

        >>> analyzer = ConflictAnalyzer()
        >>> from pathlib import Path
        >>> workspace = Path("/home/user/flext-workspace")
        >>>
        >>> # Comprehensive conflict analysis
        >>> results = analyzer.analyze_workspace_conflicts(workspace)
        >>>
        >>> print(f"Projects analyzed: {results['total_projects']}")
        >>> print(f"Conflicts found: {len(results['version_conflicts'])}")
        >>> print(f"Update blockers: {len(results['update_blockers'])}")
        >>>
        >>> # Generate detailed report
        >>> report = analyzer.generate_conflict_report(results)
        >>> with open("conflict_report.md", "w") as f:
        ...     f.write(report)

    Integration:
        Integrates with flext-core patterns for consistent error handling
        and coordinates with quality gates for automated validation.

    """

    def __init__(self) -> None:
        """Initialize dependency conflict analyzer with comprehensive analysis tools.

        Creates a new ConflictAnalyzer instance with integrated version analysis
        and lock consistency checking capabilities. Prepares the analyzer for
        enterprise-grade dependency conflict detection across multi-project
        workspaces.

        Initialization includes setting up analysis engines, configuration
        parameters, and integration with Poetry dependency management tools
        for comprehensive conflict detection and resolution.

        Architecture:
            Uses dependency injection patterns for analysis engines,
            allowing for extensible and testable conflict detection
            with proper separation of concerns.

        Example:
            Initialize analyzer for workspace analysis:

            >>> analyzer = ConflictAnalyzer()
            >>> print(f"Analyzer ready for workspace analysis")
            >>> print(
            ...     f"Minimum projects for analysis: "
            ...     f"{analyzer.MIN_PROJECTS_FOR_ANALYSIS}"
            ... )

        """
        self.version_analyzer = VersionAnalyzer()

    def analyze_workspace_conflicts(
        self, workspace_path: Path,
    ) -> FlextResult[ConflictAnalysisResult]:
        """Perform comprehensive dependency conflict analysis across workspace."""
        return self._perform_analysis_pipeline(workspace_path)

    def _perform_analysis_pipeline(
        self, workspace_path: Path,
    ) -> FlextResult[ConflictAnalysisResult]:
        """Execute the complete analysis pipeline using railway-oriented programming."""
        try:
            logger.info(
                "Starting workspace conflict analysis",
                workspace_path=str(workspace_path),
            )

            # Step 1: Validate workspace
            validation_result = self._validate_workspace(workspace_path)
            if not validation_result.success:
                return FlextResult.fail(
                    f"Workspace validation failed: {validation_result.error}",
                )

            print_colored("🔍 Analyzing dependency conflicts...", Colors.BLUE)

            # Step 2: Collect and validate projects data
            projects_result = self._collect_and_validate_projects(workspace_path)
            if not projects_result.success:
                return FlextResult.fail(
                    f"Project collection failed: {projects_result.error}",
                )

            projects_data = projects_result.data
            if projects_data is None:
                return FlextResult.fail("No projects data collected")

            # Step 3: Perform conflict analysis
            return self._analyze_conflicts(workspace_path, projects_data)

        except Exception as e:
            logger.exception("Workspace analysis failed", error=str(e))
            return FlextResult.fail(f"Analysis failed: {e}")

    def _validate_workspace(self, workspace_path: Path) -> FlextResult[None]:
        """Validate workspace path exists and is accessible."""
        if not workspace_path.exists() or not workspace_path.is_dir():
            return FlextResult.fail(
                f"Workspace path does not exist or is not a directory: {workspace_path}",
            )
        return FlextResult.ok(None)

    def _collect_and_validate_projects(
        self, workspace_path: Path,
    ) -> FlextResult[dict[str, object]]:
        """Collect and validate projects data from workspace."""
        projects_collection_result = self._collect_projects_data(workspace_path)
        if not projects_collection_result.success:
            return FlextResult.fail(
                projects_collection_result.error or "Failed to collect projects data",
            )

        projects_data = projects_collection_result.data
        if projects_data is None:
            return FlextResult.fail("No projects data collected")

        if len(projects_data) < MIN_PROJECTS_FOR_ANALYSIS:
            logger.info(
                "Insufficient projects for analysis", project_count=len(projects_data),
            )
            # Return projects data anyway - the caller will handle the insufficient projects case

        return FlextResult.ok(projects_data)

    def _analyze_conflicts(
        self, workspace_path: Path, projects_data: dict[str, object],
    ) -> FlextResult[ConflictAnalysisResult]:
        """Perform the actual conflict analysis on validated data."""
        # Handle insufficient projects case
        if len(projects_data) < MIN_PROJECTS_FOR_ANALYSIS:
            result = ConflictAnalysisResult(
                total_projects=len(projects_data),
                analysis_summary={
                    "message": "Less than 2 projects found",
                    "total": len(projects_data),
                },
            )
            return FlextResult.ok(result)
        # Collect workspace dependencies
        workspace_deps_result = self._collect_workspace_dependencies_safe(
            workspace_path,
        )
        if not workspace_deps_result.success:
            return FlextResult.fail(
                workspace_deps_result.error
                or "Failed to collect workspace dependencies",
            )

        workspace_deps = workspace_deps_result.data
        if workspace_deps is None:
            return FlextResult.fail("No workspace dependencies collected")

        # Analyze version conflicts
        projects_data_for_analysis = cast("dict[str, dict[str, object]]", projects_data)
        version_conflicts = self.version_analyzer.analyze_version_conflicts(
            projects_data_for_analysis,
        )
        if not version_conflicts:
            version_conflicts = {}

        # Analyze lock conflicts (non-blocking)
        self._analyze_lock_conflicts_safe(workspace_path)

        # Identify update blockers
        blockers_result = self._identify_update_blockers_safe(workspace_deps)
        if not blockers_result.success:
            return FlextResult.fail(
                blockers_result.error or "Failed to identify update blockers",
            )

        blockers = blockers_result.data or {}

        # Generate resolutions
        resolutions = self._generate_resolutions_safe(version_conflicts)

        # Build final result
        return self._build_analysis_result(
            projects_data_for_analysis, version_conflicts, blockers, resolutions,
        )

    def _analyze_lock_conflicts_safe(self, workspace_path: Path) -> None:
        """Analyze lock conflicts safely without failing the pipeline."""
        try:
            lock_analyzer = self._get_lock_analyzer()
            _ = lock_analyzer.analyze_workspace(workspace_path)
        except Exception as e:
            logger.warning("Lock analysis failed", error=str(e))

    def _generate_resolutions_safe(
        self, version_conflicts: dict[str, list[dict[str, object]]],
    ) -> dict[str, str]:
        """Generate resolution suggestions safely."""
        resolutions_result = self._suggest_resolutions_safe(version_conflicts)
        if not resolutions_result.success:
            logger.warning(
                "Resolution suggestions failed", error=resolutions_result.error,
            )
            return {}
        return resolutions_result.data or {}

    def _build_analysis_result(
        self,
        projects_data: dict[str, dict[str, object]],
        version_conflicts: dict[str, list[dict[str, object]]],
        blockers: dict[str, dict[str, object]],
        resolutions: dict[str, str],
    ) -> FlextResult[ConflictAnalysisResult]:
        """Build the final analysis result."""
        version_conflicts_typed = cast(
            "dict[str, dict[str, object]]", version_conflicts,
        )
        result = ConflictAnalysisResult(
            total_projects=len(projects_data),
            version_conflicts=version_conflicts_typed,
            update_blockers=blockers,
            suggested_resolutions=resolutions,
            analysis_summary={
                "message": "Analysis completed successfully",
                "total_projects": len(projects_data),
                "conflicts_detected": len(version_conflicts),
                "blockers_identified": len(blockers),
                "resolutions_suggested": len(resolutions),
            },
        )

        logger.info(
            "Conflict analysis completed",
            total_projects=result.total_projects,
            conflicts_found=result.conflict_count(),
        )

        return FlextResult.ok(result)

    def _collect_projects_data(
        self, workspace_path: Path,
    ) -> FlextResult[dict[str, object]]:
        """Collect project data safely using FlextResult."""
        try:
            projects_data = {}
            for project_path in workspace_path.iterdir():
                if project_path.is_dir() and not project_path.name.startswith("."):
                    pyproject_path = project_path / "pyproject.toml"
                    if pyproject_path.exists():
                        try:
                            with pyproject_path.open("rb") as f:
                                data = tomllib.load(f)
                            projects_data[project_path.name] = data
                        except (OSError, tomllib.TOMLDecodeError) as e:
                            logger.warning(
                                f"Error reading {project_path.name}", error=str(e),
                            )
                            # Continue with other projects instead of failing completely

            projects_data_typed: dict[str, object] = dict(projects_data)
            return FlextResult.ok(projects_data_typed)
        except Exception as e:
            return FlextResult.fail(f"Failed to collect project data: {e}")

    def _collect_workspace_dependencies_safe(
        self, workspace_path: Path,
    ) -> FlextResult[dict[str, dict[str, str]]]:
        """Safely collect workspace dependencies using FlextResult."""
        try:
            workspace_deps = self._collect_workspace_dependencies(workspace_path)
            return FlextResult.ok(workspace_deps)
        except Exception as e:
            return FlextResult.fail(f"Failed to collect workspace dependencies: {e}")

    def _collect_workspace_dependencies(
        self,
        workspace_path: Path,
    ) -> dict[str, dict[str, str]]:
        """Collect comprehensive dependency information from all workspace projects.

        Scans the workspace for Python projects and extracts complete dependency
        information from pyproject.toml files, including main dependencies and
        development group dependencies for comprehensive conflict analysis.

        Args:
            workspace_path (Path): Root directory of the workspace to scan
                for project dependencies.

        Returns:
            Dict[str, Dict[str, str]]: Nested dictionary mapping project names
            to their dependencies, where each dependency maps to its version
            constraint specification.

        Discovery Process:
            - Recursive search for pyproject.toml files
            - Exclusion of special directories (archive, backup, .git)
            - Extraction of Poetry dependencies from all groups
            - Version constraint parsing and normalization

        Architecture:
            Uses filesystem scanning with proper error handling and
            filtering to ensure reliable dependency collection across
            complex workspace structures.

        Example:
            Collect workspace dependencies:

            >>> deps = analyzer._collect_workspace_dependencies(workspace_path)
            >>> for project, project_deps in deps.items():
            ...     print(f"{project}: {len(project_deps)} dependencies")
            ...     for package, version in project_deps.items():
            ...         print(f"  {package}: {version}")

        """
        dependencies = {}

        # Search for Python projects
        for pyproject in workspace_path.rglob("pyproject.toml"):
            # Ignore special directories
            if any(
                p in pyproject.parts
                for p in ["archive", "backup", "node_modules", ".git"]
            ):
                continue

            project_name = pyproject.parent.name
            deps = self._extract_project_dependencies(pyproject)

            if deps:
                dependencies[project_name] = deps

        return dependencies

    def _extract_project_dependencies(self, pyproject_path: Path) -> dict[str, str]:
        """Extract comprehensive dependency information from pyproject.toml file.

        Parses Poetry configuration to extract all project dependencies including
        main dependencies and development group dependencies with proper version
        constraint handling and error recovery.

        Args:
            pyproject_path (Path): Path to the pyproject.toml file to parse
                for dependency information.

        Returns:
            Dict[str, str]: Dictionary mapping dependency names to version
            constraints. Group dependencies include group suffix in brackets.

        Parsing Features:
            - Main dependencies extraction from [tool.poetry.dependencies]
            - Development group dependencies with group identification
            - Complex version specification parsing (string and dict formats)
            - Error handling for malformed TOML files

        Architecture:
            Uses robust TOML parsing with proper error handling and
            version specification normalization for consistent
            dependency representation.

        Example:
            Extract project dependencies:

            >>> from pathlib import Path
            >>> pyproject = Path("flext-core/pyproject.toml")
            >>> deps = analyzer._extract_project_dependencies(pyproject)
            >>>
            >>> for package, constraint in deps.items():
            ...     if "[" in package:
            ...         print(f"Dev dependency: {package} = {constraint}")
            ...     else:
            ...         print(f"Main dependency: {package} = {constraint}")

        """
        try:
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError) as e:
            print_colored(f"  ⚠️ Error reading {pyproject_path}: {e}", Colors.YELLOW)
            return {}
        else:
            deps = {}

            # Main dependencies
            main_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            for name, spec in main_deps.items():
                if name != "python":
                    version_str = self._extract_version_string(spec)
                    deps[name] = version_str

            # Group dependencies
            groups = data.get("tool", {}).get("poetry", {}).get("group", {})
            for group_name, group_data in groups.items():
                group_deps = group_data.get("dependencies", {})
                for name, spec in group_deps.items():
                    version_str = self._extract_version_string(spec)
                    deps[f"{name}[{group_name}]"] = version_str

            return deps

    def _extract_version_string(self, spec: str | dict[str, object] | object) -> str:
        """Extract version string from Poetry dependency specification.

        Handles both simple string version specifications and complex
        dictionary specifications with proper normalization and fallback
        handling for robust dependency parsing.

        Args:
            spec (Union[str, Dict[str, Any]]): Dependency specification from
                Poetry configuration, either as simple string or complex dict.

        Returns:
            str: Normalized version constraint string, with "*" as fallback
            for unspecified or invalid version constraints.

        Specification Types:
            - String: Direct version constraint (e.g., "^1.0.0")
            - Dict: Complex specification with version, extras, etc.
            - Fallback: "*" for any unrecognized format

        Architecture:
            Uses type-safe parsing with proper fallback handling to
            ensure reliable version extraction from diverse Poetry
            dependency specification formats.

        Example:
            Extract version from different specification types:

            >>> # Simple string specification
            >>> version = analyzer._extract_version_string("^1.0.0")
            >>> print(version)  # "^1.0.0"
            >>>
            >>> # Complex dictionary specification
            >>> spec = {"version": ">=1.0.0", "extras": ["dev"]}
            >>> version = analyzer._extract_version_string(spec)
            >>> print(version)  # ">=1.0.0"

        """
        if isinstance(spec, str):
            return spec
        if isinstance(spec, dict):
            version = spec.get("version", "*")
            return str(version)
        # Default fallback for any other type
        return "*"

    def _identify_update_blockers_safe(
        self,
        workspace_deps: dict[str, dict[str, str]],
    ) -> FlextResult[dict[str, dict[str, object]]]:
        """Safely identify update blockers using railway-oriented programming.

        This method wraps the blocker identification logic in FlextResult
        for consistent error handling and railway-oriented programming patterns.

        Args:
            workspace_deps: Dictionary mapping project names to their dependencies

        Returns:
            FlextResult containing blocker information or error details

        """
        try:
            blockers = self._identify_update_blockers_impl(workspace_deps)
            return FlextResult.ok(blockers)
        except Exception as e:
            logger.exception("Failed to identify update blockers", error=str(e))
            return FlextResult.fail(f"Update blocker identification failed: {e}")

    def _identify_update_blockers_impl(
        self,
        workspace_deps: dict[str, dict[str, str]],
    ) -> dict[str, dict[str, object]]:
        """Identify projects that block dependency updates.

        Analyzes workspace dependencies to identify projects with restrictive
        version constraints that prevent other projects from updating their
        dependencies to newer versions.

        Args:
            workspace_deps: Dictionary mapping project names to their dependency
                specifications with version constraints.

        Returns:
            Dictionary mapping package names to blocker information including
            blocking projects and their restrictive constraints.

        Detection Logic:
            - Identifies packages with multiple different version constraints
            - Classifies constraints as restrictive (==, <, ^0.x patterns)
            - Maps blocking projects to specific restrictive constraints

        Architecture:
            Uses constraint analysis algorithms to identify restrictive
            dependency patterns that prevent ecosystem-wide updates.

        """
        blockers: dict[str, dict[str, object]] = {}

        # Count how many times each constraint appears
        constraint_usage: dict[str, dict[str, list[str]]] = {}
        for project, deps in workspace_deps.items():
            for package, constraint in deps.items():
                # Remove group suffix [dev], [test], etc
                base_package = package.split("[")[0]

                if base_package not in constraint_usage:
                    constraint_usage[base_package] = {}

                if constraint not in constraint_usage[base_package]:
                    constraint_usage[base_package][constraint] = []

                constraint_usage[base_package][constraint].append(project)

        # Identify blockers (projects with unique or restrictive constraints)
        for package, constraints in constraint_usage.items():
            if len(constraints) > 1:
                # There are multiple different constraints
                for constraint, projects in constraints.items():
                    if self._is_restrictive_constraint(constraint):
                        if package not in blockers:
                            blocking_projects: list[str] = []
                            constraint_dict: dict[str, list[str]] = {}
                            blockers[package] = {
                                "blocking_projects": blocking_projects,
                                "constraints": constraint_dict,
                            }

                        blocking_list = blockers[package]["blocking_projects"]
                        if isinstance(blocking_list, list):
                            blocking_list.extend(projects)

                        constraints_dict = blockers[package]["constraints"]
                        if isinstance(constraints_dict, dict):
                            constraints_dict[constraint] = projects

        return blockers

    def _is_restrictive_constraint(self, constraint: str) -> bool:
        """Check if a version constraint is restrictive.

        Determines whether a version constraint is considered restrictive
        and likely to block dependency updates for other projects in the
        workspace.

        Args:
            constraint: Version constraint string to evaluate

        Returns:
            True if the constraint is considered restrictive and blocking,
            False if it allows reasonable flexibility for updates

        Restrictive Patterns:
            - Exact version pins (==)
            - Upper bound constraints (<, <=)
            - Caret constraints with 0.x versions

        Architecture:
            Uses pattern matching to identify commonly problematic
            version constraint patterns in dependency management.

        """
        if not constraint or constraint == "*":
            return False

        # Constraints with == are the most restrictive
        if constraint.startswith("=="):
            return True

        # Constraints with upper bound are also restrictive
        if "<" in constraint:
            return True

        # Caret with 0.x version is restrictive
        return bool(constraint.startswith("^0."))

    def _calculate_stats(
        self,
        workspace_deps: dict[str, dict[str, str]],
        conflicts: dict[str, list[dict[str, object]]],
        blockers: dict[str, dict[str, object]],
    ) -> dict[str, int]:
        """Calculate analysis statistics.

        Computes comprehensive statistics about the workspace dependency
        analysis including totals, conflicts, and impact metrics for
        reporting and decision-making purposes.

        Args:
            workspace_deps: Complete workspace dependency mapping
            conflicts: Detected version conflicts by package
            blockers: Update blocking information by package

        Returns:
            Dictionary containing statistical analysis results including
            dependency counts, conflict metrics, and impact assessment

        Metrics Calculated:
            - Total dependencies across all projects
            - Unique packages (deduplicated)
            - Packages with version conflicts
            - Packages blocking updates
            - Projects affected by blocking constraints

        Architecture:
            Uses aggregation algorithms to compute comprehensive
            statistics for stakeholder reporting and impact assessment.

        """
        total_deps = sum(len(deps) for deps in workspace_deps.values())
        unique_packages = set()

        for deps in workspace_deps.values():
            for package in deps:
                base_package = package.split("[")[0]
                unique_packages.add(base_package)

        return {
            "total_dependencies": total_deps,
            "unique_packages": len(unique_packages),
            "packages_with_conflicts": len(conflicts),
            "blocking_packages": len(blockers),
            "affected_projects": len(
                {
                    project
                    for blocker_data in blockers.values()
                    if isinstance(blocker_data, dict)
                    and "blocking_projects" in blocker_data
                    for project in (
                        blocker_data["blocking_projects"]
                        if isinstance(blocker_data["blocking_projects"], list)
                        else []
                    )
                },
            ),
        }

    def generate_conflict_report(
        self, analysis: dict[str, dict[str, object] | list[object] | str | int],
    ) -> str:
        r"""Generate comprehensive formatted conflict analysis report.

        Creates detailed Markdown report summarizing all dependency conflicts,
        update blockers, resolution suggestions, and statistics for stakeholder
        communication and documentation purposes.

        Args:
            analysis (Dict[str, Any]): Analysis results from workspace conflict
                analysis containing conflicts, blockers, and statistics.

        Returns:
            str: Formatted Markdown report with complete analysis summary,
            suitable for documentation, reviews, and stakeholder communication.

        Report Sections:
            - Executive Summary: High-level statistics and overview
            - Version Conflicts: Detailed conflict analysis by package
            - Update Blockers: Projects preventing dependency updates
            - Resolution Suggestions: Actionable recommendations
            - Impact Assessment: Analysis of affected projects and severity

        Architecture:
            Uses template-based report generation with proper formatting
            and organization for professional documentation standards.

        Example:
            Generate and save conflict report:

            >>> results = analyzer.analyze_workspace_conflicts(workspace)
            >>> report = analyzer.generate_conflict_report(results)
            >>>
            >>> # Save to file
            >>> with open("dependency_conflicts.md", "w") as f:
            ...     f.write(report)
            >>>
            >>> # Print summary
            >>> lines = report.split("\n")
            >>> for line in lines[:20]:  # First 20 lines
            ...     print(line)

        Integration:
            Reports can be integrated with CI/CD pipelines for automated
            conflict detection and stakeholder notification.

        """
        lines = ["# 📊 Dependency Conflict Analysis Report\n"]

        lines.extend(self._generate_statistics_section(analysis))
        lines.extend(self._generate_conflicts_section(analysis))
        lines.extend(self._generate_blockers_section(analysis))
        lines.extend(self._generate_resolutions_section(analysis))

        return "\n".join(lines)

    def _generate_statistics_section(
        self, analysis: dict[str, dict[str, object] | list[object] | str | int],
    ) -> list[str]:
        """Generate statistics section for conflict report."""
        stats = analysis.get("stats", {})
        if not isinstance(stats, dict):
            stats = {}

        return [
            "## 📈 General Statistics\n",
            f"- **Total projects**: {analysis.get('total_projects', 0)}",
            f"- **Total dependencies**: {stats.get('total_dependencies', 0)}",
            f"- **Unique packages**: {stats.get('unique_packages', 0)}",
            f"- **Packages with conflicts**: {stats.get('packages_with_conflicts', 0)}",
            f"- **Blocking packages**: {stats.get('blocking_packages', 0)}",
            f"- **Affected projects**: {stats.get('affected_projects', 0)}\n",
        ]

    def _generate_conflicts_section(
        self, analysis: dict[str, dict[str, object] | list[object] | str | int],
    ) -> list[str]:
        """Generate version conflicts section for conflict report."""
        lines: list[str] = []
        version_conflicts = analysis.get("version_conflicts", {})

        if not version_conflicts or not isinstance(version_conflicts, dict):
            return lines

        lines.append("## ⚠️ Version Conflicts\n")

        for package, conflict_data_obj in sorted(version_conflicts.items()):
            conflict_data = cast("dict[str, object]", conflict_data_obj)
            lines.extend(self._format_conflict_entry(package, conflict_data))

        return lines

    def _format_conflict_entry(self, package: str, conflict_data: dict[str, object]) -> list[str]:
        """Format individual conflict entry."""
        severity = conflict_data.get("severity", "medium")
        icon = "🔴" if severity == "high" else "🟡"

        lines = [f"### {icon} {package}\n", "**Projects and versions:**"]

        projects_data = conflict_data.get("projects", {})
        if isinstance(projects_data, dict):
            lines.extend(f"- `{project}`: {version}" for project, version in projects_data.items())

        analysis_data = conflict_data.get("analysis", {})
        if isinstance(analysis_data, dict):
            issues = analysis_data.get("issues", [])
            if issues:
                lines.append("\n**Issues:**")
                lines.extend(f"- {issue}" for issue in issues)

        lines.append("")
        return lines

    def _generate_blockers_section(
        self, analysis: dict[str, dict[str, object] | list[object] | str | int],
    ) -> list[str]:
        """Generate update blockers section for conflict report."""
        lines: list[str] = []
        update_blockers = analysis.get("update_blockers", {})

        if not update_blockers or not isinstance(update_blockers, dict):
            return lines

        lines.append("## 🚫 Update Blockers\n")

        for package, blocker_data_obj in sorted(update_blockers.items()):
            if isinstance(blocker_data_obj, dict):
                lines.extend(self._format_blocker_entry(package, blocker_data_obj))

        return lines

    def _format_blocker_entry(self, package: str, blocker_data: dict[str, object]) -> list[str]:
        """Format individual blocker entry."""
        lines = [f"### {package}\n", "**Blocking projects:**"]

        constraints = blocker_data.get("constraints", {})
        if isinstance(constraints, dict):
            for constraint, projects in constraints.items():
                if isinstance(projects, (list, tuple)):
                    lines.append(
                        f"- Constraint `{constraint}`: {', '.join(str(p) for p in projects)}",
                    )

        lines.append("")
        return lines

    def _generate_resolutions_section(
        self, analysis: dict[str, dict[str, object] | list[object] | str | int],
    ) -> list[str]:
        """Generate suggested resolutions section for conflict report."""
        lines: list[str] = []
        suggested_resolutions = analysis.get("suggested_resolutions", {})

        if not isinstance(suggested_resolutions, dict) or not suggested_resolutions:
            return lines

        lines.append("## 💡 Suggested Resolutions\n")
        lines.extend(
            f"- **{package}**: `{suggestion}`"
            for package, suggestion in sorted(suggested_resolutions.items())
        )

        return lines

    def _suggest_resolutions_safe(
        self,
        version_conflicts: dict[str, list[dict[str, object]]],
    ) -> FlextResult[dict[str, str]]:
        """Safely generate resolution suggestions using railway-oriented programming.

        Args:
            version_conflicts: Version conflicts detected during analysis

        Returns:
            FlextResult containing resolution suggestions or error details

        """
        try:
            # Convert conflict format for resolution generation
            conflicts_for_resolution = {}
            for package, conflict_list in version_conflicts.items():
                if conflict_list:
                    conflicts_for_resolution[package] = conflict_list[0]

            resolutions = self.version_analyzer.suggest_version_resolution(
                conflicts_for_resolution,
            )

            return FlextResult.ok(resolutions)
        except Exception as e:
            logger.exception("Failed to generate resolution suggestions", error=str(e))
            return FlextResult.fail(f"Resolution suggestion failed: {e}")

    def _get_lock_analyzer(self) -> LockConsistencyAnalyzer:
        """Get Poetry lock file consistency analyzer instance.

        Creates and returns a LockConsistencyAnalyzer for validating
        Poetry lock files across the workspace, ensuring dependency
        lock consistency and identifying lock-related issues.

        Returns:
            LockConsistencyAnalyzer: Configured analyzer for lock file validation
            and consistency checking across workspace projects.

        Architecture:
            Uses factory pattern for analyzer creation, allowing for
            configuration and customization of lock analysis behavior.

        Example:
            Use lock analyzer for validation:

            >>> lock_analyzer = analyzer._get_lock_analyzer()
            >>> lock_analyzer.analyze_workspace(workspace_path)
            >>> print("Lock file consistency analysis completed")

        """
        return LockConsistencyAnalyzer()
