"""Tests for flext.workspace_models module.

Tests the workspace model classes to achieve 100% test coverage
and validate proper functionality of business rules and model validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
"""

from flext.project_types import ProjectType, WorkspaceStatus
from flext.workspace_models import FlextAdvancedWorkspaceModels


class TestProject:
    """Test the Project model with business rule validation."""

    def test_project_creation_basic(self) -> None:
        """Test basic project creation with required fields."""
        project = FlextAdvancedWorkspaceModels.Project(
            name="test-project",
            path="/path/to/project",
            project_type=ProjectType.PYTHON,
        )

        assert project.name == "test-project"
        assert project.path == "/path/to/project"
        assert project.project_type == ProjectType.PYTHON
        assert project.has_tests is False  # Default value
        assert project.has_pyproject is False  # Default value
        assert project.has_go_mod is False  # Default value
        assert project.test_count == 0  # Default value

    def test_project_creation_with_all_fields(self) -> None:
        """Test project creation with all optional fields specified."""
        project = FlextAdvancedWorkspaceModels.Project(
            name="full-project",
            path="/path/to/full/project",
            project_type=ProjectType.GO,
            has_tests=True,
            has_pyproject=True,
            has_go_mod=True,
            test_count=25,
        )

        assert project.name == "full-project"
        assert project.path == "/path/to/full/project"
        assert project.project_type == ProjectType.GO
        assert project.has_tests is True
        assert project.has_pyproject is True
        assert project.has_go_mod is True
        assert project.test_count == 25

    def test_project_validate_business_rules_success(self) -> None:
        """Test project business rule validation - success case (line 36)."""
        project = FlextAdvancedWorkspaceModels.Project(
            name="valid-project",
            path="/valid/path",
            project_type=ProjectType.PYTHON,
        )

        # This covers line 36: return FlextResult[None].ok(None)
        result = project.validate_business_rules()

        assert result.is_success
        assert result.value is None

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
            project = FlextAdvancedWorkspaceModels.Project(
                name=f"project-{project_type.value}",
                path=f"/path/to/{project_type.value}",
                project_type=project_type,
            )

            assert project.project_type == project_type

            # Test validation for each type
            result = project.validate_business_rules()
            assert result.is_success

    def test_project_test_count_validation(self) -> None:
        """Test that test_count field validates non-negative values."""
        # Valid test count
        project = FlextAdvancedWorkspaceModels.Project(
            name="test-project",
            path="/path/to/project",
            project_type=ProjectType.PYTHON,
            test_count=10,
        )
        assert project.test_count == 10

        # Zero test count (should be valid)
        project_zero = FlextAdvancedWorkspaceModels.Project(
            name="test-project-zero",
            path="/path/to/project",
            project_type=ProjectType.PYTHON,
            test_count=0,
        )
        assert project_zero.test_count == 0


class TestWorkspaceContext:
    """Test the WorkspaceContext configuration model."""

    def test_workspace_context_creation_minimal(self) -> None:
        """Test workspace context creation with minimal required fields."""
        context = FlextAdvancedWorkspaceModels.WorkspaceContext(
            workspace_root="/workspace/root",
        )

        assert context.workspace_root == "/workspace/root"
        assert context.project_filter is None  # Default value
        assert context.include_hidden is False  # Default value
        assert context.max_depth == 3  # Default value

    def test_workspace_context_creation_full(self) -> None:
        """Test workspace context creation with all fields specified."""
        context = FlextAdvancedWorkspaceModels.WorkspaceContext(
            workspace_root="/full/workspace",
            project_filter="test-*",
            include_hidden=True,
            max_depth=5,
        )

        assert context.workspace_root == "/full/workspace"
        assert context.project_filter == "test-*"
        assert context.include_hidden is True
        assert context.max_depth == 5

    def test_workspace_context_max_depth_validation(self) -> None:
        """Test that max_depth validates within range."""
        # Valid max depth values
        for depth in [1, 5, 10]:
            context = FlextAdvancedWorkspaceModels.WorkspaceContext(
                workspace_root="/workspace",
                max_depth=depth,
            )
            assert context.max_depth == depth


