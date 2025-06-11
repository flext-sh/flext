"""
Unit tests for the MultiBackendAnalyzer.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from analyzer.backends.base import AnalysisResult
from analyzer.models import AnalysisSession, BackendStatistics
from analyzer.multi_backend_analyzer import MultiBackendAnalyzer


class TestMultiBackendAnalyzer:
    """Test the MultiBackendAnalyzer class."""

    def test_init_with_default_backends(self, project_factory):
        """Test initializing analyzer with default backends."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        assert analyzer.flx_project == project
        assert analyzer.backend_names == ["ast", "external", "quality"]
        assert analyzer.session is None

    def test_init_with_custom_backends(self, project_factory):
        """Test initializing analyzer with custom backends."""
        project = project_factory()
        custom_backends = ["ast", "quality"]
        analyzer = MultiBackendAnalyzer(project, custom_backends)

        assert analyzer.backend_names == custom_backends

    def test_find_python_files(self, project_factory, temp_project_dir):
        """Test finding Python files in project directory."""
        project = project_factory(path=str(temp_project_dir))
        analyzer = MultiBackendAnalyzer(project)

        python_files = analyzer._find_python_files(temp_project_dir)

        assert len(python_files) > 0
        assert all(f.suffix == ".py" for f in python_files)
        # Should not include hidden or __pycache__ files
        assert all("__pycache__" not in str(f) for f in python_files)
        assert all(
            not any(part.startswith(".") for part in f.parts) for f in python_files
        )

    def test_find_python_files_error_handling(self, project_factory):
        """Test error handling when directory doesn't exist."""
        project = project_factory(path="/nonexistent/path")
        analyzer = MultiBackendAnalyzer(project)

        python_files = analyzer._find_python_files(Path("/nonexistent/path"))

        # Should handle error gracefully and return empty list
        assert python_files == []

    def test_get_or_create_backend_model(self, project_factory):
        """Test getting or creating backend models."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        # Should create new backend model
        backend_model = analyzer._get_or_create_backend_model("test_backend")

        assert backend_model.name == "test_backend"
        assert backend_model.display_name == "Test_backend"
        assert backend_model.is_active is True

        # Should get existing backend model
        existing_model = analyzer._get_or_create_backend_model("test_backend")
        assert existing_model.id == backend_model.id

    @patch("analyzer.multi_backend_analyzer.get_backend")
    def test_analyze_successful(
        self, mock_get_backend, project_factory, temp_project_dir
    ):
        """Test successful analysis with all backends."""
        project = project_factory(path=str(temp_project_dir))
        analyzer = MultiBackendAnalyzer(project, ["ast"])

        # Mock backend
        mock_backend_class = Mock()
        mock_backend_instance = Mock()
        mock_backend_class.return_value = mock_backend_instance
        mock_backend_instance.is_available.return_value = True

        # Mock analysis result
        mock_result = AnalysisResult()
        mock_result.files = [{"file_path": "test.py", "file_name": "test.py"}]
        mock_result.security_issues = [{"file_path": "test.py", "issue": "test"}]
        mock_backend_instance.analyze.return_value = mock_result

        mock_get_backend.return_value = mock_backend_class

        session = analyzer.analyze()

        assert session.status == "completed"
        assert session.flx_project == project
        assert session.files_analyzed > 0
        assert session.backends_used == ["ast"]

        # Verify backend was called
        mock_backend_instance.analyze.assert_called_once()

    @patch("analyzer.multi_backend_analyzer.get_backend")
    def test_analyze_backend_not_available(
        self, mock_get_backend, project_factory, temp_project_dir
    ):
        """Test analysis when backend is not available."""
        project = project_factory(path=str(temp_project_dir))
        analyzer = MultiBackendAnalyzer(project, ["unavailable_backend"])

        # Mock backend that's not available
        mock_backend_class = Mock()
        mock_backend_instance = Mock()
        mock_backend_class.return_value = mock_backend_instance
        mock_backend_instance.is_available.return_value = False

        mock_get_backend.return_value = mock_backend_class

        session = analyzer.analyze()

        assert session.status == "completed"
        # Backend should not have been called for analysis
        mock_backend_instance.analyze.assert_not_called()

        # Should have backend statistics showing it was skipped
        stats = BackendStatistics.objects.filter(session=session).first()
        assert stats is not None
        assert stats.status == "skipped"

    @patch("analyzer.multi_backend_analyzer.get_backend")
    def test_analyze_backend_failure(
        self, mock_get_backend, project_factory, temp_project_dir
    ):
        """Test analysis when backend fails."""
        project = project_factory(path=str(temp_project_dir))
        analyzer = MultiBackendAnalyzer(project, ["failing_backend"])

        # Mock backend that fails
        mock_backend_class = Mock()
        mock_backend_instance = Mock()
        mock_backend_class.return_value = mock_backend_instance
        mock_backend_instance.is_available.return_value = True
        mock_backend_instance.analyze.side_effect = Exception("Backend failed")

        mock_get_backend.return_value = mock_backend_class

        session = analyzer.analyze()

        assert (
            session.status == "completed"
        )  # Analysis continues despite backend failure

        # Should have backend statistics showing it failed
        stats = BackendStatistics.objects.filter(session=session).first()
        assert stats is not None
        assert stats.status == "failed"
        assert "Backend failed" in stats.error_message

    def test_analyze_no_python_files(self, project_factory):
        """Test analysis when no Python files are found."""
        # Create temporary directory with no Python files
        with tempfile.TemporaryDirectory() as temp_dir:
            project = project_factory(path=temp_dir)
            analyzer = MultiBackendAnalyzer(project)

            session = analyzer.analyze()

            assert session.status == "completed"
            assert session.files_analyzed == 0
            assert "No Python files found" in session.error_message

    @patch("analyzer.multi_backend_analyzer.get_backend")
    def test_analyze_general_failure(self, mock_get_backend, project_factory, temp_project_dir):
        """Test analysis when general error occurs."""
        project = project_factory(path=str(temp_project_dir))
        analyzer = MultiBackendAnalyzer(project)

        # Mock get_backend to raise exception
        mock_get_backend.side_effect = Exception("General failure")

        session = analyzer.analyze()

        assert session.status == "failed"
        assert "All backends failed to execute" in session.error_message

    def test_save_packages(self, project_factory, sample_analysis_result):
        """Test saving package analysis data."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        # Create a session
        analyzer.session = AnalysisSession.objects.create(flx_project=project)

        package_objects = analyzer._save_packages(sample_analysis_result)

        assert len(package_objects) == len(sample_analysis_result.packages)
        assert "test_package" in package_objects

        package = package_objects["test_package"]
        assert package.name == "test_package"
        assert package.python_files_count == 2
        assert package.total_functions == 4

    def test_save_files(self, project_factory, sample_analysis_result):
        """Test saving file analysis data."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        # Create a session
        analyzer.session = AnalysisSession.objects.create(flx_project=project)

        package_objects = analyzer._save_packages(sample_analysis_result)
        file_objects = analyzer._save_files(sample_analysis_result, package_objects)

        assert len(file_objects) == len(sample_analysis_result.files)
        assert "/test/main.py" in file_objects

        file_obj = file_objects["/test/main.py"]
        assert file_obj.file_name == "main.py"
        assert file_obj.lines_of_code == 30
        assert file_obj.complexity_score == 75.0

    def test_save_classes(self, project_factory, sample_analysis_result):
        """Test saving class analysis data."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        # Create a session
        analyzer.session = AnalysisSession.objects.create(flx_project=project)

        package_objects = analyzer._save_packages(sample_analysis_result)
        file_objects = analyzer._save_files(sample_analysis_result, package_objects)
        class_objects = analyzer._save_classes(
            sample_analysis_result, file_objects, package_objects
        )

        assert len(class_objects) == len(sample_analysis_result.classes)
        assert "main.TestClass" in class_objects

        class_obj = class_objects["main.TestClass"]
        assert class_obj.name == "TestClass"
        assert class_obj.method_count == 3
        assert class_obj.has_docstring is True

    def test_save_functions(self, project_factory, sample_analysis_result):
        """Test saving function analysis data."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        # Create a session and save prerequisite data
        analyzer.session = AnalysisSession.objects.create(flx_project=project)

        package_objects = analyzer._save_packages(sample_analysis_result)
        file_objects = analyzer._save_files(sample_analysis_result, package_objects)
        class_objects = analyzer._save_classes(
            sample_analysis_result, file_objects, package_objects
        )

        # Save functions
        analyzer._save_functions(
            sample_analysis_result, file_objects, package_objects, class_objects
        )

        # Verify functions were saved
        from analyzer.models import FunctionAnalysis

        functions = FunctionAnalysis.objects.filter(
            file_analysis__session=analyzer.session
        )

        assert functions.count() == len(sample_analysis_result.functions)

        function = functions.first()
        assert function.name == "method_with_complexity"
        assert function.cyclomatic_complexity == 4
        assert function.has_type_hints is True

    def test_save_security_issues(self, project_factory, sample_analysis_result):
        """Test saving security issues."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        # Create a session
        analyzer.session = AnalysisSession.objects.create(flx_project=project)

        analyzer._save_security_issues(sample_analysis_result)

        # Verify security issues were saved
        from analyzer.models import SecurityIssue

        issues = SecurityIssue.objects.filter(session=analyzer.session)

        assert issues.count() == len(sample_analysis_result.security_issues)

        issue = issues.first()
        assert issue.issue_type == "B602"
        assert issue.severity == "HIGH"
        assert issue.line_number == 32

    def test_save_quality_metrics(self, project_factory, sample_analysis_result):
        """Test saving quality metrics."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        # Create a session
        analyzer.session = AnalysisSession.objects.create(flx_project=project)

        analyzer._save_quality_metrics(sample_analysis_result)

        # Verify quality metrics were saved
        from analyzer.models import QualityMetrics

        metrics = QualityMetrics.objects.filter(session=analyzer.session)

        assert metrics.count() == 1

        metric = metrics.first()
        assert metric.total_files == len(sample_analysis_result.files)
        assert metric.total_functions == len(sample_analysis_result.functions)
        assert metric.security_issues_count == len(
            sample_analysis_result.security_issues
        )

    def test_find_file_object(self, project_factory):
        """Test finding file objects for data items."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        file_objects = {
            "/test/main.py": Mock(file_path="/test/main.py"),
            "/test/module.py": Mock(file_path="/test/module.py"),
        }

        # Test direct file_path match
        data = {"file_path": "/test/main.py"}
        result = analyzer._find_file_object(file_objects, data)
        assert result == file_objects["/test/main.py"]

        # Test no match
        data = {"file_path": "/test/nonexistent.py"}
        result = analyzer._find_file_object(file_objects, data)
        assert result is None

        # Test match by full_name pattern
        data = {"full_name": "main.TestClass"}
        result = analyzer._find_file_object(file_objects, data)
        assert result == file_objects["/test/main.py"]

    def test_find_package_object(self, project_factory):
        """Test finding package objects for data items."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        package_objects = {
            "test_package": Mock(name="test_package"),
            "__main__": Mock(name="__main__"),
        }

        # Test direct package_name match
        data = {"package_name": "test_package"}
        result = analyzer._find_package_object(package_objects, data)
        assert result == package_objects["test_package"]

        # Test extraction from full_name
        data = {"full_name": "test_package.TestClass"}
        result = analyzer._find_package_object(package_objects, data)
        assert result == package_objects["test_package"]

        # Test fallback to __main__
        data = {"full_name": "SomeFunction"}
        result = analyzer._find_package_object(package_objects, data)
        assert result == package_objects["__main__"]

    def test_save_detected_issues(
        self, project_factory, sample_analysis_result, populate_backends
    ):
        """Test saving detected issues with new DetectedIssue model."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        # Create a session and save prerequisite data
        analyzer.session = AnalysisSession.objects.create(flx_project=project)

        package_objects = analyzer._save_packages(sample_analysis_result)
        file_objects = analyzer._save_files(sample_analysis_result, package_objects)

        analyzer._save_detected_issues(sample_analysis_result, file_objects)

        # Verify detected issues were saved
        from analyzer.models import DetectedIssue

        issues = DetectedIssue.objects.filter(session=analyzer.session)

        assert issues.count() >= len(sample_analysis_result.security_issues)

        if issues.exists():
            issue = issues.first()
            assert issue.file_path is not None
            assert issue.issue_type is not None

    def test_extract_issue_code(self, project_factory):
        """Test extracting issue codes from issue data."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        # Test with test_id
        issue_data = {"test_id": "B602"}
        code = analyzer._extract_issue_code(issue_data, "external")
        assert code == "B602"

        # Test with issue_type
        issue_data = {"issue_type": "security_issue"}
        code = analyzer._extract_issue_code(issue_data, "external")
        assert code == "security_issue"

        # Test with code field
        issue_data = {"code": "CUSTOM001"}
        code = analyzer._extract_issue_code(issue_data, "external")
        assert code == "CUSTOM001"

        # Test fallback for external backend
        issue_data = {}
        code = analyzer._extract_issue_code(issue_data, "external")
        assert code == "EXT001"

        # Test fallback for other backends
        code = analyzer._extract_issue_code({}, "quality")
        assert code == "Q001"

        code = analyzer._extract_issue_code({}, "ast")
        assert code == "AST001"

        code = analyzer._extract_issue_code({}, "unknown")
        assert code == "GEN001"

    def test_get_or_create_issue_type(self, project_factory, populate_backends):
        """Test getting or creating issue types."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        from analyzer.models import AnalysisBackendModel

        backend = AnalysisBackendModel.objects.get(name="external")

        issue_data = {
            "issue_type": "Test Issue",
            "description": "A test issue",
            "severity": "HIGH",
            "recommendation": "Fix it",
        }

        # Should create new issue type
        issue_type = analyzer._get_or_create_issue_type(
            backend_model=backend,
            issue_code="TEST001",
            issue_data=issue_data,
            category="testing",
        )

        assert issue_type.backend == backend
        assert issue_type.code == "TEST001"
        assert issue_type.name == "Test Issue"
        assert issue_type.severity == "HIGH"

        # Should get existing issue type
        existing_type = analyzer._get_or_create_issue_type(
            backend_model=backend,
            issue_code="TEST001",
            issue_data=issue_data,
            category="testing",
        )

        assert existing_type.id == issue_type.id

    def test_save_backend_statistics(self, project_factory, populate_backends):
        """Test saving backend execution statistics."""
        project = project_factory()
        analyzer = MultiBackendAnalyzer(project)

        # Create a session
        analyzer.session = AnalysisSession.objects.create(flx_project=project)

        from analyzer.models import AnalysisBackendModel

        backend_model = AnalysisBackendModel.objects.get(name="ast")

        # Create mock result with security issues
        mock_result = AnalysisResult()
        mock_result.security_issues = [
            {"severity": "HIGH"},
            {"severity": "MEDIUM"},
        ]
        mock_result.errors = [
            {"backend": "ast", "error": "test error"},
        ]

        backend_stats = {
            "ast": {
                "backend_model": backend_model,
                "execution_time": 15.5,
                "files_processed": 10,
                "issues_found": 3,
                "status": "success",
                "error_message": "",
                "result": mock_result,
            }
        }

        analyzer._save_backend_statistics(backend_stats)

        # Verify statistics were saved
        stats = BackendStatistics.objects.filter(
            session=analyzer.session, backend=backend_model
        )

        assert stats.count() == 1

        stat = stats.first()
        assert stat.execution_time == 15.5
        assert stat.files_processed == 10
        assert stat.issues_found == 3
        assert stat.status == "success"
        assert stat.issues_by_severity == {"HIGH": 1, "MEDIUM": 1, "ERROR": 1}
        assert stat.issues_by_category == {"security": 2, "system": 1}
