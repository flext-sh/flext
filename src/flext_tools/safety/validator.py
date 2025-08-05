#!/usr/bin/env python3
"""Security validator for critical operations."""

from __future__ import annotations

import shutil
import tomllib
from enum import Enum
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import requests
import structlog

if TYPE_CHECKING:
    from pathlib import Path


MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 50
HTTP_OK_STATUS = 200

logger = structlog.get_logger(__name__)


class BackupRequirement(Enum):
    """Backup requirement options."""

    REQUIRED = "required"
    OPTIONAL = "optional"


class SafetyValidator:
    """Validates operations before executing them to avoid problems."""

    def __init__(self) -> None:
        """Initialize safety validator."""
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
            "urllib",  # Typosquatting comum
            "request",  # Typosquatting comum
            "beautifulsoup",  # Nome correto é beautifulsoup4
            "PIL",  # Nome correto é Pillow
            "yaml",  # Nome correto é pyyaml
        }

    def validate_package_safety(self, package_name: str) -> dict[str, object]:
        """Validate if a package is safe for installation.

        Args:
            package_name: Name of the package to validate

        Returns:
            Dict with validation result

        """
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
        """Validate operation on critical file.

        Args:
            file_path: File path
            operation: Operation type (read, write, delete)
            backup_requirement: Backup requirement (REQUIRED or OPTIONAL)

        Returns:
            Dict with validation result

        """
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

    def validate_command_execution(
        self,
        command: list[str],
        working_dir: Path | None = None,
    ) -> dict[str, object]:
        """Validate system command execution.

        Args:
            command: Command to be executed
            working_dir: Working directory

        Returns:
            Dict with validation result

        """
        result: dict[str, object] = {
            "safe": True,
            "command": " ".join(command),
            "issues": [],
            "recommendations": [],
        }

        if not command:
            result["safe"] = False
            result["issues"].append("Empty command")
            return result

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
            result["safe"] = False
            issues_list = result["issues"]
            if isinstance(issues_list, list):
                issues_list.append(
                    f"Executable '{executable}' is not in the safe commands list",
                )
            return result

        # Check if executable exists
        if not shutil.which(executable):
            result["safe"] = False
            issues_list = result["issues"]
            if isinstance(issues_list, list):
                issues_list.append(f"Executable '{executable}' not found in PATH")

        # Check dangerous arguments
        dangerous_args = {"rm", "delete", "--force", "-f", "sudo", "su"}
        command_args = set(command)

        if command_args & dangerous_args:
            result["safe"] = False
            result["issues"].append("Dangerous arguments detected")

        # Check working directory
        if working_dir and not working_dir.exists():
            result["safe"] = False
            result["issues"].append("Working directory does not exist")

        return result

    def validate_poetry_operation(
        self,
        project_path: Path,
        operation: str,
        packages: list[str] | None = None,
    ) -> dict[str, object]:
        """Validate specific Poetry operation.

        Args:
            project_path: Project path
            operation: Operation type (add, remove, update, install)
            packages: List of packages (if applicable)

        Returns:
            Dict with validation result

        """
        result: dict[str, object] = {
            "safe": True,
            "project": str(project_path),
            "operation": operation,
            "issues": [],
            "recommendations": [],
        }

        # Check if Poetry project is valid
        pyproject_path = project_path / "pyproject.toml"
        if not pyproject_path.exists():
            result["safe"] = False
            result["issues"].append("pyproject.toml not found")
            return result

        try:
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)

            if "tool" not in data or "poetry" not in data["tool"]:
                result["safe"] = False
                issues_list = result["issues"]
                if isinstance(issues_list, list):
                    issues_list.append(
                        "Poetry configuration not found in pyproject.toml",
                    )
                return result

        except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
            result["safe"] = False
            issues_list = result["issues"]
            if isinstance(issues_list, list):
                issues_list.append(f"Error reading pyproject.toml: {e}")
            return result

        # Validate packages if provided
        if packages:
            for package in packages:
                package_validation = self.validate_package_safety(package)
                if not package_validation["safe"]:
                    result["safe"] = False
                    package_issues = package_validation["issues"]
                    if isinstance(package_issues, list):
                        issues_list = result["issues"]
                        if isinstance(issues_list, list):
                            issues_list.extend(
                                [
                                    f"Package '{package}': {issue}"
                                    for issue in package_issues
                                ],
                            )

        # Specific recommendations by operation
        if operation == "add":
            result["recommendations"].append("Check version compatibility")
        elif operation == "update":
            result["recommendations"].append("Create backup before updating")
        elif operation == "remove":
            result["recommendations"].append("Check dependencies before removing")

        return result

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

    def get_safety_recommendations(
        self,
        operation_type: str,
        _context: dict[str, object],
    ) -> list[str]:
        """Get security recommendations for an operation.

        Args:
            operation_type: Operation type
            context: Operation context

        Returns:
            List of recommendations

        """
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
