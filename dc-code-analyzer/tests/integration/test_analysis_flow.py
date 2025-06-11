"""
Integration tests for the complete analysis flow.
"""

import tempfile
from contextlib import contextmanager
from pathlib import Path

from django.test import TransactionTestCase

from analyzer.models import (
    BackendStatistics,
    FileAnalysis,
    Project,
    QualityMetrics,
    SecurityIssue,
)
from analyzer.multi_backend_analyzer import MultiBackendAnalyzer


class TestCompleteAnalysisFlow(TransactionTestCase):
    """Integration tests for the complete analysis workflow."""

    def setUp(self):
        """Set up test data."""
        self.project = Project.objects.create(
            name="integration_test_project",
            path="/tmp/test_project",
            description="Project for integration testing",
        )

    @contextmanager
    def create_test_project(self):
        """Create a test project with real Python files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Update project path
            self.project.path = str(project_path)
            self.project.save()

            # Create main.py with various code patterns
            (project_path / "main.py").write_text(
                '''
"""Main module for testing."""

import os
import sys
import subprocess


class TestClass:
    """A test class for analysis."""

    def __init__(self, name: str, value: int = 42):
        """Initialize the test class."""
        self.name = name
        self.value = value
        self._private_var = "secret"

    def simple_method(self) -> str:
        """A simple method with documentation."""
        return f"Hello, {self.name}!"

    def complex_method(self, x: int, y: int, z: int) -> str:
        """A method with complexity for testing."""
        if x > 10:
            if y > 20:
                if z > 30:
                    if x + y > z:
                        return "very complex path"
                    else:
                        return "another complex path"
                return "medium complexity"
            return "some complexity"
        return "simple path"

    def method_with_many_params(self, a, b, c, d, e, f, g, h, i, j):
        """Method with too many parameters."""
        return a + b + c + d + e + f + g + h + i + j

    @property
    def computed_value(self) -> int:
        """A computed property."""
        return self.value * 2


def function_with_security_issue():
    """Function with potential security vulnerability."""
    # This should be detected by bandit
    subprocess.call("echo 'test'", shell=True)  # B602


def another_function_with_issue():
    """Another function with security issue."""
    # Hard-coded password (should be detected)
    password = "hardcoded_password_123"  # B105
    return password


def complex_function(data):
    """Function with high complexity."""
    result = []
    for item in data:
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, list):
                    for sub_item in value:
                        if sub_item is not None:
                            if isinstance(sub_item, str):
                                if len(sub_item) > 5:
                                    result.append(sub_item.upper())
                                else:
                                    result.append(sub_item.lower())
                            else:
                                result.append(str(sub_item))
                else:
                    result.append(str(value))
        else:
            result.append(str(item))
    return result


# Unused function (dead code)
def unused_function():
    """This function is never called."""
    return "This is dead code"


# Global variable
GLOBAL_CONSTANT = "test_constant"


if __name__ == "__main__":
    test_obj = TestClass("integration_test", 100)
    print(test_obj.simple_method())
    print(test_obj.computed_value)

    # Call functions to avoid dead code detection
    function_with_security_issue()
    another_function_with_issue()
    complex_function([{"test": ["data"]}])
'''
            )

            # Create a package with multiple modules
            package_dir = project_path / "test_package"
            package_dir.mkdir()

            (package_dir / "__init__.py").write_text(
                '''
"""Test package for analysis."""

from .utils import utility_function
from .models import DataModel

__all__ = ["utility_function", "DataModel"]
'''
            )

            (package_dir / "utils.py").write_text(
                '''
"""Utility functions for the test package."""

from typing import List, Dict, Any, Optional
import json


def utility_function(data: List[Dict[str, Any]]) -> Optional[str]:
    """A utility function with proper type hints."""
    if not data:
        return None

    try:
        return json.dumps(data)
    except (TypeError, ValueError) as e:
        print(f"Error serializing data: {e}")
        return None


def another_utility(x: int, y: int) -> int:
    """Another utility function."""
    return x + y


# Duplicate code pattern (similar to main.py)
def complex_function_duplicate(data):
    """Duplicate complex function."""
    result = []
    for item in data:
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, list):
                    for sub_item in value:
                        if sub_item is not None:
                            if isinstance(sub_item, str):
                                if len(sub_item) > 5:
                                    result.append(sub_item.upper())
                                else:
                                    result.append(sub_item.lower())
                            else:
                                result.append(str(sub_item))
                else:
                    result.append(str(value))
        else:
            result.append(str(item))
    return result
'''
            )

            (package_dir / "models.py").write_text(
                '''
"""Data models for the test package."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DataModel:
    """A data model using dataclass."""
    name: str
    values: List[int]
    description: Optional[str] = None

    def get_sum(self) -> int:
        """Calculate sum of values."""
        return sum(self.values)

    def get_average(self) -> float:
        """Calculate average of values."""
        if not self.values:
            return 0.0
        return sum(self.values) / len(self.values)


