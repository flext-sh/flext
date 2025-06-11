"""
Unit tests for Django models.
"""

import pytest
from django.db import IntegrityError
from django.utils import timezone

from analyzer.models import (
    AnalysisBackendModel,
    AnalysisSession,
    BackendStatistics,
    ClassAnalysis,
    DetectedIssue,
    FileAnalysis,
    FunctionAnalysis,
    IssueType,
    PackageAnalysis,
    Project,
    QualityMetrics,
    SecurityIssue,
)


@pytest.mark.django_db
class TestProject:
    """Test the Project model."""

    def test_create_project(self):
        """Test creating a project."""
        project = Project.objects.create(
            name="test_project",
            description="A test project",
            path="/path/to/project",
            package_name="test_package",
            package_version="1.0.0",
            package_type="local",
            total_files=10,
            total_lines=500,
            python_files=8,
        )

        assert project.name == "test_project"
        assert project.description == "A test project"
        assert project.path == "/path/to/project"
        assert project.package_name == "test_package"
        assert project.package_version == "1.0.0"
        assert project.package_type == "local"
        assert project.total_files == 10
        assert project.total_lines == 500
        assert project.python_files == 8
        assert project.created_at is not None
        assert project.updated_at is not None

    def test_project_str_representation(self):
        """Test project string representation."""
        project = Project.objects.create(name="test_project", path="/test")
        assert str(project) == "test_project"

    def test_project_unique_name(self):
        """Test that project names must be unique."""
        Project.objects.create(name="duplicate", path="/test1")

        with pytest.raises(IntegrityError):
            Project.objects.create(name="duplicate", path="/test2")

    def test_project_package_type_choices(self):
        """Test package type choices."""
        valid_types = ["source", "wheel", "system", "local"]

        for package_type in valid_types:
            project = Project.objects.create(
                name=f"test_{package_type}",
                path="/test",
                package_type=package_type,
            )
            assert project.package_type == package_type


class TestAnalysisSession:
    """Test the AnalysisSession model."""

    def test_create_session(self, project_factory):
        """Test creating an analysis session."""
        project = project_factory()

        session = AnalysisSession.objects.create(
            flx_project=project,
            name="Test Analysis",
            status="completed",
            include_security=True,
            include_dead_code=False,
            complexity_threshold=15.0,
            overall_score=85.5,
            quality_grade="B+",
        )

        assert session.flx_project == project
        assert session.name == "Test Analysis"
        assert session.status == "completed"
        assert session.include_security is True
        assert session.include_dead_code is False
        assert session.complexity_threshold == 15.0
        assert session.overall_score == 85.5
        assert session.quality_grade == "B+"
        assert session.created_at is not None

    def test_session_status_choices(self, project_factory):
        """Test session status choices."""
        project = project_factory()
        valid_statuses = ["pending", "running", "completed", "failed"]

        for status in valid_statuses:
            session = AnalysisSession.objects.create(
                flx_project=project,
                status=status,
            )
            assert session.status == status

    def test_session_grade_choices(self, project_factory):
        """Test session grade choices."""
        project = project_factory()
        valid_grades = [
            "A+",
            "A",
            "A-",
            "B+",
            "B",
            "B-",
            "C+",
            "C",
            "C-",
            "D+",
            "D",
            "F",
        ]

        for grade in valid_grades:
            session = AnalysisSession.objects.create(
                flx_project=project,
                quality_grade=grade,
            )
            assert session.quality_grade == grade

    def test_session_duration_property(self, project_factory):
        """Test session duration calculation."""
        project = project_factory()

        # Session without timing
        session = AnalysisSession.objects.create(flx_project=project)
        assert session.duration is None

        # Session with timing
        started = timezone.now()
        completed = started + timezone.timedelta(seconds=120)

        session = AnalysisSession.objects.create(
            flx_project=project,
            started_at=started,
            completed_at=completed,
        )
        assert session.duration == timezone.timedelta(seconds=120)

    def test_session_backends_used_json_field(self, project_factory):
        """Test backends_used JSON field."""
        project = project_factory()

        backends = ["ast", "external", "quality"]
        session = AnalysisSession.objects.create(
            flx_project=project,
            backends_used=backends,
        )

        assert session.backends_used == backends

    def test_session_cascade_delete(self):
        """Test that sessions are deleted when project is deleted."""
        project = Project.objects.create(name="test_project", path="/test")
        session = AnalysisSession.objects.create(flx_project=project)

        project_id = project.id
        session_id = session.id

        project.delete()

        assert not Project.objects.filter(id=project_id).exists()
        assert not AnalysisSession.objects.filter(id=session_id).exists()


