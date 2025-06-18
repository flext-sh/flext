"""
Configuration management commands.
"""

import click
from flx_cli.utils import handle_errors


@click.group()
@click.pass_context
def config(ctx):
    """Manage configuration."""
    pass


@config.command()
@click.argument("key")
@click.pass_context
@handle_errors
async def get(ctx, key):
    """Get a configuration value."""
    console = ctx.obj["console"]

    # TODO: Implement config get
    console.print("[yellow]Config management not yet implemented[/yellow]")


@config.command()
@click.argument("key")
@click.argument("value")
@click.pass_context
@handle_errors
async def set(ctx, key, value):
    """Set a configuration value."""
    console = ctx.obj["console"]

    # TODO: Implement config set
    console.print("[yellow]Config management not yet implemented[/yellow]")


@config.command()
@click.pass_context
@handle_errors
async def list(ctx):
    """List all configuration values."""
    console = ctx.obj["console"]

    # TODO: Implement config list
    console.print("[yellow]Config management not yet implemented[/yellow]")
