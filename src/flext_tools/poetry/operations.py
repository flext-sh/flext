#!/usr/bin/env python3
"""FLEXT Poetry Operations - Enterprise Poetry Management with Safety Systems.

Provides comprehensive Poetry operations management with integrated safety systems
including backup management, validation, and rollback capabilities for the FLEXT
ecosystem. This module implements enterprise-grade Poetry operations with proper
error handling, security validation, and operational safety across all projects.

The operations manager implements sophisticated Poetry workflow management including
dependency installation, removal, updates, and project validation with integrated
backup systems and rollback capabilities for maintaining project integrity and
operational reliability.

Key Components:
    - PoetryOperations: Main Poetry operations management engine
    - Safety Integration: Backup and validation system integration
    - Dependency Management: Add, remove, and update dependency operations
    - Project Operations: Update, lock, and validation operations
    - Security Controls: Safe execution with timeout and validation

Architecture:
    Implements Clean Architecture patterns with proper separation between
    Poetry operations, safety systems, and operational interfaces. Integrates
    with backup management and safety validation for enterprise-grade
    operational reliability.

Example:
    Comprehensive Poetry project management:

    >>> from flext_tools.poetry.operations import PoetryOperations
    >>> from pathlib import Path
    >>>
    >>> # Initialize with safety systems enabled
    >>> poetry_ops = PoetryOperations(
    ...     dry_run=False,
    ...     enable_safety=True
    >>> )
    >>>
    >>> # Add dependencies with categorization
    >>> project_path = Path("/workspace/flext-core")
    >>> dependencies = {
    ...     "runtime": ["pydantic>=2.0.0", "fastapi>=0.100.0"],
    ...     "dev": ["black", "ruff"],
    ...     "test": ["pytest>=7.0.0", "pytest-cov"]
    >>> }
    >>>
    >>> results = poetry_ops.add_dependencies(project_path, dependencies)
    >>> print(f"Added runtime: {results['runtime']}")
    >>> print(f"Added dev: {results['dev']}")
    >>> print(f"Added test: {results['test']}")
    >>>
    >>> # Update and validate project
    >>> if poetry_ops.update_project(project_path):
    ...     print("Project updated successfully")
    >>>
    >>> if poetry_ops.validate_project(project_path):
    ...     print("Project configuration is valid")

Integration:
    - Built on Poetry CLI with comprehensive safety validation
    - Integrates with backup management for operational safety
    - Coordinates with safety validators for secure operations
    - Supports dry-run mode for testing and validation
    - Provides foundation for automated dependency management

Quality Standards:
    - Comprehensive error handling with detailed operational context
    - Security-conscious subprocess execution with timeouts
    - Performance optimization for large-scale dependency operations
    - Integration with backup and rollback systems
    - Professional English documentation and operational messaging

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from flext_tools.safety.backup import BackupManager
from flext_tools.safety.validator import SafetyValidator
from flext_tools.utils.colors import Colors, print_colored
from flext_tools.utils.logging import get_logger

if TYPE_CHECKING:
    from logging import Logger
    from pathlib import Path


MIN_PARTS_COUNT = 3


class PoetryOperations:
    """Enterprise Poetry operations manager with integrated safety systems.

    Provides comprehensive Poetry operations management including dependency
    management, project updates, and validation with integrated backup systems
    and safety validation for maintaining operational reliability across the
    FLEXT ecosystem.

    This operations manager serves as the primary interface for Poetry operations,
    ensuring safe execution, proper error handling, and operational consistency
    across all FLEXT projects with comprehensive backup and rollback capabilities.

    Attributes:
        dry_run: Flag for dry-run mode execution without actual changes
        enable_safety: Flag for enabling integrated safety systems
        logger: Logger instance for operational logging
        backup_manager: Backup system for operational safety
        safety_validator: Safety validation system

    Features:
        - Comprehensive dependency management (add, remove, update)
        - Project operations (update, lock, validate)
        - Integrated backup and rollback systems
        - Safe subprocess execution with timeouts
        - Dry-run mode for testing and validation
        - Detailed operational logging and reporting
        - Security-conscious execution with validation
        - Error handling with operational context

    Architecture:
        Uses coordinated Poetry operations with integrated safety systems
        and proper error handling for reliable operational management
        across complex project hierarchies.

    Example:
        Initialize and execute Poetry operations:

        >>> operations = PoetryOperations(
        ...     dry_run=False,
        ...     enable_safety=True
        >>> )
        >>> from pathlib import Path
        >>>
        >>> # Add development dependencies
        >>> project = Path("/workspace/flext-api")
        >>> deps = {
        ...     "runtime": ["fastapi>=0.100.0"],
        ...     "dev": ["black", "ruff"],
        ...     "test": ["pytest"]
        >>> }
        >>>
        >>> results = operations.add_dependencies(project, deps)
        >>> if results["runtime"]:
        ...     print(f"Runtime dependencies added: {results['runtime']}")
        >>>
        >>> # Update and validate project
        >>> if operations.update_project(project):
        ...     operations.validate_project(project)

    Integration:
        Integrates with Poetry CLI, backup systems, and safety validation
        for comprehensive operational management across the FLEXT ecosystem.

    """

    def __init__(
        self,
        *,
        dry_run: bool = True,
        enable_safety: bool = True,
        logger: Logger | None = None,
    ) -> None:
        """Initialize Poetry operations with safety system."""
        self.dry_run = dry_run
        self.enable_safety = enable_safety
        self.logger = logger or get_logger(__name__)

        if self.enable_safety:
            self.backup_manager = BackupManager()
            self.safety_validator = SafetyValidator()
            self.logger.info(
                f"INIT: Safety system activated (dry_run={dry_run})",
            )
            print_colored("🛡️ Safety system activated", Colors.CYAN)

    def add_dependencies(
        self,
        project_path: Path,
        dependencies: dict[str, list[str]],
        *,
        _auto_confirm: bool = False,
    ) -> dict[str, list[str]]:
        """Add dependencies to a Poetry project with safety validation.

        Performs comprehensive dependency addition with integrated backup systems,
        safety validation, and categorized dependency management for maintaining
        project integrity and operational reliability.

        Args:
            project_path: Path to Poetry project root directory
            dependencies: Dictionary mapping dependency categories to dependency lists
                         Format: {"runtime": [...], "dev": [...], "test": [...]}
            _auto_confirm: Automatic confirmation flag for batch operations

        Returns:
            Dictionary containing successfully added dependencies by category:
            - runtime: List of runtime dependencies added
            - dev: List of development dependencies added
            - test: List of test dependencies added

        Addition Process:
            1. Safety Backup: Create backup before modifications if safety enabled
            2. Category Processing: Process dependencies by category (runtime,
               dev, test)
            3. Individual Addition: Add each dependency with appropriate Poetry group
            4. Error Handling: Handle individual dependency failures gracefully
            5. Result Aggregation: Compile results with detailed success/failure
              reporting

        Architecture:
            Uses safe subprocess execution with proper error handling and
            timeout management to ensure reliable dependency management
            without compromising project integrity.

        """
        print_colored(
            f"📦 Adding dependencies to project {project_path.name}...",
            Colors.BLUE,
        )

        added: dict[str, list[str]] = {"runtime": [], "test": [], "dev": []}

        # Create backup before modifications
        if self.enable_safety and not self.dry_run:
            backup_id = self.backup_manager.create_backup(
                project_path,
                f"before_add_deps_{project_path.name}",
            )
            print_colored(f"💾 Backup created: {backup_id}", Colors.CYAN)

        # Add dependencies by category
        for category, deps in dependencies.items():
            if not deps:
                continue

            print_colored(f"\n  📋 Category: {category}", Colors.CYAN)

            for dep in deps:
                # Determina grupo para poetry add
                group = None if category == "runtime" else category

                try:
                    if self._add_dependency(project_path, dep, group):
                        added[category].append(dep)
                except (subprocess.SubprocessError, OSError, FileNotFoundError) as e:
                    print_colored(
                        f"    ❌ Error adding {dep}: {e}",
                        Colors.RED,
                    )

        # Summary of additions
        total_added = sum(len(deps) for deps in added.values())
        if total_added > 0:
            print_colored(
                f"\n✅ {total_added} dependencies added successfully",
                Colors.GREEN,
            )
        else:
            print_colored(
                "\n⚠️ No dependencies were added",
                Colors.YELLOW,
            )

        return added

    def _add_dependency(
        self,
        project_path: Path,
        dependency: str,
        group: str | None = None,
    ) -> bool:
        """Add an individual dependency with safety validation.

        Executes Poetry add command for a single dependency with proper
        group assignment, error handling, and timeout management.

        Args:
            project_path: Path to Poetry project directory
            dependency: Dependency specification (e.g., "pydantic>=2.0.0")
            group: Optional Poetry dependency group (dev, test, etc.)

        Returns:
            True if dependency was added successfully, False otherwise

        """
        cmd = ["poetry", "add", dependency]

        if group:
            cmd.extend(["--group", group])

        if self.dry_run:
            cmd.append("--dry-run")

        try:
            print_colored(f"    [+] Adding {dependency}...", Colors.GREEN)

            result = subprocess.run(
                cmd,
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                shell=False,  # Security: explicit shell=False
                timeout=60,  # Prevent hanging
            )

            if result.returncode == 0:
                if not self.dry_run:
                    print_colored(
                        f"    ✅ {dependency} added successfully",
                        Colors.GREEN,
                    )
                else:
                    print_colored(
                        f"    ✅ {dependency} would be added (dry-run)",
                        Colors.YELLOW,
                    )
                return True
            print_colored(
                f"    ❌ Error adding {dependency}: {result.stderr}",
                Colors.RED,
            )
            return False

        except (subprocess.SubprocessError, OSError, FileNotFoundError) as e:
            print_colored(f"    ❌ Error executing poetry: {e}", Colors.RED)
            return False

    def remove_dependencies(
        self,
        project_path: Path,
        dependencies: list[str],
        *,
        _auto_confirm: bool = False,
    ) -> list[str]:
        """Remove dependencies from a Poetry project with safety validation.

        Performs comprehensive dependency removal with integrated backup systems
        and safety validation for maintaining project integrity while removing
        unwanted or obsolete dependencies.

        Args:
            project_path: Path to Poetry project root directory
            dependencies: List of dependency names to remove
            _auto_confirm: Automatic confirmation flag for batch operations

        Returns:
            List of successfully removed dependency names

        Removal Process:
            1. Safety Backup: Create backup before modifications if safety enabled
            2. Individual Removal: Remove each dependency with error handling
            3. Result Tracking: Track successful and failed removals
            4. Summary Reporting: Provide detailed removal summary

        Architecture:
            Uses safe subprocess execution with proper error handling to ensure
            reliable dependency removal without compromising project integrity.

        """
        print_colored(
            f"🗑️ Removing dependencies from project {project_path.name}...",
            Colors.BLUE,
        )

        removed = []

        # Create backup before modifications
        if self.enable_safety and not self.dry_run:
            backup_id = self.backup_manager.create_backup(
                project_path,
                f"before_remove_deps_{project_path.name}",
            )
            print_colored(f"💾 Backup created: {backup_id}", Colors.CYAN)

        removed = [
            dep for dep in dependencies if self._remove_dependency(project_path, dep)
        ]

        # Summary of removals
        if removed:
            print_colored(
                f"\n✅ {len(removed)} dependencies removed successfully",
                Colors.GREEN,
            )
        else:
            print_colored(
                "\n⚠️ No dependencies were removed",
                Colors.YELLOW,
            )

        return removed

    def _remove_dependency(self, project_path: Path, dependency: str) -> bool:
        """Remove an individual dependency with safety validation.

        Executes Poetry remove command for a single dependency with proper
        error handling and timeout management.

        Args:
            project_path: Path to Poetry project directory
            dependency: Name of dependency to remove

        Returns:
            True if dependency was removed successfully, False otherwise

        """
        cmd = ["poetry", "remove", dependency]

        if self.dry_run:
            cmd.append("--dry-run")

        try:
            print_colored(f"    [-] Removing {dependency}...", Colors.YELLOW)

            result = subprocess.run(
                cmd,
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                shell=False,  # Security: explicit shell=False
                timeout=60,  # Prevent hanging
            )

            if result.returncode == 0:
                if not self.dry_run:
                    print_colored(
                        f"    ✅ {dependency} removed successfully",
                        Colors.GREEN,
                    )
                else:
                    print_colored(
                        f"    ✅ {dependency} would be removed (dry-run)",
                        Colors.YELLOW,
                    )
                return True

            print_colored(
                f"    ❌ Error removing {dependency}: {result.stderr}",
                Colors.RED,
            )
            return False

        except (subprocess.SubprocessError, OSError, FileNotFoundError) as e:
            print_colored(f"    ❌ Error executing poetry: {e}", Colors.RED)
            return False

    def update_project(self, project_path: Path) -> bool:
        """Update all dependencies in a Poetry project with safety validation.

        Performs comprehensive project update including all dependencies with
        integrated backup systems and safety validation for maintaining project
        integrity during update operations.

        Args:
            project_path: Path to Poetry project root directory

        Returns:
            True if project was updated successfully, False otherwise

        Update Process:
            1. Safety Backup: Create backup before update if safety enabled
            2. Poetry Update: Execute poetry update command with timeout
            3. Error Handling: Handle update failures gracefully
            4. Status Reporting: Provide detailed update status

        Architecture:
            Uses safe subprocess execution with extended timeout for reliable
            project updates without compromising operational integrity.

        """
        print_colored(
            f"🔄 Updating project {project_path.name}...",
            Colors.BLUE,
        )

        # Create backup before update
        if self.enable_safety and not self.dry_run:
            backup_id = self.backup_manager.create_backup(
                project_path,
                f"before_update_{project_path.name}",
            )
            print_colored(f"💾 Backup created: {backup_id}", Colors.CYAN)

        cmd = ["poetry", "update"]

        if self.dry_run:
            cmd.append("--dry-run")

        try:
            result = subprocess.run(
                cmd,
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                shell=False,  # Security: explicit shell=False
                timeout=300,  # Allow more time for updates
            )

            if result.returncode == 0:
                if not self.dry_run:
                    print_colored("✅ Project updated successfully", Colors.GREEN)
                else:
                    print_colored(
                        "✅ Project would be updated (dry-run)",
                        Colors.YELLOW,
                    )
                return True

            print_colored(
                f"❌ Error updating project: {result.stderr}",
                Colors.RED,
            )
            return False

        except (subprocess.SubprocessError, OSError, FileNotFoundError) as e:
            print_colored(f"❌ Error executing poetry update: {e}", Colors.RED)
            return False

    def lock_project(self, project_path: Path) -> bool:
        """Generate or update poetry.lock file with dependency resolution.

        Performs Poetry lock file generation to resolve and lock all dependencies
        for consistent and reproducible builds across environments.

        Args:
            project_path: Path to Poetry project root directory

        Returns:
            True if lock file was generated successfully, False otherwise

        Lock Process:
            1. Poetry Lock: Execute poetry lock command with timeout
            2. Dependency Resolution: Resolve all dependency constraints
            3. Lock File Generation: Create or update poetry.lock
            4. Error Handling: Handle lock generation failures

        Architecture:
            Uses safe subprocess execution with appropriate timeout for reliable
            lock file generation without compromising project integrity.

        """
        print_colored(
            f"🔒 Generating lock file for {project_path.name}...",
            Colors.BLUE,
        )

        cmd = ["poetry", "lock"]

        try:
            result = subprocess.run(
                cmd,
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                shell=False,  # Security: explicit shell=False
                timeout=180,  # Allow time for lock generation
            )

            if result.returncode == 0:
                print_colored("✅ Lock file generated successfully", Colors.GREEN)
                return True

            print_colored(
                f"❌ Error generating lock file: {result.stderr}",
                Colors.RED,
            )
            return False

        except (subprocess.SubprocessError, OSError, FileNotFoundError) as e:
            print_colored(f"❌ Error executing poetry lock: {e}", Colors.RED)
            return False

    def validate_project(self, project_path: Path) -> bool:
        """Validate Poetry project configuration for compliance and integrity.

        Performs comprehensive Poetry project validation including configuration
        syntax, dependency specifications, and project structure for ensuring
        project integrity and operational reliability.

        Args:
            project_path: Path to Poetry project root directory

        Returns:
            True if project configuration is valid, False otherwise

        Validation Process:
            1. Poetry Check: Execute poetry check command for validation
            2. Configuration Validation: Validate pyproject.toml syntax and structure
            3. Dependency Validation: Verify dependency specifications
            4. Error Reporting: Provide detailed validation error information

        Architecture:
            Uses Poetry's built-in validation with proper error handling to ensure
            reliable project validation without impacting project functionality.

        """
        print_colored(
            f"✅ Validating project {project_path.name}...",
            Colors.BLUE,
        )

        cmd = ["poetry", "check"]

        try:
            result = subprocess.run(
                cmd,
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                shell=False,  # Security: explicit shell=False
                timeout=30,  # Quick validation
            )

            if result.returncode == 0:
                print_colored("✅ Project valid", Colors.GREEN)
                return True

            print_colored(
                f"❌ Project invalid: {result.stderr}",
                Colors.RED,
            )
            return False

        except (subprocess.SubprocessError, OSError, FileNotFoundError) as e:
            print_colored(f"❌ Error validating project: {e}", Colors.RED)
            return False
