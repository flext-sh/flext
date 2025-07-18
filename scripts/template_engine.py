#!/usr/bin/env python3
"""
FLEXT Template Engine - Jinja2 Template Management
=================================================

Sistema centralizado para gerenciar templates Jinja2 usados pelos scripts
de automação do FLEXT. Separação clara entre lógica e apresentação.

Author: FLEXT Automation Team
"""

from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from jinja2 import Environment, FileSystemLoader, Template

    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    print("⚠️  Jinja2 not available. Install with: pip install jinja2")


class TemplateEngine:
    """Centralized template management for FLEXT scripts."""

    def __init__(self, workspace_root: Path):
        """Initialize template engine with workspace root."""
        self.workspace_root = workspace_root
        self.templates_dir = workspace_root / "scripts" / "templates"

        if not JINJA2_AVAILABLE:
            msg = "Jinja2 is required. Install with: pip install jinja2"
            raise ImportError(msg)

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Add custom filters
        self.env.filters["quote"] = lambda x: f'"{x}"'
        self.env.filters["timestamp"] = lambda: datetime.now().isoformat()

    def render_makefile_enhancement(
        self,
        project_name: str,
        project_type: str = "generic",
        custom_vars: dict[str, Any] | None = None,
    ) -> str:
        """Render Makefile enhancement based on project type."""
        template_vars = {
            "project_name": project_name,
            "project_type": project_type,
            "timestamp": datetime.now().isoformat(),
        }

        if custom_vars:
            template_vars.update(custom_vars)

        # Load base template
        base_template = self.env.get_template("makefiles/base_enhancement.j2")
        base_content = base_template.render(**template_vars)

        # Add project-specific enhancements
        if project_type == "singer_project":
            singer_template = self.env.get_template("makefiles/singer_project.j2")
            singer_content = singer_template.render(**template_vars)
            return base_content + "\n\n" + singer_content

        return base_content

    def render_python_implementation(
        self,
        method_name: str,
        method_type: str,
        custom_vars: dict[str, Any] | None = None,
    ) -> str:
        """Render Python code implementation for replacing NotImplementedError."""
        # Determine method type from name if not provided
        if method_type == "auto":
            method_type = self._determine_method_type(method_name)

        template_vars = {
            "method_name": method_name,
            "method_type": method_type,
        }

        if custom_vars:
            template_vars.update(custom_vars)

        template = self.env.get_template("python_code/redis_implementations.j2")
        return template.render(**template_vars).strip()

    def render_quality_report(
        self,
        report_title: str,
        projects: list[dict[str, Any]],
        statistics: dict[str, Any] | None = None,
        recommendations: list[str] | None = None,
        custom_vars: dict[str, Any] | None = None,
    ) -> str:
        """Render quality report."""
        template_vars = {
            "report_title": report_title,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "projects": projects,
            "total_projects": len(projects),
            "projects_processed": len(
                [p for p in projects if p.get("status") != "skipped"],
            ),
            "success_rate": (
                round(
                    len([p for p in projects if p.get("status") == "success"])
                    / len(projects)
                    * 100,
                    1,
                )
                if projects
                else 0
            ),
            "statistics": statistics or {},
            "recommendations": recommendations or [],
        }

        if custom_vars:
            template_vars.update(custom_vars)

        template = self.env.get_template("reports/quality_report.j2")
        return template.render(**template_vars)

    def render_pyproject_quality_config(
        self,
        package_name: str,
        python_version: str = "py311",
        strict_typing: bool = True,
        coverage_threshold: int = 80,
        custom_vars: dict[str, Any] | None = None,
    ) -> str:
        """Render pyproject.toml quality configuration."""
        template_vars = {
            "package_name": package_name.replace("-", "_"),
            "python_version": python_version,
            "python_version_for_mypy": python_version.replace("py", "").replace(
                "3", "3.",
            ),
            "strict_typing": strict_typing,
            "coverage_threshold": coverage_threshold,
            "coverage_enabled": True,
            "line_length": 88,
            "docstring_convention": "google",
            "ignore_rules": [],
            "per_file_ignores": {
                "tests/*": ["ANN", "D", "S101", "PLR2004"],
                "__init__.py": ["F401"],
            },
            "ignore_comments": {
                "ANN": "Type annotations not required in tests",
                "D": "Docstrings not required in tests",
                "S101": "Assert statements allowed in tests",
                "PLR2004": "Magic values allowed in tests",
                "F401": "Unused imports allowed in __init__.py",
            },
        }

        if custom_vars:
            template_vars.update(custom_vars)

        template = self.env.get_template("configs/pyproject_quality.j2")
        return template.render(**template_vars)

    def _determine_method_type(self, method_name: str) -> str:
        """Determine method type from method name for auto-detection."""
        method_lower = method_name.lower()

        if "store" in method_lower or "save" in method_lower or "set" in method_lower:
            return "store"
        if (
            "get" in method_lower
            or "fetch" in method_lower
            or "retrieve" in method_lower
        ):
            return "get"
        if (
            "delete" in method_lower
            or "remove" in method_lower
            or "del" in method_lower
        ):
            return "delete"
        if (
            "exists" in method_lower
            or "has" in method_lower
            or "contains" in method_lower
        ):
            return "exists"
        if "keys" in method_lower or "list" in method_lower:
            return "keys"
        if (
            "cleanup" in method_lower
            or "clean" in method_lower
            or "purge" in method_lower
        ):
            return "cleanup"
        return "default"

    def check_template_exists(self, template_path: str) -> bool:
        """Check if template exists."""
        try:
            self.env.get_template(template_path)
            return True
        except Exception:
            return False

    def list_available_templates(self) -> dict[str, list[str]]:
        """List all available templates by category."""
        templates = {
            "makefiles": [],
            "python_code": [],
            "configs": [],
            "reports": [],
        }

        for category in templates:
            category_dir = self.templates_dir / category
            if category_dir.exists():
                templates[category] = [f.name for f in category_dir.glob("*.j2")]

        return templates


def get_template_engine(workspace_root: Path | None = None) -> TemplateEngine:
    """Get template engine instance."""
    if workspace_root is None:
        workspace_root = Path(__file__).parent.parent

    return TemplateEngine(workspace_root)


# Example usage for testing
if __name__ == "__main__":
    engine = get_template_engine()

    # Test Makefile enhancement
    makefile_content = engine.render_makefile_enhancement(
        project_name="flext-tap-ldap", project_type="singer_project",
    )
    print("=== MAKEFILE ENHANCEMENT ===")
    print(makefile_content[:200] + "...")

    # Test Python implementation
    python_code = engine.render_python_implementation(
        method_name="store_user_data", method_type="auto",
    )
    print("\n=== PYTHON IMPLEMENTATION ===")
    print(python_code)

    # Test quality report
    projects = [
        {"name": "flext-core", "status": "success", "category": "core"},
        {"name": "flext-api", "status": "success", "category": "core"},
    ]
    report = engine.render_quality_report(
        report_title="FLEXT Quality Report", projects=projects,
    )
    print("\n=== QUALITY REPORT ===")
    print(report[:300] + "...")
