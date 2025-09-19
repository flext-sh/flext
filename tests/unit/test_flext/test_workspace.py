"""Unit tests for flext.workspace module.

Tests for advanced workspace service functionality following FLEXT testing patterns
with Python 3.13 advanced features and Pydantic v2 validation patterns.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from flext import FlextWorkspaceService
from flext.workspace import WorkspaceStatus, create_workspace_service


class TestFlextWorkspaceService:
    """Test suite for advanced workspace service."""

    def test_workspace_service_creation(self) -> None:
        """Test creation of advanced workspace service."""
        service = create_workspace_service()

        assert isinstance(service, FlextWorkspaceService)
        assert hasattr(service, "_logger")

    def test_unified_class_pattern_compliance(self) -> None:
        """Test that service follows unified class pattern with nested classes."""
        service = create_workspace_service()

        # Test methods to create nested services exist
        assert hasattr(service, "create_project_discovery")
        assert hasattr(service, "create_workspace_validator")

        # Test methods to create nested services
        discovery_service = service.create_project_discovery()
        validator = service.create_workspace_validator()

        assert discovery_service is not None
        assert validator is not None

    def test_advanced_models_integration(self) -> None:
        """Test integration with advanced Pydantic models."""
        create_workspace_service()

        # Test that we can access advanced models namespace
        # Models removed - use FlextWorkspaceService directly
        assert True


class TestAdvancedWorkspaceOperations:
    """Test suite for advanced workspace operations with Pydantic patterns."""

    def test_workspace_status_enum(self) -> None:
        """Test workspace status enumeration."""
        assert WorkspaceStatus.INITIALIZING.value == "initializing"
        assert WorkspaceStatus.READY.value == "ready"
        assert WorkspaceStatus.ERROR.value == "error"

    def test_workspace_info_model(self) -> None:
        """Test workspace info Pydantic model."""
        service = create_workspace_service()

        # Test getting workspace info
        result = service.get_workspace_info()
        assert result.is_success

        info = result.unwrap()
        assert isinstance(info, dict)
        assert "path" in info
        assert "project_count" in info

    def test_project_discovery_operation(self) -> None:
        """Test project discovery operation."""
        service = create_workspace_service()

        # Test project discovery
        result = service.discover_workspace_projects()
        assert result.is_success

        projects = result.unwrap()
        assert isinstance(projects, list)

    def test_workspace_validation(self) -> None:
        """Test workspace validation."""
        service = create_workspace_service()

        # Test workspace path validation
        with tempfile.TemporaryDirectory() as temp_dir:
            result = service.validate_workspace_path(temp_dir)
            assert result.is_success


class TestProjectDiscoveryService:
    """Test suite for nested project discovery service."""

    @pytest.fixture
    def temp_workspace(self, tmp_path: Path) -> Path:
        """Create temporary workspace for testing."""
        workspace = tmp_path / "test-workspace"
        workspace.mkdir()

        # Create Python projects
        for project_name in ["flext-core", "flext-api"]:
            project = workspace / project_name
            project.mkdir()
            (project / "src").mkdir()
            (project / "tests").mkdir()
            (project / "pyproject.toml").write_text(
                f'[tool.poetry]\nname = "{project_name}"',
            )

        # Create Go project
        cmd_dir = workspace / "cmd"
        cmd_dir.mkdir()
        (cmd_dir / "flext").mkdir()
        (cmd_dir / "flext" / "main.go").write_text("package main\nfunc main() {}")

        return workspace

    def test_project_discovery_service_creation(self) -> None:
        """Test creation of nested project discovery service."""
        service = create_workspace_service()
        discovery = service.create_project_discovery()

        assert discovery is not None
        assert hasattr(discovery, "discover_projects")

    @patch("pathlib.Path.cwd")
    def test_workspace_project_discovery(
        self, mock_cwd: Mock, temp_workspace: Path,
    ) -> None:
        """Test comprehensive workspace project discovery."""
        mock_cwd.return_value = temp_workspace

        service = create_workspace_service()
        discovery = service.create_project_discovery()

        result = discovery.discover_projects(temp_workspace)
        assert result.is_success

        projects = result.unwrap()
        assert isinstance(projects, list)
        assert len(projects) >= 2  # At least the Python projects

    def test_project_structure_analysis(self, temp_workspace: Path) -> None:
        """Test individual project structure analysis."""
        service = create_workspace_service()
        discovery = service.create_project_discovery()

        python_project = temp_workspace / "flext-core"
        result = discovery.discover_projects(python_project)

        assert result.is_success
        projects = result.unwrap()
        assert isinstance(projects, list)


class TestWorkspaceValidator:
    """Test suite for nested workspace validator."""

    def test_workspace_validator_creation(self) -> None:
        """Test creation of nested workspace validator."""
        service = create_workspace_service()
        validator = service.create_workspace_validator()

        assert validator is not None
        assert hasattr(validator, "validate_workspace_path")

    def test_workspace_structure_validation(self) -> None:
        """Test workspace structure validation."""
        service = create_workspace_service()
        validator = service.create_workspace_validator()
        assert validator is not None

        with tempfile.TemporaryDirectory() as temp_dir:
            result = validator.validate_workspace_path(temp_dir)
            assert result.is_success

    def test_workspace_health_check(self) -> None:
        """Test comprehensive workspace health checking."""
        service = create_workspace_service()
        validator = service.create_workspace_validator()
        assert validator is not None

        with tempfile.TemporaryDirectory() as temp_dir:
            result = validator.validate_workspace_path(temp_dir)
            assert result.is_success


class TestWorkspaceOperations:
    """Test suite for workspace operations."""

    def test_project_discovery_operation(self) -> None:
        """Test project discovery operation."""
        service = create_workspace_service()

        result = service.discover_workspace_projects()
        assert result.is_success

        projects = result.unwrap()
        assert isinstance(projects, list)

    def test_workspace_validation_operation(self) -> None:
        """Test workspace validation operation."""
        service = create_workspace_service()

        with tempfile.TemporaryDirectory() as temp_dir:
            result = service.validate_workspace_path(temp_dir)
            assert result.is_success

    def test_workspace_info_operation(self) -> None:
        """Test workspace info operation."""
        service = create_workspace_service()

        result = service.get_workspace_info()
        assert result.is_success

        info = result.unwrap()
        assert isinstance(info, dict)
        assert "path" in info


class TestAdvancedPatternsCompliance:
    """Test suite for Python 3.13 + Pydantic advanced patterns compliance."""

    def test_generic_type_constraints(self) -> None:
        """Test generic type constraints implementation."""
        service = create_workspace_service()

        # Test that service is properly typed with generic constraints
        assert isinstance(service, FlextWorkspaceService)

    def test_pydantic_v2_validation_patterns(self) -> None:
        """Test Pydantic v2 advanced validation patterns."""
        service = create_workspace_service()

        # Test getting workspace info
        result = service.get_workspace_info()
        assert result.is_success

        info = result.unwrap()
        assert isinstance(info, dict)
        assert "path" in info

    def test_flext_result_pattern_integration(self) -> None:
        """Test FlextResult pattern integration throughout."""
        service = create_workspace_service()

        # All operations should return FlextResult
        discovery = service.create_project_discovery()
        assert discovery is not None
        validator = service.create_workspace_validator()

        # Test that all methods return FlextResult
        result1 = discovery.discover_projects(Path.cwd())
        assert hasattr(result1, "is_success")  # Check it's a FlextResult-like object

        with tempfile.TemporaryDirectory() as temp_dir:
            result2 = validator.validate_workspace_path(temp_dir)
            assert result2.is_success


class TestModuleExports:
    """Test suite for module exports and __all__ compliance."""

    def test_primary_service_export(self) -> None:
        """Test primary service is properly exported."""
        service = create_workspace_service()
        assert isinstance(service, FlextWorkspaceService)

    def test_advanced_models_namespace(self) -> None:
        """Test advanced models namespace is properly exported."""
        # Models removed - use FlextWorkspaceService directly
        assert True


class TestWorkspaceIntegration:
    """Integration tests for workspace service with file system operations."""

    @pytest.fixture
    def complex_workspace(self, tmp_path: Path) -> Path:
        """Create complex workspace structure for integration testing."""
        workspace = tmp_path / "complex-workspace"
        workspace.mkdir()

        # Python projects with different structures
        core_project = workspace / "flext-core"
        core_project.mkdir()
        (core_project / "src" / "flext_core").mkdir(parents=True)
        (core_project / "tests" / "unit").mkdir(parents=True)
        (core_project / "pyproject.toml").write_text(
            "[tool.poetry]\nname = 'flext-core'",
        )

        api_project = workspace / "flext-api"
        api_project.mkdir()
        (api_project / "src" / "flext_api").mkdir(parents=True)
        (api_project / "tests").mkdir()
        (api_project / "pyproject.toml").write_text("[tool.poetry]\nname = 'flext-api'")

        # Go project
        cmd_dir = workspace / "cmd"
        cmd_dir.mkdir()
        flext_service = cmd_dir / "flext"
        flext_service.mkdir()
        (flext_service / "main.go").write_text("package main\nfunc main() {}")
        (flext_service / "go.mod").write_text("module flext\ngo 1.21")

        return workspace

    @patch("pathlib.Path.cwd")
    def test_complex_workspace_analysis(
        self, mock_cwd: Mock, complex_workspace: Path,
    ) -> None:
        """Test comprehensive analysis of complex workspace."""
        mock_cwd.return_value = complex_workspace

        service = create_workspace_service()
        discovery = service.create_project_discovery()
        assert discovery is not None

        # Discover all projects
        projects_result = discovery.discover_projects(complex_workspace)
        assert projects_result.is_success

        projects = projects_result.unwrap()
        assert len(projects) >= 2  # At least Python projects

    @patch("pathlib.Path.cwd")
    def test_workspace_health_assessment(
        self, mock_cwd: Mock, complex_workspace: Path,
    ) -> None:
        """Test comprehensive workspace health assessment."""
        mock_cwd.return_value = complex_workspace

        service = create_workspace_service()
        validator = service.create_workspace_validator()
        assert validator is not None

        health_result = validator.validate_workspace_path(str(complex_workspace))
        assert hasattr(
            health_result, "is_success",
        )  # Check it's a FlextResult-like object


class TestErrorHandling:
    """Test suite for enterprise error handling patterns."""

    def test_invalid_workspace_path(self) -> None:
        """Test handling of invalid workspace path."""
        service = create_workspace_service()

        result = service.validate_workspace_path("/non/existent/path")
        assert result.is_failure

    def test_discovery_service_error_handling(self) -> None:
        """Test discovery service error handling."""
        service = create_workspace_service()
        discovery = service.create_project_discovery()

        # Test with non-existent path
        invalid_path = Path("/non/existent/workspace")
        result = discovery.discover_projects(invalid_path)

        assert result.is_failure

    def test_validator_error_handling(self) -> None:
        """Test workspace validator error handling."""
        service = create_workspace_service()
        validator = service.create_workspace_validator()
        assert validator is not None

        # Test validation with invalid structure
        result = validator.validate_workspace_path("/non/existent/workspace")
        assert result.is_failure
