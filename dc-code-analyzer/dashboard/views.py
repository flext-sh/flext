"""Django views for dashboard interface."""

from __future__ import annotations

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from analyzer.models import AnalysisSession, Project
from analyzer.package_discovery import PackageDiscovery


def dashboard_home(request: HttpRequest) -> HttpResponse:
    """Dashboard home page with overview statistics."""
    # Get all projects and sessions
    projects = Project.objects.all()
    sessions = AnalysisSession.objects.all()

    # Calculate statistics
    stats = {
        "total_projects": projects.count(),
        "total_sessions": sessions.count(),
        "completed_sessions": sessions.filter(status="completed").count(),
        "running_sessions": sessions.filter(status="running").count(),
        "avg_score": sessions.filter(status="completed").aggregate(
            avg=Avg("overall_score"),
        )["avg"]
        or 0,
    }

    # Get recent activity
    recent_sessions = sessions.order_by("-created_at")[:5]
    recent_projects = projects.order_by("-updated_at")[:5]

    context = {
        "stats": stats,
        "recent_sessions": recent_sessions,
        "recent_projects": recent_projects,
    }

    return render(request, "dashboard/home.html", context)


def projects_list(request: HttpRequest) -> HttpResponse:
    """List all projects."""
    projects = Project.objects.all().order_by("-updated_at")

    # Search functionality
    search_query = request.GET.get("search", "")
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query),
        )

    # Pagination
    paginator = Paginator(projects, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
    }

    return render(request, "dashboard/projects_list.html", context)


def project_detail(request: HttpRequest, project_id: str) -> HttpResponse:
    """Display flx_project details and analysis history."""
    flx_project = get_object_or_404(Project, id=project_id)

    # Get analysis sessions for this flx_project
    sessions = flx_project.analysis_sessions.order_by("-created_at")

    context = {
        "flx_project": flx_project,
        "sessions": sessions[:10],  # Show latest 10
    }

    return render(request, "dashboard/project_detail.html", context)


def packages_discovery(request: HttpRequest) -> HttpResponse:
    """Display discovered Python packages."""
    discovery = PackageDiscovery()

    # Get filter parameters
    package_type = request.GET.get("type", "all")
    search_query = request.GET.get("search", "")

    # Get packages based on filters
    if package_type == "source":
        packages = discovery.get_development_packages()
    elif package_type == "analyzable":
        packages = discovery.get_analyzable_packages()
    elif search_query:
        packages = discovery.search_packages(search_query)
    else:
        packages = discovery.get_installed_packages()

    # Pagination
    paginator = Paginator(packages, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "package_type": package_type,
        "search_query": search_query,
        "total_packages": len(packages),
    }

    return render(request, "dashboard/packages.html", context)


def create_project_from_package(request: HttpRequest) -> HttpResponse:
    """Create a flx_project from a discovered package."""
    if request.method == "POST":
        package_name = request.POST.get("package_name", "").strip()

        if not package_name:
            messages.error(request, "Package name is required.")
            return redirect("dashboard:packages_discovery")

        try:
            discovery = PackageDiscovery()
            package_info = discovery.get_package_by_name(package_name)

            if not package_info:
                messages.error(request, f"Package '{package_name}' not found.")
                return redirect("dashboard:packages_discovery")

            # Check if flx_project already exists
            existing_project = Project.objects.filter(
                package_name=package_name,
            ).first()

            if existing_project:
                messages.info(request, f"Project for '{package_name}' already exists.")
                return redirect(
                    "dashboard:project_detail",
                    project_id=existing_project.id,
                )

            # Create new flx_project
            flx_project = Project.objects.create(
                name=package_info["name"],
                description=package_info.get("description", ""),
                path=package_info["source_path"],
                package_name=package_info["name"],
                package_version=package_info["version"],
                is_installed_package=True,
                install_location=package_info.get("location", ""),
                package_type=package_info["package_type"],
            )

            messages.success(request, f"Project created for package '{package_name}'.")
            return redirect("dashboard:project_detail", project_id=flx_project.id)

        except Exception as e:
            messages.error(request, f"Error creating flx_project: {e}")

    return redirect("dashboard:packages_discovery")


