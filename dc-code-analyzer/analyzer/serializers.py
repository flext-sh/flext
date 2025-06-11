"""Django REST Framework serializers for analyzer models."""

from __future__ import annotations

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    AnalysisSession,
    DeadCodeIssue,
    DuplicateCodeBlock,
    DuplicateLocation,
    FileAnalysis,
    Project,
    QualityMetrics,
    SecurityIssue,
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""

    analysis_sessions_count = serializers.SerializerMethodField()
    latest_analysis = serializers.SerializerMethodField()
    analysis_sessions = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "path",
            "package_name",
            "package_version",
            "package_type",
            "is_installed_package",
            "install_location",
            "created_at",
            "updated_at",
            "total_files",
            "total_lines",
            "python_files",
            "analysis_sessions_count",
            "latest_analysis",
            "analysis_sessions",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_analysis_sessions_count(self, obj) -> int:
        """Get count of analysis sessions for this flx_project."""
        return obj.analysis_sessions.count()  # type: ignore[no-any-return]

    def get_latest_analysis(self, obj) -> dict | None:
        """Get latest analysis session summary."""
        latest = obj.analysis_sessions.first()
        if latest:
            return {
                "id": str(latest.id),
                "status": latest.status,
                "overall_score": latest.overall_score,
                "quality_grade": latest.quality_grade,
                "created_at": latest.created_at,
            }
        return None

    def get_analysis_sessions(self, obj) -> list:
        """Get analysis sessions for this project."""
        # Import here to avoid circular import
        sessions = obj.analysis_sessions.all()
        return [
            {
                "id": session.id,
                "name": session.name,
                "status": session.status,
                "overall_score": session.overall_score,
                "quality_grade": session.quality_grade,
                "created_at": session.created_at,
            }
            for session in sessions
        ]


