"""Template Management for FLEXT Documentation Generation.

Provides Jinja2 template management with FLEXT-specific patterns and
automated content generation capabilities.
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextLogger, FlextResult
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape


class TemplateManager:
    """Manages Jinja2 templates for FLEXT documentation generation.

    Provides template loading, rendering, and management capabilities
    with FLEXT-specific patterns and error handling.
    """

    def __init__(self, templates_dir: Path | None = None) -> None:
        """Initialize template manager.

        Args:
            templates_dir: Directory containing templates. Defaults to module templates.

        """
        self.logger = FlextLogger(self.__class__.__name__)

        if templates_dir is None:
            # Use default templates directory
            current_file = Path(__file__)
            templates_dir = current_file.parent / "templates"

        self.templates_dir = templates_dir
        self._environment = self._create_environment()

    def _create_environment(self) -> Environment:
        """Create Jinja2 environment with FLEXT-specific configuration.

        Returns:
            Configured Jinja2 environment.

        """
        env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(
                ["html", "xml"],
            ),  # Secure autoescape for appropriate formats
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Add FLEXT-specific filters
        env.filters["flext_version"] = self._flext_version_filter
        env.filters["flext_status"] = self._flext_status_filter
        env.filters["flext_category"] = self._flext_category_filter

        return env

    def _flext_version_filter(self, version: str) -> str:
        """Filter for FLEXT version formatting.

        Args:
            version: Version string to format.

        Returns:
            Formatted version string.

        """
        if not version:
            return "0.9.0"
        return version.strip()

    def _flext_status_filter(self, status: str) -> str:
        """Filter for FLEXT status formatting.

        Args:
            status: Status string to format.

        Returns:
            Formatted status string.

        """
        status_map = {
            "alpha": "Alpha",
            "beta": "Beta",
            "stable": "Stable",
            "deprecated": "Deprecated",
            "experimental": "Experimental",
        }
        return status_map.get(status.lower(), status.title())

    def _flext_category_filter(self, category: str) -> str:
        """Filter for FLEXT category formatting.

        Args:
            category: Category string to format.

        Returns:
            Formatted category string.

        """
        category_map = {
            "projects": "Projects",
            "api": "API Reference",
            "architecture": "Architecture",
            "guides": "User Guides",
            "development": "Development",
        }
        return category_map.get(category.lower(), category.title())

    def get_template(self, template_name: str) -> FlextResult[Template]:
        """Get a template by name.

        Args:
            template_name: Name of the template file.

        Returns:
            FlextResult containing the template or error.

        """
        try:
            template = self._environment.get_template(template_name)
            return FlextResult[Template].ok(template)
        except Exception as e:
            error_msg = f"Failed to load template '{template_name}': {e}"
            self.logger.exception(error_msg)
            return FlextResult[Template].fail(error_msg)

    def render_template(
        self,
        template_name: str,
        context: dict[str, object],
    ) -> FlextResult[str]:
        """Render a template with context.

        Args:
            template_name: Name of the template file.
            context: Context data for template rendering.

        Returns:
            FlextResult containing rendered content or error.

        """
        template_result = self.get_template(template_name)
        if not template_result.success:
            return FlextResult[str].fail(
                template_result.error or "Template loading failed"
            )

        try:
            template = template_result.value
            rendered = template.render(**context)
            return FlextResult[str].ok(rendered)
        except Exception as e:
            error_msg = f"Failed to render template '{template_name}': {e}"
            self.logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def render_component_readme(
        self,
        component_data: dict[str, object],
    ) -> FlextResult[str]:
        """Render component README template.

        Args:
            component_data: Component data for rendering.

        Returns:
            FlextResult containing rendered README content.

        """
        return self.render_template(
            "component_readme.md.j2",
            {"component": component_data},
        )

    def render_api_reference(self, api_data: dict[str, object]) -> FlextResult[str]:
        """Render API reference template.

        Args:
            api_data: API data for rendering.

        Returns:
            FlextResult containing rendered API reference content.

        """
        return self.render_template("api_reference.md.j2", {"api": api_data})

    def render_architecture_diagram(
        self,
        diagram_data: dict[str, object],
    ) -> FlextResult[str]:
        """Render architecture diagram template.

        Args:
            diagram_data: Diagram data for rendering.

        Returns:
            FlextResult containing rendered architecture content.

        """
        return self.render_template(
            "architecture_diagram.md.j2",
            {"diagram": diagram_data},
        )

    def list_templates(self) -> FlextResult[list[str]]:
        """List available templates.

        Returns:
            FlextResult containing list of template names.

        """
        try:
            templates = [
                file_path.name for file_path in self.templates_dir.rglob("*.j2")
            ]
            return FlextResult[list[str]].ok(templates)
        except Exception as e:
            error_msg = f"Failed to list templates: {e}"
            self.logger.exception(error_msg)
            return FlextResult[list[str]].fail(error_msg)

    def validate_template(self, template_name: str) -> FlextResult[bool]:
        """Validate that a template exists and can be loaded.

        Args:
            template_name: Name of the template to validate.

        Returns:
            FlextResult indicating validation success or failure.

        """
        template_result = self.get_template(template_name)
        if template_result.success:
            return FlextResult[bool].ok(data=True)
        return FlextResult[bool].fail(
            template_result.error or "Template validation failed"
        )
