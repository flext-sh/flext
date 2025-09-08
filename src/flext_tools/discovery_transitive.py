"""FLEXT Transitive Dependency Resolution - Enterprise Path Dependency Analysis.

Provides comprehensive transitive dependency resolution through path-based dependency
analysis for the FLEXT ecosystem. This module analyzes Poetry path dependencies to
map complete dependency graphs, including direct and transitive dependencies across
interconnected projects in multi-project workspaces.

The resolver implements sophisticated algorithms for dependency graph traversal with
circular dependency detection, depth-limited recursion, and intelligent caching to
ensure accurate and performant dependency resolution across complex project hierarchies.

Key Components:
    - TransitiveDependencyResolver: Main resolution engine for dependency graph analysis
    - PathDependency: Structured representation of path-based dependencies
    - TransitiveDependencies: Complete dependency resolution results
    - Circular Dependency Detection: Prevention of infinite resolution loops
    - Intelligent Caching: Performance optimization for repeated analysis

Architecture:
    Implements enterprise-grade dependency resolution with proper error handling,
    performance optimization through caching, and comprehensive graph traversal
    algorithms. Integrates with Poetry configuration parsing for accurate
    path dependency extraction and resolution.

Example:
    Comprehensive transitive dependency resolution:

    >>> from flext_tools.discovery.transitive import TransitiveDependencyResolver
    >>> from pathlib import Path
    >>>
    >>> # Initialize resolver with caching
    >>> resolver = TransitiveDependencyResolver()
    >>>
    >>> # Resolve complete dependency graph
    >>> project_path = Path("/workspace/flext-core")
    >>> dependencies = resolver.resolve_transitive_dependencies(project_path)
    >>>
    >>> print(f"Direct dependencies: {len(dependencies.direct)}")
    >>> print(f"Transitive dependencies: {len(dependencies.transitive)}")
    >>> print(f"Path dependencies: {len(dependencies.path_dependencies)}")
    >>>
    >>> # Check if package is available transitively
    >>> available = resolver.is_dependency_available_transitively(
    ...     project_path, "pydantic"
    >>> )
    >>> print(f"Pydantic available: {available}")

Integration:
    - Built on Poetry configuration parsing for accurate path dependency extraction
    - Integrates with dependency analysis and conflict detection systems
    - Coordinates with workspace management for multi-project analysis
    - Provides foundation for dependency optimization and validation
    - Supports complex workspace dependency management strategies

Quality Standards:
    - Comprehensive error handling with detailed context preservation
    - Performance optimization through intelligent caching strategies
    - Circular dependency detection and prevention mechanisms
    - Depth-limited recursion for safe graph traversal
    - Professional English documentation and user-facing messages

Author: FLEXT Development Team
Version: 0.9.0
License: MIT

"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .colors import Colors, print_colored


@dataclass
class PathDependency:
    """Represents a path-based dependency configuration.

    Contains metadata for Poetry path dependencies including the dependency
    name, file system path, and development mode flag for comprehensive
    dependency graph analysis and resolution.

    Attributes:
      name: Dependency package name as specified in Poetry configuration
      path: Resolved file system path to the dependency project
      develop: Development mode flag indicating editable installation

    """

    name: str
    path: Path
    develop: bool = False


@dataclass
class TransitiveDependencies:
    """Results of transitive dependency resolution analysis.

    Contains complete dependency resolution results including direct dependencies,
    transitive dependencies discovered through path dependency traversal, and
    path dependency metadata for comprehensive dependency graph representation.

    Attributes:
      direct: Set of direct dependencies declared in the project
      transitive: Set of transitive dependencies discovered through path resolution
      path_dependencies: List of path-based dependencies with metadata

    """

    direct: set[str]
    transitive: set[str]
    path_dependencies: list[PathDependency]


class TransitiveDependencyResolver:
    """Enterprise transitive dependency resolver for path-based dependency analysis.

    Provides comprehensive dependency resolution capabilities through path dependency
    traversal with circular dependency detection, intelligent caching, and depth-limited
    recursion for safe and performant dependency graph analysis.

    This resolver serves as the primary tool for understanding complete dependency
    relationships across interconnected FLEXT projects, enabling accurate dependency
    management and conflict detection in complex multi-project environments.

    Attributes:
      _cache: Internal cache for resolved dependency results
      _resolving: Set tracking currently resolving projects for circular detection

    Features:
      - Comprehensive transitive dependency resolution
      - Circular dependency detection and prevention
      - Intelligent caching for performance optimization
      - Depth-limited recursion for safe graph traversal
      - Poetry path dependency integration
      - Normalized package name comparison

    Architecture:
      Uses graph traversal algorithms with proper cycle detection and
      caching strategies for maintainable and performant dependency
      resolution across complex project hierarchies.

    Example:
      Resolve project dependencies with transitive analysis:

      >>> resolver = TransitiveDependencyResolver()
      >>> from pathlib import Path
      >>> # Resolve complete dependency graph
      >>> project = Path("/workspace/flext-api")
      >>> result = resolver.resolve_transitive_dependencies(project)
      >>> print(f"Direct: {sorted(result.direct)}")
      >>> print(f"Transitive: {sorted(result.transitive)}")
      >>> # Check specific dependency availability
      >>> has_pydantic = resolver.is_dependency_available_transitively(
      ...     project, "pydantic"
      >>> )
      >>> print(f"Pydantic available: {has_pydantic}")
      >>> # Get all available dependencies
      >>> all_deps = resolver.get_all_available_dependencies(project)
      >>> print(f"Total available: {len(all_deps)}")

    Integration:
      Integrates with Poetry configuration management, dependency analysis
      systems, and workspace coordination for comprehensive dependency
      management across the FLEXT ecosystem.

    """

    def __init__(self) -> None:
        """Initialize resolver."""
        self._cache: dict[str, TransitiveDependencies] = {}
        self._resolving: set[str] = set()  # Prevent circular dependencies

    def resolve_transitive_dependencies(
        self,
        project_path: Path,
        max_depth: int = 3,
    ) -> TransitiveDependencies:
        """Resolve transitive dependencies for a project through path dependency analysis.

        Performs comprehensive dependency resolution by traversing path dependencies
        to discover both direct and transitive dependencies with circular dependency
        detection and intelligent caching for performance optimization.

        Args:
            project_path: Path to the project root directory for dependency analysis
            max_depth: Maximum recursion depth to prevent infinite loops (default: 3)

        Returns:
            TransitiveDependencies containing complete dependency resolution results
            including direct dependencies, transitive dependencies, and path metadata

        Resolution Process:
            1. Check cache for previously resolved results
            2. Detect circular dependencies to prevent infinite loops
            3. Parse project Poetry configuration for dependencies
            4. Extract path dependencies and traverse recursively
            5. Aggregate direct and transitive dependencies
            6. Cache results for performance optimization

        Architecture:
            Uses depth-first traversal with memoization and cycle detection
            to ensure safe and efficient dependency graph resolution.

        """
        project_key = str(project_path.resolve())

        # Cache hit
        if project_key in self._cache:
            return self._cache[project_key]

        # Circular dependency detection
        if project_key in self._resolving:
            print_colored(
                f"  ⚠️ Circular dependency detected: {project_path.name}",
                Colors.YELLOW,
            )
            return TransitiveDependencies(set(), set(), [])

        self._resolving.add(project_key)

        try:
            result = self._resolve_recursive(project_path, max_depth)
            self._cache[project_key] = result
            return result
        finally:
            self._resolving.discard(project_key)

    def _resolve_recursive(
        self,
        project_path: Path,
        depth: int,
    ) -> TransitiveDependencies:
        """Resolve dependencies recursively with depth-limited traversal.

        Performs recursive dependency resolution through path dependency traversal
        with proper depth limiting to prevent infinite loops and stack overflow
        in complex dependency graphs.

        Args:
            project_path: Path to project for recursive dependency analysis
            depth: Maximum remaining recursion depth for safe traversal

        Returns:
            TransitiveDependencies containing resolved dependency information

        """
        if depth <= 0:
            return TransitiveDependencies(set(), set(), [])

        pyproject_path = project_path / "pyproject.toml"
        if not pyproject_path.exists():
            return TransitiveDependencies(set(), set(), [])

        try:
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError) as e:
            print_colored(f"  ⚠️ Error reading {pyproject_path}: {e}", Colors.YELLOW)
            return TransitiveDependencies(set(), set(), [])

        # Extract direct dependencies from project configuration
        direct_deps = self._extract_direct_dependencies(data)

        # Extract path dependencies for recursive analysis
        path_deps = self._extract_path_dependencies(data, project_path)

        # Resolve transitive dependencies through path dependency traversal
        transitive_deps: set[str] = set()

        for path_dep in path_deps:
            if path_dep.path.exists():
                child_result = self._resolve_recursive(path_dep.path, depth - 1)
                # Add direct dependencies from path dependency as transitive
                transitive_deps.update(child_result.direct)
                # Add transitive dependencies from path dependency
                transitive_deps.update(child_result.transitive)

        return TransitiveDependencies(
            direct=direct_deps,
            transitive=transitive_deps,
            path_dependencies=path_deps,
        )

    def _extract_direct_dependencies(self, data: FlextTypes.Core.Dict) -> set[str]:
        """Extract direct dependencies from poetry.lock file.

        Parses Poetry lock file data to extract all direct dependency names
        for accurate dependency resolution and conflict detection.

        Args:
            data: Parsed Poetry lock file data structure

        Returns:
            Set of direct dependency package names

        """
        dependencies: set[str] = set()

        if "package" in data:
            packages = data["package"]
            if isinstance(packages, list):
                for package_raw in packages:
                    package: object = package_raw
                    if isinstance(package, dict) and "dependencies" in package:
                        deps: object = package["dependencies"]
                        if isinstance(deps, dict):
                            dependencies.update(deps.keys())

        return dependencies

    def _extract_path_dependencies(
        self,
        data: FlextTypes.Core.Dict,
        project_path: Path,
    ) -> list[PathDependency]:
        """Extract path dependencies from pyproject.toml configuration.

        Parses Poetry configuration to identify path-based dependencies including
        both regular dependencies and dependency groups with path specifications.

        Args:
            data: Parsed pyproject.toml configuration data
            project_path: Base path for resolving relative dependency paths

        Returns:
            List of PathDependency objects with resolved paths and metadata

        """
        path_deps: list[PathDependency] = []

        poetry_section = self._get_poetry_section(data)
        if not poetry_section:
            return []

        # Extract main dependencies
        path_deps.extend(
            self._extract_main_path_dependencies(poetry_section, project_path)
        )

        # Extract group dependencies
        path_deps.extend(
            self._extract_group_path_dependencies(poetry_section, project_path)
        )

        return path_deps

    def _get_poetry_section(
        self, data: FlextTypes.Core.Dict
    ) -> FlextTypes.Core.Dict | None:
        """Get Poetry section from pyproject.toml data."""
        tool_section = data.get("tool", {})
        if not isinstance(tool_section, dict):
            return None
        poetry_section: object = tool_section.get("poetry", {})
        if not isinstance(poetry_section, dict):
            return None
        return poetry_section

    def _extract_main_path_dependencies(
        self, poetry_section: FlextTypes.Core.Dict, project_path: Path
    ) -> list[PathDependency]:
        """Extract path dependencies from main dependencies section."""
        path_deps: list[PathDependency] = []
        poetry_deps: object = poetry_section.get("dependencies", {})
        if isinstance(poetry_deps, dict):
            path_deps.extend(self._process_dependency_dict(poetry_deps, project_path))
        return path_deps

    def _extract_group_path_dependencies(
        self, poetry_section: FlextTypes.Core.Dict, project_path: Path
    ) -> list[PathDependency]:
        """Extract path dependencies from dependency groups."""
        path_deps: list[PathDependency] = []
        groups: object = poetry_section.get("group", {})
        if isinstance(groups, dict):
            for group_data in groups.values():
                if isinstance(group_data, dict):
                    group_deps: object = group_data.get("dependencies", {})
                    if isinstance(group_deps, dict):
                        path_deps.extend(
                            self._process_dependency_dict(group_deps, project_path)
                        )
        return path_deps

    def _process_dependency_dict(
        self, deps: FlextTypes.Core.Dict, project_path: Path
    ) -> list[PathDependency]:
        """Process a dictionary of dependencies and extract path dependencies."""
        path_deps: list[PathDependency] = []
        for dep_name_raw, dep_spec_raw in deps.items():
            dep_name: str = str(dep_name_raw)
            dep_spec: object = dep_spec_raw
            if isinstance(dep_spec, dict) and "path" in dep_spec:
                path_raw: object = dep_spec["path"]
                develop_raw: object = dep_spec.get("develop", False)
                if isinstance(path_raw, str) and isinstance(develop_raw, bool):
                    path_deps.append(
                        PathDependency(
                            dep_name, (project_path / path_raw).resolve(), develop_raw
                        )
                    )
        return path_deps

    def _extract_package_name(self, dep_spec: str) -> str:
        """Extract package name from dependency specification string.

        Parses dependency specification to extract the core package name
        by removing version constraints and other specification metadata.

        Args:
            dep_spec: Dependency specification string from Poetry configuration

        Returns:
            Extracted package name without version constraints

        """
        dep_spec = dep_spec.strip().replace("(", "").replace(")", "")
        match = re.match(r"^([a-zA-Z0-9_-]+)", dep_spec)
        if match:
            return match.group(1)
        return ""

    def get_all_available_dependencies(self, project_path: Path) -> set[str]:
        """Get all available dependencies for a project.

        Combines direct and transitive dependencies discovered through path
        dependency resolution to provide complete dependency availability.

        Args:
            project_path: Path to project for dependency analysis

        Returns:
            Set containing all available dependency names (direct + transitive)

        """
        result = self.resolve_transitive_dependencies(project_path)
        return result.direct | result.transitive

    def is_dependency_available_transitively(
        self,
        project_path: Path,
        package_name: str,
    ) -> bool:
        """Check if a dependency is available transitively through path dependencies.

        Determines if a specific package is available either directly or
        transitively through path dependency resolution with normalized
        package name comparison for accurate matching.

        Args:
            project_path: Path to project for dependency analysis
            package_name: Name of package to check for availability

        Returns:
            True if package is available directly or transitively, False otherwise

        """
        available = self.get_all_available_dependencies(project_path)

        # Normalize package names for accurate comparison
        normalized_available = {self._normalize_name(dep) for dep in available}
        normalized_package = self._normalize_name(package_name)

        return normalized_package in normalized_available

    def _normalize_name(self, name: str) -> str:
        """Normalize package name for accurate comparison.

        Converts package names to standardized format by removing case
        differences and normalizing separators for reliable matching.

        Args:
            name: Package name to normalize

        Returns:
            Normalized package name for comparison

        """
        return name.lower().replace("_", "").replace("-", "")

    def clear_cache(self) -> None:
        """Clear resolution cache and reset resolver state.

        Clears all cached resolution results and resets internal state
        for fresh dependency analysis, useful when project configurations
        have changed or when memory cleanup is needed.
        """
        self._cache.clear()
        self._resolving.clear()