class TestAnalysisBackendModel:
    """Test the AnalysisBackendModel."""

    def test_create_backend(self):
        """Test creating a backend model."""
        backend = AnalysisBackendModel.objects.create(
            name="test_backend",
            display_name="Test Backend",
            description="A backend for testing",
            version="1.0.0",
            is_active=True,
            is_available=True,
            default_enabled=True,
            execution_order=10,
            capabilities=["test_analysis"],
        )

        assert backend.name == "test_backend"
        assert backend.display_name == "Test Backend"
        assert backend.description == "A backend for testing"
        assert backend.version == "1.0.0"
        assert backend.is_active is True
        assert backend.is_available is True
        assert backend.default_enabled is True
        assert backend.execution_order == 10
        assert backend.capabilities == ["test_analysis"]

    def test_backend_unique_name(self):
        """Test that backend names must be unique."""
        AnalysisBackendModel.objects.create(name="duplicate", display_name="First")

        with pytest.raises(IntegrityError):
            AnalysisBackendModel.objects.create(name="duplicate", display_name="Second")

    def test_backend_str_representation(self):
        """Test backend string representation."""
        backend = AnalysisBackendModel.objects.create(
            name="test",
            display_name="Test Backend",
        )
        assert str(backend) == "Test Backend (Active)"


class TestIssueType:
    """Test the IssueType model."""

    def test_create_issue_type(self, populate_backends):
        """Test creating an issue type."""
        backend = AnalysisBackendModel.objects.get(name="ast")

        issue_type = IssueType.objects.create(
            backend=backend,
            code="TEST001",
            name="Test Issue",
            description="A test issue type",
            category="testing",
            severity="MEDIUM",
            recommendation="Fix the test issue",
        )

        assert issue_type.backend == backend
        assert issue_type.code == "TEST001"
        assert issue_type.name == "Test Issue"
        assert issue_type.category == "testing"
        assert issue_type.severity == "MEDIUM"

    def test_issue_type_unique_constraint(self, populate_backends):
        """Test that backend+code combination must be unique."""
        backend = AnalysisBackendModel.objects.get(name="ast")

        IssueType.objects.create(backend=backend, code="DUP001", name="First")

        with pytest.raises(IntegrityError):
            IssueType.objects.create(backend=backend, code="DUP001", name="Second")

    def test_issue_type_severity_choices(self, populate_backends):
        """Test issue type severity choices."""
        backend = AnalysisBackendModel.objects.get(name="ast")
        valid_severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

        for severity in valid_severities:
            issue_type = IssueType.objects.create(
                backend=backend,
                code=f"SEV_{severity}",
                name=f"Severity {severity}",
                severity=severity,
            )
            assert issue_type.severity == severity


class TestFileAnalysis:
    """Test the FileAnalysis model."""

    def test_create_file_analysis(self, session_factory):
        """Test creating a file analysis."""
        session = session_factory()

        file_analysis = FileAnalysis.objects.create(
            session=session,
            file_path="/test/main.py",
            file_name="main.py",
            lines_of_code=100,
            comment_lines=20,
            blank_lines=10,
            complexity_score=75.5,
            maintainability_score=80.0,
            function_count=5,
            class_count=2,
        )

        assert file_analysis.session == session
        assert file_analysis.file_path == "/test/main.py"
        assert file_analysis.file_name == "main.py"
        assert file_analysis.lines_of_code == 100
        assert file_analysis.complexity_score == 75.5
        assert file_analysis.function_count == 5

    def test_file_analysis_str_representation(self, session_factory):
        """Test file analysis string representation."""
        session = session_factory()
        file_analysis = FileAnalysis.objects.create(
            session=session,
            file_path="/path/to/test.py",
            file_name="test.py",
            lines_of_code=100,
            comment_lines=10,
            blank_lines=5,
            complexity_score=75.0,
            maintainability_score=80.0,
            function_count=5,
            class_count=1,
        )
        assert str(file_analysis) == "test.py (LOC: 100)"


