"""Chart data views for dashboard visualizations."""

from __future__ import annotations

from datetime import timedelta

from django.db.models import Avg, Count
from django.http import JsonResponse
from django.utils import timezone

from analyzer.models import (
    AnalysisSession,
    DeadCodeIssue,
    DuplicateCodeBlock,
    Project,
    QualityMetrics,
    SecurityIssue,
)


def quality_trends_chart(request):
    """Get quality trends data for line chart."""
    period = request.GET.get("period", "30d")
    project_id = request.GET.get("flx_project")

    # Calculate date range
    if period == "7d":
        start_date = timezone.now() - timedelta(days=7)
    elif period == "90d":
        start_date = timezone.now() - timedelta(days=90)
    elif period == "365d":
        start_date = timezone.now() - timedelta(days=365)
    else:  # default 30d
        start_date = timezone.now() - timedelta(days=30)

    # Base query for sessions
    sessions_query = AnalysisSession.objects.filter(
        status="completed",
        completed_at__gte=start_date,
        overall_score__isnull=False,
    )

    # Filter by flx_project if specified
    if project_id:
        sessions_query = sessions_query.filter(flx_project_id=project_id)

    # Get sessions ordered by completion date
    sessions = sessions_query.order_by("completed_at")

    # Prepare data for chart
    labels = []
    overall_scores = []
    complexity_scores = []
    security_scores = []
    maintainability_scores = []

    for session in sessions:
        if session.completed_at:
            labels.append(session.completed_at.strftime("%Y-%m-%d"))
        else:
            labels.append("Unknown")
        overall_scores.append(float(session.overall_score or 0))

        # Get quality metrics if available
        try:
            metrics = session.quality_metrics
            complexity_scores.append(float(metrics.complexity_score))
            security_scores.append(float(metrics.security_score))
            maintainability_scores.append(float(metrics.maintainability_score))
        except QualityMetrics.DoesNotExist:
            complexity_scores.append(0)
            security_scores.append(0)
            maintainability_scores.append(0)

    chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "Overall Score",
                "data": overall_scores,
                "borderColor": "#007bff",
                "backgroundColor": "rgba(0, 123, 255, 0.1)",
                "tension": 0.4,
            },
            {
                "label": "Complexity Score",
                "data": complexity_scores,
                "borderColor": "#fd7e14",
                "backgroundColor": "rgba(253, 126, 20, 0.1)",
                "tension": 0.4,
            },
            {
                "label": "Security Score",
                "data": security_scores,
                "borderColor": "#28a745",
                "backgroundColor": "rgba(40, 167, 69, 0.1)",
                "tension": 0.4,
            },
            {
                "label": "Maintainability Score",
                "data": maintainability_scores,
                "borderColor": "#6f42c1",
                "backgroundColor": "rgba(111, 66, 193, 0.1)",
                "tension": 0.4,
            },
        ],
    }

    return JsonResponse(chart_data)


def security_issues_distribution(request):
    """Get security issues distribution data for doughnut chart."""
    project_id = request.GET.get("flx_project")
    resolved = request.GET.get("resolved", "false").lower() == "true"

    # Base query for security issues
    issues_query = SecurityIssue.objects.filter(is_resolved=resolved)

    # Filter by flx_project if specified
    if project_id:
        issues_query = issues_query.filter(session__flx_project_id=project_id)

    # Get distribution by severity
    issues = issues_query.values("severity").annotate(count=Count("id"))

    # Prepare data
    severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for item in issues:
        severity_counts[item["severity"]] = item["count"]

    chart_data = {
        "labels": ["HIGH", "MEDIUM", "LOW", "INFO"],
        "datasets": [
            {
                "data": [
                    severity_counts["HIGH"],
                    severity_counts["MEDIUM"],
                    severity_counts["LOW"],
                    severity_counts["INFO"],
                ],
                "backgroundColor": ["#dc3545", "#fd7e14", "#ffc107", "#17a2b8"],
                "borderWidth": 2,
                "borderColor": "#fff",
            },
        ],
        "total_issues": sum(severity_counts.values()),
    }

    return JsonResponse(chart_data)