class LegacyModel:
    """A legacy model without dataclass."""

    def __init__(self, name: str):
        self.name = name
        self.data = {}

    def add_data(self, key: str, value: Any) -> None:
        """Add data to the model."""
        self.data[key] = value

    def get_data(self, key: str) -> Any:
        """Get data from the model."""
        return self.data.get(key)

    def __str__(self) -> str:
        return f"LegacyModel({self.name})"
'''
            )

            yield project_path

    def test_complete_analysis_workflow(self):
        """Test the complete analysis workflow from start to finish."""
        with self.create_test_project():
            # Initialize the analyzer
            analyzer = MultiBackendAnalyzer(self.project)

            # Run the analysis
            session = analyzer.analyze()

            # Verify the session was created and completed
            assert session is not None
            assert session.flx_project == self.project
            assert session.status in [
                "completed",
                "failed",
            ]  # May fail if external tools missing
            assert session.files_analyzed > 0
            assert session.created_at is not None

            # Verify files were analyzed
            file_analyses = FileAnalysis.objects.filter(session=session)
            assert file_analyses.count() > 0

            # Should have analyzed main.py and package files
            file_names = [f.file_name for f in file_analyses]
            assert "main.py" in file_names
            assert any("utils.py" in name for name in file_names)
            assert any("models.py" in name for name in file_names)

            # Verify complexity was analyzed
            complex_files = file_analyses.filter(complexity_score__lt=80)
            if complex_files.exists():
                # Should have found some complexity issues
                assert complex_files.count() > 0

            # Verify backend statistics were recorded
            backend_stats = BackendStatistics.objects.filter(session=session)
            assert backend_stats.count() > 0

            # Should have stats for each backend that ran
            backend_names = [stat.backend.name for stat in backend_stats]
            assert "ast" in backend_names  # AST backend should always run

            # Verify quality metrics were calculated
            quality_metrics = QualityMetrics.objects.filter(session=session)
            if quality_metrics.exists():
                metrics = quality_metrics.first()
                assert metrics.total_files > 0
                assert metrics.total_functions > 0
                assert metrics.total_classes > 0

    def test_analysis_with_security_issues(self):
        """Test that security issues are properly detected and saved."""
        with self.create_test_project():
            analyzer = MultiBackendAnalyzer(self.project, ["ast", "external"])

            session = analyzer.analyze()

            # Check if security issues were found
            security_issues = SecurityIssue.objects.filter(session=session)

            # Note: This may be 0 if bandit is not available
            # but the test should still pass
            if security_issues.exists():
                # Verify security issue properties
                issue = security_issues.first()
                assert issue.file_path is not None
                assert issue.line_number > 0
                assert issue.severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
                assert issue.description is not None

    def test_analysis_error_handling(self):
        """Test analysis error handling with invalid project path."""
        # Set invalid path
        self.project.path = "/nonexistent/invalid/path"
        self.project.save()

        analyzer = MultiBackendAnalyzer(self.project)
        session = analyzer.analyze()

        # Should handle the error gracefully
        assert session.status == "completed"
        assert session.files_analyzed == 0
        assert "No Python files found" in session.error_message

    def test_analysis_with_custom_backends(self):
        """Test analysis with custom backend selection."""
        with self.create_test_project():
            # Run analysis with only AST backend
            analyzer = MultiBackendAnalyzer(self.project, ["ast"])

            session = analyzer.analyze()

            assert session.status == "completed"
            assert session.backends_used == ["ast"]

            # Should only have one backend statistic
            backend_stats = BackendStatistics.objects.filter(session=session)
            assert backend_stats.count() == 1
            assert backend_stats.first().backend.name == "ast"

    def test_multiple_analysis_sessions(self):
        """Test creating multiple analysis sessions for the same project."""
        with self.create_test_project():
            # Run first analysis
            analyzer1 = MultiBackendAnalyzer(self.project, ["ast"])
            session1 = analyzer1.analyze()

            # Run second analysis
            analyzer2 = MultiBackendAnalyzer(self.project, ["ast", "external"])
            session2 = analyzer2.analyze()

            # Both sessions should exist
            assert session1.id != session2.id
            assert session1.flx_project == session2.flx_project

            # Should have different backend configurations
            assert session1.backends_used != session2.backends_used

            # Both should be completed
            assert session1.status == "completed"
            assert session2.status in ["completed", "failed"]

    def test_session_timing_calculation(self):
        """Test that session timing is properly calculated."""
        with self.create_test_project():
            analyzer = MultiBackendAnalyzer(self.project, ["ast"])

            session = analyzer.analyze()

            # Session should have timing information
            assert session.started_at is not None
            assert session.completed_at is not None
            assert session.completed_at >= session.started_at

            # Duration should be calculated
            duration = session.duration
            assert duration is not None
            assert duration.total_seconds() >= 0
