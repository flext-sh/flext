"""Unified CLI Pattern for FLEXT Projects using Click and Rich."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import click
from flext_core import get_logger
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
        """Setup logging configuration."""
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


def with_config(f: Any) -> Any:
    """Decorator to add config options to commands."""
    f = click.option("--verbose", is_flag=True, help="Enable verbose output")(f)
    f = click.option("--debug", is_flag=True, help="Enable debug mode")(f)
    return click.option("--quiet", is_flag=True, help="Suppress non-error output")(f)


def with_output_format(f: Any) -> Any:
    """Decorator to add output format options."""
    return click.option(
        "--output-format",
        type=click.Choice(["table", "json", "yaml"]),
        default="table",
        help="Output format",
    )(f)
