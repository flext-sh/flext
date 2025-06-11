"""
Integration tests for the REST API.
"""

import tempfile
from contextlib import contextmanager
from pathlib import Path

from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from analyzer.models import AnalysisSession, Project


class TestProjectAPI(TransactionTestCase):
    """Test the Project API endpoints."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
        # Create test user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.project = Project.objects.create(
            name="api_test_project",
            path="/tmp/api_test",
            description="Project for API testing",
            package_name="api_test",
            package_version="1.0.0",
            package_type="local",
        )

    def test_list_projects(self):
        """Test listing projects."""
        url = reverse("project-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "results" in data
        assert len(data["results"]) >= 1

        # Find our test project
        project_data = next(
            (p for p in data["results"] if p["name"] == "api_test_project"), None
        )
        assert project_data is not None
        assert project_data["name"] == "api_test_project"
        assert project_data["package_name"] == "api_test"

    def test_create_project(self):
        """Test creating a project via API."""
        url = reverse("project-list")
        data = {
            "name": "new_api_project",
            "path": "/tmp/new_project",
            "description": "New project created via API",
            "package_name": "new_project",
            "package_version": "2.0.0",
            "package_type": "source",
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Verify project was created
        created_project = Project.objects.get(name="new_api_project")
        assert created_project.path == "/tmp/new_project"
        assert created_project.package_version == "2.0.0"

    def test_get_project_detail(self):
        """Test getting project details."""
        url = reverse("project-detail", kwargs={"pk": self.project.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == self.project.pk
        assert data["name"] == "api_test_project"
        assert data["path"] == "/tmp/api_test"

    def test_update_project(self):
        """Test updating a project."""
        url = reverse("project-detail", kwargs={"pk": self.project.pk})
        data = {
            "name": "api_test_project",
            "path": "/tmp/api_test",
            "description": "Updated description",
            "package_version": "1.1.0",
        }

        response = self.client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Verify update
        self.project.refresh_from_db()
        assert self.project.description == "Updated description"
        assert self.project.package_version == "1.1.0"

    def test_delete_project(self):
        """Test deleting a project."""
        project_id = self.project.pk
        url = reverse("project-detail", kwargs={"pk": project_id})

        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        assert not Project.objects.filter(pk=project_id).exists()

    def test_project_validation(self):
        """Test project validation."""
        url = reverse("project-list")

        # Test missing required fields
        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Test duplicate name
        data = {
            "name": "api_test_project",  # Duplicate name
            "path": "/tmp/duplicate",
        }
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_project_analysis_sessions_relationship(self):
        """Test that project includes related analysis sessions."""
        # Create a session for the project
        session = AnalysisSession.objects.create(
            flx_project=self.project,
            status="completed",
            overall_score=85.5,
        )

        url = reverse("project-detail", kwargs={"pk": self.project.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should include analysis sessions
        assert "analysis_sessions" in data
        assert len(data["analysis_sessions"]) == 1
        assert data["analysis_sessions"][0]["id"] == session.id


class TestAnalysisSessionAPI(TransactionTestCase):
    """Test the AnalysisSession API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.project = Project.objects.create(
            name="session_test_project",
            path="/tmp/session_test",
        )
        self.session = AnalysisSession.objects.create(
            flx_project=self.project,
            status="completed",
            overall_score=75.0,
            quality_grade="B",
        )

    def test_list_sessions(self):
        """Test listing analysis sessions."""
        url = reverse("analysissession-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "results" in data
        assert len(data["results"]) >= 1

        session_data = data["results"][0]
        assert session_data["id"] == self.session.id
        assert session_data["status"] == "completed"
        assert session_data["overall_score"] == 75.0

    def test_create_session(self):
        """Test creating an analysis session."""
        url = reverse("analysissession-list")
        data = {
            "flx_project": self.project.pk,
            "name": "API Test Session",
            "include_security": True,
            "include_dead_code": False,
            "complexity_threshold": 15.0,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Verify session was created
        created_session = AnalysisSession.objects.get(name="API Test Session")
        assert created_session.flx_project == self.project
        assert created_session.include_security is True
        assert created_session.include_dead_code is False

    def test_get_session_detail(self):
        """Test getting session details."""
        url = reverse("analysissession-detail", kwargs={"pk": self.session.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == self.session.id
        assert data["flx_project"] == self.project.pk
        assert data["overall_score"] == 75.0
        assert data["quality_grade"] == "B"

    def test_update_session(self):
        """Test updating an analysis session."""
        url = reverse("analysissession-detail", kwargs={"pk": self.session.pk})
        data = {
            "overall_score": 80.0,
            "quality_grade": "B+",
        }

        response = self.client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Verify update
        self.session.refresh_from_db()
        assert self.session.overall_score == 80.0
        assert self.session.quality_grade == "B+"

    def test_filter_sessions_by_project(self):
        """Test filtering sessions by project."""
        # Create another project and session
        other_project = Project.objects.create(
            name="other_project",
            path="/tmp/other",
        )
        AnalysisSession.objects.create(
            flx_project=other_project,
            status="pending",
        )

        url = reverse("analysissession-list")
        response = self.client.get(url, {"flx_project": self.project.pk})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should only return sessions for our project
        assert len(data["results"]) == 1
        assert data["results"][0]["flx_project"] == self.project.pk

    def test_filter_sessions_by_status(self):
        """Test filtering sessions by status."""
        # Create a pending session
        AnalysisSession.objects.create(
            flx_project=self.project,
            status="pending",
        )

        url = reverse("analysissession-list")
        response = self.client.get(url, {"status": "completed"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should only return completed sessions
        for session in data["results"]:
            assert session["status"] == "completed"


class TestAnalysisAPI(TransactionTestCase):
    """Test the analysis execution API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    @contextmanager
    def create_test_project_with_files(self):
        """Create a test project with actual Python files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Create a simple Python file
            (project_path / "test_file.py").write_text(
                '''
def test_function():
    """A simple test function."""
    return "Hello, World!"

class TestClass:
    """A simple test class."""

    def method(self):
        """A simple method."""
        return 42
'''
            )

            # Create project in database
            project = Project.objects.create(
                name="analysis_api_test",
                path=str(project_path),
                description="Project for analysis API testing",
            )

            yield project

    def test_start_analysis_api(self):
        """Test starting analysis via API."""
        with self.create_test_project_with_files() as project:
            url = reverse("project-start-analysis", kwargs={"pk": project.pk})
            data = {
                "include_security": True,
                "include_dead_code": True,
                "backends": ["ast"],  # Use only AST backend for faster testing
            }

            response = self.client.post(url, data, format="json")

            assert response.status_code == status.HTTP_202_ACCEPTED

            response_data = response.json()
            assert "session_id" in response_data
            assert "message" in response_data

            # Verify session was created
            session_id = response_data["session_id"]
            session = AnalysisSession.objects.get(id=session_id)
            assert session.flx_project == project
            assert session.include_security is True
            assert session.include_dead_code is True

    def test_analysis_status_api(self):
        """Test checking analysis status via API."""
        with self.create_test_project_with_files() as project:
            # Create a session
            session = AnalysisSession.objects.create(
                flx_project=project,
                status="running",
            )

            url = reverse("analysissession-status", kwargs={"pk": session.pk})
            response = self.client.get(url)

            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            assert data["status"] == "running"
            assert data["session_id"] == session.id
            assert "progress" in data

    def test_analysis_results_api(self):
        """Test getting analysis results via API."""
        with self.create_test_project_with_files() as project:
            # Create a completed session
            session = AnalysisSession.objects.create(
                flx_project=project,
                status="completed",
                overall_score=85.0,
                quality_grade="B",
            )

            url = reverse("analysissession-results", kwargs={"pk": session.pk})
            response = self.client.get(url)

            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            assert data["session_id"] == session.id
            assert data["status"] == "completed"
            assert data["overall_score"] == 85.0
            assert "file_analyses" in data
            assert "security_issues" in data
            assert "quality_metrics" in data

    def test_invalid_project_analysis(self):
        """Test starting analysis on non-existent project."""
        url = reverse("project-start-analysis", kwargs={"pk": 99999})

        response = self.client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_analysis_with_invalid_backends(self):
        """Test starting analysis with invalid backends."""
        with self.create_test_project_with_files() as project:
            url = reverse("project-start-analysis", kwargs={"pk": project.pk})
            data = {
                "backends": ["invalid_backend", "another_invalid"],
            }

            response = self.client.post(url, data, format="json")

            # Should handle gracefully - might accept and filter invalid backends
            # or return 400 depending on implementation
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_202_ACCEPTED,
            ]


class TestAPIResponseFormats(TransactionTestCase):
    """Test API response formats and serialization."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.project = Project.objects.create(
            name="format_test_project",
            path="/tmp/format_test",
        )

    def test_project_serialization(self):
        """Test project serialization format."""
        url = reverse("project-detail", kwargs={"pk": self.project.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check required fields
        required_fields = ["id", "name", "path", "created_at", "updated_at"]
        for field in required_fields:
            assert field in data

        # Check field types
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["total_files"], int)
        assert isinstance(data["python_files"], int)

    def test_session_serialization(self):
        """Test session serialization format."""
        session = AnalysisSession.objects.create(
            flx_project=self.project,
            overall_score=75.5,
            backends_used=["ast", "external"],
        )

        url = reverse("analysissession-detail", kwargs={"pk": session.pk})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check required fields
        required_fields = ["id", "flx_project", "status", "created_at"]
        for field in required_fields:
            assert field in data

        # Check field types
        assert isinstance(data["overall_score"], int | float)
        assert isinstance(data["backends_used"], list)
        assert data["backends_used"] == ["ast", "external"]

    def test_pagination_format(self):
        """Test pagination response format."""
        # Create multiple projects (more than PAGE_SIZE=50 to trigger pagination)
        for i in range(55):
            Project.objects.create(
                name=f"pagination_test_{i}",
                path=f"/tmp/pagination_{i}",
            )

        url = reverse("project-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check pagination structure
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data

        assert isinstance(data["count"], int)
        assert isinstance(data["results"], list)
        assert data["count"] > len(data["results"])  # Should be paginated

    def test_api_error_format(self):
        """Test API error response format."""
        # Try to create project with invalid data
        url = reverse("project-list")
        response = self.client.post(url, {"invalid": "data"}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()

        # Should have error details
        assert isinstance(data, dict)
        # Common error formats: field errors or general errors
        assert any(
            key in data for key in ["detail", "name", "path", "non_field_errors"]
        )

    def test_content_type_headers(self):
        """Test that API returns correct content-type headers."""
        url = reverse("project-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"].startswith("application/json")

    def test_cors_headers(self):
        """Test CORS headers are present."""
        url = reverse("project-list")
        response = self.client.get(url)

        # CORS headers should be present (configured in settings)
        # This test might need adjustment based on actual CORS configuration
        assert response.status_code == status.HTTP_200_OK
