"""Main entry point for Oracle OIC extension."""

from __future__ import annotations

import structlog
import typer
from meltano.edk.logging import default_logging_config, parse_log_level
from oracle_oic_ext.extension import OracleOICExtension

APP_NAME = "oracle_oic_extension"

default_logging_config(level=parse_log_level())

log = structlog.get_logger(APP_NAME)

ext = OracleOICExtension()

app = typer.Typer(
    name=APP_NAME,
    help="Oracle Integration Cloud extension for Meltano.",
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    log_level: str = typer.Option("INFO", envvar="LOG_LEVEL"),
    log_json: bool = typer.Option(False, envvar="LOG_JSON"),
) -> None:
    """Oracle OIC Extension for lifecycle management and monitoring."""
    if ctx.invoked_subcommand is None:
        # No subcommand was invoked, show help
        typer.echo(ctx.get_help())


@app.command()
def initialize(
    ctx: typer.Context,
    force: bool = typer.Option(False, help="Force initialization"),
) -> None:
    """Initialize the Oracle OIC extension."""
    try:
        # Extension initialization logic
        log.info("Initializing Oracle OIC extension...")
        ext.initialize(force)
        log.info("Extension initialized successfully")
    except Exception as e:
        log.error(f"Failed to initialize extension: {e}")
        raise typer.Exit(1)


@app.command()
def invoke(
    ctx: typer.Context,
    command_args: list[str] = typer.Argument(None, help="Command and arguments"),
) -> None:
    """Invoke an Oracle OIC extension command."""
    if not command_args:
        typer.echo("No command provided. Use --help for available commands.")
        raise typer.Exit(1)

    command = command_args[0] if command_args else None
    args = command_args[1:] if len(command_args) > 1 else []

    try:
        ext.invoke(command, *args)
    except Exception as e:
        log.error(f"Command failed: {e}")
        raise typer.Exit(1)


@app.command()
def describe(
    ctx: typer.Context,
    output_format: str = typer.Option("json", help="Output format (json or text)"),
) -> None:
    """Describe the capabilities of the Oracle OIC extension."""
    description = ext.describe()

    if output_format == "json":
        # Output as JSON
        import json

        typer.echo(json.dumps(description.model_dump(), indent=2))
    else:
        # Output as text
        typer.echo("Oracle OIC Extension Commands:")
        typer.echo("")
        for cmd in description.commands:
            typer.echo(f"  {cmd.name}")
            typer.echo(f"    {cmd.description}")
            if cmd.args:
                typer.echo(f"    Usage: {cmd.name} {cmd.args}")
            typer.echo("")


if __name__ == "__main__":
    app()
