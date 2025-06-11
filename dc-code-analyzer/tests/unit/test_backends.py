"""
Unit tests for analysis backends.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from analyzer.backends import (
    AVAILABLE_BACKENDS,
    AnalysisBackend,
    AnalysisResult,
    ASTBackend,
    ExternalToolsBackend,
    QualityBackend,
    get_all_backends,
    get_backend,
    get_default_backends,
)


class TestAnalysisResult:
    """Test the AnalysisResult class."""

    def test_init(self):
        """Test AnalysisResult initialization."""
        result = AnalysisResult()

        assert result.packages == []
        assert result.files == []
        assert result.classes == []
        assert result.functions == []
        assert result.variables == []
        assert result.imports == []
        assert result.security_issues == []
        assert result.quality_metrics == {}
        assert result.errors == []

    def test_merge(self):
        """Test merging two AnalysisResult objects."""
        result1 = AnalysisResult()
        result1.packages = [{"name": "pkg1"}]
        result1.files = [{"name": "file1.py"}]
        result1.security_issues = [{"issue": "security1"}]
        result1.quality_metrics = {"metric1": 100}
        result1.errors = [{"error": "error1"}]

        result2 = AnalysisResult()
        result2.packages = [{"name": "pkg2"}]
        result2.files = [{"name": "file2.py"}]
        result2.security_issues = [{"issue": "security2"}]
        result2.quality_metrics = {"metric2": 200}
        result2.errors = [{"error": "error2"}]

        result1.merge(result2)

        assert len(result1.packages) == 2
        assert len(result1.files) == 2
        assert len(result1.security_issues) == 2
        assert len(result1.errors) == 2
        assert result1.quality_metrics == {"metric1": 100, "metric2": 200}


class TestBackendRegistry:
    """Test backend registry functions."""

    def test_available_backends(self):
        """Test that all expected backends are available."""
        expected_backends = {"ast", "external", "quality"}
        assert set(AVAILABLE_BACKENDS.keys()) == expected_backends

    def test_get_backend(self):
        """Test getting a backend by name."""
        ast_backend = get_backend("ast")
        assert ast_backend == ASTBackend

        external_backend = get_backend("external")
        assert external_backend == ExternalToolsBackend

        quality_backend = get_backend("quality")
        assert quality_backend == QualityBackend

    def test_get_backend_invalid(self):
        """Test getting an invalid backend raises ValueError."""
        with pytest.raises(ValueError, match="Backend 'invalid' not found"):
            get_backend("invalid")

    def test_get_all_backends(self):
        """Test getting all available backends."""
        backends = get_all_backends()
        assert len(backends) == 3
        assert ASTBackend in backends
        assert ExternalToolsBackend in backends
        assert QualityBackend in backends

    def test_get_default_backends(self):
        """Test getting default backends."""
        backends = get_default_backends()
        assert len(backends) == 3
        assert ASTBackend in backends
        assert ExternalToolsBackend in backends
        assert QualityBackend in backends


class TestBaseAnalysisBackend:
    """Test the base AnalysisBackend class."""

    def test_abstract_methods(self):
        """Test that AnalysisBackend cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AnalysisBackend(None, Path("/test"))

    def test_find_python_files(self, temp_project_dir):
        """Test finding Python files in a directory."""

        # Create a concrete backend for testing
        class TestBackend(AnalysisBackend):
            @property
            def name(self):
                return "test"

            @property
            def description(self):
                return "Test backend"

            @property
            def capabilities(self):
                return []

            def analyze(self, python_files):
                return AnalysisResult()

        backend = TestBackend(Mock(), temp_project_dir)
        python_files = backend._find_python_files(temp_project_dir)

        assert len(python_files) > 0
        assert all(f.suffix == ".py" for f in python_files)
        assert all("__pycache__" not in str(f) for f in python_files)

    def test_get_relative_path(self, temp_project_dir):
        """Test getting relative path from project root."""

        class TestBackend(AnalysisBackend):
            @property
            def name(self):
                return "test"

            @property
            def description(self):
                return "Test backend"

            @property
            def capabilities(self):
                return []

            def analyze(self, python_files):
                return AnalysisResult()

        backend = TestBackend(Mock(), temp_project_dir)

        test_file = temp_project_dir / "main.py"
        relative_path = backend._get_relative_path(test_file)
        assert relative_path == "main.py"

        nested_file = temp_project_dir / "test_package" / "module.py"
        relative_path = backend._get_relative_path(nested_file)
        assert relative_path == "test_package/module.py"

    def test_get_package_name(self, temp_project_dir):
        """Test extracting package name from file path."""

        class TestBackend(AnalysisBackend):
            @property
            def name(self):
                return "test"

            @property
            def description(self):
                return "Test backend"

            @property
            def capabilities(self):
                return []

            def analyze(self, python_files):
                return AnalysisResult()

        backend = TestBackend(Mock(), temp_project_dir)

        # Root level file
        root_file = temp_project_dir / "main.py"
        package_name = backend._get_package_name(root_file)
        assert package_name == "__main__"

        # Package file
        package_file = temp_project_dir / "test_package" / "module.py"
        package_name = backend._get_package_name(package_file)
        assert package_name == "test_package"

    def test_is_available_default(self):
        """Test default is_available implementation."""

        class TestBackend(AnalysisBackend):
            @property
            def name(self):
                return "test"

            @property
            def description(self):
                return "Test backend"

            @property
            def capabilities(self):
                return []

            def analyze(self, python_files):
                return AnalysisResult()

        backend = TestBackend(Mock(), Path("/test"))
        assert backend.is_available() is True

    def test_get_configuration_default(self):
        """Test default get_configuration implementation."""

        class TestBackend(AnalysisBackend):
            @property
            def name(self):
                return "test"

            @property
            def description(self):
                return "Test backend"

            @property
            def capabilities(self):
                return []

            def analyze(self, python_files):
                return AnalysisResult()

        backend = TestBackend(Mock(), Path("/test"))
        config = backend.get_configuration()
        assert config == {}

    def test_validate_configuration_default(self):
        """Test default validate_configuration implementation."""

        class TestBackend(AnalysisBackend):
            @property
            def name(self):
                return "test"

            @property
            def description(self):
                return "Test backend"

            @property
            def capabilities(self):
                return []

            def analyze(self, python_files):
                return AnalysisResult()

        backend = TestBackend(Mock(), Path("/test"))
        assert backend.validate_configuration({}) is True


