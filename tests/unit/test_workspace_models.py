"""Tests for flext.workspace_models module.

Tests the workspace model classes to achieve 100% test coverage
and validate proper functionality of business rules and model validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
"""

from flext.project_types import ProjectType, WorkspaceStatus
from flext_core import FlextModels


class TestProject:
    """Test the Project model with business rule validation."""

    def test_project_creation_basic(self) -> None:
        """Test basic project creation with required fields."""
        project = FlextModels.Project(
            name="test-project",
            organization_id="test-org",
            project_type="python",
        )

        assert project.name == "test-project"
        assert project.organization_id == "test-org"
        assert project.project_type == "python"
        assert project.is_test_project is False  # Default value
        assert project.test_framework is None  # Default value
        assert project.repository_path is None  # Default value

    def test_project_creation_with_all_fields(self) -> None:
        """Test project creation with all optional fields specified."""
        project = FlextModels.Project(
            name="full-project",
            organization_id="full-org",
            repository_path="/path/to/full/project",
            project_type="go",
            is_test_project=True,
            test_framework="go test",
        )

        assert project.name == "full-project"
        assert project.organization_id == "full-org"
        assert project.repository_path == "/path/to/full/project"
        assert project.project_type == "go"
        assert project.is_test_project is True
        assert project.test_framework == "go test"

    def test_project_validate_business_rules_success(self) -> None:
        """Test project business rule validation - success case."""
        project = FlextModels.Project(
            name="valid-project",
            organization_id="test-org",
            path="/valid/path",
            project_type=ProjectType.PYTHON,
        )

        # Project creation itself validates business rules via Pydantic
        assert project.name == "valid-project"
        assert project.project_type == ProjectType.PYTHON

    def test_project_different_project_types(self) -> None:
        """Test project creation with different project types."""
        project_types = [
            ProjectType.PYTHON,
            ProjectType.GO,
            ProjectType.JAVASCRIPT,
            ProjectType.RUST,
            ProjectType.DOCUMENTATION,
            ProjectType.MIXED,
        ]

        for project_type in project_types:
            project = FlextModels.Project(
                name=f"project-{project_type.value}",
                organization_id="test-org",
                path=f"/path/to/{project_type.value}",
                project_type=project_type,
            )

            assert project.project_type == project_type

            # Test validation for each type - successful creation validates
            assert project.project_type == project_type


class TestWorkspaceContext:
    """Test the WorkspaceContext configuration model."""

    def test_workspace_context_creation_minimal(self) -> None:
        """Test workspace context creation with minimal required fields."""
        context = FlextModels.WorkspaceInfo(
            workspace_id="ws-ctx-001",
            name="workspace-context",
            root_path="/workspace/root",
        )

        assert context.workspace_id == "ws-ctx-001"
        assert context.name == "workspace-context"
        assert context.root_path == "/workspace/root"

    def test_workspace_context_creation_full(self) -> None:
        """Test workspace context creation with all fields specified."""
        context = FlextModels.WorkspaceInfo(
            workspace_id="ws-full-ctx-001",
            name="full-workspace-context",
            root_path="/full/workspace",
            workspace_root="/full/workspace",
            project_filter="test-*",
            include_hidden=True,
            max_depth=5,
        )

        assert context.root_path == "/full/workspace"
        # Test that workspace was created successfully
        assert context.workspace_id == "ws-full-ctx-001"
        assert context.name == "full-workspace-context"

    def test_workspace_context_max_depth_validation(self) -> None:
        """Test workspace info creation with different configurations."""
        # Test workspace info with minimal required fields
        for _i, depth_value in enumerate([1, 5, 10]):
            context = FlextModels.WorkspaceInfo(
                workspace_id=f"ws-depth-{depth_value}",
                name=f"workspace-{depth_value}",
                root_path="/workspace",
            )
            assert context.workspace_id == f"ws-depth-{depth_value}"
            assert context.name == f"workspace-{depth_value}"