def projects_comparison_chart(_request):
    """Get projects comparison data for bar chart."""
    # Get latest sessions for each flx_project
    projects = Project.objects.all()[:10]  # Limit to top 10 projects

    project_names = []
    quality_scores = []
    security_issues = []

    for flx_project in projects:
        # Get latest completed session
        latest_session = (
            AnalysisSession.objects.filter(
                flx_project=flx_project,
                status="completed",
            )
            .order_by("-completed_at")
            .first()
        )

        if latest_session:
            project_names.append(flx_project.name)
            quality_scores.append(float(latest_session.overall_score or 0))

            # Count unresolved security issues
            security_count = SecurityIssue.objects.filter(
                session=latest_session,
                is_resolved=False,
            ).count()
            security_issues.append(security_count)

    chart_data = {
        "labels": project_names,
        "datasets": [
            {
                "label": "Quality Score",
                "data": quality_scores,
                "backgroundColor": "rgba(0, 123, 255, 0.8)",
                "borderColor": "#007bff",
                "borderWidth": 1,
                "yAxisID": "y",
            },
            {
                "label": "Security Issues",
                "data": security_issues,
                "backgroundColor": "rgba(220, 53, 69, 0.8)",
                "borderColor": "#dc3545",
                "borderWidth": 1,
                "yAxisID": "y1",
            },
        ],
    }

    return JsonResponse(chart_data)


def quality_radar_chart(request):
    """Get quality radar chart data."""
    project_id = request.GET.get("flx_project")

    if project_id:
        # Get latest session for specific flx_project
        session = AnalysisSession.objects.filter(
            flx_project_id=project_id,
            status="completed",
        ).first()

        if session and hasattr(session, "quality_metrics"):
            metrics = session.quality_metrics
            data = [
                float(metrics.overall_score),
                float(metrics.complexity_score),
                float(metrics.security_score),
                float(metrics.maintainability_score),
                float(metrics.documentation_score),
                float(metrics.duplication_score),
            ]
            label = f"Project: {session.flx_project.name}"
        else:
            data = [0, 0, 0, 0, 0, 0]
            label = "No Data"
    else:
        # Get average scores across all completed sessions
        completed_sessions = AnalysisSession.objects.filter(status="completed")

        if completed_sessions.exists():
            # Calculate averages
            try:
                avg_metrics = QualityMetrics.objects.filter(
                    session__in=completed_sessions,
                ).aggregate(
                    overall=Avg("overall_score"),
                    complexity=Avg("complexity_score"),
                    security=Avg("security_score"),
                    maintainability=Avg("maintainability_score"),
                    documentation=Avg("documentation_score"),
                    duplication=Avg("duplication_score"),
                )

                data = [
                    float(avg_metrics["overall"] or 0),
                    float(avg_metrics["complexity"] or 0),
                    float(avg_metrics["security"] or 0),
                    float(avg_metrics["maintainability"] or 0),
                    float(avg_metrics["documentation"] or 0),
                    float(avg_metrics["duplication"] or 0),
                ]
                label = "Average Across All Projects"
            except Exception:
                data = [0, 0, 0, 0, 0, 0]
                label = "No Data"
        else:
            data = [0, 0, 0, 0, 0, 0]
            label = "No Data"

    chart_data = {
        "labels": [
            "Overall",
            "Complexity",
            "Security",
            "Maintainability",
            "Documentation",
            "Duplication",
        ],
        "datasets": [
            {
                "label": label,
                "data": data,
                "backgroundColor": "rgba(0, 123, 255, 0.2)",
                "borderColor": "#007bff",
                "borderWidth": 2,
                "pointBackgroundColor": "#007bff",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "#007bff",
            },
        ],
    }

    return JsonResponse(chart_data)


