"""Unit tests for flext.dev module.

Tests for development tools manager following FLEXT testing patterns
with comprehensive mocking of subprocess operations and filesystem interactions.
"""
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from flext.dev import DevToolsManager


class TestDevToolsManager:
    """Test suite for DevToolsManager following enterprise patterns."""

    @pytest.fixture
    def temp_workspace(self, tmp_path) -> Path:
        """Create temporary workspace for testing."""
        workspace = tmp_path / "dev-test-workspace"
        workspace.mkdir()

        # Create mock project structure
        flext_core = workspace / "flext-core"
        flext_core.mkdir()
        (flext_core / "tests").mkdir()
        (flext_core / "pyproject.toml").write_text("[tool.poetry]\nname = 'flext-core'")

        return workspace

    @pytest.fixture
    def dev_tools_manager(self, temp_workspace: Path) -> DevToolsManager:
        """Create DevToolsManager instance for testing."""
        return DevToolsManager(workspace_root=temp_workspace)

    def test_dev_tools_manager_initialization_with_path(self, temp_workspace: Path) -> None:
        """Test DevToolsManager initialization with explicit workspace path."""
        # Act
        dev_tools = DevToolsManager(workspace_root=temp_workspace)

        # Assert
        assert dev_tools.workspace_root == temp_workspace
        assert dev_tools.max_workers == 4
        assert "test" in dev_tools.timeout_config
        assert "lint" in dev_tools.timeout_config
        assert "format" in dev_tools.timeout_config
        assert "build" in dev_tools.timeout_config

    def test_dev_tools_manager_initialization_with_string_path(self, temp_workspace: Path) -> None:
        """Test DevToolsManager initialization with string workspace path."""
        # Act
        dev_tools = DevToolsManager(workspace_root=str(temp_workspace))

        # Assert
        assert dev_tools.workspace_root == temp_workspace
        assert isinstance(dev_tools.workspace_root, Path)

    def test_dev_tools_manager_initialization_default(self) -> None:
        """Test DevToolsManager initialization with default workspace (cwd)."""
        with patch("pathlib.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/mock/workspace")

            # Act
            dev_tools = DevToolsManager()

            # Assert
            assert dev_tools.workspace_root == Path("/mock/workspace")
            mock_cwd.assert_called_once()

    def test_timeout_configuration(self, dev_tools_manager: DevToolsManager) -> None:
        """Test that timeout configuration is properly set."""
        # Assert timeout values
        assert dev_tools_manager.timeout_config["test"] == 300  # 5 minutes
        assert dev_tools_manager.timeout_config["lint"] == 180  # 3 minutes
        assert dev_tools_manager.timeout_config["format"] == 180  # 3 minutes
        assert dev_tools_manager.timeout_config["build"] == 600  # 10 minutes

    def test_logger_initialization(self, dev_tools_manager: DevToolsManager) -> None:
        """Test that logger is properly initialized."""
        # Assert
        assert dev_tools_manager.logger is not None
        assert dev_tools_manager.logger.name.endswith("DevToolsManager")


