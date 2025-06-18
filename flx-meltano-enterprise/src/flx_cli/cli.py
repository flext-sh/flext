"""
FLX Command Line Interface.

Main CLI entry point using Click framework.
"""

import asyncio
import sys

import click
from flx_cli import __version__
from flx_cli.client import FlxGrpcClient
from flx_cli.commands import config, monitor, pipeline, plugin, system
from rich.console import Console

# Rich console for beautiful output
console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="flx")
@click.option("--host", default="localhost", help="FLX daemon host")
@click.option("--port", default=50051, type=int, help="FLX daemon port")
@click.option("--token", envvar="FLX_TOKEN", help="Authentication token")
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.pass_context
def cli(ctx, host, port, token, debug):
    """
    FLX Enterprise Data Platform CLI.

    Manage pipelines, plugins, and monitor your data platform.
    """
    # Ensure context object
    ctx.ensure_object(dict)

    # Create client
    ctx.obj["client"] = FlxGrpcClient(host, port, token)
    ctx.obj["console"] = console
    ctx.obj["debug"] = debug

    if debug:
        console.print("[dim]Debug mode enabled[/dim]")
        console.print(f"[dim]Connecting to {host}:{port}[/dim]")


# Add command groups
cli.add_command(pipeline.pipeline)
cli.add_command(plugin.plugin)
cli.add_command(config.config)
cli.add_command(monitor.monitor)
cli.add_command(system.system)


@cli.command()
@click.pass_context
def info(ctx):
    """Show FLX system information."""
    client = ctx.obj["client"]

    with console.status("[bold green]Getting system info..."):
        try:
            info = asyncio.run(client.get_system_info())

            console.print("\n[bold]FLX System Information[/bold]")
            console.print(f"Version: {info.version}")
            console.print(f"Environment: {info.environment}")
            console.print(f"Python: {info.python_version}")
            console.print(f"Meltano: {info.meltano_version}")

            console.print("\n[bold]Features:[/bold]")
            for feature, enabled in info.features.items():
                status = "[green]✓[/green]" if enabled == "True" else "[red]✗[/red]"
                console.print(f"  {status} {feature}")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            if ctx.obj["debug"]:
                console.print_exception()
            sys.exit(1)


@cli.command()
@click.pass_context
def health(ctx):
    """Check system health."""
    client = ctx.obj["client"]

    with console.status("[bold green]Checking health..."):
        try:
            health = asyncio.run(client.health_check())

            if health.healthy:
                console.print("[green]✓[/green] System is healthy")
            else:
                console.print("[red]✗[/red] System is unhealthy")

            console.print("\n[bold]Component Status:[/bold]")
            for name, component in health.components.items():
                if component.healthy:
                    console.print(f"  [green]✓[/green] {name}: {component.message}")
                else:
                    console.print(f"  [red]✗[/red] {name}: {component.message}")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            if ctx.obj["debug"]:
                console.print_exception()
            sys.exit(1)


def main():
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