class QualityMetricsSerializer(serializers.ModelSerializer):
    """Serializer for QualityMetrics model."""

    class Meta:
        model = QualityMetrics
        fields = [
            "overall_score",
            "complexity_score",
            "maintainability_score",
            "security_score",
            "documentation_score",
            "duplication_score",
            "total_files",
            "total_lines",
            "total_functions",
            "total_classes",
            "avg_complexity",
            "max_complexity",
            "complex_functions_count",
            "docstring_coverage",
            "documented_functions",
            "security_issues_count",
            "dead_code_items_count",
            "duplicate_blocks_count",
            "duplicate_lines_ratio",
            "technical_debt_ratio",
            "estimated_debt_hours",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class AnalysisSessionSerializer(serializers.ModelSerializer):
    """Serializer for AnalysisSession model."""

    flx_project = serializers.IntegerField(source='flx_project.id', read_only=True)
    project_detail = ProjectSerializer(source='flx_project', read_only=True)
    quality_metrics = QualityMetricsSerializer(read_only=True)
    duration = serializers.ReadOnlyField()

    # Counts for related objects
    security_issues_count = serializers.SerializerMethodField()
    dead_code_issues_count = serializers.SerializerMethodField()
    duplicate_blocks_count = serializers.SerializerMethodField()
    file_analyses_count = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisSession
        fields = [
            "id",
            "name",
            "flx_project",
            "project_detail",
            "status",
            "include_security",
            "include_dead_code",
            "include_duplicates",
            "complexity_threshold",
            "similarity_threshold",
            "backends_used",
            "started_at",
            "completed_at",
            "created_at",
            "overall_score",
            "quality_grade",
            "files_analyzed",
            "error_message",
            "duration",
            "quality_metrics",
            "security_issues_count",
            "dead_code_issues_count",
            "duplicate_blocks_count",
            "file_analyses_count",
        ]
        read_only_fields = [
            "id",
            "started_at",
            "completed_at",
            "created_at",
            "duration",
        ]

    def get_security_issues_count(self, obj) -> int:
        """Get count of security issues."""
        return obj.security_issues.count()  # type: ignore[no-any-return]

    def get_dead_code_issues_count(self, obj) -> int:
        """Get count of dead code issues."""
        return obj.dead_code_issues.count()  # type: ignore[no-any-return]

    def get_duplicate_blocks_count(self, obj) -> int:
        """Get count of duplicate blocks."""
        return obj.duplicate_blocks.count()  # type: ignore[no-any-return]

    def get_file_analyses_count(self, obj) -> int:
        """Get count of file analyses."""
        return obj.file_analyses.count()  # type: ignore[no-any-return]


class CreateAnalysisSessionSerializer(serializers.ModelSerializer):
    """Serializer for creating analysis sessions."""

    flx_project = serializers.IntegerField(write_only=True)

    class Meta:
        model = AnalysisSession
        fields = [
            "flx_project",
            "name",
            "include_security",
            "include_dead_code",
            "include_duplicates",
            "complexity_threshold",
            "similarity_threshold",
            "backends_used",
        ]

    def create(self, validated_data) -> AnalysisSession:
        """Create analysis session with flx_project lookup."""
        project_id = validated_data.pop("flx_project")
        try:
            flx_project: Project = Project.objects.get(id=project_id)
            validated_data["flx_project"] = flx_project
            return super().create(validated_data)  # type: ignore[no-any-return]
        except Project.DoesNotExist as e:
            raise serializers.ValidationError(
                {"flx_project": "Project not found"}
            ) from e


class FileAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for FileAnalysis model."""

    session: serializers.StringRelatedField = serializers.StringRelatedField(
        read_only=True
    )
    security_issues_count = serializers.SerializerMethodField()
    dead_code_issues_count = serializers.SerializerMethodField()
    duplicate_locations_count = serializers.SerializerMethodField()

    class Meta:
        model = FileAnalysis
        fields = [
            "id",
            "session",
            "file_path",
            "file_name",
            "lines_of_code",
            "comment_lines",
            "blank_lines",
            "complexity_score",
            "maintainability_score",
            "documentation_score",
            "function_count",
            "class_count",
            "created_at",
            "security_issues_count",
            "dead_code_issues_count",
            "duplicate_locations_count",
        ]
        read_only_fields = ["id", "created_at"]

    def get_security_issues_count(self, obj) -> int:
        """Get count of security issues for this file."""
        return obj.security_issues.count()  # type: ignore[no-any-return]

    def get_dead_code_issues_count(self, obj) -> int:
        """Get count of dead code issues for this file."""
        return obj.dead_code_issues.count()  # type: ignore[no-any-return]

    def get_duplicate_locations_count(self, obj) -> int:
        """Get count of duplicate locations for this file."""
        return obj.duplicate_locations.count()  # type: ignore[no-any-return]


class SecurityIssueSerializer(serializers.ModelSerializer):
    """Serializer for SecurityIssue model."""

    session: serializers.StringRelatedField = serializers.StringRelatedField(
        read_only=True
    )
    file_analysis: serializers.StringRelatedField = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = SecurityIssue
        fields = [
            "id",
            "session",
            "file_analysis",
            "severity",
            "confidence",
            "issue_type",
            "test_id",
            "file_path",
            "line_number",
            "description",
            "recommendation",
            "code_snippet",
            "is_resolved",
            "resolved_at",
            "resolution_notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class DeadCodeIssueSerializer(serializers.ModelSerializer):
    """Serializer for DeadCodeIssue model."""

    session: serializers.StringRelatedField = serializers.StringRelatedField(
        read_only=True
    )
    file_analysis: serializers.StringRelatedField = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = DeadCodeIssue
        fields = [
            "id",
            "session",
            "file_analysis",
            "dead_type",
            "name",
            "file_path",
            "line_number",
            "confidence",
            "size_estimate",
            "is_resolved",
            "resolved_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class DuplicateLocationSerializer(serializers.ModelSerializer):
    """Serializer for DuplicateLocation model."""

    file_analysis: serializers.StringRelatedField = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = DuplicateLocation
        fields = [
            "id",
            "file_analysis",
            "file_path",
            "start_line",
            "end_line",
            "function_name",
            "class_name",
        ]
        read_only_fields = ["id"]


class DuplicateCodeBlockSerializer(serializers.ModelSerializer):
    """Serializer for DuplicateCodeBlock model."""

    session: serializers.StringRelatedField = serializers.StringRelatedField(
        read_only=True
    )
    locations = DuplicateLocationSerializer(many=True, read_only=True)
    locations_count = serializers.SerializerMethodField()

    class Meta:
        model = DuplicateCodeBlock
        fields = [
            "id",
            "session",
            "block_hash",
            "lines_count",
            "similarity_score",
            "content_preview",
            "is_resolved",
            "resolved_at",
            "created_at",
            "locations",
            "locations_count",
        ]
        read_only_fields = ["id", "created_at"]

    def get_locations_count(self, obj) -> int:
        """Get count of locations for this duplicate block."""
        return obj.locations.count()  # type: ignore[no-any-return]


class AnalysisSessionSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for analysis session summaries."""

    project_name = serializers.CharField(source="flx_project.name", read_only=True)
    duration = serializers.ReadOnlyField()

    class Meta:
        model = AnalysisSession
        fields = [
            "id",
            "name",
            "flx_project",
            "project_name",
            "status",
            "overall_score",
            "quality_grade",
            "started_at",
            "completed_at",
            "created_at",
            "duration",
        ]
        read_only_fields = ["id", "created_at"]


class ProjectSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for flx_project summaries."""

    latest_score = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "package_name",
            "package_version",
            "package_type",
            "created_at",
            "updated_at",
            "total_files",
            "total_lines",
            "python_files",
            "latest_score",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_latest_score(self, obj) -> float | None:
        """Get latest analysis score."""
        latest = obj.analysis_sessions.first()
        return latest.overall_score if latest else None