class TestWorkspaceInfo:
    """Test the WorkspaceInfo model with business rule validation."""

    def test_workspace_info_creation_minimal(self) -> None:
        """Test workspace info creation with minimal required fields."""
        info = FlextAdvancedWorkspaceModels.WorkspaceInfo(
            name="test-workspace",
            path="/workspace/path",
        )

        assert info.name == "test-workspace"
        assert info.path == "/workspace/path"
        assert info.project_count == 0  # Default value
        assert info.total_size_mb == 0.0  # Default value
        assert info.projects is None  # Default value
        assert info.status == WorkspaceStatus.READY  # Default value

    def test_workspace_info_creation_full(self) -> None:
        """Test workspace info creation with all fields specified."""
        project_list = ["project1", "project2", "project3"]

        info = FlextAdvancedWorkspaceModels.WorkspaceInfo(
            name="full-workspace",
            path="/full/workspace/path",
            project_count=3,
            total_size_mb=150.5,
            projects=project_list,
            status=WorkspaceStatus.INITIALIZING,
        )

        assert info.name == "full-workspace"
        assert info.path == "/full/workspace/path"
        assert info.project_count == 3
        assert info.total_size_mb == 150.5
        assert info.projects == project_list
        assert info.status == WorkspaceStatus.INITIALIZING

    def test_workspace_info_validate_business_rules_success(self) -> None:
        """Test workspace info business rule validation - success case (line 70)."""
        info = FlextAdvancedWorkspaceModels.WorkspaceInfo(
            name="valid-workspace",
            path="/valid/path",
            project_count=5,
            total_size_mb=100.0,
        )

        # This covers line 70: return FlextResult[None].ok(None)
        result = info.validate_business_rules()

        assert result.is_success
        assert result.value is None

    def test_workspace_info_validate_business_rules_edge_cases(self) -> None:
        """Test workspace info business rule validation - edge cases."""
        # Test with valid values at boundaries
        info = FlextAdvancedWorkspaceModels.WorkspaceInfo(
            name="edge-workspace",
            path="/edge/path",
            project_count=0,  # Valid boundary value
            total_size_mb=0.0,  # Valid boundary value
        )

        # Test that business rules pass for valid boundary values
        result = info.validate_business_rules()
        assert result.is_success

        # Test with normal positive values
        info_normal = FlextAdvancedWorkspaceModels.WorkspaceInfo(
            name="normal-workspace",
            path="/normal/path",
            project_count=10,
            total_size_mb=250.5,
        )

        result_normal = info_normal.validate_business_rules()
        assert result_normal.is_success

    def test_workspace_info_different_statuses(self) -> None:
        """Test workspace info with different status values."""
        statuses = [
            WorkspaceStatus.READY,
            WorkspaceStatus.INITIALIZING,
            WorkspaceStatus.ERROR,
        ]

        for status in statuses:
            info = FlextAdvancedWorkspaceModels.WorkspaceInfo(
                name=f"workspace-{status.value}",
                path=f"/path/to/{status.value}",
                status=status,
            )

            assert info.status == status

            # Test validation for each status
            result = info.validate_business_rules()
            assert result.is_success

    def test_workspace_info_zero_values_valid(self) -> None:
        """Test that zero values are valid for numeric fields."""
        info = FlextAdvancedWorkspaceModels.WorkspaceInfo(
            name="zero-workspace",
            path="/zero/path",
            project_count=0,
            total_size_mb=0.0,
        )

        result = info.validate_business_rules()
        assert result.is_success

    def test_workspace_info_with_projects_list(self) -> None:
        """Test workspace info with projects list populated."""
        projects = ["flext-core", "flext-cli", "flext-auth", "flext-tools"]

        info = FlextAdvancedWorkspaceModels.WorkspaceInfo(
            name="multi-project-workspace",
            path="/multi/project/path",
            project_count=len(projects),
            total_size_mb=500.25,
            projects=projects,
        )

        assert info.projects == projects
        assert len(info.projects) == info.project_count

        result = info.validate_business_rules()
        assert result.is_success


class TestWorkspaceModelsIntegration:
    """Integration tests for workspace model interactions."""

    def test_full_workspace_modeling_workflow(self) -> None:
        """Test a complete workflow using all workspace models."""
        # Create workspace context
        context = FlextAdvancedWorkspaceModels.WorkspaceContext(
            workspace_root="/flext/workspace",
            project_filter="flext-*",
            include_hidden=False,
            max_depth=2,
        )

        # Create projects
        projects = [
            FlextAdvancedWorkspaceModels.Project(
                name="flext-core",
                path="/flext/workspace/flext-core",
                project_type=ProjectType.PYTHON,
                has_tests=True,
                has_pyproject=True,
                test_count=45,
            ),
            FlextAdvancedWorkspaceModels.Project(
                name="flext-cli",
                path="/flext/workspace/flext-cli",
                project_type=ProjectType.PYTHON,
                has_tests=True,
                has_pyproject=True,
                test_count=20,
            ),
            FlextAdvancedWorkspaceModels.Project(
                name="flext-tools",
                path="/flext/workspace/flext-tools",
                project_type=ProjectType.GO,
                has_tests=True,
                has_go_mod=True,
                test_count=15,
            ),
        ]

        # Validate all projects
        for project in projects:
            result = project.validate_business_rules()
            assert result.is_success

        # Create workspace info
        workspace_info = FlextAdvancedWorkspaceModels.WorkspaceInfo(
            name="flext-ecosystem",
            path=context.workspace_root,
            project_count=len(projects),
            total_size_mb=sum([50.0, 30.0, 25.0]),  # Simulated sizes
            projects=[p.name for p in projects],
            status=WorkspaceStatus.READY,
        )

        # Validate workspace info
        result = workspace_info.validate_business_rules()
        assert result.is_success

        # Verify data consistency
        assert workspace_info.project_count == len(projects)
        assert set(workspace_info.projects or []) == {p.name for p in projects}
        assert workspace_info.total_size_mb > 0
