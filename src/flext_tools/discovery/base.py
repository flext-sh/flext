"""FLEXT Dependency Discovery - Enterprise Dependency Analysis Base.

Provides comprehensive dependency discovery capabilities for Python projects
across the FLEXT ecosystem with support for runtime, development, and test
dependency analysis. This module implements sophisticated dependency resolution
through multiple discovery strategies including Python import analysis,
configuration file parsing, and transitive dependency resolution.

The discovery system implements enterprise-grade dependency analysis with
proper categorization, conflict detection, and optimization for maintaining
accurate dependency management across complex multi-project environments.

Key Components:
    - DependencyDiscovery: Main dependency analysis coordination engine
    - Multi-Strategy Discovery: Python imports, configuration files, transitive
        resolution
    - Dependency Categorization: Runtime, development, and test dependency
        classification
    - Transitive Resolution: Automatic transitive dependency detection and optimization
    - Package Normalization: Intelligent package name normalization and matching

Architecture:
    Implements Clean Architecture patterns with proper separation between
    discovery strategies, dependency analysis, and result aggregation for
    maintainable and extensible dependency management systems.

Example:
    Comprehensive project dependency discovery:

    >>> from flext_tools.discovery.base import DependencyDiscovery
    >>> from pathlib import Path
    >>>
    >>> # Initialize discovery engine with transitive resolution
    >>> discovery = DependencyDiscovery(resolve_transitive=True)
    >>>
    >>> # Discover project dependencies with categorization
    >>> project_path = Path("/workspace/flext-core")
    >>> dependencies = discovery.discover_project_dependencies(
    ...     project_path,
    ...     include_dev=True,
    ...     include_test=True
    >>> )
    >>>
    >>> print(f"Runtime dependencies: {len(dependencies['runtime'])}")
    >>> print(f"Development dependencies: {len(dependencies['dev'])}")
    >>> print(f"Test dependencies: {len(dependencies['test'])}")
    >>>
    >>> # Review specific dependency categories
    >>> for category, deps in dependencies.items():
    ...     if deps:
    ...         print(f"{category.title()}: {sorted(deps)}")

Integration:
    - Built on Poetry configuration parsing and Python import analysis
    - Integrates with transitive dependency resolution for optimization
    - Coordinates with dependency management and quality assurance systems
    - Supports PEP 621 and Poetry configuration standards
    - Provides foundation for automated dependency management

Quality Standards:
    - Comprehensive error handling with detailed context preservation
    - Performance optimization for large project analysis
    - Configurable discovery parameters and dependency categories
    - Integration with dependency validation and security scanning
    - Professional English documentation and user-facing messages

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

import re
import tomllib
from pathlib import Path

from flext_tools.discovery.config import ConfigFileDiscovery
from flext_tools.discovery.python import PythonImportDiscovery
from flext_tools.discovery.transitive import TransitiveDependencyResolver
from flext_tools.utils import (
    Colors,
    get_stdlib_modules,
    print_colored,
)


class DependencyDiscovery:
    """Enterprise dependency discovery engine for comprehensive project analysis.

    Provides sophisticated dependency discovery capabilities through multiple
    analysis strategies including Python import analysis, configuration file
    parsing, and transitive dependency resolution with intelligent categorization
    and optimization for maintaining accurate dependency management.

    This discovery engine serves as the primary tool for understanding project
    dependency requirements, enabling accurate dependency management, conflict
    detection, and optimization across the FLEXT ecosystem.

    Attributes:
        stdlib_modules: Set of Python standard library modules for filtering
        python_discovery: Python import analysis engine
        config_discovery: Configuration file dependency discovery
        resolve_transitive: Flag for enabling transitive dependency resolution
        transitive_resolver: Optional transitive dependency resolver

    Features:
        - Multi-strategy dependency discovery and analysis
        - Intelligent dependency categorization (runtime, dev, test)
        - Transitive dependency resolution and optimization
        - Package name normalization and variation matching
        - PEP 621 and Poetry configuration support
        - Installed dependency filtering and conflict detection

    Architecture:
        Uses coordinated discovery strategies with proper error handling
        and performance optimization for reliable dependency analysis
        across complex project hierarchies.

    Example:
        Initialize and execute comprehensive dependency discovery:

        >>> discovery = DependencyDiscovery(resolve_transitive=True)
        >>> from pathlib import Path
        >>> # Discover complete project dependencies
        >>> project = Path("/workspace/flext-api")
        >>> deps = discovery.discover_project_dependencies(
        ...     project,
        ...     include_dev=True,
        ...     include_test=True
        >>> )
        >>> # Analyze dependency requirements
        >>> total_deps = sum(len(category_deps) for category_deps in deps.values())
        >>> print(f"Total dependencies discovered: {total_deps}")
        >>> # Review category-specific dependencies
        >>> for category, category_deps in deps.items():
        ...     if category_deps:
        ...         print(
        ...             f"{category.title()} ({len(category_deps)}): "
        ...             f"{sorted(category_deps)}"
        ...         )

    Integration:
        Integrates with Python import analysis, configuration parsing, and
        transitive dependency resolution for comprehensive dependency
        management across the FLEXT ecosystem.

    """

    def __init__(self, *, resolve_transitive: bool = True) -> None:
        self.stdlib_modules = get_stdlib_modules()
        self.python_discovery = PythonImportDiscovery(self.stdlib_modules)
        self.config_discovery = ConfigFileDiscovery()
        self.resolve_transitive = resolve_transitive
        if resolve_transitive:
            self.transitive_resolver = TransitiveDependencyResolver()

    def discover_project_dependencies(
        self,
        project_path: Path,
        *,
        include_dev: bool = True,
        include_test: bool = True,
    ) -> dict[str, set[str]]:
        """Discover all project dependencies with comprehensive categorization.

        Performs complete dependency analysis using multiple discovery strategies
        including Python import analysis, configuration file parsing, and transitive
        dependency resolution with intelligent filtering and optimization.

        Args:
            project_path: Path to project root directory for dependency analysis
            include_dev: Include development dependencies in analysis results
            include_test: Include test dependencies in analysis results

        Returns:
            Dictionary containing categorized dependencies:
            - runtime: Required runtime dependencies for application execution
            - dev: Development dependencies for development workflow
            - test: Test dependencies for testing and quality assurance

        Discovery Process:
            1. Installed Dependency Analysis: Identify currently installed dependencies
            2. Python Import Discovery: Analyze Python imports and usage patterns
            3. Configuration Discovery: Parse pyproject.toml and other config files
            4. Result Combination: Merge discovery results with proper categorization
            5. Transitive Resolution: Optimize dependencies through transitive analysis
            6. Filtering: Remove already installed dependencies from results

        Architecture:
            Uses parallel discovery strategies with proper error handling and
            performance optimization to ensure comprehensive dependency analysis
            without impacting project functionality.

        """
        print_colored(f"🔍 Analyzing project: {project_path.name}", Colors.BLUE)

        # Get currently installed dependencies for filtering
        installed = self.get_installed_dependencies(project_path)
        print_colored(f"  📦 Installed dependencies: {len(installed)}", Colors.CYAN)

        # Discover Python import dependencies
        python_deps = self.python_discovery.discover(project_path, installed)

        # Discover configuration file dependencies
        config_deps = self.config_discovery.discover_dependencies(
            project_path,
            installed,
        )

        # Combine discovery results with proper categorization
        result = {
            "runtime": (
                python_deps.get("runtime", set()) | config_deps.get("runtime", set())
            ),
            "test": set(),
            "dev": set(),
        }

        if include_test:
            result["test"] = python_deps.get("test", set()) | config_deps.get(
                "test",
                set(),
            )

        if include_dev:
            result["dev"] = config_deps.get("dev", set())

        # OPTIMIZATION: Remove transitive dependencies (optional)
        if self.resolve_transitive and hasattr(self, "transitive_resolver"):
            available_transitive = (
                self.transitive_resolver.get_all_available_dependencies(project_path)
            )
            print_colored(
                f"  🔗 Transitive dependencies: {len(available_transitive)}",
                Colors.CYAN,
            )

            # Remove dependencies that are available transitively
            for category, deps in result.items():
                original_count = len(deps)
                result[category] = {
                    dep
                    for dep in deps
                    if not self._is_dependency_available_transitively(
                        dep,
                        available_transitive,
                    )
                }
                removed_count = original_count - len(result[category])
                if removed_count > 0:
                    print_colored(
                        f"    ✓ {removed_count} transitive removed from {category}",
                        Colors.GREEN,
                    )

        # Remove already installed dependencies from results
        for category, deps in result.items():
            result[category] = {
                dep for dep in deps if not self._is_installed(dep, installed)
            }

        return result

    def get_installed_dependencies(self, project_path: Path) -> set[str]:
        """Get list of dependencies already installed in the project.

        Parses project configuration files to identify currently installed
        dependencies including PEP 621 and Poetry configurations with
        comprehensive package name normalization for accurate matching.

        Args:
            project_path: Path to project root directory

        Returns:
            Set of normalized package names for installed dependencies

        """
        installed: set[str] = set()
        pyproject_path = project_path / "pyproject.toml"

        if not pyproject_path.exists():
            return installed

        try:
            with Path(pyproject_path).open("rb") as f:
                data = tomllib.load(f)

            # CRITICAL SUPPORT: PEP 621 (project.dependencies) configuration
            pep621_deps = data.get("project", {}).get("dependencies", [])
            if pep621_deps:
                print_colored(
                    f"  🔍 PEP 621 detected: {len(pep621_deps)} dependencies",
                    Colors.CYAN,
                )
                for dep_spec in pep621_deps:
                    # Extract package name from specification
                    # (e.g.: "pydantic>=2.0.0" -> "pydantic")
                    dep_name = self._extract_package_name(dep_spec)
                    if dep_name and dep_name != "python":
                        self._add_package_variations(installed, dep_name)

            # Poetry main dependencies
            poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            for dep_name in poetry_deps:
                if dep_name != "python":
                    self._add_package_variations(installed, dep_name)

            # Poetry group dependencies
            groups = data.get("tool", {}).get("poetry", {}).get("group", {})
            for group_data in groups.values():
                group_deps = group_data.get("dependencies", {})
                for dep_name in group_deps:
                    self._add_package_variations(installed, dep_name)
        except (OSError, tomllib.TOMLDecodeError, KeyError) as e:
            print_colored(f"  ⚠️ Error reading pyproject.toml: {e}", Colors.YELLOW)

        return installed

    def _is_installed(self, package: str, installed: set[str]) -> bool:
        """Check if a package is already installed.

        Performs comprehensive package name matching using multiple name
        variations to account for different naming conventions and ensure
        accurate installed dependency detection.

        Args:
            package: Package name to check for installation
            installed: Set of installed package names

        Returns:
            True if package is already installed, False otherwise

        """
        variations = {
            package,
            package.lower(),
            package.replace("_", "-"),
            package.replace("-", "_"),
            self._normalize_name(package),
        }
        return any(var in installed for var in variations)

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

    def _extract_package_name(self, dep_spec: str) -> str:
        """Extract package name from PEP 621 dependency specification.

        Parses dependency specifications to extract the core package name
        by removing version constraints, extras, and other specification metadata.

        Args:
            dep_spec: Dependency specification string from PEP 621 configuration

        Returns:
            Extracted package name without version constraints or extras

        Examples:
            "pydantic>=2.0.0" -> "pydantic"
            "fastapi (>=0.116.1,<0.117.0)" -> "fastapi"
            "passlib[bcrypt]>=1.7.4" -> "passlib"

        """
        # Remove extra spaces and parentheses
        dep_spec = dep_spec.strip().replace("(", "").replace(")", "")

        # Extract name before any version operator or extra specification
        match = re.match(r"^([a-zA-Z0-9_-]+)", dep_spec)
        if match:
            return match.group(1)
        return ""

    def _add_package_variations(self, installed: set[str], dep_name: str) -> None:
        """Add all variations of a package name to the installed set.

        Generates multiple name variations to account for different naming
        conventions and ensure comprehensive installed dependency matching.

        Args:
            installed: Set to add package name variations to
            dep_name: Base package name to generate variations for

        """
        installed.add(dep_name)
        installed.add(dep_name.lower())
        installed.add(dep_name.replace("-", "_"))
        installed.add(dep_name.replace("_", "-"))

    def _is_dependency_available_transitively(
        self,
        package: str,
        available_transitive: set[str],
    ) -> bool:
        """Check if a dependency is available transitively through path dependencies.

        Determines if a specific package is available through transitive dependency
        resolution with normalized package name comparison for accurate matching.

        Args:
            package: Package name to check for transitive availability
            available_transitive: Set of packages available transitively

        Returns:
            True if package is available transitively, False otherwise

        """
        variations = {
            package,
            package.lower(),
            package.replace("_", "-"),
            package.replace("-", "_"),
            self._normalize_name(package),
        }

        # Normalize transitive dependencies for accurate comparison
        normalized_transitive = {
            self._normalize_name(dep) for dep in available_transitive
        }

        return any(
            self._normalize_name(var) in normalized_transitive for var in variations
        )