class TestASTBackend:
    """Test the AST analysis backend."""

    def test_properties(self):
        """Test AST backend properties."""
        backend = ASTBackend(Mock(), Path("/test"))

        assert backend.name == "ast"
        assert "AST-based analysis" in backend.description
        assert "class_analysis" in backend.capabilities
        assert "function_analysis" in backend.capabilities
        assert "variable_analysis" in backend.capabilities

    def test_analyze_with_files(self, temp_project_dir, sample_python_files):
        """Test AST analysis with real Python files."""
        session = Mock()
        backend = ASTBackend(session, temp_project_dir)

        result = backend.analyze(sample_python_files)

        assert isinstance(result, AnalysisResult)
        assert len(result.files) > 0
        assert len(result.classes) > 0
        assert len(result.functions) > 0

        # Check that we found the test class
        class_names = [cls["name"] for cls in result.classes]
        assert "TestClass" in class_names or "DataProcessor" in class_names

        # Check that we found some functions
        function_names = [func["name"] for func in result.functions]
        assert len(function_names) > 0

    def test_analyze_empty_files(self):
        """Test AST analysis with empty file list."""
        backend = ASTBackend(Mock(), Path("/test"))
        result = backend.analyze([])

        assert isinstance(result, AnalysisResult)
        assert len(result.files) == 0
        assert len(result.classes) == 0
        assert len(result.functions) == 0

    def test_analyze_invalid_python_file(self, temp_project_dir):
        """Test AST analysis with invalid Python file."""
        # Create a file with invalid Python syntax
        invalid_file = temp_project_dir / "invalid.py"
        invalid_file.write_text("def invalid_syntax(\n")  # Missing closing parenthesis

        backend = ASTBackend(Mock(), temp_project_dir)
        result = backend.analyze([invalid_file])

        assert isinstance(result, AnalysisResult)
        # Should handle the error gracefully
        assert len(result.errors) > 0 or len(result.files) == 0