class TestSecurityIssue:
    """Test the SecurityIssue model."""

    def test_create_security_issue(self, session_factory):
        """Test creating a security issue."""
        session = session_factory()

        issue = SecurityIssue.objects.create(
            session=session,
            file_path="/test/main.py",
            line_number=42,
            issue_type="B602",
            test_id="B602",
            severity="HIGH",
            confidence="HIGH",
            description="subprocess call with shell=True",
            recommendation="Use shell=False",
            code_snippet='subprocess.call("echo test", shell=True)',
        )

        assert issue.session == session
        assert issue.file_path == "/test/main.py"
        assert issue.line_number == 42
        assert issue.issue_type == "B602"
        assert issue.severity == "HIGH"
        assert issue.confidence == "HIGH"
        assert issue.is_resolved is False

    def test_security_issue_severity_choices(self, session_factory):
        """Test security issue severity choices."""
        session = session_factory()
        valid_severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

        for severity in valid_severities:
            issue = SecurityIssue.objects.create(
                session=session,
                severity=severity,
                confidence="HIGH",
                issue_type=f"TEST_{severity}",
                test_id=f"T{severity[:3]}001",
                file_path="/test/file.py",
                line_number=42,
                description=f"Test {severity} issue",
                recommendation=f"Fix {severity} issue",
            )
            assert issue.severity == severity

    def test_security_issue_resolution(self, session_factory):
        """Test security issue resolution."""
        session = session_factory()
        issue = SecurityIssue.objects.create(
            session=session,
            severity="HIGH",
            confidence="HIGH",
            issue_type="TEST001",
            test_id="T001",
            file_path="/test/file.py",
            line_number=42,
            description="Test security issue",
            recommendation="Fix this issue",
        )

        assert issue.is_resolved is False
        assert issue.resolved_at is None

        # Mark as resolved
        issue.is_resolved = True
        issue.resolved_at = timezone.now()
        issue.resolution_notes = "Fixed the issue"
        issue.save()

        assert issue.is_resolved is True
        assert issue.resolved_at is not None
        assert issue.resolution_notes == "Fixed the issue"


class TestQualityMetrics:
    """Test the QualityMetrics model."""

    def test_create_quality_metrics(self, session_factory):
        """Test creating quality metrics."""
        session = session_factory()

        metrics = QualityMetrics.objects.create(
            session=session,
            overall_score=85.5,
            complexity_score=80.0,
            maintainability_score=90.0,
            security_score=75.0,
            documentation_score=60.0,
            duplication_score=70.0,
            total_files=10,
            total_lines=1000,
            total_functions=50,
            total_classes=15,
            avg_complexity=3.5,
            max_complexity=12.0,
            complex_functions_count=5,
            docstring_coverage=0.6,
            documented_functions=30,
            security_issues_count=2,
            dead_code_items_count=3,
            duplicate_blocks_count=1,
            duplicate_lines_ratio=0.05,
            technical_debt_ratio=0.15,
            estimated_debt_hours=2.5,
        )

        assert metrics.session == session
        assert metrics.overall_score == 85.5
        assert metrics.total_files == 10
        assert metrics.avg_complexity == 3.5
        assert metrics.docstring_coverage == 0.6

    def test_quality_metrics_one_per_session(self, session_factory):
        """Test that only one QualityMetrics per session is allowed."""
        session = session_factory()

        QualityMetrics.objects.create(
            session=session,
            overall_score=80.0,
            complexity_score=75.0,
            maintainability_score=85.0,
            security_score=70.0,
            documentation_score=65.0,
            duplication_score=80.0,
            total_files=5,
            total_lines=500,
            total_functions=25,
            total_classes=8,
            avg_complexity=3.0,
            max_complexity=10.0,
            complex_functions_count=3,
            docstring_coverage=0.5,
            documented_functions=15,
            security_issues_count=1,
            dead_code_items_count=2,
            duplicate_blocks_count=0,
            duplicate_lines_ratio=0.02,
            technical_debt_ratio=0.10,
            estimated_debt_hours=1.5,
        )

        with pytest.raises(IntegrityError):
            QualityMetrics.objects.create(
                session=session,
                overall_score=85.0,
                complexity_score=75.0,
                maintainability_score=85.0,
                security_score=70.0,
                documentation_score=65.0,
                duplication_score=80.0,
                total_files=5,
                total_lines=500,
                total_functions=25,
                total_classes=8,
                avg_complexity=3.0,
                max_complexity=10.0,
                complex_functions_count=3,
                docstring_coverage=0.5,
                documented_functions=15,
                security_issues_count=1,
                dead_code_items_count=2,
                duplicate_blocks_count=0,
                duplicate_lines_ratio=0.02,
                technical_debt_ratio=0.10,
                estimated_debt_hours=1.5,
            )


