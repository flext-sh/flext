#!/usr/bin/env python3
"""
FLX-Meltano Enterprise Demo Script.

This script demonstrates the key features of the FLX platform.
"""

import subprocess
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

console = Console()


def print_banner():
    """Print welcome banner."""
    banner = """
    ███████╗██╗     ██╗  ██╗
    ██╔════╝██║     ╚██╗██╔╝
    █████╗  ██║      ╚███╔╝
    ██╔══╝  ██║      ██╔██╗
    ██║     ███████╗██╔╝ ██╗
    ╚═╝     ╚══════╝╚═╝  ╚═╝

    Enterprise Data Platform
    """
    console.print(
        Panel(banner, title="FLX-Meltano Enterprise", border_style="bold blue")
    )


def check_environment():
    """Check if environment is ready."""
    console.print("\n[bold yellow]Checking environment...[/bold yellow]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Check Python
        task = progress.add_task("Checking Python version...", total=1)
        time.sleep(0.5)
        python_version = sys.version.split()[0]
        progress.update(task, completed=1)
        console.print(f"✅ Python {python_version}")

        # Check venv
        task = progress.add_task("Checking virtual environment...", total=1)
        time.sleep(0.5)
        in_venv = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )
        progress.update(task, completed=1)
        if in_venv:
            console.print("✅ Virtual environment active")
        else:
            console.print("⚠️  Not in virtual environment")

        # Check imports
        task = progress.add_task("Checking FLX modules...", total=1)
        time.sleep(0.5)
        try:
            import flx_api
            import flx_cli
            import flx_web

            import flx

            progress.update(task, completed=1)
            console.print("✅ All FLX modules found")
        except ImportError as e:
            progress.update(task, completed=1)
            console.print(f"❌ Import error: {e}")


def demo_cli():
    """Demo CLI functionality."""
    console.print("\n[bold cyan]CLI Demo[/bold cyan]")
    console.print("The FLX CLI provides powerful pipeline management capabilities.\n")

    if Confirm.ask("Run CLI demo?"):
        console.print("[dim]$ python test_cli_simple.py status[/dim]")
        subprocess.run([sys.executable, "test_cli_simple.py", "status"])

        console.print("\n[dim]$ python test_cli_simple.py list[/dim]")
        subprocess.run([sys.executable, "test_cli_simple.py", "list"])


def demo_api():
    """Demo API functionality."""
    console.print("\n[bold cyan]API Demo[/bold cyan]")
    console.print("The FLX API provides RESTful endpoints for programmatic access.\n")

    console.print("Example endpoints:")
    console.print("  • GET  /health - Health check")
    console.print("  • GET  /api/pipelines - List pipelines")
    console.print("  • POST /api/pipelines - Create pipeline")
    console.print("  • GET  /api/executions - List executions")

    if Confirm.ask("\nStart test API server?"):
        console.print("\n[yellow]Starting API server on http://localhost:8001[/yellow]")
        console.print(
            "[yellow]Visit http://localhost:8001/docs for interactive API docs[/yellow]"
        )
        console.print("[dim]Press Ctrl+C to stop the server[/dim]\n")

        try:
            subprocess.run([sys.executable, "test_api_simple.py"])
        except KeyboardInterrupt:
            console.print("\n[red]API server stopped[/red]")


def show_architecture():
    """Show system architecture."""
    console.print("\n[bold cyan]System Architecture[/bold cyan]")

    architecture = """
    ┌─────────────────────────────────────────────────────────────┐
    │                        User Interfaces                       │
    ├──────────────┬────────────────┬────────────────┬───────────┤
    │  Django Web  │  FastAPI REST  │   Click CLI    │  Meltano  │
    ├──────────────┴────────────────┴────────────────┴───────────┤
    │                      gRPC Service Layer                      │
    ├─────────────────────────────────────────────────────────────┤
    │                       FLX Core Daemon                        │
    ├──────────────┬────────────────┬────────────────┬───────────┤
    │  Event Bus   │ Health Monitor │ Metrics Collect│  Meltano  │
    ├──────────────┴────────────────┴────────────────┴───────────┤
    │                    Infrastructure Layer                      │
    ├──────────────┬────────────────┬────────────────┬───────────┤
    │  PostgreSQL  │     Redis      │   Prometheus   │  Grafana  │
    └──────────────┴────────────────┴────────────────┴───────────┘
    """
    console.print(Panel(architecture, title="Architecture", border_style="green"))


def show_features():
    """Show key features."""
    console.print("\n[bold cyan]Key Features[/bold cyan]")

    features = [
        ("🚀", "High Performance", "Built with async Python and gRPC"),
        ("🔌", "Extensible", "Plugin architecture based on Meltano"),
        ("📊", "Real-time Monitoring", "Prometheus metrics and health checks"),
        ("🔒", "Secure", "JWT authentication and role-based access"),
        ("📈", "Scalable", "Kubernetes-ready with horizontal scaling"),
        ("🛠", "Developer Friendly", "Rich CLI and comprehensive API"),
    ]

    for icon, title, desc in features:
        console.print(f"{icon} [bold]{title}[/bold] - {desc}")


def main():
    """Run the demo."""
    print_banner()

    # Check environment
    check_environment()

    # Show architecture
    show_architecture()

    # Show features
    show_features()

    # Interactive demos
    console.print("\n[bold magenta]Interactive Demos[/bold magenta]")

    while True:
        console.print("\nWhat would you like to explore?")
        console.print("1. CLI Demo")
        console.print("2. API Demo")
        console.print("3. Exit")

        choice = Prompt.ask("Select an option", choices=["1", "2", "3"], default="3")

        if choice == "1":
            demo_cli()
        elif choice == "2":
            demo_api()
        else:
            break

    console.print(
        "\n[bold green]Thank you for exploring FLX-Meltano Enterprise![/bold green]"
    )
    console.print("For more information, see the documentation.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Demo interrupted[/red]")
        sys.exit(0)
