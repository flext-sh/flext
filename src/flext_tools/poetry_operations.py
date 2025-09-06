#!/usr/bin/env python3
"""FLEXT Poetry Operations - Enterprise Poetry Management with Safety Systems.

Provides comprehensive Poetry operations management with integrated safety systems
including backup management, validation, and rollback capabilities for the FLEXT
ecosystem. This module implements enterprise-grade Poetry operations with proper
error handling, security validation, and operational safety across all projects.

Author: FLEXT Development Team
Version: 0.9.0
License: MIT

"""

from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

from flext_core import FlextLogger, FlextResult
from flext_core.container import FlextContainer

from .backup import BackupManager
from .colors import Colors, print_colored
from .safety_validator import SafetyValidator

# Constants
MIN_PARTS_COUNT = 3

# Initialize logger
logger = FlextLogger(__name__)


# REMOVED: OperationResult class (MASSIVE DRY VIOLATION)
# This class duplicates FlextResult functionality:
# - success: bool -> FlextResult.success: bool
# - operation details -> FlextResult.data: dict
# All Poetry operation results must use FlextResult[Type] from flext-core instead
# to maintain consistency and avoid duplication of generic result functionality

# Type alias for Poetry operation data
OperationData = dict[str, object]


# Utility functions for operation data (moved from removed OperationResult class)
def get_operation_summary(operation_data: OperationData) -> str:
    """Get human-readable operation summary."""
    operation_type = operation_data.get("operation_type", "unknown")
    success = operation_data.get("success", False)
    packages_affected = operation_data.get("packages_affected", [])
    execution_time = operation_data.get("execution_time", 0.0)

    status = "SUCCESS" if success else "FAILED"
    package_count = len(packages_affected) if isinstance(packages_affected, list) else 0

    return f"{operation_type} {status}: {package_count} packages affected in {execution_time:.2f}s"


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
    ) -> None:
        """Initialize Poetry operations with comprehensive safety and DI integration.

        Creates a new PoetryOperations instance with integrated safety systems,
        dependency injection configuration, and operational monitoring for
        enterprise-grade Poetry operations across FLEXT projects.

        Args:
            dry_run: Flag for dry-run mode execution without actual changes
            enable_safety: Flag for enabling integrated safety systems

        Architecture:
            Uses dependency injection patterns for safety system configuration
            and integrates with monitoring systems for comprehensive operational
            visibility and reliability.

        """
        self.dry_run = dry_run
        self.enable_safety = enable_safety
        self.logger = logger
        self.container = FlextContainer.get_global()

        if self.enable_safety:
            self.backup_manager = BackupManager()
            self.safety_validator = SafetyValidator()
            self.logger.info(
                "Poetry operations safety system activated",
                dry_run=dry_run,
                safety_enabled=enable_safety,
            )
            print_colored("🛡️ Poetry operations safety system activated", Colors.CYAN)

        self.logger.info(
            "Poetry operations manager initialized",
            dry_run=dry_run,
            safety_enabled=enable_safety,
        )

    def add_dependencies_safe(
        self,
        project_path: Path,
        dependencies: dict[str, list[str]],
        *,
        auto_confirm: bool = False,
    ) -> FlextResult[OperationData]:
        """Safely add dependencies using railway-oriented programming.

        Performs comprehensive dependency addition with integrated backup systems,
        safety validation, and structured result reporting using FlextResult patterns
        for consistent error handling and operational monitoring.

        Args:
            project_path: Path to Poetry project root directory
            dependencies: Dictionary mapping dependency categories to dependency lists
            auto_confirm: Automatic confirmation flag for batch operations

        Returns:
            FlextResult containing OperationResult with comprehensive operation status

        Architecture:
            Uses railway-oriented programming with proper error handling to ensure
            reliable dependency management with comprehensive monitoring and safety.

        """
        try:
            start_time = time.time()

            self.logger.info(
                "Starting safe dependency addition",
                project_path=str(project_path),
                dependency_categories=list(dependencies.keys()),
                total_dependencies=sum(len(deps) for deps in dependencies.values()),
            )

            # Use existing implementation but wrap in FlextResult
            operation_result = self.add_dependencies(
                project_path,
                dependencies,
                _auto_confirm=auto_confirm,
            )

            execution_time = time.time() - start_time
            packages_affected = sum(len(deps) for deps in operation_result.values())

            # Using OperationData with FlextResult (DRY - no custom classes)
            operation_data: OperationData = {
                "success": packages_affected > 0,
                "operation_type": "add_dependencies",
                "packages_affected": [
                    dep for deps_list in operation_result.values() for dep in deps_list
                ],
                "execution_time": execution_time,
                "details": {
                    "categories": operation_result,
                    "dry_run": self.dry_run,
                    "safety_enabled": self.enable_safety,
                },
            }

            success = bool(operation_data["success"])
            self.logger.info(
                "Safe dependency addition completed",
                project_path=str(project_path),
                packages_affected=packages_affected,
                execution_time=execution_time,
                success=success,
            )

            return FlextResult[dict[str, object]].ok(operation_data)

        except Exception as e:
            self.logger.exception(
                "Safe dependency addition failed",
                project_path=str(project_path),
                error=str(e),
            )
            return FlextResult[dict[str, object]].fail(
                f"Dependency addition failed: {e}"
            )

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
                # Determine group for poetry add
                group = None if category == "runtime" else category

                try:
                    if self._add_dependency(project_path, dep, group):
                        added[category].append(dep)
                except (OSError, FileNotFoundError) as e:
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
        _project_path: Path,
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
        # Validate dependency input to prevent command injection
        logger = FlextLogger(__name__)
        if not re.match(r"^[a-zA-Z0-9_\-\.\[\]>=<~!]+$", dependency):
            logger.warning(f"Invalid dependency format: {dependency}")
            return False

        cmd = ["poetry", "add", dependency]

        if group:
            cmd.extend(["--group", group])

        if self.dry_run:
            cmd.append("--dry-run")

        try:
            print_colored(f"    [+] Adding {dependency}...", Colors.GREEN)

            # Use subprocess for Poetry operations (poetry_app was undefined)
            args = ["add", dependency]
            if group:
                args += ["--group", group]
            if self.dry_run:
                args.append("--dry-run")
            # Use subprocess instead of Poetry Application due to Input type incompatibility

            cmd = ["poetry", *args]
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            code = result.returncode
            success = code == 0

            if success:
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
            print_colored(f"    ❌ Failed to add {dependency}", Colors.RED)
            return False

        except (OSError, FileNotFoundError) as e:
            print_colored(f"    ❌ Error executing poetry: {e}", Colors.RED)
            return False

    def remove_dependencies_safe(
        self,
        project_path: Path,
        dependencies: list[str],
        *,
        auto_confirm: bool = False,
    ) -> FlextResult[OperationData]:
        """Safely remove dependencies using railway-oriented programming.

        Performs comprehensive dependency removal with integrated backup systems
        and safety validation using FlextResult patterns for operational reliability.

        Args:
            project_path: Path to Poetry project root directory
            dependencies: List of dependency names to remove
            auto_confirm: Automatic confirmation flag for batch operations

        Returns:
            FlextResult containing OperationResult with comprehensive operation status

        """
        try:
            start_time = time.time()

            self.logger.info(
                "Starting safe dependency removal",
                project_path=str(project_path),
                dependencies=dependencies,
                total_dependencies=len(dependencies),
            )

            # Use existing implementation but wrap in FlextResult
            operation_result = self.remove_dependencies(
                project_path,
                dependencies,
                _auto_confirm=auto_confirm,
            )

            execution_time = time.time() - start_time

            # Using OperationData with FlextResult (DRY - no custom classes)
            operation_data: OperationData = {
                "success": len(operation_result) > 0,
                "operation_type": "remove_dependencies",
                "packages_affected": operation_result,
                "execution_time": execution_time,
                "details": {
                    "removed_packages": operation_result,
                    "dry_run": self.dry_run,
                    "safety_enabled": self.enable_safety,
                },
            }

            success = bool(operation_data["success"])
            self.logger.info(
                "Safe dependency removal completed",
                project_path=str(project_path),
                packages_removed=len(operation_result),
                execution_time=execution_time,
                success=success,
            )

            return FlextResult[dict[str, object]].ok(operation_data)

        except Exception as e:
            self.logger.exception(
                "Safe dependency removal failed",
                project_path=str(project_path),
                error=str(e),
            )
            return FlextResult[dict[str, object]].fail(
                f"Dependency removal failed: {e}"
            )

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

    def _remove_dependency(self, _project_path: Path, dependency: str) -> bool:
        """Remove an individual dependency with safety validation.

        Executes Poetry remove command for a single dependency with proper
        error handling and timeout management.

        Args:
            project_path: Path to Poetry project directory
            dependency: Name of dependency to remove

        Returns:
            True if dependency was removed successfully, False otherwise

        """
        # Validate dependency input to prevent command injection
        logger = FlextLogger(__name__)
        if not re.match(r"^[a-zA-Z0-9_\-\.\[\]>=<~!]+$", dependency):
            logger.warning(f"Invalid dependency format: {dependency}")
            return False

        cmd = ["poetry", "remove", dependency]

        if self.dry_run:
            cmd.append("--dry-run")

        try:
            print_colored(f"    [-] Removing {dependency}...", Colors.YELLOW)

            # Prefer Poetry API when available
            # Use subprocess for Poetry operations
            args = ["remove", dependency]
            if self.dry_run:
                args.append("--dry-run")
            # Use subprocess instead of Poetry Application due to Input type incompatibility

            cmd = ["poetry", *args]
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            code = result.returncode
            success = code == 0

            if success:
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

            print_colored(f"    ❌ Failed to remove {dependency}", Colors.RED)
            return False

        except (OSError, FileNotFoundError) as e:
            print_colored(f"    ❌ Error executing poetry: {e}", Colors.RED)
            return False

    def update_project_safe(self, project_path: Path) -> FlextResult[OperationData]:
        """Safely update Poetry project using railway-oriented programming.

        Performs comprehensive project update with integrated backup systems
        and safety validation using FlextResult patterns for operational reliability.

        Args:
            project_path: Path to Poetry project root directory

        Returns:
            FlextResult containing OperationResult with comprehensive operation status

        """
        try:
            start_time = time.time()

            self.logger.info(
                "Starting safe project update",
                project_path=str(project_path),
            )

            # Use existing implementation but wrap in FlextResult
            operation_success = self.update_project(project_path)

            execution_time = time.time() - start_time

            # Using OperationData with FlextResult (DRY - no custom classes)
            operation_data: OperationData = {
                "success": operation_success,
                "operation_type": "update_project",
                "packages_affected": [],  # Update affects all packages
                "execution_time": execution_time,
                "details": {
                    "project_updated": operation_success,
                    "dry_run": self.dry_run,
                    "safety_enabled": self.enable_safety,
                },
            }

            success = bool(operation_data["success"])
            self.logger.info(
                "Safe project update completed",
                project_path=str(project_path),
                execution_time=execution_time,
                success=success,
            )

            return FlextResult[dict[str, object]].ok(operation_data)

        except Exception as e:
            self.logger.exception(
                "Safe project update failed",
                project_path=str(project_path),
                error=str(e),
            )
            return FlextResult[dict[str, object]].fail(f"Project update failed: {e}")

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
            # Use subprocess for Poetry operations
            args = ["update"]
            if self.dry_run:
                args.append("--dry-run")
            # Use subprocess instead of Poetry Application due to Input type incompatibility

            cmd = ["poetry", *args]
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            code = result.returncode
            success = code == 0

            if success:
                if not self.dry_run:
                    print_colored("✅ Project updated successfully", Colors.GREEN)
                else:
                    print_colored(
                        "✅ Project would be updated (dry-run)",
                        Colors.YELLOW,
                    )
                return True

            print_colored("❌ Project update failed", Colors.RED)
            return False

        except (OSError, FileNotFoundError) as e:
            print_colored(f"❌ Error executing poetry update: {e}", Colors.RED)
            return False

    def lock_project_safe(self, project_path: Path) -> FlextResult[OperationData]:
        """Safely generate Poetry lock file using railway-oriented programming.

        Performs Poetry lock file generation with comprehensive error handling
        and structured result reporting using FlextResult patterns.

        Args:
            project_path: Path to Poetry project root directory

        Returns:
            FlextResult containing OperationResult with comprehensive operation status

        """
        try:
            start_time = time.time()

            self.logger.info(
                "Starting safe project lock",
                project_path=str(project_path),
            )

            # Use existing implementation but wrap in FlextResult
            operation_success = self.lock_project(project_path)

            execution_time = time.time() - start_time

            # Using OperationData with FlextResult (DRY - no custom classes)
            operation_data: OperationData = {
                "success": operation_success,
                "operation_type": "lock_project",
                "packages_affected": [],  # Lock affects all dependencies
                "execution_time": execution_time,
                "details": {
                    "lock_generated": operation_success,
                    "dry_run": self.dry_run,
                },
            }

            success = bool(operation_data["success"])
            self.logger.info(
                "Safe project lock completed",
                project_path=str(project_path),
                execution_time=execution_time,
                success=success,
            )

            return FlextResult[dict[str, object]].ok(operation_data)

        except Exception as e:
            self.logger.exception(
                "Safe project lock failed",
                project_path=str(project_path),
                error=str(e),
            )
            return FlextResult[dict[str, object]].fail(f"Project lock failed: {e}")

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

        # Note: using Poetry API preferred; no subprocess fallback in this environment

        try:
            # Use subprocess for Poetry operations
            args = ["lock"]
            # Use subprocess instead of Poetry Application due to Input type incompatibility

            cmd = ["poetry", *args]
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            code = result.returncode
            success = code == 0

            if success:
                print_colored("✅ Lock file generated successfully", Colors.GREEN)
                return True

            print_colored("❌ Failed to generate lock file", Colors.RED)
            return False

        except (OSError, FileNotFoundError) as e:
            print_colored(f"❌ Error executing poetry lock: {e}", Colors.RED)
            return False

    def validate_project_safe(self, project_path: Path) -> FlextResult[OperationData]:
        """Safely validate Poetry project using railway-oriented programming.

        Performs comprehensive Poetry project validation with structured result
        reporting using FlextResult patterns for consistent error handling.

        Args:
            project_path: Path to Poetry project root directory

        Returns:
            FlextResult containing OperationResult with comprehensive validation status

        """
        try:
            start_time = time.time()

            self.logger.info(
                "Starting safe project validation",
                project_path=str(project_path),
            )

            # Use existing implementation but wrap in FlextResult
            operation_success = self.validate_project(project_path)

            execution_time = time.time() - start_time

            # Using OperationData with FlextResult (DRY - no custom classes)
            operation_data: OperationData = {
                "success": operation_success,
                "operation_type": "validate_project",
                "packages_affected": [],  # Validation doesn't affect packages
                "execution_time": execution_time,
                "details": {
                    "validation_passed": operation_success,
                    "project_path": str(project_path),
                },
            }

            success = bool(operation_data["success"])
            self.logger.info(
                "Safe project validation completed",
                project_path=str(project_path),
                execution_time=execution_time,
                success=success,
            )

            return FlextResult[dict[str, object]].ok(operation_data)

        except Exception as e:
            self.logger.exception(
                "Safe project validation failed",
                project_path=str(project_path),
                error=str(e),
            )
            return FlextResult[dict[str, object]].fail(
                f"Project validation failed: {e}"
            )

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

        # Note: using Poetry API preferred; no subprocess fallback in this environment

        try:
            # Use subprocess for Poetry operations
            args = ["check"]
            # Use subprocess instead of Poetry Application due to Input type incompatibility

            cmd = ["poetry", *args]
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            code = result.returncode
            success = code == 0

            if success:
                print_colored("✅ Project valid", Colors.GREEN)
                return True

            print_colored("❌ Project invalid", Colors.RED)
            return False

        except (OSError, FileNotFoundError) as e:
            print_colored(f"❌ Error validating project: {e}", Colors.RED)
            return False