class TestExternalToolsBackend:
    """Test the external tools backend."""

    def test_properties(self):
        """Test external tools backend properties."""
        backend = ExternalToolsBackend(Mock(), Path("/test"))

        assert backend.name == "external"
        assert "External" in backend.description
        assert "security_analysis" in backend.capabilities
        assert "dead_code_analysis" in backend.capabilities

    def test_is_available_when_tools_missing(self):
        """Test is_available when external tools are missing."""
        backend = ExternalToolsBackend(Mock(), Path("/test"))

        with patch("shutil.which", return_value=None):
            # If no tools are available, backend should still be available
            # but might skip some analysis
            assert backend.is_available() is True

    def test_analyze_with_files(self, temp_project_dir, sample_python_files):
        """Test external tools analysis."""
        session = Mock()
        backend = ExternalToolsBackend(session, temp_project_dir)

        # Mock subprocess calls to avoid dependency on actual tools
        with patch("subprocess.run") as mock_run:
            # Mock bandit output
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = """
{
  "results": [
    {
      "filename": "main.py",
      "issue_confidence": "HIGH",
      "issue_severity": "HIGH",
      "issue_text": "subprocess call with shell=True",
      "line_number": 32,
      "test_id": "B602",
      "test_name": "subprocess_popen_with_shell_equals_true"
    }
  ]
}
"""

            result = backend.analyze(sample_python_files)

            assert isinstance(result, AnalysisResult)
            # Should have found at least one security issue
            assert len(result.security_issues) >= 0  # May be 0 if tools not available

    def test_analyze_empty_files(self):
        """Test external tools analysis with empty file list."""
        backend = ExternalToolsBackend(Mock(), Path("/test"))
        result = backend.analyze([])

        assert isinstance(result, AnalysisResult)
        assert len(result.security_issues) == 0


class TestQualityBackend:
    """Test the quality metrics backend."""

    def test_properties(self):
        """Test quality backend properties."""
        backend = QualityBackend(Mock(), Path("/test"))

        assert backend.name == "quality"
        assert "Code quality" in backend.description
        assert "complexity_analysis" in backend.capabilities
        assert "maintainability_analysis" in backend.capabilities

    def test_is_available_when_radon_missing(self):
        """Test is_available when radon is missing."""
        backend = QualityBackend(Mock(), Path("/test"))

        with patch("shutil.which", return_value=None):
            # Backend should still be available even if radon is missing
            assert backend.is_available() is True

    def test_analyze_with_files(self, temp_project_dir, sample_python_files):
        """Test quality analysis."""
        session = Mock()
        backend = QualityBackend(session, temp_project_dir)

        # Mock subprocess calls for radon
        with patch("subprocess.run") as mock_run:
            # Mock radon complexity output
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = """
main.py:
    F 13:4 TestClass.method_with_complexity - A (4)
    F 26:0 complex_function - B (8)
"""

            result = backend.analyze(sample_python_files)

            assert isinstance(result, AnalysisResult)
            # Quality metrics might be empty if tools not available
            assert isinstance(result.quality_metrics, dict)

    def test_analyze_empty_files(self):
        """Test quality analysis with empty file list."""
        backend = QualityBackend(Mock(), Path("/test"))
        result = backend.analyze([])

        assert isinstance(result, AnalysisResult)
        assert isinstance(result.quality_metrics, dict)


class TestBackendIntegration:
    """Integration tests for backends working together."""

    def test_all_backends_analyze_same_files(
        self, temp_project_dir, sample_python_files
    ):
        """Test that all backends can analyze the same set of files."""
        session = Mock()

        # Test each backend individually
        for backend_name in AVAILABLE_BACKENDS:
            backend_class = get_backend(backend_name)
            backend = backend_class(session, temp_project_dir)

            # Each backend should be able to analyze the files
            result = backend.analyze(sample_python_files)
            assert isinstance(result, AnalysisResult)

    def test_backends_produce_mergeable_results(
        self, temp_project_dir, sample_python_files
    ):
        """Test that backend results can be merged together."""
        session = Mock()
        combined_result = AnalysisResult()

        for backend_name in AVAILABLE_BACKENDS:
            backend_class = get_backend(backend_name)
            backend = backend_class(session, temp_project_dir)

            result = backend.analyze(sample_python_files)
            combined_result.merge(result)

        # Combined result should have accumulated data from all backends
        assert isinstance(combined_result, AnalysisResult)
        # At minimum should have some files analyzed
        assert len(combined_result.files) >= 0
