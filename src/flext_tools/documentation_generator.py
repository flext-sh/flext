"""FLEXT Documentation Generator.

Provides comprehensive documentation generation for the FLEXT ecosystem
using Jinja2 templates, MkDocs integration, and automated content generation.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import shutil
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path

import mkdocs.__main__
from flext_core import FlextLogger, FlextResult

from .discovery_base import DependencyDiscovery
from .documentation_templates import TemplateManager
from .script_base import FlextScript, ScriptMetadata


class DocumentationGenerator(FlextScript):
    """FLEXT Documentation Generator using enterprise patterns.

    Generates comprehensive documentation for the FLEXT ecosystem using
    Jinja2 templates, MkDocs integration, and automated content generation.
    """

    def __init__(self, project_root: Path) -> None:
        """Initialize documentation generator.

        Parameters
        ----------
        project_root:
            Root directory of the FLEXT workspace.

        """
        super().__init__()
        self.project_root = project_root
        self.docs_dir = project_root / "docs"
        self.mkdocs_config = project_root / "mkdocs.yml"
        self.template_manager = TemplateManager()
        self.discovery = DependencyDiscovery()
        # Explicitly initialize logger from flext-core
        self.logger = FlextLogger(__name__)

    @property
    def metadata(self) -> ScriptMetadata:
        """Get script metadata.

        Returns
        -------
        ScriptMetadata
            Script metadata for CLI integration and discovery.

        """
        return ScriptMetadata(
            name="generate-docs",
            description="Generate comprehensive documentation for FLEXT ecosystem",
            category="documentation",
            version="0.9.0",
            dry_run_supported=True,
            requires_confirmation=False,
        )

    def validate_preconditions(self) -> FlextResult[None]:
        """Validate that all required tools are available.

        Returns
        -------
        FlextResult[None]
            Validation result indicating success or failure.

        """
        self.logger.info("Validating documentation generation environment...")

        # Validate required tools (without spawning processes)
        required_tools = ["mkdocs", "git"]

        missing_tools_errors = []

        for tool_name in required_tools:
            tool_path = shutil.which(tool_name)
            if tool_path:
                self.logger.info(f"✓ {tool_name}: found at {tool_path}")
            else:
                error_msg = f"✗ {tool_name} not found in PATH"
                self.logger.error(error_msg)
                missing_tools_errors.append(error_msg)

        # Python info via sys.version
        self.logger.info(f"✓ python: {sys.version.split()[0]}")

        # Validate MkDocs configuration
        if not self.mkdocs_config.exists():
            error_msg = "mkdocs.yml not found in project root"
            self.logger.error(error_msg)
            missing_tools_errors.append(error_msg)

        # Validate templates
        templates_result = self.template_manager.list_templates()
        if not templates_result.success:
            error_msg = f"Template validation failed: {templates_result.error}"
            self.logger.error(error_msg)
            missing_tools_errors.append(error_msg)

        if missing_tools_errors:
            return FlextResult[None].fail(
                "Precondition validation failed: " + "; ".join(missing_tools_errors),
            )

        self.logger.info("All preconditions validated successfully!")

        return FlextResult[None].ok(None)

    def execute_main_logic(self, **kwargs: object) -> FlextResult[object]:
        """Execute documentation generation.

        Parameters
        ----------
        **kwargs:
            Additional keyword arguments to configure generation.

        Returns
        -------
        FlextResult[object]
            Result containing generation details or error.

        """
        try:
            self.logger.info("Starting FLEXT documentation generation...")

            # Get arguments
            clean = kwargs.get("clean", False)
            serve = bool(kwargs.get("serve"))
            components_only = kwargs.get("components_only", False)
            dry_run = bool(kwargs.get("dry_run"))

            # Step 1: Clean previous build if requested
            if clean:
                if dry_run:
                    self.logger.info("[dry-run] Would clean previous build directories")
                else:
                    self._clean_build()

            # Step 2: Generate component documentation
            if dry_run:
                self.logger.info("[dry-run] Would generate component documentation")
                components_result = FlextResult[FlextTypes.Core.Dict].ok({})
            else:
                components_result = self._generate_component_docs()
            if not components_result.success:
                return FlextResult[object].fail(
                    components_result.error or "Component generation failed",
                )

            if components_only:
                self.logger.info("Component documentation generation completed")
                return FlextResult[object].ok({"status": "components_generated"})

            # Execute full generation pipeline
            # Use type: ignore for the variance issue (FlextTypes.Core.Dict is compatible with object)
            if dry_run:
                self.logger.info(
                    "[dry-run] Would generate API docs, diagrams and build"
                )
                return FlextResult[object].ok(
                    {
                        "status": "dry_run",
                        "message": "Documentation steps validated",
                        "components": components_result.value,
                    },
                )
            return self._execute_full_generation_pipeline(
                components_result,
                serve=serve,
            )

        except Exception as e:
            error_msg = f"Documentation generation failed: {e}"
            self.logger.exception(error_msg)
            return FlextResult[object].fail(error_msg)

    def _execute_full_generation_pipeline(
        self,
        components_result: FlextResult[FlextTypes.Core.Dict],
        *,
        serve: bool,
    ) -> FlextResult[object]:
        """Execute the full documentation generation pipeline."""
        # Step 3: Generate API documentation
        api_result = self._generate_api_docs()
        if not api_result.success:
            return FlextResult[object].fail(api_result.error or "API generation failed")

        # Step 4: Generate architecture diagrams
        diagrams_result = self._generate_architecture_diagrams()
        if not diagrams_result.success:
            return FlextResult[object].fail(
                diagrams_result.error or "Diagram generation failed",
            )

        # Step 5: Build documentation
        build_result = self._build_docs()
        if not build_result.success:
            return FlextResult[object].fail(build_result.error or "Build failed")

        # Step 6: Serve documentation if requested
        if serve:
            self._serve_docs()

        self.logger.info("Documentation generation completed successfully!")
        return FlextResult[object].ok(
            {
                "status": "success",
                "message": "Documentation generated",
                "components": components_result.value,
                "apis": api_result.value,
                "diagrams": diagrams_result.value,
            },
        )

    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser for documentation generation.

        Returns
        -------
        argparse.ArgumentParser
            Configured parser with generator options.

        """
        parser = super().create_parser()

        parser.add_argument(
            "--clean",
            action="store_true",
            help="Clean previous build before generating",
        )
        parser.add_argument(
            "--serve",
            action="store_true",
            help="Serve documentation after building",
        )
        parser.add_argument(
            "--components-only",
            action="store_true",
            help="Generate only component documentation",
        )
        parser.add_argument(
            "--project-root",
            type=Path,
            default=Path.cwd(),
            help="Project root directory",
        )

        return parser

    def _clean_build(self) -> None:
        """Clean previous documentation build."""
        self.logger.info("Cleaning previous build...")

        build_dirs = [
            self.project_root / "site",
            self.docs_dir / ".cache",
            self.docs_dir / "build",
        ]

        for build_dir in build_dirs:
            if build_dir.exists():
                shutil.rmtree(build_dir)
                self.logger.info(f"Removed {build_dir}")

    def _generate_component_docs(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Generate documentation for individual components.

        Returns
        -------
        FlextResult[FlextTypes.Core.Dict]
            Component generation results keyed by project name.

        """
        self.logger.info("Generating component documentation...")

        # Discover projects manually since DependencyDiscovery doesn't have discover_projects
        projects = [
            item
            for item in self.project_root.iterdir()
            if item.is_dir()
            and (item.name.startswith("flext-") or item.name == "flexcore")
        ]

        components_data: FlextTypes.Core.Dict = {}

        for project_path in projects:
            project_name = project_path.name

            self.logger.info(f"Processing component: {project_name}")

            # Create component documentation directory
            component_docs_dir = self.docs_dir / "projects" / project_name
            component_docs_dir.mkdir(parents=True, exist_ok=True)

            # Generate component data
            component_data = self._extract_component_data(project_path, project_name)

            # Generate README using template
            readme_result = self.template_manager.render_component_readme(
                component_data,
            )
            if not readme_result.success:
                self.logger.warning(
                    f"Failed to render README for {project_name}: {readme_result.error}",
                )
                continue

            # Write README
            readme_path = component_docs_dir / "README.md"
            if readme_result.value is not None:
                readme_path.write_text(readme_result.value)

            # Copy existing documentation if available
            existing_docs = project_path / "docs"
            if existing_docs.exists():
                self._copy_existing_docs(existing_docs, component_docs_dir)

            # Generate API documentation if Python component
            if self._is_python_component(project_path):
                api_result = self._generate_component_api_docs(
                    project_name,
                    project_path,
                    component_docs_dir,
                )
                if api_result.success:
                    component_data["api_generated"] = True

            components_data[project_name] = component_data

        return FlextResult[FlextTypes.Core.Dict].ok(components_data)

    def _extract_component_data(
        self,
        project_path: Path,
        project_name: str,
    ) -> FlextTypes.Core.Dict:
        """Extract component data for template rendering.

        Parameters
        ----------
        project_path:
            Path to the project.
        project_name:
            Name of the project.

        Returns
        -------
        FlextTypes.Core.Dict
            Component data dictionary for templates.

        """
        # Try to read existing README for data extraction
        existing_readme = project_path / "README.md"
        if existing_readme.exists():
            content = existing_readme.read_text()
            # Extract version, description, etc. from existing README
            # This is a simplified extraction - could be enhanced with regex
            description = self._extract_description(content, project_name)
        else:
            description = f"{project_name.replace('-', ' ').title()} Component"

        # Try to extract version from pyproject.toml
        version = self._extract_version(project_path)

        return {
            "name": project_name,
            "description": description,
            "version": version,
            "status": self._determine_status(project_path),
            "last_updated": datetime.now(UTC).strftime("%Y-%m-%d"),
            "path": str(project_path),
            "features": self._extract_features(project_path),
            "installation": self._extract_installation(project_path),
            "usage": self._extract_usage(project_path),
            "configuration": self._extract_configuration(project_path),
        }

    def _extract_description(self, content: str, project_name: str) -> str:
        """Extract description from README content.

        Parameters
        ----------
        content:
            README content.
        project_name:
            Project name.

        Returns
        -------
        str
            Extracted description text.

        """
        # Simple extraction - look for first heading or description
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# ") and not line.startswith("# " + project_name):
                return line[2:].strip()
            if line.strip() and not line.startswith("#") and not line.startswith("---"):
                return line.strip()

        return f"{project_name.replace('-', ' ').title()} Component"

    def _extract_version(self, project_path: Path) -> str:
        """Extract version from pyproject.toml.

        Parameters
        ----------
        project_path:
            Path to the project.

        Returns
        -------
        str
            Extracted version string.

        """
        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with pyproject_path.open("rb") as f:
                    data = tomllib.load(f)
                    version = data.get("project", {}).get("version", "0.9.0")
                    return str(version)
            except Exception:
                self.logger.exception("Failed to extract version from pyproject.toml")
                raise

        return "0.9.0"

    def _determine_status(self, project_path: Path) -> str:
        """Determine component status based on project structure.

        Parameters
        ----------
        project_path:
            Path to the project.

        Returns
        -------
        str
            Component status label.

        """
        # Check for indicators of status
        if (project_path / "tests").exists() and (project_path / "src").exists():
            return "stable"
        if (project_path / "src").exists():
            return "beta"
        return "alpha"

    def _extract_features(self, project_path: Path) -> FlextTypes.Core.StringList:
        """Extract features from project structure.

        Parameters
        ----------
        project_path:
            Path to the project.

        Returns
        -------
        FlextTypes.Core.StringList
            List of feature labels.

        """
        features = []

        if (project_path / "src").exists():
            features.append("Python implementation")
        if (project_path / "tests").exists():
            features.append("Test coverage")
        if (project_path / "docs").exists():
            features.append("Documentation")
        if (project_path / "examples").exists():
            features.append("Examples")

        return features

    def _extract_installation(self, project_path: Path) -> str:
        """Extract installation instructions.

        Parameters
        ----------
        project_path:
            Path to the project.

        Returns
        -------
        str
            Installation instructions snippet.

        """
        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists():
            return "pip install -e ."
        return "Installation instructions will be added"

    def _extract_usage(self, project_path: Path) -> str:
        """Extract usage examples.

        Parameters
        ----------
        project_path:
            Path to the project.

        Returns
        -------
        str
            Usage examples summary.

        """
        examples_dir = project_path / "examples"
        if examples_dir.exists():
            example_files = list(examples_dir.glob("*.py"))
            if example_files:
                return f"See examples in {examples_dir.name}/"

        return "# Usage examples will be added"

    def _extract_configuration(self, project_path: Path) -> str:
        """Extract configuration information.

        Parameters
        ----------
        project_path:
            Path to the project.

        Returns
        -------
        str
            Configuration information summary.

        """
        config_files = list(project_path.glob("*.yaml")) + list(
            project_path.glob("*.yml"),
        )
        if config_files:
            return f"Configuration files: {', '.join(f.name for f in config_files)}"

        return "Configuration options will be documented here"

    def _is_python_component(self, project_path: Path) -> bool:
        """Check if project is a Python component.

        Parameters
        ----------
        project_path:
            Path to the project.

        Returns
        -------
        bool
            True if a Python component is detected.

        """
        return (project_path / "src").exists() or (
            project_path / "pyproject.toml"
        ).exists()

    def _generate_component_api_docs(
        self,
        project_name: str,
        _project_path: Path,
        docs_dir: Path,
    ) -> FlextResult[None]:
        """Generate API documentation for a component.

        Parameters
        ----------
        project_name:
            Name of the project.
        docs_dir:
            Target documentation directory.

        Returns
        -------
        FlextResult[None]
            Result indicating success or failure.

        """
        self.logger.info(f"Generating API docs for {project_name}")

        # Create API documentation directory
        api_dir = docs_dir / "api"
        api_dir.mkdir(exist_ok=True)

        # Prepare API data
        api_data: FlextTypes.Core.Dict = {
            "name": project_name.title(),
            "status": "published",
            "version": "0.9.0",
            "last_updated": datetime.now(UTC).strftime("%Y-%m-%d"),
            "module_name": project_name.replace("-", "_"),
            "handler": "python",
            "docstring_style": "google",
            "description": f"API reference for {project_name} component",
        }

        # Render API documentation
        api_result = self.template_manager.render_api_reference(api_data)
        if not api_result.success:
            return FlextResult[None].fail(
                f"Failed to render API docs for {project_name}: {api_result.error}",
            )

        # Write API documentation
        api_file = api_dir / "README.md"
        if api_result.value is not None:
            api_file.write_text(api_result.value)

        return FlextResult[None].ok(None)

    def _copy_existing_docs(self, source: Path, target: Path) -> None:
        """Copy existing documentation from a component.

        Parameters
        ----------
        source:
            Source directory containing documentation.
        target:
            Target directory to receive copied files.

        """
        self.logger.info(f"Copying existing documentation from {source} to {target}")

        for item in source.iterdir():
            if item.is_file() and item.suffix == ".md":
                shutil.copy2(item, target / item.name)
            elif item.is_dir():
                shutil.copytree(item, target / item.name, dirs_exist_ok=True)

    def _generate_api_docs(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Generate comprehensive API documentation.

        Returns
        -------
        FlextResult[FlextTypes.Core.Dict]
            Mapping of API documentation sections and metadata.

        """
        self.logger.info("Generating API documentation...")

        # Create API reference directory
        api_ref_dir = self.docs_dir / "reference" / "api"
        api_ref_dir.mkdir(parents=True, exist_ok=True)

        api_results: FlextTypes.Core.Dict = {}

        # Generate REST API documentation
        rest_api_data: FlextTypes.Core.Dict = {
            "name": "REST API",
            "status": "published",
            "version": "0.9.0",
            "last_updated": datetime.now(UTC).strftime("%Y-%m-%d"),
            "description": "Complete REST API reference for the FLEXT platform",
            "installation": "pip install flext",
            "quick_start": self._get_rest_api_quick_start(),
            "module_name": "flext.api",
            "handler": "python",
            "docstring_style": "google",
        }

        rest_api_result = self.template_manager.render_api_reference(rest_api_data)
        if rest_api_result.success and rest_api_result.value is not None:
            rest_api_file = api_ref_dir / "rest-api.md"
            rest_api_file.write_text(rest_api_result.value)
            api_results["rest_api"] = rest_api_data

        # Generate Python SDK documentation
        python_sdk_data: FlextTypes.Core.Dict = {
            "name": "Python SDK",
            "status": "published",
            "version": "0.9.0",
            "last_updated": datetime.now(UTC).strftime("%Y-%m-%d"),
            "description": "Python client library for the FLEXT platform",
            "installation": "pip install flext",
            "quick_start": self._get_python_sdk_quick_start(),
            "module_name": "flext.client",
            "handler": "python",
            "docstring_style": "google",
        }

        python_sdk_result = self.template_manager.render_api_reference(python_sdk_data)
        if python_sdk_result.success and python_sdk_result.value is not None:
            python_sdk_file = api_ref_dir / "python-sdk.md"
            python_sdk_file.write_text(python_sdk_result.value)
            api_results["python_sdk"] = python_sdk_data

        return FlextResult[FlextTypes.Core.Dict].ok(api_results)

    def _get_rest_api_quick_start(self) -> str:
        """Get REST API quick start example.

        Returns
        -------
        str
            Example code snippet.

        """
        return """from flext import FlextClient

# Initialize client
client = FlextClient(api_key="your-api-key")

# Create a pipeline
pipeline = client.pipelines.create(
    name="my-pipeline",
    source="oracle",
    target="postgresql"
)

# Run the pipeline
result = pipeline.run()
print(f"Pipeline status: {result.status}")"""

    def _get_python_sdk_quick_start(self) -> str:
        """Get Python SDK quick start example.

        Returns
        -------
        str
            Example code snippet.

        """
        return """from flext import FlextClient

# Initialize client
client = FlextClient(api_key="your-api-key")

# Create a pipeline
pipeline = client.pipelines.create(
    name="my-pipeline",
    source="oracle",
    target="postgresql"
)

# Run the pipeline
result = pipeline.run()
print(f"Pipeline status: {result.status}")"""

    def _generate_architecture_diagrams(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Generate architecture diagrams using templates.

        Returns
        -------
        FlextResult[FlextTypes.Core.Dict]
            Diagram generation results and metadata.

        """
        self.logger.info("Generating architecture diagrams...")

        # Create architecture documentation directory
        arch_dir = self.docs_dir / "developer" / "architecture"
        arch_dir.mkdir(parents=True, exist_ok=True)

        diagram_results: FlextTypes.Core.Dict = {}

        # Generate system overview diagram
        overview_data: FlextTypes.Core.Dict = {
            "title": "System Architecture Overview",
            "status": "published",
            "version": "0.9.0",
            "last_updated": datetime.now(UTC).strftime("%Y-%m-%d"),
            "description": "Complete system architecture overview for FLEXT platform",
            "section_title": "System Overview",
            "mermaid_code": self._get_system_overview_mermaid(),
            "principles": [
                {
                    "title": "Clean Architecture",
                    "description": "FLEXT follows Clean Architecture principles with clear separation of concerns",
                    "details": [
                        "Domain Layer: Core business logic and entities",
                        "Application Layer: Use cases and application services",
                        "Infrastructure Layer: External interfaces and implementations",
                        "Presentation Layer: APIs and user interfaces",
                    ],
                },
                {
                    "title": "Multi-Language Integration",
                    "description": "FLEXT integrates multiple programming languages for optimal performance",
                    "details": [
                        "Python 3.13+: Main application logic and APIs",
                        "Go 1.19+: High-performance core services",
                        "TypeScript: Web interface components",
                        "SQL: Data transformation and analytics",
                    ],
                },
            ],
        }

        overview_result = self.template_manager.render_architecture_diagram(
            overview_data,
        )
        if overview_result.success and overview_result.value is not None:
            overview_file = arch_dir / "overview.md"
            overview_file.write_text(overview_result.value)
            diagram_results["overview"] = overview_data

        # Generate component interaction diagram
        interaction_data: FlextTypes.Core.Dict = {
            "title": "Component Interactions",
            "status": "published",
            "version": "0.9.0",
            "last_updated": datetime.now(UTC).strftime("%Y-%m-%d"),
            "description": "Component interaction flow and data processing",
            "section_title": "Component Interaction Flow",
            "mermaid_code": self._get_component_interaction_mermaid(),
            "data_flow": [
                {
                    "title": "Pipeline Creation",
                    "description": "User creates pipeline configuration",
                },
                {
                    "title": "Data Extraction",
                    "description": "TAP components extract data from sources",
                },
                {
                    "title": "Transformation",
                    "description": "Data is transformed as needed",
                },
                {
                    "title": "Data Loading",
                    "description": "Target components load data to destinations",
                },
                {
                    "title": "Monitoring",
                    "description": "Progress and status are tracked throughout",
                },
            ],
        }

        interaction_result = self.template_manager.render_architecture_diagram(
            interaction_data,
        )
        if interaction_result.success and interaction_result.value is not None:
            interaction_file = arch_dir / "component-interactions.md"
            interaction_file.write_text(interaction_result.value)
            diagram_results["interactions"] = interaction_data

        return FlextResult[FlextTypes.Core.Dict].ok(diagram_results)

    def _get_system_overview_mermaid(self) -> str:
        """Get system overview Mermaid diagram.

        Returns
        -------
        str
            Mermaid diagram code.

        """
        return """graph TB
    subgraph "Client Layer"
      CLI[FLEXT CLI]
      WEB[FLEXT Web]
      SDK[Python/Go SDK]
    end

    subgraph "API Layer"
      API[FLEXT API]
      AUTH[Authentication]
    end

    subgraph "Core Services"
      CORE[FlexCore - Go]
      WORKER[Worker Pool]
      QUEUE[Message Queue]
    end

    subgraph "Data Integration"
      TAP[Data Taps]
      TARGET[Data Targets]
      TRANSFORM[Transformations]
    end

    subgraph "External Systems"
      ORACLE[Oracle DB]
      LDAP[LDAP Directory]
      POSTGRES[PostgreSQL]
    end

    CLI --> API
    WEB --> API
    SDK --> API
    API --> AUTH
    API --> CORE
    CORE --> WORKER
    WORKER --> QUEUE
    CORE --> TAP
    CORE --> TARGET
    CORE --> TRANSFORM
    TAP --> ORACLE
    TAP --> LDAP
    TARGET --> POSTGRES"""

    def _get_component_interaction_mermaid(self) -> str:
        """Get component interaction Mermaid diagram.

        Returns
        -------
        str
            Mermaid diagram code.

        """
        return """sequenceDiagram
    participant User
    participant CLI as FLEXT CLI
    participant API as FLEXT API
    participant Core as FlexCore
    participant Tap as Data TAP
    participant Target as Data Target
    participant DB as Database

    User->>CLI: Create Pipeline
    CLI->>API: POST /pipelines
    API->>Core: Create Pipeline
    Core->>DB: Store Pipeline Config
    API->>CLI: Pipeline Created
    CLI->>User: Success

    User->>CLI: Run Pipeline
    CLI->>API: POST /pipelines/{id}/run
    API->>Core: Execute Pipeline
    Core->>Tap: Extract Data
    Tap->>Core: Data Stream
    Core->>Target: Load Data
    Target->>DB: Store Data
    Core->>API: Pipeline Complete
    API->>CLI: Success
    CLI->>User: Pipeline Complete"""

    def _build_docs(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Build the documentation using MkDocs.

        Returns
        -------
        FlextResult[FlextTypes.Core.Dict]
            Build results with status and output logs.

        """
        self.logger.info("Building documentation with MkDocs...")

        try:
            # Use in-process mkdocs entrypoint

            stdout = io.StringIO()
            stderr = io.StringIO()
            with (
                contextlib.redirect_stdout(stdout),
                contextlib.redirect_stderr(stderr),
            ):
                try:
                    exit_code = int(
                        mkdocs.__main__.cli(
                            ["build", "-f", str(self.mkdocs_config), "--clean"],
                        ),
                    )
                except SystemExit as exc:
                    exit_code = int(getattr(exc, "code", 0) or 0)
            if exit_code != 0:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    f"MkDocs build failed: {stderr.getvalue().strip()}",
                )
            self.logger.info("Documentation built successfully")
            return FlextResult[FlextTypes.Core.Dict].ok(
                {
                    "status": "built",
                    "output": stdout.getvalue(),
                }
            )
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(f"MkDocs build failed: {e}")

    def _serve_docs(self) -> None:
        """Serve the documentation locally."""
        self.logger.info("Starting documentation server...")
        self.logger.info("Documentation will be available at: http://localhost:8000")
        self.logger.info("Press Ctrl+C to stop the server")

        try:
            # Prefer programmatic serve via mkdocs if available
            try:
                if mkdocs.__main__ is not None:
                    mkdocs.__main__.cli(["serve", "-f", str(self.mkdocs_config)])
                    return
            except Exception as e:
                self.logger.debug(f"mkdocs python entrypoint not available: {e}")
            # Validate mkdocs executable name; if not available, report error
            mk = shutil.which("mkdocs")
            if not mk:
                self.logger.error("mkdocs executable not found in PATH")
                return
            # Avoid background serve in scripts; instruct the user instead
            self.logger.info("Run 'mkdocs serve' manually if needed")
        except KeyboardInterrupt:
            self.logger.info("Documentation server stopped")
        except Exception:
            self.logger.exception("Failed to start documentation server")


def main() -> int:
    """Run the documentation generator entry point."""
    parser = argparse.ArgumentParser(description="Generate FLEXT documentation")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean previous build before generating",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Serve documentation after building",
    )
    parser.add_argument(
        "--components-only",
        action="store_true",
        help="Generate only component documentation",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory",
    )

    args = parser.parse_args()

    # Initialize generator
    generator = DocumentationGenerator(args.project_root)

    # Generate documentation
    return generator.run(
        clean=args.clean,
        serve=args.serve,
        components_only=args.components_only,
    )


if __name__ == "__main__":
    sys.exit(main())
