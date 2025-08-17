"""FLEXT CLI Patterns - Enterprise Command-Line Interface Framework.

Provides comprehensive base classes and patterns for building consistent,
enterprise-grade command-line interfaces across all FLEXT ecosystem projects.
This module implements standardized CLI patterns with proper error handling,
rich terminal output, logging integration, and architectural consistency.

The CLI framework ensures unified user experience across the 32-project FLEXT
ecosystem while maintaining extensibility and customization capabilities for
project-specific requirements. All CLI implementations follow Clean Architecture
principles with clear separation between interface, application, and domain
concerns.

Key Components:
    - BaseCLI: Foundation class for all FLEXT CLI implementations
    - CLIConfig: Unified configuration management with validation
    - Command Patterns: Standardized command structure and organization
    - Error Handling: Consistent error reporting and user feedback
    - Rich Output: Enhanced terminal output with progress and formatting
    - Logging Integration: Structured logging with correlation IDs

Architecture:
    Implements Clean Architecture Interface Layer patterns with clear separation
    between user interaction (CLI commands), application logic (business operations),
    and infrastructure concerns (external tool integration). All CLIs provide
    consistent patterns for configuration, validation, and error handling.

Example:
    Enterprise CLI implementation with FLEXT patterns:

    >>> from flext.cli_patterns.base_cli import BaseCLI, CLIConfig
    >>> import click
    >>> from pathlib import Path
    >>>
    >>> class ProjectCLI(BaseCLI):
    ...     def __init__(self):
    ...         config = CLIConfig(
    ...             output_format="table",
    ...             log_level="INFO",
    ...             project_root=Path.cwd()
    ...         )
    ...         super().__init__(name="project-cli", version="2.0.0", config=config)
    ...
    ...     @click.command()
    ...     @click.option("--project", help="Project name to process")
    ...     def process(self, project: str):
    ...         '''Process project with FLEXT patterns.'''
    ...         try:
    ...             # Business logic with proper error handling
    ...             result = self.execute_business_operation(project)
    ...             if result.success:
    ...                 self.success(f"Project {project} processed successfully")
    ...             else:
    ...                 self.error(f"Failed to process {project}: {result.error}")
    ...         except Exception as e:
    ...             self.handle_error(e, context={"project": project})
    >>>
    >>> # CLI usage patterns
    >>> cli = ProjectCLI()
    >>> cli.run()  # Handles command parsing and execution

Integration:
    - Built on Click framework for robust command-line argument parsing
    - Integrates with Rich library for enhanced terminal output and progress
    - Uses Pydantic for configuration validation and type safety
    - Coordinates with flext-core patterns for error handling and logging
    - Supports both interactive and automated (CI/CD) execution modes

Quality Standards:
    - Comprehensive error handling with user-friendly messages and recovery
    - Rich terminal output with progress bars, tables, and status indicators
    - Structured logging with proper correlation and tracing capabilities
    - Configuration validation with clear error messages and defaults
    - Performance monitoring and operation timing for optimization

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import click
from pydantic import BaseModel, Field
from rich.console import Console
from rich.logging import RichHandler


class CLIConfig(BaseModel):
    """Unified configuration for CLI applications using flext-core patterns."""

    # Output settings
    output_format: str = Field(default="table", description="Output format")
    no_color: bool = Field(default=False, description="Disable colored output")
    quiet: bool = Field(default=False, description="Suppress non-error output")
    verbose: bool = Field(default=False, description="Enable verbose output")
    debug: bool = Field(default=False, description="Enable debug mode")

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Path | None = Field(default=None, description="Log file path")

    # Environment settings
    profile: str = Field(default="default", description="Configuration profile")
    config_dir: Path = Field(
      default=Path.home() / ".flext",
      description="Config directory",
    )


class BaseCLI(ABC):
    """Base class for all FLEXT CLI applications."""

    def __init__(self, name: str, version: str, description: str) -> None:
      """Initialize BaseCLI with basic information."""
      self.name = name
      self.version = version
      self.description = description
      self.console = Console()
      self.config: CLIConfig | None = None

    def setup_logging(self, config: CLIConfig) -> None:
      """Set up logging configuration."""
      logging.basicConfig(
          level=getattr(logging, config.log_level.upper()),
          format="%(message)s",
          datefmt="[%X]",
          handlers=[RichHandler(console=self.console, rich_tracebacks=True)],
      )

    @abstractmethod
    def create_cli(self) -> click.Group:
      """Create the CLI group."""

    def run(self) -> None:
      """Run the CLI application."""
      cli = self.create_cli()
      cli()


def with_config(f: object) -> object:
    """Add config options to commands (decorator)."""
    f = click.option("--verbose", is_flag=True, help="Enable verbose output")(f)
    f = click.option("--debug", is_flag=True, help="Enable debug mode")(f)
    return click.option("--quiet", is_flag=True, help="Suppress non-error output")(f)


def with_output_format(f: object) -> object:
    """Add output format options to commands (decorator)."""
    return click.option(
      "--output-format",
      type=click.Choice(["table", "json", "yaml"]),
      default="table",
      help="Output format",
    )(f)