class TestRunTests:
    """Test suite for test execution functionality."""

    @pytest.fixture
    def mock_workspace(self, tmp_path) -> Path:
        """Create mock workspace with test projects."""
        workspace = tmp_path / "test-workspace"
        workspace.mkdir()

        # Create projects with tests
        for project_name in ["flext-core", "flext-api", "flexcore"]:
            project_dir = workspace / project_name
            project_dir.mkdir()
            tests_dir = project_dir / "tests"
            tests_dir.mkdir()
            # Create a simple test file
            (tests_dir / "test_example.py").write_text("def test_example(): pass")

        return workspace

    @pytest.fixture
    def dev_tools(self, mock_workspace: Path) -> DevToolsManager:
        """Create DevToolsManager with mock workspace."""
        return DevToolsManager(workspace_root=mock_workspace)

    @patch("subprocess.run")
    def test_run_tests_specific_project_success(
        self,
        mock_subprocess: Mock,
        dev_tools: DevToolsManager
    ) -> None:
        """Test running tests for a specific project successfully."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=0, stdout="Test output", stderr="")

        # Act
        result = dev_tools.run_tests("flext-core")

        # Assert
        assert result == 0
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        assert "python" in args
        assert "-m" in args
        assert "pytest" in args

    @patch("subprocess.run")
    def test_run_tests_specific_project_failure(
        self,
        mock_subprocess: Mock,
        dev_tools: DevToolsManager
    ) -> None:
        """Test running tests for a specific project with failures."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=1, stdout="", stderr="Test failed")

        # Act
        result = dev_tools.run_tests("flext-core")

        # Assert
        assert result == 1
        mock_subprocess.assert_called_once()

    def test_run_tests_nonexistent_project(self, dev_tools: DevToolsManager) -> None:
        """Test running tests for a project that doesn't exist."""
        # Act
        result = dev_tools.run_tests("nonexistent-project")

        # Assert
        assert result == 1

    @patch("subprocess.run")
    def test_run_tests_all_projects_success(
        self,
        mock_subprocess: Mock,
        dev_tools: DevToolsManager
    ) -> None:
        """Test running tests for all projects successfully."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=0, stdout="All tests passed", stderr="")

        # Act
        result = dev_tools.run_tests()

        # Assert
        assert result == 0
        # Should be called multiple times for different projects
        assert mock_subprocess.call_count >= 1

    @patch("subprocess.run")
    def test_run_tests_timeout_handling(
        self,
        mock_subprocess: Mock,
        dev_tools: DevToolsManager
    ) -> None:
        """Test handling of test execution timeout."""
        # Arrange
        mock_subprocess.side_effect = subprocess.TimeoutExpired(cmd=["pytest"], timeout=300)

        # Act
        result = dev_tools.run_tests("flext-core")

        # Assert
        assert result == 1

    def test_run_project_tests_no_tests_directory(self, dev_tools: DevToolsManager) -> None:
        """Test running tests for project without tests directory."""
        # Arrange - Create project without tests
        project_without_tests = dev_tools.workspace_root / "no-tests-project"
        project_without_tests.mkdir()

        # Act
        result = dev_tools._run_project_tests(project_without_tests)

        # Assert
        assert result == 0  # Not an error if no tests exist

    @patch("subprocess.run")
    def test_run_project_tests_with_coverage(
        self,
        mock_subprocess: Mock,
        dev_tools: DevToolsManager
    ) -> None:
        """Test running project tests with coverage configuration."""
        # Arrange
        project_path = dev_tools.workspace_root / "flext-core"
        coverage_file = project_path / ".coveragerc"
        coverage_file.write_text("[run]\nsource = src/")

        mock_subprocess.return_value = Mock(returncode=0, stdout="Coverage output", stderr="")

        # Act
        result = dev_tools._run_project_tests(project_path)

        # Assert
        assert result == 0
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        assert "--cov" in args


class TestLintAll:
    """Test suite for code quality analysis functionality."""

    @pytest.fixture
    def dev_tools(self, tmp_path) -> DevToolsManager:
        """Create DevToolsManager for linting tests."""
        workspace = tmp_path / "lint-workspace"
        workspace.mkdir()
        return DevToolsManager(workspace_root=workspace)

    @patch("subprocess.run")
    def test_lint_all_success(self, mock_subprocess: Mock, dev_tools: DevToolsManager) -> None:
        """Test successful linting operation."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=0, stdout="No issues found", stderr="")

        # Act
        result = dev_tools.lint_all()

        # Assert
        assert result == 0
        # Should be called multiple times for different tools
        assert mock_subprocess.call_count >= 1

    @patch("subprocess.run")
    def test_lint_all_with_issues(self, mock_subprocess: Mock, dev_tools: DevToolsManager) -> None:
        """Test linting operation with code quality issues."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=1, stdout="", stderr="Linting issues found")

        # Act
        result = dev_tools.lint_all()

        # Assert
        assert result != 0

    @patch("subprocess.run")
    def test_lint_all_timeout(self, mock_subprocess: Mock, dev_tools: DevToolsManager) -> None:
        """Test handling of linting timeout."""
        # Arrange
        mock_subprocess.side_effect = subprocess.TimeoutExpired(cmd=["ruff"], timeout=180)

        # Act
        result = dev_tools.lint_all()

        # Assert
        assert result == 1

    @patch("flext.dev.DevToolsManager._run_mypy_check")
    @patch("flext.dev.DevToolsManager._run_security_scan")
    @patch("flext.dev.DevToolsManager._run_go_linting")
    @patch("subprocess.run")
    def test_lint_all_comprehensive_checks(
        self,
        mock_subprocess: Mock,
        mock_go_lint: Mock,
        mock_security: Mock,
        mock_mypy: Mock,
        dev_tools: DevToolsManager
    ) -> None:
        """Test that lint_all runs all comprehensive checks."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_mypy.return_value = 0
        mock_security.return_value = 0
        mock_go_lint.return_value = 0

        # Act
        result = dev_tools.lint_all()

        # Assert
        assert result == 0
        mock_subprocess.assert_called()  # ruff check
        mock_mypy.assert_called_once()
        mock_security.assert_called_once()
        mock_go_lint.assert_called_once()


