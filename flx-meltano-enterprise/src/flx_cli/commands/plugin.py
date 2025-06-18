"""
Plugin management commands.
"""

import click
from flx_cli.utils import handle_errors
from rich.table import Table


@click.group()
@click.pass_context
def plugin(ctx):
    """Manage plugins."""
    pass


@plugin.command()
@click.option(
    "--type",
    "-t",
    type=click.Choice(
        ["extractor", "loader", "transformer", "orchestrator", "utility"]
    ),
    help="Filter by plugin type",
)
@click.option("--installed", is_flag=True, help="Show only installed plugins")
@click.pass_context
@handle_errors
async def list(ctx, type, installed):
    """List available plugins."""
    client = ctx.obj["client"]
    console = ctx.obj["console"]

    with console.status("[bold green]Loading plugins..."):
        plugins = await client.list_plugins(
            plugin_type=type,
            installed_only=installed,
        )

    if not plugins:
        console.print("[yellow]No plugins found[/yellow]")
        return

    # Group by type
    by_type = {}
    for p in plugins:
        type_name = p.type.name.replace("PLUGIN_TYPE_", "").title()
        if type_name not in by_type:
            by_type[type_name] = []
        by_type[type_name].append(p)

    for type_name, type_plugins in by_type.items():
        table = Table(title=f"{type_name}s")
        table.add_column("Name", style="cyan")
        table.add_column("Variant", style="magenta")
        table.add_column("Version", style="green")
        table.add_column("Installed", style="yellow")
        table.add_column("Description", style="dim", max_width=50)

        for p in type_plugins:
            table.add_row(
                p.name,
                p.variant or "-",
                p.version or "-",
                "[green]✓[/green]" if p.installed else "[red]✗[/red]",
                p.description or "",
            )

        console.print(table)
        console.print()


@plugin.command()
@click.argument("name")
@click.option(
    "--type",
    "-t",
    required=True,
    type=click.Choice(
        ["extractor", "loader", "transformer", "orchestrator", "utility"]
    ),
    help="Plugin type",
)
@click.option("--variant", "-v", help="Plugin variant")
@click.pass_context
@handle_errors
async def install(ctx, name, type, variant):
    """Install a plugin."""
    client = ctx.obj["client"]
    console = ctx.obj["console"]

    with console.status(f"[bold green]Installing {type} '{name}'..."):
        await client.install_plugin(
            name=name,
            plugin_type=type,
            variant=variant,
        )

    console.print(f"[green]✓[/green] Plugin '{name}' installed successfully!")


@plugin.command()
@click.argument("name")
@click.option(
    "--type",
    "-t",
    required=True,
    type=click.Choice(
        ["extractor", "loader", "transformer", "orchestrator", "utility"]
    ),
    help="Plugin type",
)
@click.confirmation_option(prompt="Are you sure you want to uninstall this plugin?")
@click.pass_context
@handle_errors
async def uninstall(ctx, name, type):
    """Uninstall a plugin."""
    client = ctx.obj["client"]
    console = ctx.obj["console"]

    with console.status(f"[bold green]Uninstalling {type} '{name}'..."):
        await client.uninstall_plugin(
            name=name,
            plugin_type=type,
        )

    console.print(f"[green]✓[/green] Plugin '{name}' uninstalled successfully!")
