"""
Pytest configuration and fixtures for the dc-code-analyzer project.
"""

import os
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import django
import pytest
from django.core.management import call_command
from django.test import override_settings

# Configure Django settings for tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")


def pytest_configure(config: Any) -> None:
    """Configure pytest and Django."""
    django.setup()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up the test database."""
    with django_db_blocker.unblock():
        call_command("migrate", "--run-syncdb")


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Create a temporary directory with some Python files for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Create a simple Python project structure
        (project_path / "main.py").write_text(
            '''
"""Main module for testing."""

import os
import sys


class TestClass:
    """A test class."""

    def __init__(self, name: str):
        self.name = name
        self.value = 42

    def method_with_complexity(self, x: int) -> str:
        """Method with some complexity."""
        if x > 10:
            if x > 20:
                if x > 30:
                    return "high"
                return "medium-high"
            return "medium"
        return "low"

    def simple_method(self) -> str:
        """Simple method."""
        return f"Hello, {self.name}!"


def function_with_security_issue():
    """Function with potential security issue."""
    import subprocess
    subprocess.call("echo test", shell=True)  # B602: subprocess_popen_with_shell_equals_true


def complex_function(a, b, c, d, e, f, g, h):
    """Function with too many parameters."""
    result = 0
    for i in range(a):
        for j in range(b):
            for k in range(c):
                if i + j + k > d:
                    if e > f:
                        if g > h:
                            result += 1
                        else:
                            result -= 1
                    else:
                        result *= 2
                else:
                    result //= 2
    return result


# Unused function for dead code detection
def unused_function():
    """This function is never called."""
    return "dead code"


if __name__ == "__main__":
    test_obj = TestClass("test")
    print(test_obj.simple_method())
'''
        )

        # Create a package with __init__.py
        package_dir = project_path / "test_package"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text('"""Test package."""\n')

        (package_dir / "module.py").write_text(
            '''
"""Test module in package."""

from typing import List, Dict, Any


class DataProcessor:
    """Class for processing data."""

    def __init__(self):
        self.data: List[Dict[str, Any]] = []

    def add_item(self, item: Dict[str, Any]) -> None:
        """Add an item to the data."""
        self.data.append(item)

    def process_data(self) -> List[str]:
        """Process the data."""
        results = []
        for item in self.data:
            if "name" in item:
                results.append(item["name"])
        return results


# Duplicate code block (similar to main.py)
def method_with_complexity(x: int) -> str:
    """Method with some complexity (duplicate)."""
    if x > 10:
        if x > 20:
            if x > 30:
                return "high"
            return "medium-high"
        return "medium"
    return "low"
'''
        )

        yield project_path


@pytest.fixture
def sample_python_files(temp_project_dir: Path) -> list[Path]:
    """Get list of Python files in the test project."""
    return list(temp_project_dir.rglob("*.py"))


@pytest.fixture
def mock_session() -> Any:
    """Create a mock analysis session."""

    class MockSession:
        def __init__(self):
            self.id = 1
            self.flx_project = MockProject()

    class MockProject:
        def __init__(self):
            self.id = 1
            self.name = "test_project"

    return MockSession()


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
@pytest.fixture
def celery_settings():
    """Configure Celery for testing."""
    pass


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Give all tests access to the database.

    By default, pytest-django only allows database access in tests marked with
    @pytest.mark.django_db. This fixture enables it for all tests.
    """
    pass


# Remove the migrate_database fixture - let pytest-django handle it


@pytest.fixture
def populate_backends():
    """Populate the database with backend and issue type data."""
    call_command("populate_backends", force=True, verbosity=0)


