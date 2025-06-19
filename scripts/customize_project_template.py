#!/usr/bin/env python3
"""
Project-Specific Template Customization Script

Applies project-specific configurations to the enterprise pyproject.toml template.
Handles different project types (Singer taps, API integrations, databases, etc.)
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()

# Project type configurations
PROJECT_CONFIGURATIONS = {
    "singer_tap": {
        "dependencies": {
            "singer-sdk": "^0.40.0",
            "requests": "^2.32.3",
            "backoff": "^2.2.1",
        },
        "scripts_pattern": 'tap-{project_name} = "{module_name}.cli:main"',
        "description_template": "Singer tap for extracting data from {service_name}",
    },
    "api_integration": {
        "dependencies": {
            "httpx": "^0.28.1",
            "fastapi": "^0.115.6",
            "uvicorn": "^0.32.1",
        },
        "scripts_pattern": '{project_name}-api = "{module_name}.main:app"',
        "description_template": "API integration service for {service_name}",
    },
    "database": {
        "dependencies": {
            "sqlalchemy": "^2.0.36",
            "alembic": "^1.14.0",
            "cx-oracle": "^8.3.0",
        },
        "scripts_pattern": '{project_name}-cli = "{module_name}.cli:main"',
        "description_template": "Database integration for {service_name}",
    },
    "ldap": {
        "dependencies": {
            "python-ldap": "^3.4.4",
            "ldap3": "^2.9.1",
        },
        "scripts_pattern": '{project_name}-ldap = "{module_name}.cli:main"',
        "description_template": "LDAP integration and migration tools",
    },
    "meltano": {
        "dependencies": {
            "meltano": "^3.4.0",
            "grpcio": "^1.68.1",
            "grpcio-tools": "^1.68.1",
        },
        "scripts_pattern": '{project_name} = "{module_name}.__main__:main"',
        "description_template": "Meltano enterprise data integration platform",
    },
}

# Service name mappings for description generation
SERVICE_MAPPINGS = {
    "oracle-oic": "Oracle Integration Cloud",
    "oracle-wms": "Oracle Warehouse Management System",
    "ldap": "LDAP Directory Services",
    "meltano": "Meltano Data Platform",
}


def load_pyproject(file_path: Path) -> dict[str, Any]:
    """Load and parse pyproject.toml file."""
    try:
        with open(file_path, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load {file_path}: {e}") from e


def detect_project_type(project_name: str, project_path: Path) -> str:
    """Detect project type based on name and structure."""
    name_lower = project_name.lower()

    # Singer tap detection
    if name_lower.startswith("tap-") or "tap" in name_lower:
        return "singer_tap"

    # Database integration detection
    if "database" in name_lower or "oracle" in name_lower:
        return "database"

    # LDAP detection
    if "ldap" in name_lower:
        return "ldap"

    # Meltano detection
    if "meltano" in name_lower:
        return "meltano"

    # API integration detection (default for HTTP services)
    if "http" in name_lower or "api" in name_lower:
        return "api_integration"

    # Default to API integration
    return "api_integration"


def generate_project_scripts(
    project_name: str, module_name: str, project_type: str
) -> dict[str, str]:
    """Generate CLI scripts configuration for the project."""
    config = PROJECT_CONFIGURATIONS.get(project_type, {})
    pattern = config.get(
        "scripts_pattern", '{project_name}-cli = "{module_name}.cli:main"'
    )

    script_name = pattern.format(project_name=project_name, module_name=module_name)
    script_parts = script_name.split(" = ")

    if len(script_parts) == 2:
        return {script_parts[0]: script_parts[1].strip('"')}

    return {}


def generate_project_description(project_name: str, project_type: str) -> str:
    """Generate appropriate description for the project."""
    config = PROJECT_CONFIGURATIONS.get(project_type, {})
    template = config.get(
        "description_template", "Enterprise Python automation component"
    )

    # Extract service name from project name
    service_name = "Unknown Service"
    for key, value in SERVICE_MAPPINGS.items():
        if key in project_name.lower():
            service_name = value
            break

    return template.format(service_name=service_name)


def customize_pyproject_for_project(
    project_path: Path,
    project_name: str,
    module_name: str,
    project_type: str | None = None,
    dry_run: bool = False,
) -> bool:
    """Customize pyproject.toml for specific project requirements."""

    if project_type is None:
        project_type = detect_project_type(project_name, project_path)

    logger.info(
        "Customizing project",
        project=project_name,
        type=project_type,
        module=module_name,
        dry_run=dry_run,
    )

    pyproject_file = project_path / "pyproject.toml"
    if not pyproject_file.exists():
        logger.error("pyproject.toml not found", path=pyproject_file)
        return False

    try:
        config = load_pyproject(pyproject_file)
    except ValueError as e:
        logger.error("Failed to load pyproject.toml", error=str(e))
        return False

    # Get project-specific configuration
    project_config = PROJECT_CONFIGURATIONS.get(project_type, {})

    # Update dependencies
    dependencies = (
        config.setdefault("tool", {})
        .setdefault("poetry", {})
        .setdefault("dependencies", {})
    )
    project_deps = project_config.get("dependencies", {})

    for dep_name, dep_version in project_deps.items():
        if dep_name not in dependencies:
            dependencies[dep_name] = dep_version
            logger.info("Adding dependency", dependency=dep_name, version=dep_version)

    # Update scripts
    scripts = config["tool"]["poetry"].setdefault("scripts", {})
    project_scripts = generate_project_scripts(project_name, module_name, project_type)

    for script_name, script_command in project_scripts.items():
        scripts[script_name] = script_command
        logger.info("Adding script", script=script_name, command=script_command)

    # Update description
    poetry_config = config["tool"]["poetry"]
    if (
        poetry_config.get("description")
        == "Enterprise-grade Python automation component"
    ):
        new_description = generate_project_description(project_name, project_type)
        poetry_config["description"] = new_description
        logger.info("Updated description", description=new_description)

    # Update keywords based on project type
    keywords = poetry_config.setdefault(
        "keywords", ["automation", "enterprise", "oracle", "integration"]
    )
    type_keywords = {
        "singer_tap": ["singer", "tap", "etl", "data-extraction"],
        "api_integration": ["api", "rest", "http", "integration"],
        "database": ["database", "sql", "oracle", "data"],
        "ldap": ["ldap", "directory", "authentication", "migration"],
        "meltano": ["meltano", "elt", "data-platform", "orchestration"],
    }

    project_keywords = type_keywords.get(project_type, [])
    for keyword in project_keywords:
        if keyword not in keywords:
            keywords.append(keyword)

    if dry_run:
        logger.info("Dry run completed - no changes made")
        return True

    # Write updated configuration
    try:
        # Convert back to TOML format (simplified approach)
        toml_content = generate_toml_content(config)

        # Backup original file
        backup_file = pyproject_file.with_suffix(".toml.backup")
        pyproject_file.rename(backup_file)
        logger.info("Created backup", backup=backup_file)

        # Write updated file
        with open(pyproject_file, "w", encoding="utf-8") as f:
            f.write(toml_content)

        logger.info("Successfully customized project", project=project_name)
        return True

    except Exception as e:
        logger.error("Failed to write customized pyproject.toml", error=str(e))
        return False


def generate_toml_content(config: dict[str, Any]) -> str:
    """Generate TOML content from configuration dictionary."""
    # This is a simplified TOML generator for the specific structure we need
    # In a production environment, you might want to use a proper TOML library

    lines = []

    # Build system
    if "build-system" in config:
        lines.append("[build-system]")
        build_system = config["build-system"]
        if "requires" in build_system:
            requires = ", ".join(f'"{req}"' for req in build_system["requires"])
            lines.append(f"requires = [{requires}]")
        if "build-backend" in build_system:
            lines.append(f'build-backend = "{build_system["build-backend"]}"')
        lines.append("")

    # Tool configuration
    if "tool" in config and "poetry" in config["tool"]:
        lines.append("[tool.poetry]")
        poetry = config["tool"]["poetry"]

        # Basic metadata
        for key in ["name", "version", "description"]:
            if key in poetry:
                lines.append(f'{key} = "{poetry[key]}"')

        # Authors
        if "authors" in poetry:
            authors = ", ".join(f'"{author}"' for author in poetry["authors"])
            lines.append(f"authors = [{authors}]")

        # Other metadata
        for key in ["license", "readme", "homepage", "repository", "documentation"]:
            if key in poetry:
                lines.append(f'{key} = "{poetry[key]}"')

        # Keywords
        if "keywords" in poetry:
            keywords = ", ".join(f'"{kw}"' for kw in poetry["keywords"])
            lines.append(f"keywords = [{keywords}]")

        # Classifiers
        if "classifiers" in poetry:
            lines.append("classifiers = [")
            for classifier in poetry["classifiers"]:
                lines.append(f'    "{classifier}",')
            lines.append("]")

        # Packages
        if "packages" in poetry:
            lines.append("packages = [")
            for package in poetry["packages"]:
                if isinstance(package, dict):
                    include = package.get("include", "")
                    from_dir = package.get("from", "")
                    lines.append(
                        f'    {{ include = "{include}", from = "{from_dir}" }},'
                    )
            lines.append("]")

        lines.append("")

        # Dependencies
        if "dependencies" in poetry:
            lines.append("[tool.poetry.dependencies]")
            for dep, version in poetry["dependencies"].items():
                lines.append(f'{dep} = "{version}"')
            lines.append("")

        # Scripts
        if "scripts" in poetry:
            lines.append("[tool.poetry.scripts]")
            for script, command in poetry["scripts"].items():
                lines.append(f'{script} = "{command}"')
            lines.append("")

    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Customize pyproject.toml template for specific project requirements"
    )
    parser.add_argument("project_path", type=Path, help="Path to the project directory")
    parser.add_argument(
        "--project-name", help="Project name (defaults to directory name)"
    )
    parser.add_argument(
        "--module-name",
        help="Python module name (defaults to project name with hyphens replaced by underscores)",
    )
    parser.add_argument(
        "--project-type",
        choices=list(PROJECT_CONFIGURATIONS.keys()),
        help="Project type for specific configurations",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    log_level = "DEBUG" if args.verbose else "INFO"
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        level=log_level,
    )

    # Validate project path
    if not args.project_path.exists():
        logger.error("Project path does not exist", path=args.project_path)
        return 1

    if not args.project_path.is_dir():
        logger.error("Project path is not a directory", path=args.project_path)
        return 1

    # Determine project and module names
    project_name = args.project_name or args.project_path.name
    module_name = args.module_name or project_name.replace("-", "_")

    logger.info(
        "Starting project customization",
        project_path=args.project_path,
        project_name=project_name,
        module_name=module_name,
        project_type=args.project_type,
        dry_run=args.dry_run,
    )

    # Customize the project
    success = customize_pyproject_for_project(
        args.project_path, project_name, module_name, args.project_type, args.dry_run
    )

    if success:
        logger.info("Project customization completed successfully")
        return 0
    logger.error("Project customization failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
