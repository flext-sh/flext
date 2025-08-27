"""Unit tests for flext.workspace module.

Tests for workspace management functionality following FLEXT testing patterns
with proper mocking and filesystem isolation.
"""
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from flext_core import FlextResult

from flext.workspace import WorkspaceManager


class TestWorkspaceManager:
    """Test suite for WorkspaceManager class."""

    @pytest.fixture
    def mock_workspace(self) -> Path:
        """Mock workspace path for testing."""
        return Path("/tmp/test-workspace")

    @pytest.fixture
    def workspace_manager(self, mock_workspace: Path) -> WorkspaceManager:
        """Create WorkspaceManager instance with mocked dependencies."""
        return WorkspaceManager(workspace_root=mock_workspace)

    def test_workspace_manager_initialization(
        self,
        workspace_manager: WorkspaceManager,
        mock_workspace: Path
    ) -> None:
        """Test WorkspaceManager initialization."""
        # Assert
        assert workspace_manager.workspace_root == mock_workspace
        assert hasattr(workspace_manager, "workspace_root")

    @patch("flext.workspace.Path.iterdir")
    def test_list_projects_success(
        self,
        mock_iterdir: Mock,
        workspace_manager: WorkspaceManager
    ) -> None:
        """Test successful project listing."""
        # Arrange
        mock_project1 = Mock()
        mock_project1.is_dir.return_value = True
        mock_project1.name = "flext-core"
        mock_project1.__truediv__.return_value = Path("/test/flext-core/pyproject.toml")

        mock_project2 = Mock()
        mock_project2.is_dir.return_value = True
        mock_project2.name = "flext-api"
        mock_project2.__truediv__.return_value = Path("/test/flext-api/pyproject.toml")

        mock_iterdir.return_value = [mock_project1, mock_project2]

        with patch("flext.workspace.Path.exists", return_value=True):
            # Act
            projects = workspace_manager.list_projects()

            # Assert
            assert len(projects) == 2
            assert all(isinstance(p, Path) for p in projects)

    @patch("flext.workspace.Path.iterdir")
    def test_list_projects_no_projects(
        self,
        mock_iterdir: Mock,
        workspace_manager: WorkspaceManager
    ) -> None:
        """Test project listing with no valid projects."""
        # Arrange
        mock_iterdir.return_value = []

        # Act
        projects = workspace_manager.list_projects()

        # Assert
        assert len(projects) == 0
        assert isinstance(projects, list)

    @patch("flext.workspace.Path.iterdir")
    def test_list_projects_filter_invalid(
        self,
        mock_iterdir: Mock,
        workspace_manager: WorkspaceManager
    ) -> None:
        """Test project listing filters invalid directories."""
        # Arrange
        mock_file = Mock()
        mock_file.is_dir.return_value = False
        mock_file.name = "file.txt"

        mock_invalid_dir = Mock()
        mock_invalid_dir.is_dir.return_value = True
        mock_invalid_dir.name = "invalid-dir"
        mock_invalid_dir.__truediv__.return_value = Path("/test/invalid-dir/pyproject.toml")

        mock_iterdir.return_value = [mock_file, mock_invalid_dir]

        with patch("flext.workspace.Path.exists", return_value=False):
            # Act
            projects = workspace_manager.list_projects()

            # Assert
            assert len(projects) == 0

    @patch("flext.workspace.Path.exists")
    def test_validate_project_structure_success(
        self,
        mock_exists: Mock,
        workspace_manager: WorkspaceManager
    ) -> None:
        """Test successful project structure validation."""
        # Arrange
        project_path = Path("/test/flext-core")
        mock_exists.return_value = True

        # Act
        result = workspace_manager.validate_project_structure(project_path)

        # Assert
        assert result.is_success is True

    @patch("flext.workspace.Path.exists")
    def test_validate_project_structure_missing_files(
        self,
        mock_exists: Mock,
        workspace_manager: WorkspaceManager
    ) -> None:
        """Test project structure validation with missing files."""
        # Arrange
        project_path = Path("/test/invalid-project")
        mock_exists.return_value = False

        # Act
        result = workspace_manager.validate_project_structure(project_path)

        # Assert
        assert result.is_success is False

    def test_validate_all_projects_no_projects(
        self,
        workspace_manager: WorkspaceManager
    ) -> None:
        """Test validation when no projects exist."""
        with patch.object(workspace_manager, "list_projects", return_value=[]):
            # Act
            result = workspace_manager.validate_all_projects()

            # Assert
            assert result.is_success is True
            assert result.value == []

    @patch.object(WorkspaceManager, "list_projects")
    @patch.object(WorkspaceManager, "validate_project_structure")
    def test_validate_all_projects_success(
        self,
        mock_validate: Mock,
        mock_list: Mock,
        workspace_manager: WorkspaceManager
    ) -> None:
        """Test successful validation of all projects."""
        # Arrange
        mock_projects = [Path("/test/project1"), Path("/test/project2")]
        mock_list.return_value = mock_projects
        mock_validate.return_value = FlextResult[bool].ok(True)

        # Act
        result = workspace_manager.validate_all_projects()

        # Assert
        assert result.is_success is True
        assert mock_validate.call_count == len(mock_projects)

    @patch.object(WorkspaceManager, "list_projects")
    @patch.object(WorkspaceManager, "validate_project_structure")
    def test_validate_all_projects_partial_failure(
        self,
        mock_validate: Mock,
        mock_list: Mock,
        workspace_manager: WorkspaceManager
    ) -> None:
        """Test validation with some project failures."""
        # Arrange
        mock_projects = [Path("/test/project1"), Path("/test/project2")]
        mock_list.return_value = mock_projects
        mock_validate.side_effect = [
            FlextResult[bool].ok(True),
            FlextResult[bool].fail("Validation failed")
        ]

        # Act
        result = workspace_manager.validate_all_projects()

        # Assert
        assert result.is_success is False


class TestWorkspaceManagerIntegration:
    """Integration tests for WorkspaceManager."""

    @pytest.fixture
    def temp_workspace(self, tmp_path: Path) -> Path:
        """Create temporary workspace for integration testing."""
        workspace = tmp_path / "workspace-integration-test"
        workspace.mkdir()

        # Create mock project structure
        project_dir = workspace / "flext-test"
        project_dir.mkdir()

        # Create pyproject.toml
        pyproject_content = """[tool.poetry]
name = "flext-test"
version = "0.1.0"
"""
        (project_dir / "pyproject.toml").write_text(pyproject_content)

        # Create src directory
        src_dir = project_dir / "src"
        src_dir.mkdir()

        return workspace

    def test_workspace_manager_real_filesystem(self, temp_workspace: Path) -> None:
        """Test WorkspaceManager with real filesystem."""
        # Act
        manager = WorkspaceManager(workspace_root=temp_workspace)
        projects = manager.list_projects()

        # Assert
        assert len(projects) == 1
        assert projects[0].name == "flext-test"

    def test_project_validation_real_filesystem(self, temp_workspace: Path) -> None:
        """Test project validation with real filesystem."""
        # Arrange
        manager = WorkspaceManager(workspace_root=temp_workspace)
        project_path = temp_workspace / "flext-test"

        # Act
        result = manager.validate_project_structure(project_path)

        # Assert
        assert result.is_success is True