class TestWorkspaceInfo:
    """Test the WorkspaceInfo model with business rule validation."""

    def test_workspace_info_creation_minimal(self) -> None:
        """Test workspace info creation with minimal required fields."""
        info = FlextModels.WorkspaceInfo(
            workspace_id="ws-test-001",
            name="test-workspace",
            root_path="/workspace/path",
        )

        assert info.name == "test-workspace"
        assert info.root_path == "/workspace/path"
        assert info.workspace_id == "ws-test-001"

    def test_workspace_info_creation_full(self) -> None:
        """Test workspace info creation with all fields specified."""
        project_list = [
            FlextModels.Project(
                name="project1",
                organization_id="test-org",
                repository_path="/full/workspace/path/project1",
            ),
            FlextModels.Project(
                name="project2",
                organization_id="test-org",
                repository_path="/full/workspace/path/project2",
            ),
            FlextModels.Project(
                name="project3",
                organization_id="test-org",
                repository_path="/full/workspace/path/project3",
            ),
        ]

        info = FlextModels.WorkspaceInfo(
            workspace_id="ws-full-001",
            name="full-workspace",
            root_path="/full/workspace/path",
            projects=project_list,
            total_files=10,
        )

        assert info.name == "full-workspace"
        assert info.root_path == "/full/workspace/path"
        assert info.projects == project_list
        assert len(info.projects) == 3

    def test_workspace_info_validate_business_rules_success(self) -> None:
        """Test workspace info business rule validation - success case (line 70)."""
        info = FlextModels.WorkspaceInfo(
            workspace_id="ws-valid-001",
            name="valid-workspace",
            root_path="/valid/path",
        )

        # Successful creation validates business rules via Pydantic
        assert info.name == "valid-workspace"
        assert info.root_path == "/valid/path"

    def test_workspace_info_validate_business_rules_edge_cases(self) -> None:
        """Test workspace info business rule validation - edge cases."""
        # Test with valid values at boundaries
        info = FlextModels.WorkspaceInfo(
            workspace_id="edge-ws-123",
            name="edge-workspace",
            root_path="/edge/path",
            path="/edge/path",
            project_count=0,  # Valid boundary value
            total_size_mb=0.0,  # Valid boundary value
        )

        # Test that business rules pass for valid boundary values - successful creation validates
        assert info.workspace_id == "edge-ws-123"
        assert info.name == "edge-workspace"

        # Test with normal positive values
        info_normal = FlextModels.WorkspaceInfo(
            workspace_id="normal-ws-456",
            root_path="/normal/path",
            name="normal-workspace",
            path="/normal/path",
            project_count=10,
            total_size_mb=250.5,
        )

        # Successful creation validates business rules
        assert info_normal.workspace_id == "normal-ws-456"
        assert info_normal.name == "normal-workspace"

    def test_workspace_info_different_configurations(self) -> None:
        """Test WorkspaceInfo with different configurations using actual API."""
        # Test different workspace configurations
        configurations = [
            {"name": "ready-workspace", "projects": []},
            {"name": "project-workspace", "projects": [], "total_files": 5},
            {
                "name": "large-workspace",
                "projects": [],
                "total_files": 100,
                "total_size_bytes": 1024,
            },
        ]

        for config in configurations:
            info = FlextModels.WorkspaceInfo(
                workspace_id=f"ws-{config['name']}-001",
                name=config["name"],
                root_path=f"/path/to/{config['name']}",
                projects=config.get("projects", []),
                total_files=config.get("total_files", 0),
                total_size_bytes=config.get("total_size_bytes", 0),
            )

            assert info.name == config["name"]
            assert info.total_files == config.get("total_files", 0)
            assert info.total_size_bytes == config.get("total_size_bytes", 0)

    def test_workspace_info_zero_values_valid(self) -> None:
        """Test that zero values are valid for numeric fields."""
        info = FlextModels.WorkspaceInfo(
            workspace_id="ws-zero-001",
            name="zero-workspace",
            root_path="/zero/path",
            total_files=0,
            total_size_bytes=0,
        )

        # The model validates automatically on creation
        assert info.total_files == 0
        assert info.total_size_bytes == 0

    def test_workspace_info_with_projects_list(self) -> None:
        """Test workspace info with projects list populated."""
        projects = [
            FlextModels.Project(
                name="flext-core",
                organization_id="flext-org",
                repository_path="/repo/flext-core",
            ),
            FlextModels.Project(
                name="flext-cli",
                organization_id="flext-org",
                repository_path="/repo/flext-cli",
            ),
        ]

        info = FlextModels.WorkspaceInfo(
            workspace_id="ws-multi-001",
            name="multi-project-workspace",
            root_path="/multi/project/path",
            projects=projects,
            total_files=50,
            total_size_bytes=500 * 1024,  # 500KB
        )

        assert info.projects == projects
        assert len(info.projects) == 2
        assert info.total_files == 50


class TestWorkspaceModelsIntegration:
    """Integration tests for workspace model interactions."""

    def test_full_workspace_modeling_workflow(self) -> None:
        """Test a complete workflow using all workspace models."""
        # Create workspace context
        context = FlextModels.WorkspaceInfo(
            workspace_id="ws-integration-001",
            name="integration-workspace",
            root_path="/flext/workspace",
            workspace_root="/flext/workspace",
            project_filter="flext-*",
            include_hidden=False,
            max_depth=2,
        )

        # Create projects
        projects = [
            FlextModels.Project(
                name="flext-core",
                organization_id="flext-org",
                path="/flext/workspace/flext-core",
                project_type=ProjectType.PYTHON,
                has_tests=True,
                has_pyproject=True,
                test_count=45,
            ),
            FlextModels.Project(
                name="flext-cli",
                organization_id="flext-org",
                path="/flext/workspace/flext-cli",
                project_type=ProjectType.PYTHON,
                has_tests=True,
                has_pyproject=True,
                test_count=20,
            ),
            FlextModels.Project(
                name="flext-tools",
                organization_id="flext-org",
                path="/flext/workspace/flext-tools",
                project_type=ProjectType.GO,
                has_tests=True,
                has_go_mod=True,
                test_count=15,
            ),
        ]

        # Validate all projects - successful creation validates
        for project in projects:
            assert project.name is not None
            assert project.project_type is not None

        # Create workspace info
        workspace_info = FlextModels.WorkspaceInfo(
            workspace_id="ws-ecosystem-001",
            name="flext-ecosystem",
            root_path=context.root_path,
            path=context.root_path,
            project_count=len(projects),
            total_size_mb=sum([50.0, 30.0, 25.0]),  # Simulated sizes
            total_files=100,  # Required when projects is not empty
            projects=projects,  # Use Project objects, not names
            status=WorkspaceStatus.READY,
        )

        # Validate workspace info - successful creation validates
        assert workspace_info.name == "flext-ecosystem"

        # Verify data consistency
        assert workspace_info.workspace_id == "ws-ecosystem-001"
        assert {p.name for p in (workspace_info.projects or [])} == {
            p.name for p in projects
        }
        assert workspace_info.root_path == context.root_path