# Test data fixtures
@pytest.fixture
def sample_analysis_result():
    """Create a sample AnalysisResult for testing."""
    from analyzer.backends.base import AnalysisResult

    result = AnalysisResult()

    # Add sample packages
    result.packages.extend(
        [
            {
                "name": "__main__",
                "full_path": "/test",
                "python_files_count": 1,
                "total_lines": 30,
                "code_lines": 25,
                "comment_lines": 3,
                "blank_lines": 2,
                "avg_complexity": 4.0,
                "max_complexity": 4.0,
                "total_functions": 1,
                "total_classes": 1,
            },
            {
                "name": "test_package",
                "full_path": "/test/test_package",
                "python_files_count": 2,
                "total_lines": 50,
                "code_lines": 40,
                "comment_lines": 5,
                "blank_lines": 5,
                "avg_complexity": 3.5,
                "max_complexity": 8.0,
                "total_functions": 4,
                "total_classes": 2,
            }
        ]
    )

    # Add sample files
    result.files.extend(
        [
            {
                "file_path": "/test/main.py",
                "file_name": "main.py",
                "lines_of_code": 30,
                "comment_lines": 3,
                "blank_lines": 5,
                "complexity_score": 75.0,
                "maintainability_score": 80.0,
                "function_count": 3,
                "class_count": 1,
            },
            {
                "file_path": "/test/test_package/module.py",
                "file_name": "module.py",
                "lines_of_code": 20,
                "comment_lines": 2,
                "blank_lines": 3,
                "complexity_score": 85.0,
                "maintainability_score": 90.0,
                "function_count": 3,
                "class_count": 1,
            },
        ]
    )

    # Add sample classes
    result.classes.extend(
        [
            {
                "name": "TestClass",
                "full_name": "main.TestClass",
                "file_path": "/test/main.py",
                "package_name": "__main__",
                "line_start": 8,
                "line_end": 25,
                "lines_of_code": 17,
                "method_count": 3,
                "property_count": 0,
                "class_method_count": 0,
                "static_method_count": 0,
                "base_classes": [],
                "inheritance_depth": 0,
                "has_docstring": True,
                "docstring_length": 15,
                "is_abstract": False,
                "is_dataclass": False,
            }
        ]
    )

    # Add sample functions
    result.functions.extend(
        [
            {
                "name": "method_with_complexity",
                "full_name": "main.TestClass.method_with_complexity",
                "file_path": "/test/main.py",
                "package_name": "__main__",
                "class_name": "main.TestClass",
                "function_type": "method",
                "line_start": 13,
                "line_end": 22,
                "lines_of_code": 9,
                "parameter_count": 2,
                "return_statement_count": 4,
                "cyclomatic_complexity": 4,
                "complexity_level": "medium",
                "has_docstring": True,
                "has_type_hints": True,
                "docstring_length": 30,
            }
        ]
    )

    # Add sample security issues
    result.security_issues.extend(
        [
            {
                "file_path": "/test/main.py",
                "line_number": 32,
                "issue_type": "B602",
                "test_id": "B602",
                "severity": "HIGH",
                "confidence": "HIGH",
                "description": "subprocess call with shell=True identified, security issue.",
                "recommendation": "Use subprocess with shell=False or consider using shlex.quote().",
                "code_snippet": 'subprocess.call("echo test", shell=True)',
            }
        ]
    )

    return result


@pytest.fixture
def project_factory():
    """Factory for creating test projects."""

    def _create_project(name: str = "test_project", path: str = "/test/path"):
        from analyzer.models import Project

        return Project.objects.create(
            name=name,
            description=f"Test project: {name}",
            path=path,
            package_name=name.replace("-", "_"),
            package_version="1.0.0",
            package_type="local",
            total_files=10,
            total_lines=500,
            python_files=8,
        )

    return _create_project


@pytest.fixture
def session_factory():
    """Factory for creating test analysis sessions."""
    import uuid

    def _create_session(project=None, status="completed"):
        from analyzer.models import AnalysisSession

        if project is None:
            from analyzer.models import Project

            # Create unique project name to avoid conflicts
            unique_name = f"test_project_{uuid.uuid4().hex[:8]}"
            project = Project.objects.create(name=unique_name, path="/test/path")

        return AnalysisSession.objects.create(
            flx_project=project,
            status=status,
            include_security=True,
            include_dead_code=True,
            include_duplicates=True,
            overall_score=75.5,
            quality_grade="B",
        )

    return _create_session