def create_project(request: HttpRequest) -> HttpResponse:
    """Create a new flx_project manually."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        path = request.POST.get("path", "").strip()

        if not all([name, path]):
            messages.error(request, "Name and path are required.")
            return render(request, "dashboard/create_project.html")

        try:
            flx_project = Project.objects.create(
                name=name,
                description=description,
                path=path,
                package_type="local",
            )

            messages.success(request, f"Project '{name}' created successfully.")
            return redirect("dashboard:project_detail", project_id=flx_project.id)

        except Exception as e:
            messages.error(request, f"Error creating flx_project: {e}")

    return render(request, "dashboard/create_project.html")


def start_analysis(request: HttpRequest, project_id: str) -> HttpResponse:
    """Start analysis for a flx_project."""
    if request.method == "POST":
        flx_project = get_object_or_404(Project, id=project_id)

        try:
            # Check if there's already a running session
            running_session = AnalysisSession.objects.filter(
                flx_project=flx_project,
                status__in=["pending", "running"],
            ).first()

            if running_session:
                messages.warning(
                    request,
                    "Analysis is already running for this flx_project.",
                )
                return redirect("dashboard:project_detail", project_id=flx_project.id)

            # Create new analysis session
            session = AnalysisSession.objects.create(
                flx_project=flx_project,
                status="pending",
                include_security=True,
                include_dead_code=True,
                include_duplicates=True,
                include_documentation=True,
                include_complexity=True,
            )

            # Start actual analysis task
            try:
                from analyzer.tasks import run_analysis_task

                # Start background analysis
                run_analysis_task.delay(session.id, ["ast", "external", "quality"])

                messages.success(request, "Analysis started in background!")
            except ImportError:
                # Fallback to synchronous analysis if Celery is not available
                from analyzer.multi_backend_analyzer import MultiBackendAnalyzer

                analyzer = MultiBackendAnalyzer(
                    flx_project, ["ast", "external", "quality"]
                )
                session = analyzer.analyze()

                messages.success(request, "Analysis completed successfully!")

        except Exception as e:
            messages.error(request, f"Error starting analysis: {e}")

    return redirect("dashboard:project_detail", project_id=project_id)


def refresh_packages(_request: HttpRequest) -> JsonResponse:
    """Refresh package discovery cache."""
    try:
        discovery = PackageDiscovery()
        packages = discovery.get_installed_packages()

        return JsonResponse(
            {
                "status": "success",
                "message": f"Found {len(packages)} packages",
                "count": len(packages),
            },
        )
    except Exception as e:
        return JsonResponse(
            {
                "status": "error",
                "message": str(e),
            },
            status=500,
        )


def run_analysis(request, project_id):
    """Start analysis for a flx_project."""
    flx_project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        # Get backend selection from form
        backend_names = request.POST.getlist("backends")
        if not backend_names:
            backend_names = ["ast", "external", "quality"]

        # Create analysis session
        session = AnalysisSession.objects.create(
            flx_project=flx_project,
            name=f"Analysis - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            status="pending",
            backends_used=backend_names,
        )

        # Start background analysis
        try:
            from analyzer.tasks import run_analysis_task

            run_analysis_task.delay(session.id, backend_names)

            messages.success(
                request,
                f"Analysis started in background! Session ID: {session.id}. "
                f"You can monitor progress in the Analysis Overview.",
            )
        except ImportError:
            # Fallback to synchronous analysis if Celery is not available
            from analyzer.multi_backend_analyzer import MultiBackendAnalyzer

            analyzer = MultiBackendAnalyzer(flx_project, backend_names)
            analyzer.session = session
            session = analyzer.analyze()

            messages.success(request, f"Analysis completed! Session ID: {session.id}")

        return redirect("dashboard:analysis_session_detail", session_id=session.id)

    # GET - show analysis form
    from analyzer.backends import AVAILABLE_BACKENDS

    available_backends = [
        {"name": name, "description": backend_class.description}
        for name, backend_class in AVAILABLE_BACKENDS.items()
    ]

    context = {
        "flx_project": flx_project,
        "available_backends": available_backends,
    }
    return render(request, "dashboard/run_analysis.html", context)


def analysis_session_detail(request, session_id):
    """Show detailed analysis session results."""
    from analyzer.models import (
        AnalysisSession,
        ClassAnalysis,
        FunctionAnalysis,
        PackageAnalysis,
        SecurityIssue,
    )

    session = get_object_or_404(AnalysisSession, id=session_id)

    # Get summary statistics
    packages = PackageAnalysis.objects.filter(session=session)
    classes = ClassAnalysis.objects.filter(package_analysis__session=session)
    functions = FunctionAnalysis.objects.filter(package_analysis__session=session)
    security_issues = SecurityIssue.objects.filter(session=session)

    context = {
        "session": session,
        "packages_count": packages.count(),
        "classes_count": classes.count(),
        "functions_count": functions.count(),
        "security_issues_count": security_issues.count(),
        "packages": packages[:10],  # Top 10 for overview
    }
    return render(request, "dashboard/analysis_session_detail.html", context)


def package_analysis_view(request, session_id, package_id):
    """Show detailed package analysis with drill-down options."""
    from analyzer.models import ClassAnalysis, FunctionAnalysis, PackageAnalysis

    session = get_object_or_404(AnalysisSession, id=session_id)
    package = get_object_or_404(PackageAnalysis, id=package_id, session=session)

    # Get package details
    classes = ClassAnalysis.objects.filter(package_analysis=package).order_by(
        "-method_count",
    )
    functions = FunctionAnalysis.objects.filter(
        package_analysis=package,
        class_analysis__isnull=True,
    ).order_by("-cyclomatic_complexity")

    # Statistics
    high_complexity_functions = functions.filter(
        complexity_level__in=["high", "very_high"],
    )
    undocumented_classes = classes.filter(has_docstring=False)

    context = {
        "session": session,
        "package": package,
        "classes": classes,
        "functions": functions,
        "high_complexity_functions": high_complexity_functions,
        "undocumented_classes": undocumented_classes,
    }
    return render(request, "dashboard/package_analysis.html", context)


def class_analysis_view(request, session_id, class_id):
    """Show detailed class analysis with methods breakdown."""
    from analyzer.models import ClassAnalysis, FunctionAnalysis, VariableAnalysis

    session = get_object_or_404(AnalysisSession, id=session_id)
    class_obj = get_object_or_404(ClassAnalysis, id=class_id)

    # Get class details
    methods = FunctionAnalysis.objects.filter(class_analysis=class_obj).order_by(
        "line_start",
    )
    variables = VariableAnalysis.objects.filter(class_analysis=class_obj).order_by(
        "line_number",
    )

    # Method statistics
    complex_methods = methods.filter(complexity_level__in=["high", "very_high"])
    undocumented_methods = methods.filter(has_docstring=False)

    context = {
        "session": session,
        "class_obj": class_obj,
        "methods": methods,
        "variables": variables,
        "complex_methods": complex_methods,
        "undocumented_methods": undocumented_methods,
    }
    return render(request, "dashboard/class_analysis.html", context)


def function_analysis_view(request, session_id, function_id):
    """Show detailed function analysis."""
    from analyzer.models import FunctionAnalysis, VariableAnalysis

    session = get_object_or_404(AnalysisSession, id=session_id)
    function = get_object_or_404(FunctionAnalysis, id=function_id)

    # Get function variables
    variables = VariableAnalysis.objects.filter(function_analysis=function).order_by(
        "line_number",
    )

    context = {
        "session": session,
        "function": function,
        "variables": variables,
    }
    return render(request, "dashboard/function_analysis.html", context)


def analysis_overview(request):
    """Overview of all analysis sessions."""
    from analyzer.models import AnalysisSession

    sessions = (
        AnalysisSession.objects.select_related("flx_project")
        .prefetch_related(
            "detected_issues",
            "backend_statistics",
        )
        .order_by("-created_at")
    )

    # Calculate statistics
    completed_count = sessions.filter(status="completed").count()
    running_count = sessions.filter(status="running").count()
    failed_count = sessions.filter(status="failed").count()

    # Add pagination
    from django.core.paginator import Paginator

    paginator = Paginator(sessions, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "sessions": page_obj,
        "completed_count": completed_count,
        "running_count": running_count,
        "failed_count": failed_count,
    }
    return render(request, "dashboard/analysis_overview.html", context)


def hierarchical_report(request, session_id):
    """Generate hierarchical drill-down report."""
    from analyzer.models import (
        AnalysisSession,
        ClassAnalysis,
        FunctionAnalysis,
        PackageAnalysis,
        SecurityIssue,
    )

    session = get_object_or_404(AnalysisSession, id=session_id)

    # Build hierarchical data structure
    report_data = {
        "session": session,
        "packages": [],
    }

    packages = PackageAnalysis.objects.filter(session=session).order_by("name")

    for package in packages:
        package_data = {
            "package": package,
            "classes": [],
            "functions": [],
            "security_issues": SecurityIssue.objects.filter(
                session=session,
                file_analysis__package_name=package.name,
            ).count(),
        }

        # Get classes in this package
        classes = ClassAnalysis.objects.filter(package_analysis=package).order_by(
            "name",
        )

        for cls in classes:
            class_data = {
                "class": cls,
                "methods": FunctionAnalysis.objects.filter(class_analysis=cls).order_by(
                    "name",
                ),
            }
            package_data["classes"].append(class_data)

        # Get standalone functions (not in classes)
        standalone_functions = FunctionAnalysis.objects.filter(
            package_analysis=package,
            class_analysis__isnull=True,
        ).order_by("name")

        package_data["functions"] = standalone_functions
        report_data["packages"].append(package_data)

    context = {
        "report_data": report_data,
        "session": session,
    }
    return render(request, "dashboard/hierarchical_report.html", context)


def backend_issues_report(request, session_id):
    """Enhanced report showing backend statistics and detected issues."""
    session = get_object_or_404(AnalysisSession, id=session_id)

    # Get backend statistics
    backend_stats = session.backend_statistics.all().order_by(
        "backend__execution_order",
    )

    # Get detected issues grouped by backend and severity
    detected_issues = session.detected_issues.select_related(
        "issue_type__backend",
        "file_analysis",
    ).order_by("-detected_at")

    # Group issues by backend
    issues_by_backend = {}
    for issue in detected_issues:
        backend_name = issue.issue_type.backend.name
        if backend_name not in issues_by_backend:
            issues_by_backend[backend_name] = {
                "backend": issue.issue_type.backend,
                "issues": [],
                "severity_counts": {
                    "CRITICAL": 0,
                    "HIGH": 0,
                    "MEDIUM": 0,
                    "LOW": 0,
                    "INFO": 0,
                },
                "category_counts": {},
            }

        issues_by_backend[backend_name]["issues"].append(issue)

        # Count by severity
        severity = issue.severity
        if severity in issues_by_backend[backend_name]["severity_counts"]:
            issues_by_backend[backend_name]["severity_counts"][severity] += 1

        # Count by category
        category = issue.category
        if category not in issues_by_backend[backend_name]["category_counts"]:
            issues_by_backend[backend_name]["category_counts"][category] = 0
        issues_by_backend[backend_name]["category_counts"][category] += 1

    # Calculate overall statistics
    total_issues = detected_issues.count()
    total_files_with_issues = detected_issues.values("file_path").distinct().count()

    # Get top issue types
    top_issue_types = (
        detected_issues.values(
            "issue_type__code",
            "issue_type__name",
            "issue_type__severity",
        )
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    # Get files with most issues
    files_with_issues = (
        detected_issues.values("file_path")
        .annotate(issue_count=Count("id"))
        .order_by("-issue_count")[:10]
    )

    context = {
        "session": session,
        "backend_stats": backend_stats,
        "issues_by_backend": issues_by_backend,
        "detected_issues": detected_issues[:50],  # Latest 50 issues
        "total_issues": total_issues,
        "total_files_with_issues": total_files_with_issues,
        "top_issue_types": top_issue_types,
        "files_with_issues": files_with_issues,
    }

    return render(request, "dashboard/backend_issues_report.html", context)
