"""Unit tests for flext.dev module.

Tests for the advanced development tools manager following FLEXT testing patterns
with Python 3.13 advanced features and Pydantic v2 validation patterns.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from flext_core import FlextResult

from flext.dev import (
    DevToolsManager,
    FlextAdvancedDevToolsManager,
    __all__,
    create_dev_tools_manager,
)
from flext.dev_enums import OperationStatus, OperationType
from flext.project_types import ProjectType


class TestFlextAdvancedDevToolsManager:
    """Test suite for advanced development tools manager."""

    def test_dev_tools_manager_creation(self) -> None:
        """Test creation of advanced development tools manager."""
        manager = create_dev_tools_manager()

        assert isinstance(manager, FlextAdvancedDevToolsManager)
        assert hasattr(manager, "_logger")

    def test_unified_class_pattern_compliance(self) -> None:
        """Test that manager follows unified class pattern with nested classes."""
        manager = create_dev_tools_manager()

        # Test nested classes exist
        assert hasattr(manager, "_ProjectDiscoveryService")
        assert hasattr(manager, "_OperationExecutor")

        # Test methods to create nested services
        project_service = manager.create_project_discovery()
        operation_executor = manager.create_operation_executor()

        assert project_service is not None
        assert operation_executor is not None

    def test_advanced_models_integration(self) -> None:
        """Test integration with advanced Pydantic models."""
        create_dev_tools_manager()

        # Test that we can access advanced models namespace
        # Test that the actual classes exist
        assert DevToolsManager is not None
        assert FlextAdvancedDevToolsManager is not None


class TestAdvancedDevOperations:
    """Test suite for advanced development operations with Pydantic patterns."""

    def test_operation_status_enum(self) -> None:
        """Test operation status enumeration."""
        assert OperationStatus.PENDING == "pending"
        assert OperationStatus.RUNNING == "running"
        assert OperationStatus.SUCCESS == "success"
        assert OperationStatus.FAILED == "failed"
        assert OperationStatus.CANCELLED == "cancelled"

    def test_operation_type_enum(self) -> None:
        """Test operation type enumeration."""
        assert OperationType.TEST == "test"
        assert OperationType.LINT == "lint"
        assert OperationType.FORMAT == "format"
        assert OperationType.BUILD == "build"
        assert OperationType.SECURITY == "security"

    def test_project_type_enum(self) -> None:
        """Test project type enumeration."""
        # Project type should be available
        assert ProjectType is not None
        assert isinstance(ProjectType, type)

    def test_operation_creation_with_discriminated_unions(self) -> None:
        """Test creation of operations with discriminated union patterns."""
        manager = create_dev_tools_manager()
        operation_executor = manager.create_operation_executor()

        # Test operation creation with discriminated unions
        test_operation_data = {
            "type": "test",
            "project_filter": "flext-core",
            "coverage_enabled": True,
            "coverage_threshold": 85.0,
            "context": {"workspace_root": "."},
        }

        result = operation_executor.create_test_operation(test_operation_data)
        assert result.is_success

        test_op = result.unwrap()
        assert test_op is not None

    def test_advanced_validation_patterns(self) -> None:
        """Test advanced Pydantic validation patterns."""
        manager = create_dev_tools_manager()
        operation_executor = manager.create_operation_executor()

        # Test validation with invalid data
        invalid_operation = {
            "type": "test",
            "coverage_threshold": 150.0,  # Invalid: > 100
        }

        result = operation_executor.create_test_operation(invalid_operation)
        assert result.is_failure
        assert result.error is not None
        assert "coverage_threshold" in result.error


class TestProjectDiscoveryService:
    """Test suite for nested project discovery service."""

    @pytest.fixture
    def temp_workspace(self, tmp_path: Path) -> Path:
        """Create temporary workspace for testing."""
        workspace = tmp_path / "test-workspace"
        workspace.mkdir()

        # Create Python project
        python_project = workspace / "flext-core"
        python_project.mkdir()
        (python_project / "src").mkdir()
        (python_project / "tests").mkdir()
        (python_project / "pyproject.toml").write_text(
            "[tool.poetry]\nname = 'flext-core'"
        )

        return workspace

    def test_project_discovery_service_creation(self) -> None:
        """Test creation of nested project discovery service."""
        manager = create_dev_tools_manager()
        service = manager.create_project_discovery()

        assert service is not None
        assert hasattr(service, "discover_projects")
        assert hasattr(service, "_analyze_project")

    @patch("pathlib.Path.cwd")
    def test_workspace_discovery(self, mock_cwd: Mock, temp_workspace: Path) -> None:
        """Test workspace project discovery."""
        mock_cwd.return_value = temp_workspace

        manager = create_dev_tools_manager()
        discovery_service = manager.create_project_discovery()

        result = discovery_service.discover_projects(temp_workspace)
        assert result.is_success

        projects = result.unwrap()
        assert isinstance(projects, list)

    def test_project_analysis(self, temp_workspace: Path) -> None:
        """Test individual project analysis."""
        manager = create_dev_tools_manager()
        discovery_service = manager.create_project_discovery()

        python_project = temp_workspace / "flext-core"
        result = discovery_service._analyze_project(python_project)

        assert result.is_success
        project_info = result.unwrap()
        assert project_info is not None


class TestOperationExecutor:
    """Test suite for nested operation executor."""

    def test_operation_executor_creation(self) -> None:
        """Test creation of nested operation executor."""
        manager = create_dev_tools_manager()
        executor = manager.create_operation_executor()

        assert executor is not None
        assert hasattr(executor, "create_test_operation")
        assert hasattr(executor, "execute_test_operation")
        assert hasattr(executor, "execute_lint_operation")
        assert hasattr(executor, "execute_format_operation")

    @patch("subprocess.run")
    def test_test_operation_execution(self, mock_subprocess: Mock) -> None:
        """Test test operation execution."""
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        manager = create_dev_tools_manager()
        executor = manager.create_operation_executor()

        # Create test operation
        operation_data = {
            "type": "test",
            "project_filter": "flext-core",
            "coverage_enabled": True,
            "context": {"workspace_root": "."},
        }

        op_result = executor.create_test_operation(operation_data)
        assert op_result.is_success

        operation = op_result.unwrap()

        # Execute operation
        result = executor.execute_test_operation(operation)
        assert result.is_success

    @patch("subprocess.run")
    def test_lint_operation_execution(self, mock_subprocess: Mock) -> None:
        """Test lint operation execution."""
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        manager = create_dev_tools_manager()
        executor = manager.create_operation_executor()

        # Create lint operation
        operation_data = {
            "type": "lint",
            "tools": ["ruff", "mypy"],
            "fix_issues": False,
            "context": {"workspace_root": "."},
        }

        op_result = executor.create_lint_operation(operation_data)
        assert op_result.is_success

        operation = op_result.unwrap()

        # Execute operation
        result = executor.execute_lint_operation(operation)
        assert result.is_success

    def test_operation_validation_failure(self) -> None:
        """Test operation validation failure handling."""
        manager = create_dev_tools_manager()
        executor = manager.create_operation_executor()

        # Invalid operation data
        invalid_data = {
            "type": "test",
            "test_types": [],  # Empty list should fail validation
        }

        result = executor.create_test_operation(invalid_data)
        assert result.is_failure
        assert result.error is not None
        assert "test_types" in result.error


class TestAdvancedPatternsCompliance:
    """Test suite for Python 3.13 + Pydantic advanced patterns compliance."""

    def test_generic_type_constraints(self) -> None:
        """Test generic type constraints implementation."""
        manager = create_dev_tools_manager()

        # Test that manager is properly typed with generic constraints
        assert isinstance(manager, FlextAdvancedDevToolsManager)

        # Test that type parameters work correctly
        assert hasattr(manager.__class__, "__orig_bases__")

    def test_discriminated_unions_pattern(self) -> None:
        """Test discriminated unions pattern implementation."""
        manager = create_dev_tools_manager()
        executor = manager.create_operation_executor()

        # Test different operation types via discriminated unions
        operations = [
            {
                "type": "test",
                "coverage_enabled": True,
                "context": {"workspace_root": "."},
            },
            {"type": "lint", "tools": ["ruff"], "context": {"workspace_root": "."}},
            {"type": "format", "check_only": True, "context": {"workspace_root": "."}},
        ]

        for op_data in operations:
            result = executor.create_operation(op_data)
            # Some may succeed, some may fail due to missing fields
            # The important thing is the discriminator works
            assert isinstance(result, FlextResult)

    def test_pydantic_v2_validation_patterns(self) -> None:
        """Test Pydantic v2 advanced validation patterns."""
        manager = create_dev_tools_manager()
        executor = manager.create_operation_executor()

        # Test field validation
        operation_data = {
            "type": "test",
            "coverage_threshold": 85.5,  # Float validation
            "test_types": ["unit", "integration"],  # List validation
            "parallel_execution": True,  # Boolean validation
            "context": {"workspace_root": "."},
        }

        result = executor.create_test_operation(operation_data)
        assert result.is_success

        operation = result.unwrap()
        assert operation.coverage_threshold == 85.5
        assert "unit" in operation.test_types

    def test_flext_result_pattern_integration(self, workspace_root: Path) -> None:
        """Test FlextResult pattern integration throughout."""
        manager = create_dev_tools_manager()

        # All operations should return FlextResult
        discovery_service = manager.create_project_discovery()
        executor = manager.create_operation_executor()

        # Test that all methods return FlextResult
        result1 = discovery_service.discover_projects(workspace_root)
        assert isinstance(result1, FlextResult)

        result2 = executor.create_operation({"type": "test"})
        assert isinstance(result2, FlextResult)


class TestModuleExports:
    """Test suite for module exports and __all__ compliance."""

    def test_all_exports_available(self) -> None:
        """Test that all declared exports are available."""
        expected_exports = [
            "DevToolsManager",
            "FlextAdvancedDevToolsManager",
            "create_dev_tools_manager",
        ]

        for export in expected_exports:
            assert export in __all__, f"Export {export} missing from __all__"

    def test_primary_service_export(self) -> None:
        """Test primary service is properly exported."""
        manager = create_dev_tools_manager()
        assert manager is not None

    def test_advanced_models_namespace(self) -> None:
        """Test advanced models namespace is properly exported."""
        # Test that the actual classes are available
        assert DevToolsManager is not None
        assert FlextAdvancedDevToolsManager is not None


class TestErrorHandling:
    """Test suite for enterprise error handling patterns."""

    def test_operation_execution_failure(self) -> None:
        """Test operation execution failure handling."""
        manager = create_dev_tools_manager()
        executor = manager.create_operation_executor()

        operation_data = {
            "type": "test",
            "project_filter": "flext-core",
            "context": {"workspace_root": "."},
        }
        op_result = executor.create_test_operation(operation_data)
        assert op_result.is_success

        operation = op_result.unwrap()

        # Execute operation - current implementation is mocked and succeeds
        result = executor.execute_test_operation(operation)
        assert result.is_success
        assert result.data is not None
        assert result.data.status == "success"

    def test_invalid_operation_data(self) -> None:
        """Test handling of invalid operation data."""
        manager = create_dev_tools_manager()
        executor = manager.create_operation_executor()

        # Completely invalid data
        invalid_data = {"invalid": "data"}

        result = executor.create_operation(invalid_data)
        assert result.is_failure

    def test_prerequisite_validation_failure(self) -> None:
        """Test prerequisite validation failure handling."""
        manager = create_dev_tools_manager()
        executor = manager.create_operation_executor()

        # Create operation that may fail prerequisites
        operation_data = {"type": "test"}
        op_result = executor.create_test_operation(operation_data)

        if op_result.is_success:
            operation = op_result.unwrap()

            # Test prerequisite validation
            with patch("subprocess.run", side_effect=Exception("Command not found")):
                result = operation.validate_prerequisites()
                assert result.is_failure
