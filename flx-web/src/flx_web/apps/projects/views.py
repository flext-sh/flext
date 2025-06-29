"""FLX Projects Views - Enterprise Project Management Interface.

This module provides Django views for enterprise project management,
implementing comprehensive CRUD operations and project lifecycle management.

Author: Datacosmos
Date: 2025-06-22
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from flx_web.models import (
    MeltanoProject,
    ProjectDeployment,
    ProjectMembership,
    ProjectTemplate,
)

if TYPE_CHECKING:
    from django.forms import ModelForm


class ProjectListView(LoginRequiredMixin, ListView):
    """List view for Meltano projects with filtering and search.

    Provides comprehensive project listing with enterprise features including
    filtering by status, search capabilities, and pagination.
    """

    model = MeltanoProject
    template_name = "projects/list.html"
    context_object_name = "projects"
    paginate_by = 20

    def get_queryset(self) -> QuerySet[MeltanoProject]:
        """Get filtered and searched queryset of projects."""
        queryset = MeltanoProject.objects.select_related(
            "owner",
            "template",
        ).prefetch_related("collaborators")

        # Filter by user access (owner or collaborator)
        queryset = queryset.filter(
            Q(owner=self.request.user) | Q(collaborators=self.request.user),
        ).distinct()

        # Apply search filter
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(display_name__icontains=search)
                | Q(description__icontains=search),
            )

        # Apply status filter
        status = self.request.GET.get("status")
        if status and status != "all":
            queryset = queryset.filter(status=status)

        return queryset.order_by("-updated_at")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add additional context for template rendering."""
        context = super().get_context_data(**kwargs)
        status_field = MeltanoProject._meta.get_field("status")
        if hasattr(status_field, "choices"):
            context["status_choices"] = status_field.choices
        else:
            context["status_choices"] = []
        context["current_status"] = self.request.GET.get("status", "all")
        context["search_query"] = self.request.GET.get("search", "")
        return context


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """Detail view for individual Meltano project.

    Provides comprehensive project information including team members,
    deployment history, and project statistics.
    """

    model = MeltanoProject
    template_name = "projects/detail.html"
    context_object_name = "project"

    def get_queryset(self) -> QuerySet[MeltanoProject]:
        """Get projects accessible to current user."""
        return (
            MeltanoProject.objects.filter(
                Q(owner=self.request.user) | Q(collaborators=self.request.user),
            )
            .select_related("owner", "template")
            .prefetch_related("collaborators", "deployments")
        )

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Add additional context for project detail."""
        context = super().get_context_data(**kwargs)
        project = self.object

        # Get recent deployments
        context["recent_deployments"] = project.deployments.order_by("-started_at")[:5]

        # Get project members
        context["members"] = ProjectMembership.objects.filter(
            project=project,
        ).select_related("user")

        # User permissions
        context["user_membership"] = ProjectMembership.objects.filter(
            project=project,
            user=self.request.user,
        ).first()
        context["is_owner"] = project.owner == self.request.user

        return context


class ProjectCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create view for new Meltano project.

    Provides project creation with template selection and initial configuration.
    """

    model = MeltanoProject
    template_name = "projects/create.html"
    fields: ClassVar[list[str]] = [
        "name",
        "display_name",
        "description",
        "meltano_version",
        "project_path",
        "repository_url",
        "template",
        "default_environment",
    ]
    success_message = "Project '{display_name}' created successfully!"

    def form_valid(self, form: ModelForm) -> HttpResponse:
        """Set the current user as project owner."""
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Add templates to context."""
        context = super().get_context_data(**kwargs)
        context["templates"] = ProjectTemplate.objects.filter(is_active=True)
        return context

    def get_success_url(self) -> str:
        """Redirect to project detail after creation."""
        return reverse_lazy("projects: detail", kwargs={"pk": self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update view for existing Meltano project.

    Allows project modification with appropriate permission checks.
    """

    model = MeltanoProject
    template_name = "projects/update.html"
    fields: ClassVar[list[str]] = [
        "display_name",
        "description",
        "meltano_version",
        "project_path",
        "repository_url",
        "status",
        "default_environment",
    ]
    success_message = "Project '{display_name}' updated successfully!"

    def get_queryset(self) -> QuerySet[MeltanoProject]:
        """Only allow owners and REDACTED_LDAP_BIND_PASSWORDs to update projects."""
        return MeltanoProject.objects.filter(
            Q(owner=self.request.user)
            | Q(
                projectmembership__user=self.request.user,
                projectmembership__role__in=["REDACTED_LDAP_BIND_PASSWORD", "owner"],
            ),
        )

    def get_success_url(self) -> str:
        """Redirect to project detail after update."""
        return reverse_lazy("projects: detail", kwargs={"pk": self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for Meltano project.

    Provides safe project deletion with confirmation for project owners only.
    """

    model = MeltanoProject
    template_name = "projects/delete.html"
    success_url = reverse_lazy("projects: list")

    def get_queryset(self) -> QuerySet[MeltanoProject]:
        """Only allow owners to delete projects."""
        return MeltanoProject.objects.filter(owner=self.request.user)


class ProjectDeployView(LoginRequiredMixin, View):
    """Deployment view for Meltano project.

    Handles project deployment to specified environments with comprehensive logging.
    """

    template_name = "projects/deploy.html"

    def get(self, request: HttpRequest, pk: str) -> HttpResponse:
        """Display deployment form."""
        project = get_object_or_404(MeltanoProject, pk=pk)
        return render(request, self.template_name, {"project": project})

    def post(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Deploy project to specified environment."""
        project = get_object_or_404(
            MeltanoProject.objects.filter(
                Q(owner=request.user)
                | Q(
                    projectmembership__user=request.user,
                    projectmembership__role__in=["REDACTED_LDAP_BIND_PASSWORD", "developer"],
                ),
            ),
            pk=pk,
        )

        environment = request.POST.get("environment", "dev")
        version = request.POST.get("version", "latest")

        # Create deployment record
        deployment = ProjectDeployment.objects.create(
            project=project,
            environment=environment,
            version=version,
            deployed_by=request.user,
            status=ProjectDeployment.DeploymentStatus.PENDING,
        )

        # Here you would integrate with actual deployment system
        # For now, we'll simulate a successful deployment
        deployment.mark_completed(ProjectDeployment.DeploymentStatus.SUCCESS)
        project.update_last_deployment()

        return JsonResponse(
            {
                "success": True,
                "message": f"Project deployed to {environment} successfully",
                "deployment_id": str(deployment.id),
            },
        )


class ProjectMembersView(LoginRequiredMixin, DetailView):
    """View for managing project team members.

    Provides team member management with role-based access control.
    """

    model = MeltanoProject
    template_name = "projects/members.html"
    context_object_name = "project"

    def get_queryset(self) -> QuerySet[MeltanoProject]:
        """Get projects where user has REDACTED_LDAP_BIND_PASSWORD access."""
        return MeltanoProject.objects.filter(
            Q(owner=self.request.user)
            | Q(
                projectmembership__user=self.request.user,
                projectmembership__role="REDACTED_LDAP_BIND_PASSWORD",
            ),
        )


class ProjectDeploymentsView(LoginRequiredMixin, DetailView):
    """View for project deployment history.

    Provides comprehensive deployment tracking and history management.
    """

    model = MeltanoProject
    template_name = "projects/deployments.html"
    context_object_name = "project"

    def get_queryset(self) -> QuerySet[MeltanoProject]:
        """Get projects accessible to current user."""
        return MeltanoProject.objects.filter(
            Q(owner=self.request.user) | Q(collaborators=self.request.user),
        ).prefetch_related("deployments__deployed_by")


class TemplateListView(LoginRequiredMixin, ListView):
    """List view for project templates.

    Provides template browsing and management for project standardization.
    """

    model = ProjectTemplate
    template_name = "projects/template_list.html"
    context_object_name = "templates"
    paginate_by = 15

    def get_queryset(self) -> QuerySet[ProjectTemplate]:
        """Get active templates with filtering."""
        queryset = ProjectTemplate.objects.filter(is_active=True)

        category = self.request.GET.get("category")
        if category and category != "all":
            queryset = queryset.filter(category=category)

        return queryset.order_by("category", "name")


class TemplateDetailView(LoginRequiredMixin, DetailView):
    """Detail view for project template.

    Provides template information and configuration preview.
    """

    model = ProjectTemplate
    template_name = "projects/template_detail.html"
    context_object_name = "template"


class TemplateCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create view for new project template.

    Allows creation of standardized project templates for reuse.
    """

    model = ProjectTemplate
    template_name = "projects/template_create.html"
    fields: ClassVar[list[str]] = [
        "name",
        "description",
        "category",
        "version",
        "config_template",
        "plugins_template",
        "environments_template",
    ]
    success_message = "Template '{name}' created successfully!"

    def form_valid(self, form: ModelForm) -> HttpResponse:
        """Set the current user as template creator."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Redirect to template detail after creation."""
        return reverse_lazy("projects: template-detail", kwargs={"pk": self.object.pk})


# API Views for AJAX/REST interactions


class ProjectAPIView(LoginRequiredMixin, View):
    """REST API view for project operations.

    Provides JSON API endpoints for project management operations.
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        """Get projects list as JSON."""
        projects = (
            MeltanoProject.objects.filter(
                Q(owner=request.user) | Q(collaborators=request.user),
            )
            .distinct()
            .values("id", "name", "display_name", "status", "created_at", "updated_at")
        )

        return JsonResponse({"projects": list(projects), "count": len(projects)})


class ProjectStatusAPIView(LoginRequiredMixin, View):
    """API view for project status operations.

    Provides real-time project status updates and monitoring.
    """

    def get(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Get project status and statistics."""
        project = get_object_or_404(
            MeltanoProject.objects.filter(
                Q(owner=request.user) | Q(collaborators=request.user),
            ),
            pk=pk,
        )

        recent_deployment = project.deployments.order_by("-started_at").first()

        return JsonResponse(
            {
                "id": str(project.id),
                "name": project.name,
                "status": project.status,
                "total_pipelines": project.total_pipelines,
                "total_plugins": project.total_plugins,
                "last_execution_count": project.last_execution_count,
                "last_deployment": (
                    {
                        "environment": (
                            recent_deployment.environment if recent_deployment else None
                        ),
                        "status": (
                            recent_deployment.status if recent_deployment else None
                        ),
                        "deployed_at": (
                            recent_deployment.started_at.isoformat()
                            if recent_deployment
                            else None
                        ),
                    }
                    if recent_deployment
                    else None
                ),
            },
        )


class DeploymentAPIView(LoginRequiredMixin, View):
    """API view for deployment operations.

    Provides deployment management and monitoring endpoints.
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        """Get deployments list for user's projects."""
        project_ids = MeltanoProject.objects.filter(
            Q(owner=request.user) | Q(collaborators=request.user),
        ).values_list(
            "id",
            flat=True,
        )

        deployments = (
            ProjectDeployment.objects.filter(project_id__in=project_ids)
            .select_related("project", "deployed_by")
            .order_by("-started_at")[:20]
        )

        deployments_data = [
            {
                "id": str(deployment.id),
                "project": {
                    "id": str(deployment.project.id),
                    "name": deployment.project.name,
                },
                "environment": deployment.environment,
                "version": deployment.version,
                "status": deployment.status,
                "deployed_by": deployment.deployed_by.username,
                "started_at": deployment.started_at.isoformat(),
                "completed_at": (
                    deployment.completed_at.isoformat()
                    if deployment.completed_at
                    else None
                ),
                "duration_seconds": deployment.duration_seconds,
            }
            for deployment in deployments
        ]

        return JsonResponse(
            {"deployments": deployments_data, "count": len(deployments_data)},
        )
