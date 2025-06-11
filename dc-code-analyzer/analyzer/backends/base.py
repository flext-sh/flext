"""Base class for analysis backends."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AnalysisResult:
    """Container for analysis results from a backend."""

    def __init__(self) -> None:
        self.packages: list[dict[str, Any]] = []
        self.files: list[dict[str, Any]] = []
        self.classes: list[dict[str, Any]] = []
        self.functions: list[dict[str, Any]] = []
        self.variables: list[dict[str, Any]] = []
        self.imports: list[dict[str, Any]] = []
        self.security_issues: list[dict[str, Any]] = []
        self.quality_metrics: dict[str, Any] = {}
        self.errors: list[dict[str, Any]] = []

    def merge(self, other: AnalysisResult) -> None:
        """Merge another result into this one."""
        self.packages.extend(other.packages)
        self.files.extend(other.files)
        self.classes.extend(other.classes)
        self.functions.extend(other.functions)
        self.variables.extend(other.variables)
        self.imports.extend(other.imports)
        self.security_issues.extend(other.security_issues)
        self.quality_metrics.update(other.quality_metrics)
        self.errors.extend(other.errors)


class AnalysisBackend(ABC):
    """Abstract base class for analysis backends."""

    def __init__(self, session: Any, project_path: Path) -> None:
        self.session = session
        self.project_path = project_path
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    @abstractmethod
    def name(self) -> str:
        """Backend name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Backend description."""

    @property
    @abstractmethod
    def capabilities(self) -> list[str]:
        """List of analysis capabilities this backend provides."""

    @abstractmethod
    def analyze(self, python_files: list[Path]) -> AnalysisResult:
        """
        Perform analysis on the given Python files.

        Args:
            python_files: List of Python files to analyze

        Returns:
            AnalysisResult object containing all analysis data
        """

    def is_available(self) -> bool:
        """Check if this backend is available (dependencies installed, etc.)."""
        return True

    def get_configuration(self) -> dict[str, Any]:
        """Get backend configuration options."""
        return {}

    def validate_configuration(self, _config: dict[str, Any]) -> bool:
        """Validate backend configuration."""
        return True

    def _find_python_files(self, path: Path) -> list[Path]:
        """Find all Python files in a directory."""
        python_files = []
        try:
            for py_file in path.rglob("*.py"):
                # Skip hidden files and directories
                if not any(part.startswith(".") for part in py_file.parts):
                    python_files.append(py_file)
        except Exception as e:
            self.logger.exception(f"Error finding Python files in {path}: {e}")

        return python_files

    def _get_relative_path(self, file_path: Path) -> str:
        """Get path relative to flx_project root."""
        try:
            return str(file_path.relative_to(self.project_path))
        except ValueError:
            return str(file_path)

    def _get_package_name(self, file_path: Path) -> str:
        """Extract package name from file path."""
        try:
            relative_path = file_path.relative_to(self.project_path)
            parts = list(relative_path.parts[:-1])  # Remove filename
            if parts and parts[-1] == "__pycache__":
                parts = parts[:-1]
            return ".".join(parts) if parts else "__main__"
        except ValueError:
            return "__main__"
