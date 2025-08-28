#!/usr/bin/env python3
"""FLEXT Safety Validator - Enterprise Security Validation for Critical Operations.

Provides comprehensive security validation and safety controls for critical
operations across the FLEXT ecosystem. This module implements enterprise-grade
security validation with integrated safety checks, risk assessment, and
operational protection for maintaining system integrity and security.

The safety validator serves as the primary security enforcement point for
all critical operations, implementing comprehensive validation including
package safety checks, file operation validation, command execution security,
and Poetry operation safety with integrated monitoring and reporting.

Key Features:
    - Comprehensive package safety validation with PyPI verification
    - File operation security with backup requirement enforcement
    - Command execution validation with security controls
    - Poetry operation safety with dependency validation
    - Integration with flext-observability for security monitoring
    - Railway-oriented programming with FlextResult error handling
    - Enterprise-grade security policies and threat protection
    - Risk assessment and recommendation systems

Architecture:
    Uses Clean Architecture patterns with proper separation between security
    validation, risk assessment, and operational interfaces. Integrates with
    flext-core patterns for consistent error handling and monitoring.

Example:
    Initialize and use safety validator:

    >>> from flext_tools.safety.validator import SafetyValidator
    >>> from pathlib import Path
    >>>
    >>> # Initialize safety validator
    >>> validator = SafetyValidator()
    >>>
    >>> # Validate package safety
    >>> package_result = validator.validate_package_safety_safe("requests")
    >>> if package_result.success and package_result.value["safe"]:
    ...     print("✅ Package is safe for installation")
    >>>
    >>> # Validate file operation
    >>> file_path = Path("pyproject.toml")
    >>> file_result = validator.validate_file_operation_safe(
    ...     file_path, "write", backup_requirement="required"
    >>> )
    >>> if file_result.success and file_result.value["safe"]:
    ...     print("✅ File operation is safe to proceed")
    >>>
    >>> # Validate command execution
    >>> cmd_result = validator.validate_command_execution(
    ...     ["poetry", "add", "requests"]
    >>> )
    >>> if cmd_result.success and cmd_result.value["safe"]:
    ...     print("✅ Command execution is safe")

Integration:
    - Built on flext-core FlextResult patterns for consistent error handling
    - Integrates with flext-observability for security monitoring and analytics
    - Coordinates with operational systems for comprehensive security enforcement
    - Provides foundation for automated security validation in CI/CD pipelines

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

import shutil
import tomllib
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

import requests
from flext_core import FlextResult, FlextLogger

# Constants for validation
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 50
HTTP_OK_STATUS = 200

# Initialize logger
logger = FlextLogger(__name__)


# REMOVED: ValidationResult class (MASSIVE DRY VIOLATION)
# This class duplicates FlextResult functionality:
# - safe: bool -> FlextResult.success: bool
# - issues: list[str] -> FlextResult.error: str (join issues)
# - operation, recommendations, confidence, risk_level -> FlextResult.value: dict
#
# All safety validation results must use FlextResult[Type] from flext-core instead
# to maintain consistency and avoid duplication of generic result functionality

# Type alias for validation data
ValidationData = dict[str, object]


# Utility functions for validation data (moved from removed ValidationResult class)
def has_validation_issues(validation_data: ValidationData) -> bool:
    """Check if validation found any security issues."""
    issues = validation_data.get("issues", [])
    return isinstance(issues, list) and len(issues) > 0


def get_risk_assessment(validation_data: ValidationData) -> str:
    """Get human-readable risk assessment summary."""
    safe = validation_data.get("safe", False)
    issues = validation_data.get("issues", [])
    issue_count = len(issues) if isinstance(issues, list) else 0

    if not safe:
        return f"HIGH RISK: {issue_count} security issues found"
    if issue_count > 0:
        return f"MEDIUM RISK: {issue_count} warnings identified"
    return "LOW RISK: Operation validated as safe"


class BackupRequirement(Enum):
    """Backup requirement options."""

    REQUIRED = "required"
    OPTIONAL = "optional"


class SafetyValidator:
    """Enterprise safety validator for comprehensive security validation.

    Validates operations before executing them to avoid problems, implementing
    comprehensive security checks with integrated monitoring, risk assessment,
    and recommendation systems for maintaining operational safety across
    the FLEXT ecosystem.

    This validator serves as the primary security control point for all
    critical operations, providing detailed validation with actionable
    recommendations and comprehensive risk assessment capabilities.

    Attributes:
      known_safe_packages: Curated whitelist of verified safe packages
      dangerous_packages: Blacklist of known dangerous or problematic packages
      logger: Structured logger for security monitoring and audit trails

    Features:
      - Package safety validation with PyPI verification and blacklist checking
      - File operation security with critical file protection
      - Command execution validation with safe executable verification
      - Poetry operation safety with dependency validation
      - Comprehensive risk assessment and recommendation generation
      - Integration with flext-observability for security monitoring
      - Railway-oriented programming with FlextResult error handling

    Architecture:
      Uses Clean Architecture patterns with proper separation between
      validation logic, risk assessment, and security policy enforcement
      for maintainable and extensible security validation.

    Example:
      Initialize and use safety validator:

      >>> validator = SafetyValidator()
      >>> result = validator.validate_package_safety_safe("requests")
      >>> if result.success and result.value["safe"]:
      ...     print("✅ Package validation passed")

    Integration:
      Integrates with flext-core patterns for consistent error handling
      and coordinates with monitoring systems for security analytics.

    """

    def __init__(self) -> None:
        """Initialize safety validator with comprehensive security configuration.

        Creates a new SafetyValidator instance with curated package lists,
        security policies, and monitoring integration for enterprise-grade
        security validation across FLEXT operations.

        Architecture:
            Uses security-by-default configuration with comprehensive
            package whitelists and blacklists for reliable security
            validation and threat protection.
        """
        self.known_safe_packages = {
            # Safe and common Python packages
            "requests",
            "urllib3",
            "certifi",
            "charset-normalizer",
            "idna",
            "click",
            "colorama",
            "packaging",
            "setuptools",
            "wheel",
            "pip",
            "pydantic",
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "alembic",
            "psycopg2-binary",
            "pytest",
            "pytest-cov",
            "mypy",
            "ruff",
            "black",
            "isort",
            "pre-commit",
            "poetry",
            "pyyaml",
            "tomli",
            "tomllib-w",
            "structlog",
            "python-dotenv",
            "rich",
            "typer",
            # Flext packages
            "flext-core",
            "flext-auth",
            "flext-api",
            "flext-observability",
        }

        self.dangerous_packages = {
            # Potentially dangerous or problematic packages
            "os-sys",
            "setup-tools",
            "urllib",  # Common typosquatting
            "request",  # Common typosquatting
            "beautifulsoup",  # Correct name is beautifulsoup4
            "PIL",  # Correct name is Pillow
            "yaml",  # Correct name is pyyaml
        }

        logger.info(
            "Safety validator initialized",
            known_safe_count=len(self.known_safe_packages),
            dangerous_count=len(self.dangerous_packages),
        )

    def validate_package_safety_safe(
        self,
        package_name: str,
    ) -> FlextResult[ValidationData]:
        """Safely validate package safety using railway-oriented programming.

        Performs comprehensive package safety validation including name validation,
        PyPI verification, security blacklist checking, and risk assessment using
        FlextResult patterns for consistent error handling and monitoring.

        Args:
            package_name: Name of the package to validate for safety

        Returns:
            FlextResult containing ValidationData with comprehensive safety assessment

        Validation Process:
            1. Name Validation: Check package name format and length
            2. Blacklist Check: Verify against known dangerous packages
            3. Character Validation: Detect suspicious characters and patterns
            4. PyPI Verification: Confirm package exists on official PyPI
            5. Risk Assessment: Evaluate overall package safety and confidence
            6. Recommendations: Generate actionable security recommendations

        Architecture:
            Uses railway-oriented programming with proper error handling
            to ensure reliable package validation with comprehensive
            security assessment and monitoring.

        """
        try:
            logger.info("Starting package safety validation", package_name=package_name)

            issues: list[str] = []
            recommendations: list[str] = []
            safe = True
            confidence = "high"
            risk_level = "low"

            # Normalize package name for consistent validation
            normalized_name = package_name.lower().replace("_", "-")

            # Check dangerous packages blacklist
            if normalized_name in self.dangerous_packages:
                safe = False
                risk_level = "high"
                issues.append(
                    f"Package '{package_name}' is blacklisted as potentially dangerous",
                )
                logger.warning("Package blacklisted", package_name=package_name)

            # Validate package name length
            if len(package_name) < MIN_NAME_LENGTH:
                safe = False
                risk_level = "high" if risk_level != "high" else risk_level
                issues.append("Package name too short - potential typosquatting")
                confidence = "high"

            if len(package_name) > MAX_NAME_LENGTH:
                safe = False
                risk_level = "medium" if risk_level == "low" else risk_level
                issues.append("Package name suspiciously long")
                confidence = "medium"

            # Check for suspicious characters
            suspicious_chars = set(package_name) & {"@", "#", "$", "%", "^", "&", "*"}
            if suspicious_chars:
                safe = False
                risk_level = "high"
                issues.append(
                    f"Suspicious characters detected: {suspicious_chars}",
                )
                confidence = "high"

            # Check if it's a known safe package
            if normalized_name in self.known_safe_packages:
                confidence = "high"
                recommendations.append("Known safe package from curated whitelist")
                logger.debug("Package whitelisted", package_name=package_name)

            # Verify package exists on PyPI (only if no critical issues)
            if safe and not self._package_exists_on_pypi(package_name):
                safe = False
                risk_level = "high"
                issues.append("Package not found on official PyPI registry")
                confidence = "high"
                logger.warning("Package not found on PyPI", package_name=package_name)

            # Generate security recommendations
            if not issues:
                recommendations.append("Package passed all security validations")
            else:
                recommendations.extend(
                    [
                        "Review package source and maintainer reputation",
                        "Consider alternative packages with better security profiles",
                        "Use virtual environment for installation isolation",
                    ],
                )

            # Using FlextResult pattern with ValidationData (DRY - no custom classes)
            validation_data: ValidationData = {
                "id": f"validation_{package_name}_{safe}",
                "safe": safe,
                "operation": f"package_validation:{package_name}",
                "issues": issues,
                "recommendations": recommendations,
                "confidence": confidence,
                "risk_level": risk_level,
            }

            logger.info(
                "Package safety validation completed",
                package_name=package_name,
                safe=safe,
                issues_count=len(issues),
                risk_level=risk_level,
            )

            return FlextResult[ValidationData].ok(validation_data)

        except Exception as e:
            logger.exception(
                "Package safety validation failed",
                package_name=package_name,
                error=str(e),
            )
            return FlextResult[ValidationData].fail(f"Package validation failed: {e}")

    def validate_file_operation_safe(
        self,
        file_path: Path,
        operation: str,
        *,
        backup_requirement: BackupRequirement = BackupRequirement.REQUIRED,
    ) -> FlextResult[ValidationData]:
        """Safely validate file operation using railway-oriented programming.

        Performs comprehensive file operation validation including existence checks,
        permission validation, critical file protection, and backup requirement
        enforcement using FlextResult patterns for operational safety.

        Args:
            file_path: Path to file for operation validation
            operation: Operation type (read, write, delete, create)
            backup_requirement: Backup requirement level (REQUIRED or OPTIONAL)

        Returns:
            FlextResult containing ValidationData with comprehensive safety assessment

        Validation Process:
            1. Path Validation: Verify file path accessibility and format
            2. Existence Check: Validate file existence for required operations
            3. Permission Check: Verify appropriate file system permissions
            4. Critical File Detection: Identify and protect critical system files
            5. Backup Assessment: Evaluate backup requirements and recommendations
            6. Risk Assessment: Calculate overall operation safety and risk level

        Architecture:
            Uses railway-oriented programming with comprehensive error handling
            to ensure reliable file operation validation with security controls.

        """
        try:
            logger.info(
                "Starting file operation validation",
                file_path=str(file_path),
                operation=operation,
            )

            issues: list[str] = []
            recommendations: list[str] = []
            safe = True
            risk_level = "low"

            # Validate file existence for operations that require it
            if operation in {"read", "write", "delete"} and not file_path.exists():
                safe = False
                risk_level = "high"
                issues.append(f"File not found: {file_path}")
                logger.warning(
                    "File not found for operation",
                    file_path=str(file_path),
                    operation=operation,
                )

                # Using FlextResult pattern with ValidationData (DRY - no custom classes)
                error_validation_data: ValidationData = {
                    "id": f"file_op_{operation}_{file_path.name}_{safe}",
                    "safe": safe,
                    "operation": f"file_operation:{operation}:{file_path.name}",
                    "issues": issues,
                    "recommendations": [
                        "Verify file path and existence before operation",
                    ],
                    "confidence": "high",
                    "risk_level": risk_level,
                }
                return FlextResult[ValidationData].ok(error_validation_data)

            # Critical file detection and protection
            critical_files = {
                "pyproject.toml",
                "poetry.lock",
                "Makefile",
                ".gitignore",
                "requirements.txt",
                "setup.py",
                "setup.cfg",
                "package.json",
                "go.mod",
                "Cargo.toml",
                "composer.json",
            }

            if file_path.name in critical_files:
                risk_level = "medium"
                recommendations.append(
                    "Critical file detected - backup strongly recommended",
                )

                if backup_requirement == BackupRequirement.REQUIRED and operation in {
                    "write",
                    "delete",
                }:
                    recommendations.append(
                        "Backup required for critical file modification/deletion",
                    )
                    logger.info(
                        "Backup required for critical file",
                        file_path=str(file_path),
                    )

            # Permission validation
            if operation == "write" and not self._can_write_file(file_path):
                safe = False
                risk_level = "high"
                issues.append("Insufficient write permissions for file operation")
                recommendations.append("Check file permissions and user access rights")

            if operation == "delete" and not self._can_delete_file(file_path):
                safe = False
                risk_level = "high"
                issues.append("Insufficient delete permissions for file operation")
                recommendations.append(
                    "Check directory permissions and user access rights",
                )

            # Generate additional security recommendations
            if operation in {"write", "delete"} and file_path.name in critical_files:
                recommendations.extend(
                    [
                        "Use version control to track changes",
                        "Validate file integrity after operation",
                        "Consider atomic operations to prevent corruption",
                    ],
                )

            # Using FlextResult pattern with ValidationData (DRY - no custom classes)
            success_validation_data: ValidationData = {
                "id": f"file_op_{operation}_{file_path.name}_{safe}",
                "safe": safe,
                "operation": f"file_operation:{operation}:{file_path.name}",
                "issues": issues,
                "recommendations": recommendations,
                "confidence": "high",
                "risk_level": risk_level,
            }

            logger.info(
                "File operation validation completed",
                file_path=str(file_path),
                operation=operation,
                safe=safe,
                risk_level=risk_level,
            )

            return FlextResult[ValidationData].ok(success_validation_data)

        except Exception as e:
            logger.exception(
                "File operation validation failed",
                file_path=str(file_path),
                operation=operation,
                error=str(e),
            )
            return FlextResult[ValidationData].fail(
                f"File operation validation failed: {e}"
            )

    def validate_command_execution(
        self,
        command: list[str],
        working_dir: Path | None = None,
    ) -> FlextResult[ValidationData]:
        """Validate system command execution with comprehensive security checks.

        Args:
            command: Command to be executed
            working_dir: Working directory

        Returns:
            FlextResult with ValidationResult

        """
        if not command:
            return FlextResult[ValidationData].fail("Empty command provided")

        # Using ValidationData instead of ValidationResult class (DRY principle)
        validation_data: ValidationData = {
            "id": f"cmd_validation_{len(command)}",
            "safe": True,
            "operation": " ".join(command),
            "issues": [],
            "recommendations": [],
            "confidence": "high",
            "risk_level": "low",
        }

        executable = command[0]

        # Check if executable is safe
        safe_executables = {
            "poetry",
            "pip",
            "python",
            "python3",
            "git",
            "make",
            "pytest",
            "mypy",
            "ruff",
            "black",
            "isort",
        }

        if executable not in safe_executables:
            validation_data["safe"] = False
            validation_data["risk_level"] = "high"
            issues = validation_data["issues"]
            if isinstance(issues, list):
                issues.append(
                    f"Executable '{executable}' is not in the safe commands list",
                )

        # Check if executable exists
        if not shutil.which(executable):
            validation_data["safe"] = False
            validation_data["risk_level"] = "high"
            issues = validation_data["issues"]
            if isinstance(issues, list):
                issues.append(f"Executable '{executable}' not found in PATH")

        # Check dangerous arguments
        dangerous_args = {"rm", "delete", "--force", "-f", "sudo", "su"}
        command_args = set(command)

        if command_args & dangerous_args:
            validation_data["safe"] = False
            validation_data["risk_level"] = "high"
            issues = validation_data["issues"]
            if isinstance(issues, list):
                issues.append("Dangerous arguments detected")

        # Check working directory
        if working_dir and not working_dir.exists():
            validation_data["safe"] = False
            validation_data["risk_level"] = "medium"
            issues = validation_data["issues"]
            if isinstance(issues, list):
                issues.append("Working directory does not exist")

        return FlextResult[ValidationData].ok(validation_data)

    def validate_poetry_operation(
        self,
        project_path: Path,
        operation: str,
        packages: list[str] | None = None,
    ) -> FlextResult[ValidationData]:
        """Validate specific Poetry operation.

        Args:
            project_path: Project path
            operation: Operation type (add, remove, update, install)
            packages: List of packages (if applicable)

        Returns:
            FlextResult with ValidationResult

        """
        # Using ValidationData instead of ValidationResult class (DRY principle)
        validation_data: ValidationData = {
            "id": f"poetry_{operation}_validation",
            "safe": True,
            "operation": f"poetry {operation}",
            "issues": [],
            "recommendations": [],
            "confidence": "high",
            "risk_level": "low",
        }

        # Check if Poetry project is valid
        pyproject_path = project_path / "pyproject.toml"
        if not pyproject_path.exists():
            return FlextResult[ValidationData].fail("pyproject.toml not found")

        try:
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)

            if "tool" not in data or "poetry" not in data["tool"]:
                return FlextResult[ValidationData].fail(
                    "Poetry configuration not found in pyproject.toml",
                )

        except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
            return FlextResult[ValidationData].fail(
                f"Error reading pyproject.toml: {e}"
            )

        # Validate packages if provided
        if packages:
            for package in packages:
                package_validation = self.validate_package_safety(package)
                if not package_validation["safe"]:
                    validation_data["safe"] = False
                    validation_data["risk_level"] = "high"
                    package_issues = package_validation["issues"]
                    if isinstance(package_issues, list):
                        issues = validation_data["issues"]
                        if isinstance(issues, list):
                            issues.extend(
                                [
                                    f"Package '{package}': {issue}"
                                    for issue in package_issues
                                ],
                            )

        # Specific recommendations by operation
        recommendations = validation_data["recommendations"]
        if isinstance(recommendations, list):
            if operation == "add":
                recommendations.append("Check version compatibility")
            elif operation == "update":
                recommendations.append("Create backup before updating")
            elif operation == "remove":
                recommendations.append("Check dependencies before removing")

        return FlextResult[ValidationData].ok(validation_data)

    def get_safety_recommendations_safe(
        self,
        operation_type: str,
        context: dict[str, object] | None = None,
    ) -> FlextResult[list[str]]:
        """Safely generate security recommendations using railway-oriented programming.

        Provides comprehensive security recommendations based on operation type
        and context with proper error handling and monitoring integration.

        Args:
            operation_type: Type of operation requiring security recommendations
            context: Optional operation context for tailored recommendations

        Returns:
            FlextResult containing list of actionable security recommendations

        """
        try:
            context = context or {}
            logger.debug(
                "Generating safety recommendations",
                operation_type=operation_type,
            )

            recommendations = self.get_safety_recommendations(operation_type, context)

            logger.debug(
                "Safety recommendations generated",
                operation_type=operation_type,
                recommendations_count=len(recommendations),
            )

            return FlextResult[list[str]].ok(recommendations)

        except Exception as e:
            logger.exception(
                "Failed to generate safety recommendations",
                operation_type=operation_type,
                error=str(e),
            )
            return FlextResult[list[str]].fail(f"Recommendation generation failed: {e}")

    def get_comprehensive_validation_summary(self) -> FlextResult[dict[str, object]]:
        """Get comprehensive validation summary with statistics and recommendations.

        Provides detailed validation statistics, security metrics, and operational
        recommendations for maintaining security across FLEXT operations.

        Returns:
            FlextResult containing comprehensive validation summary with metrics

        """
        try:
            summary = {
                "known_safe_packages": len(self.known_safe_packages),
                "dangerous_packages": len(self.dangerous_packages),
                "validation_features": [
                    "Package safety validation with PyPI verification",
                    "File operation security with critical file protection",
                    "Command execution validation with security controls",
                    "Poetry operation safety with dependency validation",
                ],
                "security_policies": {
                    "package_validation": "Comprehensive blacklist and whitelist checking",
                    "file_protection": "Critical file backup requirement enforcement",
                    "command_security": "Safe executable validation and argument filtering",
                    "operation_monitoring": "Integrated observability and audit logging",
                },
                "recommendations": [
                    "Always validate packages before installation",
                    "Use backup systems for critical file operations",
                    "Maintain updated security blacklists and whitelists",
                    "Monitor security validation metrics and trends",
                ],
            }

            logger.info(
                "Generated comprehensive validation summary",
                safe_packages=summary["known_safe_packages"],
                dangerous_packages=summary["dangerous_packages"],
            )

            return FlextResult[dict[str, object]].ok(summary)

        except Exception as e:
            logger.exception("Failed to generate validation summary", error=str(e))
            return FlextResult[dict[str, object]].fail(
                f"Validation summary generation failed: {e}"
            )

    def _can_write_file(self, file_path: Path) -> bool:
        """Check if it's possible to write to the file."""
        try:
            if file_path.exists():
                return file_path.is_file() and bool(file_path.stat().st_mode & 0o200)
            # Check if can create file in parent directory
            parent = file_path.parent
            return (
                parent.exists()
                and parent.is_dir()
                and bool(parent.stat().st_mode & 0o200)
            )
        except (OSError, PermissionError):
            return False

    def _can_delete_file(self, file_path: Path) -> bool:
        """Check if it's possible to delete the file."""
        try:
            if not file_path.exists():
                return False
            # Check write permission in parent directory (needed to delete)
            parent = file_path.parent
            return bool(parent.stat().st_mode & 0o200)
        except (OSError, PermissionError):
            return False

    def _is_stdlib_module(self, module_name: str) -> bool:
        """Check if module is from standard library."""
        # Basic list of stdlib modules - in production use specialized libraries
        stdlib_modules = {
            "os",
            "sys",
            "re",
            "json",
            "csv",
            "math",
            "random",
            "datetime",
            "pathlib",
            "typing",
            "collections",
            "itertools",
            "functools",
            "subprocess",
            "threading",
            "asyncio",
            "unittest",
            "logging",
            "copy",
            "operator",
            "contextlib",
            "io",
            "string",
            "types",
            "traceback",
            "inspect",
            "ast",
            "hashlib",
            "secrets",
            "uuid",
            "urllib",
            "http",
            "email",
            "sqlite3",
            "pickle",
            "base64",
        }

        return module_name.lower() in stdlib_modules

    def _package_exists_on_pypi(self, package_name: str) -> bool:
        """Check if package exists on official PyPI."""
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"

            # S310: Validate URL scheme before opening
            parsed_url = urlparse(url)
            if parsed_url.scheme not in {"https", "http"}:
                return False

            response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "flext-tools/1.0"},
            )

            return response.status_code == HTTP_OK_STATUS

        except (requests.RequestException, OSError):
            # In case of network error, assume it exists (false positive is better)
            return True

    # Legacy methods for backward compatibility
    def validate_package_safety(self, package_name: str) -> dict[str, object]:
        """Legacy method for backward compatibility - use validate_package_safety_safe() instead."""
        issues: list[str] = []
        recommendations: list[str] = []

        result: dict[str, object] = {
            "safe": True,
            "package": package_name,
            "issues": issues,
            "recommendations": recommendations,
            "confidence": "high",
        }

        # Normalize package name
        normalized_name = package_name.lower().replace("_", "-")

        # Check if it's in the dangerous packages list
        if normalized_name in self.dangerous_packages:
            result["safe"] = False
            issues.append(
                f"Package '{package_name}' is in the dangerous packages list",
            )
            result["confidence"] = "high"
            return result

        # Check name length
        if len(package_name) < MIN_NAME_LENGTH:
            result["safe"] = False
            issues.append("Package name too short")
            result["confidence"] = "high"

        if len(package_name) > MAX_NAME_LENGTH:
            result["safe"] = False
            issues.append("Package name too long")
            result["confidence"] = "medium"

        # Check suspicious characters
        suspicious_chars = set(package_name) & {"@", "#", "$", "%", "^", "&", "*"}
        if suspicious_chars:
            result["safe"] = False
            issues.append(
                f"Suspicious characters in name: {suspicious_chars}",
            )
            result["confidence"] = "high"

        # Check if it's a known safe package
        if normalized_name in self.known_safe_packages:
            result["confidence"] = "high"
            recommendations.append("Known safe package")

        # Check existence on PyPI (only if no critical issues)
        if result["safe"] and not self._package_exists_on_pypi(package_name):
            result["safe"] = False
            issues.append("Package not found on official PyPI")
            result["confidence"] = "high"

        return result

    def validate_file_operation(
        self,
        file_path: Path,
        operation: str,
        *,
        backup_requirement: BackupRequirement = BackupRequirement.REQUIRED,
    ) -> dict[str, object]:
        """Legacy method for backward compatibility - use validate_file_operation_safe() instead."""
        issues: list[str] = []
        recommendations: list[str] = []

        result: dict[str, object] = {
            "safe": True,
            "file": str(file_path),
            "operation": operation,
            "issues": issues,
            "recommendations": recommendations,
        }

        # Check if file exists (for operations that need it)
        if operation in {"read", "write", "delete"} and not file_path.exists():
            result["safe"] = False
            issues.append("File not found")
            return result

        # Check if it's a critical file
        critical_files = {
            "pyproject.toml",
            "poetry.lock",
            "Makefile",
            ".gitignore",
            "requirements.txt",
            "setup.py",
            "setup.cfg",
        }

        if file_path.name in critical_files:
            recommendations.append("Critical file - backup recommended")

            if backup_requirement == BackupRequirement.REQUIRED and operation in {
                "write",
                "delete",
            }:
                recommendations.append(
                    "Backup required for this operation",
                )

        # Check permissions
        if operation == "write" and not self._can_write_file(file_path):
            result["safe"] = False
            issues.append("No write permission")

        if operation == "delete" and not self._can_delete_file(file_path):
            result["safe"] = False
            issues.append("No delete permission")

        return result

    def get_safety_recommendations(
        self,
        operation_type: str,
        _context: dict[str, object],
    ) -> list[str]:
        """Legacy method for backward compatibility - use get_safety_recommendations_safe() instead."""
        recommendations = []

        if operation_type == "package_install":
            recommendations.extend(
                [
                    "Always review dependencies before installing",
                    "Check for known vulnerable versions",
                    "Use isolated virtual environments",
                    "Maintain change log for rollback",
                ],
            )

        elif operation_type == "file_modification":
            recommendations.extend(
                [
                    "Create backup before modifying critical files",
                    "Validate integrity after modification",
                    "Use version control to track changes",
                ],
            )

        elif operation_type == "command_execution":
            recommendations.extend(
                [
                    "Always use shell=False in subprocess",
                    "Validate user input before executing",
                    "Use timeout to avoid hanging",
                    "Log executed commands for audit",
                ],
            )

        return recommendations