class TestFormatAll:
    """Test suite for code formatting functionality."""

    @pytest.fixture
    def dev_tools(self, tmp_path) -> DevToolsManager:
        """Create DevToolsManager for formatting tests."""
        workspace = tmp_path / "format-workspace"
        workspace.mkdir()
        return DevToolsManager(workspace_root=workspace)

    @patch("subprocess.run")
    def test_format_all_success(self, mock_subprocess: Mock, dev_tools: DevToolsManager) -> None:
        """Test successful formatting operation."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=0, stdout="Formatting completed", stderr="")

        # Act
        result = dev_tools.format_all()

        # Assert
        assert result == 0
        mock_subprocess.assert_called()
        args = mock_subprocess.call_args[0][0]
        assert "ruff" in args
        assert "format" in args

    @patch("subprocess.run")
    def test_format_all_with_errors(self, mock_subprocess: Mock, dev_tools: DevToolsManager) -> None:
        """Test formatting operation with errors."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=1, stdout="", stderr="Formatting errors")

        # Act
        result = dev_tools.format_all()

        # Assert
        assert result != 0

    @patch("subprocess.run")
    def test_format_all_timeout(self, mock_subprocess: Mock, dev_tools: DevToolsManager) -> None:
        """Test handling of formatting timeout."""
        # Arrange
        mock_subprocess.side_effect = subprocess.TimeoutExpired(cmd=["ruff", "format"], timeout=180)

        # Act
        result = dev_tools.format_all()

        # Assert
        assert result == 1

    @patch("flext.dev.DevToolsManager._run_go_formatting")
    @patch("subprocess.run")
    def test_format_all_includes_go_formatting(
        self,
        mock_subprocess: Mock,
        mock_go_format: Mock,
        dev_tools: DevToolsManager
    ) -> None:
        """Test that format_all includes Go formatting."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_go_format.return_value = 0

        # Act
        result = dev_tools.format_all()

        # Assert
        assert result == 0
        mock_subprocess.assert_called()  # Python formatting
        mock_go_format.assert_called_once()  # Go formatting


class TestPrivateMethods:
    """Test suite for private helper methods."""

    @pytest.fixture
    def dev_tools(self, tmp_path) -> DevToolsManager:
        """Create DevToolsManager for testing private methods."""
        workspace = tmp_path / "private-methods-workspace"
        workspace.mkdir()
        return DevToolsManager(workspace_root=workspace)

    @patch("subprocess.run")
    def test_run_mypy_check_success(self, mock_subprocess: Mock, dev_tools: DevToolsManager) -> None:
        """Test successful MyPy type checking."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=0, stdout="Type checking passed", stderr="")

        # Act
        result = dev_tools._run_mypy_check()

        # Assert
        assert result == 0
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        assert "make" in args
        assert "type-check-all" in args

    @patch("subprocess.run")
    def test_run_security_scan_success(self, mock_subprocess: Mock, dev_tools: DevToolsManager) -> None:
        """Test successful security scanning."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=0, stdout="No security issues", stderr="")

        # Act
        result = dev_tools._run_security_scan()

        # Assert
        assert result == 0
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        assert "bandit" in args

    @patch("subprocess.run")
    def test_run_go_linting_no_go_files(self, mock_subprocess: Mock, dev_tools: DevToolsManager) -> None:
        """Test Go linting when no Go files exist."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        # Act
        result = dev_tools._run_go_linting()

        # Assert
        assert result == 0

    @patch("subprocess.run")
    def test_run_go_formatting_no_go_files(self, mock_subprocess: Mock, dev_tools: DevToolsManager) -> None:
        """Test Go formatting when no Go files exist."""
        # Arrange
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        # Act
        result = dev_tools._run_go_formatting()

        # Assert
        assert result == 0

    @patch("subprocess.run")
    def test_private_methods_exception_handling(self, mock_subprocess: Mock, dev_tools: DevToolsManager) -> None:
        """Test that private methods handle exceptions gracefully."""
        # Arrange
        mock_subprocess.side_effect = Exception("Command failed")

        # Act & Assert
        # MyPy check should return 1 on exception
        assert dev_tools._run_mypy_check() == 1

        # Security scan should return 0 (non-critical failure)
        assert dev_tools._run_security_scan() == 0

        # Go linting should return 0 (non-critical failure)
        assert dev_tools._run_go_linting() == 0

        # Go formatting should return 0 (non-critical failure)
        assert dev_tools._run_go_formatting() == 0


class TestWorkspaceIntegration:
    """Integration tests for DevToolsManager with real workspace scenarios."""

    @pytest.fixture
    def complex_workspace(self, tmp_path) -> Path:
        """Create complex workspace with multiple project types."""
        workspace = tmp_path / "complex-workspace"
        workspace.mkdir()

        # Python projects
        for project in ["flext-core", "flext-api"]:
            project_dir = workspace / project
            project_dir.mkdir()
            (project_dir / "tests").mkdir()
            (project_dir / "src").mkdir()
            (project_dir / "pyproject.toml").write_text(f"[tool.poetry]\nname = '{project}'")

        # Go projects
        cmd_dir = workspace / "cmd"
        cmd_dir.mkdir()
        flext_service = cmd_dir / "flext"
        flext_service.mkdir()
        (flext_service / "main.go").write_text("package main\nfunc main() {}")

        # Special projects
        client-a = workspace / "client-a-oud-mig"
        client-a.mkdir()
        (client-a / "tests").mkdir()

        return workspace

    def test_complex_workspace_discovery(self, complex_workspace: Path) -> None:
        """Test that DevToolsManager properly discovers various project types."""
        # Act
        dev_tools = DevToolsManager(workspace_root=complex_workspace)

        # Assert
        assert dev_tools.workspace_root == complex_workspace

        # Test that we can iterate through projects
        project_dirs = list(dev_tools.workspace_root.iterdir())
        project_names = [d.name for d in project_dirs if d.is_dir()]

        assert "flext-core" in project_names
        assert "flext-api" in project_names
        assert "cmd" in project_names
        assert "client-a-oud-mig" in project_names
