"""FLEXT CLI - Unified command line interface for the workspace."""

from pathlib import Path

import click

from flext.dev import DevToolsManager
from flext.workspace import WorkspaceManager
from flext.workspace.cli import cli as workspace_cli


@click.group()
@click.option(
    "--workspace",
    type=click.Path(exists=True),
    help="Workspace root path",
)
@click.pass_context
def main(ctx: click.Context, workspace: str | None) -> None:
    """FLEXT - Multi-Project Workspace Coordinator for Enterprise Data Integration."""
    ctx.ensure_object(dict)
    ctx.obj["workspace"] = Path(workspace) if workspace else None


@main.command()
@click.pass_context
def dev(ctx: click.Context) -> None:
    """Development tools for the workspace."""
    workspace = ctx.obj.get("workspace")
    dev_tools = DevToolsManager(workspace)
    click.echo("Running development tools...")
    dev_tools.run_tests()


@main.command()
@click.pass_context
def test(ctx: click.Context) -> None:
    """Run tests for all projects."""
    workspace = ctx.obj.get("workspace")
    dev_tools = DevToolsManager(workspace)
    exit_code = dev_tools.run_tests()
    if exit_code == 0:
        click.echo("✅ All tests passed!")
    else:
        click.echo("❌ Some tests failed!")
        ctx.exit(exit_code)


@main.command()
@click.pass_context
def lint(ctx: click.Context) -> None:
    """Run linting for all projects."""
    workspace = ctx.obj.get("workspace")
    dev_tools = DevToolsManager(workspace)
    exit_code = dev_tools.lint_all()
    if exit_code == 0:
        click.echo("✅ Linting passed!")
    else:
        click.echo("❌ Linting failed!")
        ctx.exit(exit_code)


@main.command("format")
@click.pass_context
def format_code(ctx: click.Context) -> None:
    """Format all projects."""
    workspace = ctx.obj.get("workspace")
    dev_tools = DevToolsManager(workspace)
    exit_code = dev_tools.format_all()
    if exit_code == 0:
        click.echo("✅ Formatting completed!")
    else:
        click.echo("❌ Formatting failed!")
        ctx.exit(exit_code)


@main.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """Show workspace information."""
    workspace = ctx.obj.get("workspace")
    workspace_manager = WorkspaceManager(workspace)

    click.echo(f"Workspace root: {workspace_manager.workspace_root}")
    click.echo(f"Projects found: {len(workspace_manager.projects)}")

    for project in workspace_manager.list_projects():
        click.echo(f"  - {project}")


# Add workspace management commands as a group
main.add_command(workspace_cli, name="workspace")


if __name__ == "__main__":
    main()