def issues_timeline_chart(request):
    """Get issues timeline data for area chart."""
    period = request.GET.get("period", "30d")

    # Calculate date range
    if period == "7d":
        start_date = timezone.now() - timedelta(days=7)
    elif period == "90d":
        start_date = timezone.now() - timedelta(days=90)
    elif period == "365d":
        start_date = timezone.now() - timedelta(days=365)
    else:  # default 30d
        start_date = timezone.now() - timedelta(days=30)

    # Get sessions in date range
    sessions = AnalysisSession.objects.filter(
        status="completed",
        completed_at__gte=start_date,
    ).order_by("completed_at")

    # Prepare data
    labels = []
    security_data = []
    dead_code_data = []
    duplicate_data = []

    for session in sessions:
        if session.completed_at:
            labels.append(session.completed_at.strftime("%Y-%m-%d"))
        else:
            labels.append("Unknown")

        # Count issues for this session
        security_count = SecurityIssue.objects.filter(
            session=session,
            is_resolved=False,
        ).count()
        dead_code_count = DeadCodeIssue.objects.filter(
            session=session,
            is_resolved=False,
        ).count()
        duplicate_count = DuplicateCodeBlock.objects.filter(
            session=session,
            is_resolved=False,
        ).count()

        security_data.append(security_count)
        dead_code_data.append(dead_code_count)
        duplicate_data.append(duplicate_count)

    chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "Security Issues",
                "data": security_data,
                "backgroundColor": "rgba(220, 53, 69, 0.6)",
                "borderColor": "#dc3545",
                "borderWidth": 1,
                "fill": True,
            },
            {
                "label": "Dead Code Issues",
                "data": dead_code_data,
                "backgroundColor": "rgba(255, 193, 7, 0.6)",
                "borderColor": "#ffc107",
                "borderWidth": 1,
                "fill": True,
            },
            {
                "label": "Duplicate Code",
                "data": duplicate_data,
                "backgroundColor": "rgba(111, 66, 193, 0.6)",
                "borderColor": "#6f42c1",
                "borderWidth": 1,
                "fill": True,
            },
        ],
    }

    return JsonResponse(chart_data)


def complexity_distribution_chart(_request):
    """Get complexity distribution data for histogram."""
    # Get all completed sessions
    sessions = AnalysisSession.objects.filter(status="completed")

    # Define complexity ranges
    ranges = [
        (0, 5, "Very Low"),
        (5, 10, "Low"),
        (10, 20, "Medium"),
        (20, 30, "High"),
        (30, float("inf"), "Very High"),
    ]

    distribution = []
    for min_val, max_val, label in ranges:
        if max_val == float("inf"):
            count = sessions.filter(overall_score__gte=min_val).count()
        else:
            count = sessions.filter(
                overall_score__gte=min_val,
                overall_score__lt=max_val,
            ).count()
        distribution.append({"range": label, "count": count})

    chart_data = {
        "labels": [item["range"] for item in distribution],
        "datasets": [
            {
                "label": "Number of Projects",
                "data": [item["count"] for item in distribution],
                "backgroundColor": [
                    "rgba(40, 167, 69, 0.8)",
                    "rgba(23, 162, 184, 0.8)",
                    "rgba(255, 193, 7, 0.8)",
                    "rgba(253, 126, 20, 0.8)",
                    "rgba(220, 53, 69, 0.8)",
                ],
                "borderColor": [
                    "#28a745",
                    "#17a2b8",
                    "#ffc107",
                    "#fd7e14",
                    "#dc3545",
                ],
                "borderWidth": 1,
            },
        ],
    }

    return JsonResponse(chart_data)


def dashboard_summary_stats(_request):
    """Get summary statistics for dashboard cards."""
    total_projects = Project.objects.count()
    total_sessions = AnalysisSession.objects.count()
    completed_sessions = AnalysisSession.objects.filter(status="completed").count()

    # Get average quality score
    avg_score = AnalysisSession.objects.filter(
        status="completed",
        overall_score__isnull=False,
    ).aggregate(avg=Avg("overall_score"))["avg"]

    # Get critical issues count
    critical_security = SecurityIssue.objects.filter(
        severity="HIGH",
        is_resolved=False,
    ).count()

    # Get total unresolved issues
    total_dead_code = DeadCodeIssue.objects.filter(is_resolved=False).count()

    total_duplicates = DuplicateCodeBlock.objects.filter(is_resolved=False).count()

    # Get recent activity (last 5 completed sessions)
    recent_sessions = AnalysisSession.objects.filter(status="completed").order_by(
        "-completed_at",
    )[:5]

    recent_activity = []
    for session in recent_sessions:
        recent_activity.append(
            {
                "project_name": session.flx_project.name,
                "session_id": str(session.id),
                "score": float(session.overall_score or 0),
                "created_at": session.completed_at.isoformat()
                if session.completed_at
                else "",
            },
        )

    stats = {
        "total_projects": total_projects,
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "avg_quality_score": round(float(avg_score or 0), 1),
        "critical_security_issues": critical_security,
        "total_dead_code_issues": total_dead_code,
        "total_duplicate_blocks": total_duplicates,
        "recent_activity": recent_activity,
    }

    return JsonResponse(stats)