class TestPackageAnalysis:
    """Test the PackageAnalysis model."""

    def test_create_package_analysis(self, session_factory):
        """Test creating a package analysis."""
        session = session_factory()

        package = PackageAnalysis.objects.create(
            session=session,
            name="test_package",
            full_path="/test/test_package",
            python_files_count=5,
            total_lines=500,
            code_lines=400,
            comment_lines=50,
            blank_lines=50,
            avg_complexity=4.5,
            max_complexity=10.0,
            total_functions=20,
            total_classes=8,
        )

        assert package.name == "test_package"
        assert package.python_files_count == 5
        assert package.avg_complexity == 4.5
        assert package.total_functions == 20

    def test_package_analysis_str_representation(self, session_factory):
        """Test package analysis string representation."""
        session = session_factory()
        package = PackageAnalysis.objects.create(
            session=session,
            name="test_package",
        )
        assert str(package) == "test_package (Files: 0)"


class TestClassAnalysis:
    """Test the ClassAnalysis model."""

    def test_create_class_analysis(self, session_factory):
        """Test creating a class analysis."""
        session = session_factory()
        file_analysis = FileAnalysis.objects.create(
            session=session,
            file_path="/test/test.py",
            file_name="test.py",
            lines_of_code=100,
            comment_lines=10,
            blank_lines=5,
            complexity_score=75.0,
            maintainability_score=80.0,
            function_count=5,
            class_count=1,
        )
        package = PackageAnalysis.objects.create(session=session, name="test_package")

        class_analysis = ClassAnalysis.objects.create(
            file_analysis=file_analysis,
            package_analysis=package,
            name="TestClass",
            full_name="test_package.TestClass",
            line_start=10,
            line_end=50,
            lines_of_code=40,
            method_count=5,
            property_count=2,
            base_classes=["BaseClass"],
            inheritance_depth=1,
            has_docstring=True,
            is_abstract=False,
        )

        assert class_analysis.name == "TestClass"
        assert class_analysis.method_count == 5
        assert class_analysis.has_docstring is True
        assert class_analysis.base_classes == ["BaseClass"]


class TestFunctionAnalysis:
    """Test the FunctionAnalysis model."""

    def test_create_function_analysis(self, session_factory):
        """Test creating a function analysis."""
        session = session_factory()
        file_analysis = FileAnalysis.objects.create(
            session=session,
            file_path="/test/test.py",
            file_name="test.py",
            lines_of_code=100,
            comment_lines=10,
            blank_lines=5,
            complexity_score=75.0,
            maintainability_score=80.0,
            function_count=5,
            class_count=1,
        )
        package = PackageAnalysis.objects.create(session=session, name="test_package")

        function = FunctionAnalysis.objects.create(
            file_analysis=file_analysis,
            package_analysis=package,
            name="test_function",
            full_name="test_package.test_function",
            function_type="function",
            line_start=5,
            line_end=15,
            lines_of_code=10,
            parameter_count=3,
            cyclomatic_complexity=2,
            complexity_level="low",
            has_docstring=True,
            has_type_hints=True,
        )

        assert function.name == "test_function"
        assert function.function_type == "function"
        assert function.parameter_count == 3
        assert function.cyclomatic_complexity == 2
        assert function.has_type_hints is True

    def test_function_type_choices(self, session_factory):
        """Test function type choices."""
        session = session_factory()
        file_analysis = FileAnalysis.objects.create(
            session=session,
            file_path="/test/test.py",
            file_name="test.py",
            lines_of_code=100,
            comment_lines=10,
            blank_lines=5,
            complexity_score=75.0,
            maintainability_score=80.0,
            function_count=5,
            class_count=1,
        )
        package = PackageAnalysis.objects.create(session=session, name="test_package")

        valid_types = ["function", "method", "staticmethod", "classmethod", "property"]

        for func_type in valid_types:
            function = FunctionAnalysis.objects.create(
                file_analysis=file_analysis,
                package_analysis=package,
                name=f"test_{func_type}",
                function_type=func_type,
                line_start=1,
                line_end=5,
            )
            assert function.function_type == func_type


