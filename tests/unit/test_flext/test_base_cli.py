"""Unit tests for flext.base_cli module.

Tests for the base CLI functionality following FLEXT testing patterns
with proper mocking and isolation.
"""
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from flext.base_cli import BaseCLI


class TestBaseCLI:
    """Test suite for BaseCLI following enterprise patterns."""

    @pytest.fixture
    def mock_workspace(self) -> Path:
        """Mock workspace path for testing."""
        return Path("/tmp/test-workspace")

    @pytest.fixture
    def base_cli(self, mock_workspace: Path) -> BaseCLI:
        """Create BaseCLI instance with mocked dependencies."""
        return BaseCLI(workspace=mock_workspace)

    def test_base_cli_initialization(self, base_cli: BaseCLI, mock_workspace: Path) -> None:
        """Test BaseCLI initialization with workspace."""
        # Assert
        assert base_cli.workspace == mock_workspace
        assert hasattr(base_cli, "workspace")

    def test_workspace_property(self, base_cli: BaseCLI, mock_workspace: Path) -> None:
        """Test workspace property access."""
        # Act & Assert
        assert base_cli.workspace == mock_workspace
        assert isinstance(base_cli.workspace, Path)

    @patch("flext.base_cli.WorkspaceManager")
    def test_get_workspace_manager_success(
        self,
        mock_workspace_manager: Mock,
        base_cli: BaseCLI
    ) -> None:
        """Test successful workspace manager creation."""
        # Arrange
        mock_manager_instance = Mock()
        mock_workspace_manager.return_value = mock_manager_instance

        # Act
        result = base_cli.get_workspace_manager()

        # Assert
        assert result.is_success is True
        assert result.value == mock_manager_instance
        mock_workspace_manager.assert_called_once_with(base_cli.workspace)

    @patch("flext.base_cli.WorkspaceManager")
    def test_get_workspace_manager_failure(
        self,
        mock_workspace_manager: Mock,
        base_cli: BaseCLI
    ) -> None:
        """Test workspace manager creation failure handling."""
        # Arrange
        mock_workspace_manager.side_effect = Exception("Workspace error")

        # Act
        result = base_cli.get_workspace_manager()

        # Assert
        assert result.is_success is False
        assert "Workspace error" in str(result.error)

    @patch("flext.base_cli.PipelineService")
    def test_get_pipeline_service_success(
        self,
        mock_pipeline_service: Mock,
        base_cli: BaseCLI
    ) -> None:
        """Test successful pipeline service creation."""
        # Arrange
        mock_service_instance = Mock()
        mock_pipeline_service.return_value = mock_service_instance

        # Act
        result = base_cli.get_pipeline_service()

        # Assert
        assert result.is_success is True
        assert result.value == mock_service_instance
        mock_pipeline_service.assert_called_once()

    @patch("flext.base_cli.PipelineService")
    def test_get_pipeline_service_failure(
        self,
        mock_pipeline_service: Mock,
        base_cli: BaseCLI
    ) -> None:
        """Test pipeline service creation failure handling."""
        # Arrange
        mock_pipeline_service.side_effect = Exception("Pipeline error")

        # Act
        result = base_cli.get_pipeline_service()

        # Assert
        assert result.is_success is False
        assert "Pipeline error" in str(result.error)

    def test_base_cli_with_different_workspace(self) -> None:
        """Test BaseCLI with different workspace paths."""
        # Arrange
        workspace1 = Path("/workspace1")
        workspace2 = Path("/workspace2")

        # Act
        cli1 = BaseCLI(workspace=workspace1)
        cli2 = BaseCLI(workspace=workspace2)

        # Assert
        assert cli1.workspace == workspace1
        assert cli2.workspace == workspace2
        assert cli1.workspace != cli2.workspace

    def test_base_cli_str_representation(self, base_cli: BaseCLI) -> None:
        """Test string representation of BaseCLI."""
        # Act
        str_repr = str(base_cli)

        # Assert
        assert "BaseCLI" in str_repr
        assert str(base_cli.workspace) in str_repr

    def test_base_cli_repr_representation(self, base_cli: BaseCLI) -> None:
        """Test repr representation of BaseCLI."""
        # Act
        repr_str = repr(base_cli)

        # Assert
        assert "BaseCLI" in repr_str
        assert "workspace=" in repr_str


class TestBaseCLIErrorHandling:
    """Test suite for BaseCLI error handling scenarios."""

    def test_none_workspace_handling(self) -> None:
        """Test BaseCLI behavior with None workspace."""
        with pytest.raises(TypeError):
            BaseCLI(workspace=None)  # type: ignore[arg-type]

    def test_invalid_workspace_type(self) -> None:
        """Test BaseCLI behavior with invalid workspace type."""
        with pytest.raises(TypeError):
            BaseCLI(workspace="invalid")  # type: ignore[arg-type]

    @patch("flext.base_cli.WorkspaceManager")
    def test_multiple_service_failures(self, mock_workspace_manager: Mock) -> None:
        """Test handling of multiple consecutive service failures."""
        # Arrange
        mock_workspace_manager.side_effect = Exception("Persistent error")
        base_cli = BaseCLI(workspace=Path("/test"))

        # Act & Assert
        result1 = base_cli.get_workspace_manager()
        result2 = base_cli.get_workspace_manager()

        assert result1.is_success is False
        assert result2.is_success is False
        assert "Persistent error" in str(result1.error)
        assert "Persistent error" in str(result2.error)


class TestBaseCLIIntegration:
    """Integration tests for BaseCLI with real dependencies."""

    @pytest.fixture
    def temp_workspace(self, tmp_path: Path) -> Path:
        """Create temporary workspace for integration testing."""
        workspace = tmp_path / "integration-test"
        workspace.mkdir()
        return workspace

    def test_base_cli_with_real_workspace(self, temp_workspace: Path) -> None:
        """Test BaseCLI with real filesystem workspace."""
        # Act
        base_cli = BaseCLI(workspace=temp_workspace)

        # Assert
        assert base_cli.workspace.exists()
        assert base_cli.workspace.is_dir()
        assert base_cli.workspace == temp_workspace
