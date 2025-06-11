"""Django REST Framework views for analyzer API."""

from __future__ import annotations

import logging

from django.contrib import messages
from django.db.models import Avg
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_filters.rest_framework import (
    DjangoFilterBackend,  # type: ignore[import-untyped]
)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .analysis_engine import CodeAnalysisEngine
from .models import (
    AnalysisSession,
    DeadCodeIssue,
    DuplicateCodeBlock,
    FileAnalysis,
    Project,
    QualityMetrics,
    SecurityIssue,
)
from .package_discovery import PackageDiscovery
from .report_generator import WebReportGenerator, create_download_response
from .serializers import (
    AnalysisSessionSerializer,
    AnalysisSessionSummarySerializer,
    CreateAnalysisSessionSerializer,
    DeadCodeIssueSerializer,
    DuplicateCodeBlockSerializer,
    FileAnalysisSerializer,
    ProjectSerializer,
    ProjectSummarySerializer,
    QualityMetricsSerializer,
    SecurityIssueSerializer,
)
from .tasks import run_code_analysis

logger = logging.getLogger(__name__)


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing projects."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["name", "package_type"]
    search_fields = ["name", "description", "path"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        """Get all projects (no user filtering since Project doesn't have created_by field)."""
        return Project.objects.all()

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return ProjectSummarySerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        """Save the project (no created_by field in Project model)."""
        serializer.save()

    @action(detail=True, methods=["get"])
    def analysis_sessions(self, _request: Request, _pk=None) -> Response:
        """Get analysis sessions for a flx_project."""
        flx_project = self.get_object()
        sessions = flx_project.analysis_sessions.all()

        serializer = AnalysisSessionSummarySerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def statistics(self, _request: Request, _pk=None) -> Response:
        """Get flx_project statistics."""
        flx_project = self.get_object()
        sessions = flx_project.analysis_sessions.all()

        stats = {
            "total_analyses": sessions.count(),
            "completed_analyses": sessions.filter(status="completed").count(),
            "failed_analyses": sessions.filter(status="failed").count(),
            "avg_score": sessions.filter(status="completed").aggregate(
                avg=Avg("overall_score"),
            )["avg"],
            "last_analysis": sessions.first(),
            "project_info": {
                "total_files": flx_project.total_files,
                "total_lines": flx_project.total_lines,
                "python_files": flx_project.python_files,
            },
        }

        return Response(stats)

    @action(detail=True, methods=["post"], url_path="start-analysis")
    def start_analysis(self, request: Request, pk=None) -> Response:
        """Start analysis for a project."""
        flx_project = self.get_object()
        
        # Create analysis session
        data = {
            "flx_project": flx_project.id,
            "include_security": request.data.get("include_security", True),
            "include_dead_code": request.data.get("include_dead_code", True),
            "include_duplicates": request.data.get("include_duplicates", True),
            "backends": request.data.get("backends", ["ast", "external"]),
        }
        
        serializer = CreateAnalysisSessionSerializer(data=data)
        if serializer.is_valid():
            session = serializer.save()
            
            # Start the analysis
            try:
                # Update status to running
                session.status = "running"
                session.started_at = timezone.now()
                session.save()
                
                # Start analysis task (would be Celery task in production)
                run_code_analysis.delay(session.id)  # type: ignore[attr-defined]
                
                return Response({
                    "session_id": session.id,
                    "message": "Analysis started successfully"
                }, status=status.HTTP_202_ACCEPTED)
                
            except Exception as e:
                logger.exception(f"Failed to start analysis for session {session.id}: {e}")
                session.status = "failed"
                session.error_message = str(e)
                session.save()
                
                return Response(
                    {"error": "Failed to start analysis"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnalysisSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing analysis sessions."""

    queryset = AnalysisSession.objects.all()
    serializer_class = AnalysisSessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "flx_project"]
    ordering_fields = ["created_at", "started_at", "completed_at", "overall_score"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Get all analysis sessions (no user filtering since Project doesn't have created_by field)."""
        return AnalysisSession.objects.all()

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return CreateAnalysisSessionSerializer
        if self.action == "list":
            return AnalysisSessionSummarySerializer
        return AnalysisSessionSerializer

    @action(detail=True, methods=["post"])
    def start(self, _request: Request, _pk=None) -> Response:
        """Start an analysis session."""
        session = self.get_object()

        if session.status != "pending":
            return Response(
                {"error": "Session is not in pending state"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Update status to running
            session.status = "running"
            session.started_at = timezone.now()
            session.save()

            # Start analysis task (would be Celery task in production)
            run_code_analysis.delay(session.id)  # type: ignore[attr-defined]

            return Response({"message": "Analysis started successfully"})

        except Exception as e:
            logger.exception(f"Failed to start analysis {session.id}: {e}")
            session.status = "failed"
            session.error_message = str(e)
            session.save()

            return Response(
                {"error": "Failed to start analysis"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def cancel(self, _request: Request, _pk=None) -> Response:
        """Cancel a running analysis session."""
        session = self.get_object()

        if session.status not in {"pending", "running"}:
            return Response(
                {"error": "Session cannot be cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session.status = "cancelled"
        session.completed_at = timezone.now()
        session.save()

        return Response({"message": "Analysis cancelled successfully"})

    @action(detail=True, methods=["get"])
    def status(self, _request: Request, pk=None) -> Response:
        """Get analysis session status."""
        session = self.get_object()
        
        progress = 0
        if session.status == "completed":
            progress = 100
        elif session.status == "running":
            progress = 50  # Estimate for running state
        
        return Response({
            "session_id": session.id,
            "status": session.status,
            "progress": progress,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "error_message": session.error_message or "",
        })

    @action(detail=True, methods=["get"])
    def results(self, _request: Request, pk=None) -> Response:
        """Get comprehensive analysis results."""
        session = self.get_object()

        if session.status != "completed":
            return Response(
                {"error": "Analysis not completed yet"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = {
            "session_id": session.id,
            "status": session.status,
            "overall_score": session.overall_score,
            "quality_grade": session.quality_grade,
            "quality_metrics": (
                QualityMetricsSerializer(session.quality_metrics).data
                if hasattr(session, "quality_metrics")
                else None
            ),
            "security_issues": SecurityIssueSerializer(
                session.security_issues.all(),
                many=True,
            ).data,
            "dead_code_issues": DeadCodeIssueSerializer(
                session.dead_code_issues.all(),
                many=True,
            ).data,
            "duplicate_blocks": DuplicateCodeBlockSerializer(
                session.duplicate_blocks.all(),
                many=True,
            ).data,
            "file_analyses": FileAnalysisSerializer(
                session.file_analyses.all(),
                many=True,
            ).data,
        }

        return Response(results)

    @action(detail=False, methods=["get"])
    def dashboard_stats(self, _request: Request) -> Response:
        """Get dashboard statistics for current user."""
        user_sessions = self.get_queryset()

        stats = {
            "total_sessions": user_sessions.count(),
            "completed_sessions": user_sessions.filter(status="completed").count(),
            "running_sessions": user_sessions.filter(status="running").count(),
            "failed_sessions": user_sessions.filter(status="failed").count(),
            "avg_score": user_sessions.filter(status="completed").aggregate(
                avg=Avg("overall_score"),
            )["avg"]
            or 0,
            "recent_sessions": AnalysisSessionSummarySerializer(
                user_sessions[:5],
                many=True,
            ).data,
        }

        return Response(stats)


class FileAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing file analyses."""

    queryset = FileAnalysis.objects.all()
    serializer_class = FileAnalysisSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["session", "file_name"]
    search_fields = ["file_path", "file_name"]
    ordering_fields = ["file_path", "complexity_score", "lines_of_code"]
    ordering = ["file_path"]

    def get_queryset(self):
        """Filter file analyses by sessions owned by current user."""
        return FileAnalysis.objects.filter(
            session__project__created_by=self.request.user,
        )

    @action(detail=False, methods=["get"])
    def most_complex(self, _request: Request) -> Response:
        """Get most complex files across all sessions."""
        files = self.get_queryset().order_by("-complexity_score")[:10]
        serializer = self.get_serializer(files, many=True)
        return Response(serializer.data)


class SecurityIssueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing security issues."""

    queryset = SecurityIssue.objects.all()
    serializer_class = SecurityIssueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["severity", "confidence", "issue_type", "is_resolved"]
    ordering_fields = ["severity", "line_number", "created_at"]
    ordering = ["-severity", "line_number"]

    def get_queryset(self):
        """Filter security issues by sessions owned by current user."""
        return SecurityIssue.objects.filter(
            session__project__created_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def resolve(self, request: Request, _pk=None) -> Response:
        """Mark security issue as resolved."""
        issue = self.get_object()
        resolution_notes = request.data.get("resolution_notes", "")

        issue.is_resolved = True
        issue.resolved_at = timezone.now()
        issue.resolution_notes = resolution_notes
        issue.save()

        return Response({"message": "Issue marked as resolved"})

    @action(detail=False, methods=["get"])
    def by_severity(self, _request: Request) -> Response:
        """Get security issues grouped by severity."""
        issues = self.get_queryset().filter(is_resolved=False)

        severity_counts = {
            "HIGH": issues.filter(severity="HIGH").count(),
            "MEDIUM": issues.filter(severity="MEDIUM").count(),
            "LOW": issues.filter(severity="LOW").count(),
            "INFO": issues.filter(severity="INFO").count(),
        }

        return Response(severity_counts)


class DeadCodeIssueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing dead code issues."""

    queryset = DeadCodeIssue.objects.all()
    serializer_class = DeadCodeIssueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["dead_type", "is_resolved"]
    ordering_fields = ["confidence", "size_estimate", "created_at"]
    ordering = ["-confidence", "-size_estimate"]

    def get_queryset(self):
        """Filter dead code issues by sessions owned by current user."""
        return DeadCodeIssue.objects.filter(
            session__project__created_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def resolve(self, _request: Request, _pk=None) -> Response:
        """Mark dead code issue as resolved."""
        issue = self.get_object()

        issue.is_resolved = True
        issue.resolved_at = timezone.now()
        issue.save()

        return Response({"message": "Dead code issue marked as resolved"})

    @action(detail=False, methods=["get"])
    def by_type(self, _request: Request) -> Response:
        """Get dead code issues grouped by type."""
        issues = self.get_queryset().filter(is_resolved=False)

        type_counts = {
            "function": issues.filter(dead_type="function").count(),
            "class": issues.filter(dead_type="class").count(),
            "variable": issues.filter(dead_type="variable").count(),
            "import": issues.filter(dead_type="import").count(),
            "attribute": issues.filter(dead_type="attribute").count(),
        }

        return Response(type_counts)


class DuplicateCodeBlockViewSet(viewsets.ModelViewSet):
    """ViewSet for managing duplicate code blocks."""

    queryset = DuplicateCodeBlock.objects.all()
    serializer_class = DuplicateCodeBlockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["is_resolved"]
    ordering_fields = ["lines_count", "similarity_score", "created_at"]
    ordering = ["-lines_count", "-similarity_score"]

    def get_queryset(self):
        """Filter duplicate blocks by sessions owned by current user."""
        return DuplicateCodeBlock.objects.filter(
            session__project__created_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def resolve(self, _request: Request, _pk=None) -> Response:
        """Mark duplicate code block as resolved."""
        block = self.get_object()

        block.is_resolved = True
        block.resolved_at = timezone.now()
        block.save()

        return Response({"message": "Duplicate block marked as resolved"})

    @action(detail=False, methods=["get"])
    def largest(self, _request: Request) -> Response:
        """Get largest duplicate blocks."""
        blocks = (
            self.get_queryset().filter(is_resolved=False).order_by("-lines_count")[:10]
        )
        serializer = self.get_serializer(blocks, many=True)
        return Response(serializer.data)


class QualityMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing quality metrics."""

    queryset = QualityMetrics.objects.all()
    serializer_class = QualityMetricsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["overall_score", "created_at"]
    ordering = ["-overall_score"]

    def get_queryset(self):
        """Filter quality metrics by sessions owned by current user."""
        return QualityMetrics.objects.filter(
            session__project__created_by=self.request.user,
        )

    @action(detail=False, methods=["get"])
    def trends(self, _request: Request) -> Response:
        """Get quality trends over time."""
        metrics = self.get_queryset().order_by("created_at")

        trends = []
        for metric in metrics:
            trends.append(
                {
                    "date": metric.created_at.date(),
                    "overall_score": metric.overall_score,
                    "complexity_score": metric.complexity_score,
                    "security_score": metric.security_score,
                    "maintainability_score": metric.maintainability_score,
                    "project_name": metric.session.flx_project.name,
                },
            )

        return Response(trends)


# Django template views for web interface
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """Main dashboard view."""
    projects = Project.objects.all()
    recent_sessions = AnalysisSession.objects.select_related("flx_project").order_by(
        "-created_at",
    )[:5]

    # Get package discovery
    discovery = PackageDiscovery()
    packages = discovery.get_installed_packages()

    context = {
        "projects": projects,
        "recent_sessions": recent_sessions,
        "packages": packages[:10],  # Top 10 packages
        "total_projects": projects.count(),
        "completed_analyses": AnalysisSession.objects.filter(
            status="completed",
        ).count(),
    }

    return render(request, "dashboard/home.html", context)


def packages_discovery(request: HttpRequest) -> HttpResponse:
    """Package discovery view."""
    from django.core.cache import cache

    # Get filter parameters
    package_type = request.GET.get("type", "")
    search = request.GET.get("search", "")
    refresh = request.GET.get("refresh")

    # Cache key for packages
    cache_key = "installed_packages"

    # Get packages from cache or discover them
    if refresh or not cache.get(cache_key):
        discovery = PackageDiscovery()
        discovery.clear_cache()
        packages = discovery.get_installed_packages()
        # Cache for 5 minutes
        cache.set(cache_key, packages, 300)
    else:
        packages = cache.get(cache_key, [])

    # Filter by type if provided
    if package_type:
        packages = [pkg for pkg in packages if pkg["package_type"] == package_type]

    # Filter by search query if provided
    if search:
        packages = [
            pkg
            for pkg in packages
            if search.lower() in pkg["name"].lower()
            or search.lower() in pkg.get("description", "").lower()
        ]

    context = {
        "packages": packages,
        "search": search,
        "selected_type": package_type,
    }

    return render(request, "dashboard/packages.html", context)


@require_http_methods(["POST"])
def create_project_from_package(request: HttpRequest) -> HttpResponse:
    """Create flx_project from package."""
    package_name = request.POST.get("package_name")

    if not package_name:
        messages.error(request, "Package name is required")
        return redirect("packages_discovery")

    discovery = PackageDiscovery()
    packages = discovery.get_installed_packages()

    # Find the package
    package = next((p for p in packages if p["name"] == package_name), None)

    if not package:
        messages.error(request, f"Package '{package_name}' not found")
        return redirect("packages_discovery")

    try:
        # Create flx_project
        flx_project = Project.objects.create(
            name=package["name"],
            description=f"Auto-discovered Python package: {package.get('description', '')}",
            path=package["location"],
            package_name=package["name"],
            package_version=package.get("version", ""),
            is_installed_package=True,
            install_location=package["location"],
            package_type=package.get("type", "unknown"),
        )

        messages.success(request, f"Project '{flx_project.name}' created successfully")
        return redirect("project_detail", project_id=flx_project.id)

    except Exception as e:
        logger.exception(
            f"Failed to create flx_project from package {package_name}: {e}",
        )
        messages.error(request, f"Failed to create flx_project: {e}")
        return redirect("packages_discovery")


def project_detail(request: HttpRequest, project_id: int) -> HttpResponse:
    """Project detail view."""
    flx_project = get_object_or_404(Project, id=project_id)
    sessions = flx_project.analysis_sessions.order_by("-created_at")
    latest_session = sessions.first()

    context = {
        "flx_project": flx_project,
        "sessions": sessions,
        "latest_session": latest_session,
    }

    return render(request, "dashboard/project_detail.html", context)


def analysis_session_detail(request: HttpRequest, session_id: int) -> HttpResponse:
    """Analysis session detail view."""
    session = get_object_or_404(AnalysisSession, id=session_id)

    # Get analysis data
    file_analyses = session.file_analyses.order_by("-complexity_score")
    security_issues = session.security_issues.order_by("-severity", "-confidence")
    dead_code_issues = session.dead_code_issues.order_by("-confidence")
    duplicate_blocks = session.duplicate_blocks.order_by("-similarity_score")
    quality_metrics = getattr(session, "quality_metrics", None)

    context = {
        "session": session,
        "file_analyses": file_analyses,
        "security_issues": security_issues,
        "dead_code_issues": dead_code_issues,
        "duplicate_blocks": duplicate_blocks,
        "quality_metrics": quality_metrics,
    }

    return render(request, "dashboard/session_detail.html", context)


@require_http_methods(["POST"])
def start_analysis(request: HttpRequest, project_id: int) -> HttpResponse:
    """Start analysis for a flx_project."""
    flx_project = get_object_or_404(Project, id=project_id)

    try:
        # Create analysis session
        session = AnalysisSession.objects.create(
            flx_project=flx_project,
            name=f"Analysis {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            include_security=request.POST.get("include_security") == "on",
            include_dead_code=request.POST.get("include_dead_code") == "on",
            include_duplicates=request.POST.get("include_duplicates") == "on",
            complexity_threshold=float(request.POST.get("complexity_threshold", 10.0)),
            similarity_threshold=float(request.POST.get("similarity_threshold", 0.8)),
        )

        # Start analysis engine
        engine = CodeAnalysisEngine(session)
        success = engine.run_analysis()

        if success:
            messages.success(request, "Analysis completed successfully")
        else:
            messages.error(request, f"Analysis failed: {session.error_message}")

        return redirect("analysis_session_detail", session_id=session.id)

    except Exception as e:
        logger.exception(f"Failed to start analysis for flx_project {project_id}: {e}")
        messages.error(request, f"Failed to start analysis: {e}")
        return redirect("project_detail", project_id=project_id)


def generate_report(request: HttpRequest, session_id: int) -> HttpResponse:
    """Generate and download report."""
    session = get_object_or_404(AnalysisSession, id=session_id)
    report_type = request.GET.get("type", "summary")
    format = request.GET.get("format", "html")

    try:
        generator = WebReportGenerator(session)

        if report_type == "summary":
            report = generator.generate_summary_report(format)
        elif report_type == "detailed":
            report = generator.generate_detailed_report(format)
        elif report_type == "security":
            report = generator.generate_security_report(format)
        else:
            messages.error(request, f"Unknown report type: {report_type}")
            return redirect("analysis_session_detail", session_id=session_id)

        # Return download response
        return create_download_response(report)

    except Exception as e:
        logger.exception(f"Failed to generate report for session {session_id}: {e}")
        messages.error(request, f"Failed to generate report: {e}")
        return redirect("analysis_session_detail", session_id=session_id)


def view_report(request: HttpRequest, session_id: int) -> HttpResponse:
    """View report in browser."""
    session = get_object_or_404(AnalysisSession, id=session_id)
    report_type = request.GET.get("type", "summary")

    try:
        generator = WebReportGenerator(session)

        if report_type == "summary":
            report = generator.generate_summary_report("html")
        elif report_type == "detailed":
            report = generator.generate_detailed_report("html")
        elif report_type == "security":
            report = generator.generate_security_report("html")
        else:
            messages.error(request, f"Unknown report type: {report_type}")
            return redirect("analysis_session_detail", session_id=session_id)

        # Return HTML content directly
        return HttpResponse(report.content, content_type="text/html")

    except Exception as e:
        logger.exception(f"Failed to view report for session {session_id}: {e}")
        messages.error(request, f"Failed to view report: {e}")
        return redirect("analysis_session_detail", session_id=session_id)


@csrf_exempt
def refresh_packages(_request: HttpRequest) -> JsonResponse:
    """Refresh package discovery (AJAX endpoint)."""
    try:
        discovery = PackageDiscovery()
        discovery.clear_cache()  # Clear cache to force refresh
        packages = discovery.get_installed_packages()

        return JsonResponse(
            {
                "status": "success",
                "count": len(packages),
                "packages": packages[:20],  # Return first 20
            },
        )

    except Exception as e:
        logger.exception(f"Failed to refresh packages: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": str(e),
            },
            status=500,
        )
