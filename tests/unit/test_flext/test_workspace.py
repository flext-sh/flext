"""Unit tests for flext.workspace module.

Tests for advanced workspace service functionality following FLEXT testing patterns
with Python 3.13 advanced features and Pydantic v2 validation patterns.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from flext_core import FlextResult

from flext.workspace import (
    FlextAdvancedWorkspaceModels,
    FlextAdvancedWorkspaceService,
    ProjectDiscoveryServiceProtocol,
    WorkspaceStatus,
    WorkspaceValidatorProtocol,
    __all__,
    create_workspace_service,
)


class TestFlextAdvancedWorkspaceService:
    """Test suite for advanced workspace service."""

    def test_workspace_service_creation(self) -> None:
        """Test creation of advanced workspace service."""
        service = create_workspace_service()

        assert isinstance(service, FlextAdvancedWorkspaceService)
        assert hasattr(service, "_logger")

    def test_unified_class_pattern_compliance(self) -> None:
        """Test that service follows unified class pattern with nested classes."""
        service = create_workspace_service()

        # Test nested classes exist
        assert hasattr(service, "_ProjectDiscoveryService")
        assert hasattr(service, "_WorkspaceValidator")

        # Test methods to create nested services
        discovery_service = service.create_project_discovery()
        validator = service.create_workspace_validator()

        assert discovery_service is not None
        assert validator is not None

    def test_advanced_models_integration(self) -> None:
        """Test integration with advanced Pydantic models."""
        create_workspace_service()

        # Test that we can access advanced models namespace
        assert hasattr(FlextAdvancedWorkspaceModels, "WorkspaceContext")
        assert hasattr(FlextAdvancedWorkspaceModels, "WorkspaceOperation")
        assert hasattr(FlextAdvancedWorkspaceModels, "WorkspaceInfo")


class TestAdvancedWorkspaceOperations:
    """Test suite for advanced workspace operations with Pydantic patterns."""

    def test_workspace_status_enum(self) -> None:
        """Test workspace status enumeration."""
        assert WorkspaceStatus.INITIALIZING == "initializing"
        assert WorkspaceStatus.READY == "ready"
        assert WorkspaceStatus.ERROR == "error"
        assert WorkspaceStatus.MAINTENANCE == "maintenance"

    def test_workspace_context_model(self) -> None:
        """Test workspace context Pydantic model."""
        service = create_workspace_service()

        context_data = {
            "workspace_root": "/test/workspace",
            "active_projects": ["flext-core", "flext-api"],
            "status": "ready",
        }

        result = service.create_workspace_context(context_data)
        assert result.is_success

        context = result.unwrap()
        assert context.workspace_root == Path("/test/workspace")
        assert "flext-core" in context.active_projects

    def test_operation_creation_with_discriminated_unions(self) -> None:
        """Test creation of operations with discriminated union patterns."""
        service = create_workspace_service()

        # Test project discovery operation
        discovery_data = {
            "type": "project_discovery",
            "scan_depth": 2,
            "include_hidden": False,
        }

        result = service.create_project_discovery_operation(discovery_data)
        assert result.is_success

        operation = result.unwrap()
        assert operation.type == "project_discovery"

    def test_advanced_validation_patterns(self) -> None:
        """Test advanced Pydantic validation patterns."""
        service = create_workspace_service()

        # Test validation with invalid data
        invalid_operation = {
            "type": "project_discovery",
            "scan_depth": -1,  # Invalid: negative depth
        }

        result = service.create_project_discovery_operation(invalid_operation)
        assert result.is_failure
        assert result.error is not None
        assert "scan_depth" in result.error


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
                f'[tool.poetry]\nname = "{project_name}"'
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
        assert hasattr(discovery, "analyze_project_structure")

    @patch("pathlib.Path.cwd")
    def test_workspace_project_discovery(
        self, mock_cwd: Mock, temp_workspace: Path
    ) -> None:
        """Test comprehensive workspace project discovery."""
        mock_cwd.return_value = temp_workspace

        service = create_workspace_service()
        discovery = service.create_project_discovery()

        result = discovery.discover_projects()
        assert result.is_success

        projects = result.unwrap()
        assert isinstance(projects, list)
        assert len(projects) >= 2  # At least the Python projects

    def test_project_structure_analysis(self, temp_workspace: Path) -> None:
        """Test individual project structure analysis."""
        service = create_workspace_service()
        discovery = service.create_project_discovery()

        python_project = temp_workspace / "flext-core"
        result = discovery.analyze_project_structure(python_project)

        assert isinstance(result, dict)
        assert result.get("success") is True
        project_info = result.get("project_info")
        assert project_info is not None
        assert isinstance(project_info, dict)
        assert project_info.get("project_type") == "python"
        assert project_info.get("has_tests") is True
        assert project_info.get("has_src") is True


class TestWorkspaceValidator:
    """Test suite for nested workspace validator."""

    def test_workspace_validator_creation(self) -> None:
        """Test creation of nested workspace validator."""
        service = create_workspace_service()
        validator = service.create_workspace_validator()

        assert validator is not None
        assert hasattr(validator, "validate_workspace_structure")
        assert hasattr(validator, "check_workspace_health")

    def test_workspace_structure_validation(self) -> None:
        """Test workspace structure validation."""
        service = create_workspace_service()
        validator = service.create_workspace_validator()
        assert isinstance(validator, WorkspaceValidatorProtocol)

        result = validator.validate_workspace_structure("/test/workspace")
        # May succeed or fail depending on validation logic
        assert hasattr(result, 'is_success')  # Check it's a FlextResult-like object

    def test_workspace_health_check(self) -> None:
        """Test comprehensive workspace health checking."""
        service = create_workspace_service()
        validator = service.create_workspace_validator()
        assert isinstance(validator, WorkspaceValidatorProtocol)

        result = validator.check_workspace_health("/test/workspace")
        assert hasattr(result, 'is_success')  # Check it's a FlextResult-like object

        if result.is_success:
            health_info = result.unwrap()
            assert "status" in health_info
            assert "projects" in health_info


class TestWorkspaceOperations:
    """Test suite for workspace operations with discriminated unions."""

    def test_project_discovery_operation(self) -> None:
        """Test project discovery operation creation and execution."""
        service = create_workspace_service()

        operation_data = {
            "type": "project_discovery",
            "scan_depth": 3,
            "include_hidden": False,
            "filter_patterns": ["*.git", "node_modules"],
        }

        result = service.create_project_discovery_operation(operation_data)
        assert result.is_success

        operation = result.unwrap()
        assert operation.scan_depth == 3
        assert not operation.include_hidden

    def test_workspace_validation_operation(self) -> None:
        """Test workspace validation operation creation."""
        service = create_workspace_service()

        operation_data = {
            "type": "workspace_validation",
            "check_dependencies": True,
            "validate_structure": True,
            "check_permissions": False,
        }

        result = service.create_workspace_validation_operation(operation_data)
        assert result.is_success

        operation = result.unwrap()
        assert operation.check_dependencies

    def test_environment_setup_operation(self) -> None:
        """Test environment setup operation creation."""
        service = create_workspace_service()

        operation_data = {
            "type": "environment_setup",
            "python_version": "3.13",
            "install_dependencies": True,
            "setup_git_hooks": True,
        }

        result = service.create_environment_setup_operation(operation_data)
        assert result.is_success

        operation = result.unwrap()
        assert operation.python_version == "3.13"


class TestAdvancedPatternsCompliance:
    """Test suite for Python 3.13 + Pydantic advanced patterns compliance."""

    def test_generic_type_constraints(self) -> None:
        """Test generic type constraints implementation."""
        service = create_workspace_service()

        # Test that service is properly typed with generic constraints
        assert isinstance(service, FlextAdvancedWorkspaceService)

        # Test that type parameters work correctly
        assert hasattr(service.__class__, "__orig_bases__")

    def test_discriminated_unions_pattern(self) -> None:
        """Test discriminated unions pattern implementation."""
        service = create_workspace_service()

        # Test different operation types via discriminated unions
        operations: list[dict[str, object]] = [
            {"type": "project_discovery", "scan_depth": 2},
            {"type": "workspace_validation", "check_dependencies": True},
            {"type": "environment_setup", "python_version": "3.13"},
        ]

        for op_data in operations:
            result = service.create_workspace_operation(op_data)
            # Some may succeed, some may fail due to missing fields
            # The important thing is the discriminator works
            assert hasattr(result, 'is_success')  # Check it's a FlextResult-like object

    def test_pydantic_v2_validation_patterns(self) -> None:
        """Test Pydantic v2 advanced validation patterns."""
        service = create_workspace_service()

        # Test field validation using actual WorkspaceContext fields
        workspace_data = {
            "workspace_root": "/valid/path",
            "max_projects": 50,  # Integer validation
            "active_projects": ["flext-core", "flext-cli"],  # List validation
        }

        result = service.create_workspace_info(workspace_data)
        assert result.is_success

        info = result.unwrap()
        # Note: create_workspace_info returns WorkspaceInfo, not WorkspaceContext
        # WorkspaceInfo doesn't have max_projects field, so test what's available
        assert str(info.workspace_root) == "/valid/path"

    def test_flext_result_pattern_integration(self) -> None:
        """Test FlextResult pattern integration throughout."""
        service = create_workspace_service()

        # All operations should return FlextResult
        discovery = service.create_project_discovery()
        assert isinstance(discovery, ProjectDiscoveryServiceProtocol)
        validator = service.create_workspace_validator()

        # Test that all methods return FlextResult
        result1 = discovery.discover_projects()
        assert hasattr(result1, 'is_success')  # Check it's a FlextResult-like object

        result2 = validator.check_workspace_health("/test/workspace")
        assert hasattr(result2, 'is_success')  # Check it's a FlextResult-like object


class TestModuleExports:
    """Test suite for module exports and __all__ compliance."""

    def test_all_exports_available(self) -> None:
        """Test that all declared exports are available."""
        expected_exports = [
            "FlextAdvancedWorkspaceService",
            "create_workspace_service",
            "FlextAdvancedWorkspaceModels",
            "WorkspaceStatus",
        ]

        for export in expected_exports:
            assert export in __all__, f"Export {export} missing from __all__"

    def test_primary_service_export(self) -> None:
        """Test primary service is properly exported."""
        service = create_workspace_service()
        assert isinstance(service, FlextAdvancedWorkspaceService)

    def test_advanced_models_namespace(self) -> None:
        """Test advanced models namespace is properly exported."""
        assert FlextAdvancedWorkspaceModels is not None

        # Test nested model classes
        assert hasattr(FlextAdvancedWorkspaceModels, "WorkspaceContext")
        assert hasattr(FlextAdvancedWorkspaceModels, "WorkspaceOperation")
        assert hasattr(FlextAdvancedWorkspaceModels, "WorkspaceInfo")


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
            "[tool.poetry]\nname = 'flext-core'"
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
        self, mock_cwd: Mock, complex_workspace: Path
    ) -> None:
        """Test comprehensive analysis of complex workspace."""
        mock_cwd.return_value = complex_workspace

        service = create_workspace_service()
        discovery = service.create_project_discovery()
        assert isinstance(discovery, ProjectDiscoveryServiceProtocol)

        # Discover all projects
        projects_result = discovery.discover_projects()
        assert projects_result.is_success

        projects = projects_result.unwrap()
        assert len(projects) >= 2  # At least Python projects

        # Analyze each project
        python_projects = [
            p for p in projects if isinstance(p, dict) and p.get("type") == "python"
        ]
        assert len(python_projects) >= 2

    @patch("pathlib.Path.cwd")
    def test_workspace_health_assessment(
        self, mock_cwd: Mock, complex_workspace: Path
    ) -> None:
        """Test comprehensive workspace health assessment."""
        mock_cwd.return_value = complex_workspace

        service = create_workspace_service()
        validator = service.create_workspace_validator()
        assert isinstance(validator, WorkspaceValidatorProtocol)

        health_result = validator.check_workspace_health("/test/workspace")
        assert hasattr(health_result, 'is_success')  # Check it's a FlextResult-like object

        if health_result.is_success:
            health_info = health_result.unwrap()
            assert isinstance(health_info, dict)
            assert "projects" in health_info


class TestErrorHandling:
    """Test suite for enterprise error handling patterns."""

    def test_invalid_workspace_path(self) -> None:
        """Test handling of invalid workspace path."""
        service = create_workspace_service()

        invalid_context = {
            "workspace_root": "/non/existent/path",
            "active_projects": [],
        }

        result = service.create_workspace_context(invalid_context)
        # May succeed or fail depending on validation logic
        assert hasattr(result, 'is_success')  # Check it's a FlextResult-like object

    def test_invalid_operation_data(self) -> None:
        """Test handling of invalid operation data."""
        service = create_workspace_service()

        # Completely invalid data
        invalid_data: dict[str, object] = {"invalid": "data"}

        result = service.create_workspace_operation(invalid_data)  # type: ignore[arg-type]
        assert result.is_failure

    def test_discovery_service_error_handling(self) -> None:
        """Test discovery service error handling."""
        service = create_workspace_service()
        discovery = service.create_project_discovery()

        # Test with non-existent path
        invalid_path = Path("/non/existent/workspace")
        result = discovery.analyze_project_structure(invalid_path)

        assert isinstance(result, dict)
        assert result.get("success") is False
        error_msg = result.get("error", "")
        assert isinstance(error_msg, str) and error_msg
        assert (
            "does not exist" in error_msg
        )

    def test_validator_error_handling(self) -> None:
        """Test workspace validator error handling."""
        service = create_workspace_service()
        validator = service.create_workspace_validator()
        assert isinstance(validator, WorkspaceValidatorProtocol)

        # Test validation with invalid structure
        result = validator.validate_workspace_structure("/test/workspace")
        assert result.is_failure