class TestDetectedIssue:
    """Test the DetectedIssue model."""

    def test_create_detected_issue(self, session_factory, populate_backends):
        """Test creating a detected issue."""
        session = session_factory()
        backend = AnalysisBackendModel.objects.get(name="ast")
        issue_type = IssueType.objects.create(
            backend=backend,
            code="TEST001",
            name="Test Issue",
            severity="MEDIUM",
        )

        detected_issue = DetectedIssue.objects.create(
            session=session,
            issue_type=issue_type,
            file_path="/test/main.py",
            line_number=42,
            column=10,
            message="Test issue detected",
            code_snippet="test_code()",
            confidence="HIGH",
            context={"extra": "data"},
            raw_data={"raw": "issue_data"},
        )

        assert detected_issue.session == session
        assert detected_issue.issue_type == issue_type
        assert detected_issue.file_path == "/test/main.py"
        assert detected_issue.line_number == 42
        assert detected_issue.confidence == "HIGH"
        assert detected_issue.context == {"extra": "data"}

    def test_detected_issue_properties(self, session_factory, populate_backends):
        """Test detected issue computed properties."""
        session = session_factory()
        backend = AnalysisBackendModel.objects.get(name="external")
        issue_type = IssueType.objects.create(
            backend=backend,
            code="B602",
            name="Shell Injection",
            category="security",
            severity="HIGH",
        )

        detected_issue = DetectedIssue.objects.create(
            session=session,
            issue_type=issue_type,
            file_path="/test/main.py",
            line_number=42,
            column=10,
            message="Shell injection vulnerability detected",
        )

        assert detected_issue.backend_name == "external"
        assert detected_issue.category == "security"
        assert detected_issue.severity == "HIGH"


class TestBackendStatistics:
    """Test the BackendStatistics model."""

    def test_create_backend_statistics(self, session_factory, populate_backends):
        """Test creating backend statistics."""
        session = session_factory()
        backend = AnalysisBackendModel.objects.get(name="ast")

        stats = BackendStatistics.objects.create(
            session=session,
            backend=backend,
            execution_time=15.5,
            files_processed=10,
            issues_found=5,
            status="success",
            issues_by_severity={"HIGH": 2, "MEDIUM": 3},
            issues_by_category={"security": 3, "quality": 2},
        )

        assert stats.backend == backend
        assert stats.execution_time == 15.5
        assert stats.files_processed == 10
        assert stats.issues_found == 5
        assert stats.status == "success"
        assert stats.issues_by_severity == {"HIGH": 2, "MEDIUM": 3}

    def test_backend_statistics_status_choices(
        self, session_factory, populate_backends
    ):
        """Test backend statistics status choices."""
        backend = AnalysisBackendModel.objects.get(name="ast")
        valid_statuses = ["success", "failed", "skipped"]

        for status in valid_statuses:
            # Create a new session for each status to avoid unique constraint violation
            session = session_factory()
            stats = BackendStatistics.objects.create(
                session=session,
                backend=backend,
                execution_time=10.0,
                files_processed=5,
                issues_found=2,
                status=status,
                issues_by_severity={"HIGH": 1, "MEDIUM": 1},
                issues_by_category={"security": 1, "quality": 1},
            )
            assert stats.status == status
