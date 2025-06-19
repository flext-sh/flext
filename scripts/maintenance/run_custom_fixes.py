#!/usr/bin/env python3
"""
Run custom fix modules independently.

This script allows running individual custom fix modules with full control
over dry-run and confirmation modes.
"""

import argparse
import sys
from pathlib import Path

# Import all custom modules
from modules import (
    MODULE_REGISTRY,
)
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def list_modules():
    """List all available custom fix modules."""
    table = Table(title="Available Custom Fix Modules")
    table.add_column("Module", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Description")

    for name, module_class in MODULE_REGISTRY.items():
        instance = module_class()
        table.add_row(
            name,
            instance.category,
            instance.description
        )

    console.print(table)


def run_module(
    module_name: str,
    targets: list[Path],
    dry_run: bool = True,
    interactive: bool = False,
    verbose: bool = False
) -> int:
    """Run a specific module on targets."""

    # Get module class
    module_class = MODULE_REGISTRY.get(module_name)
    if not module_class:
        console.print(f"[red]Error: Unknown module '{module_name}'[/red]")
        console.print("Use --list to see available modules")
        return 1

    # Create module instance
    module = module_class(
        dry_run=dry_run,
        interactive=interactive,
        verbose=verbose
    )

    # Display header
    console.print(Panel.fit(
        f"[bold cyan]{module.name}[/bold cyan]\n"
        f"Category: {module.category}\n"
        f"Mode: {'DRY RUN' if dry_run else 'APPLY FIXES'}\n"
        f"Interactive: {'Yes' if interactive else 'No'}",
        title=f"🔧 Running {module_name}",
        border_style="cyan"
    ))

    # Process all targets
    all_results = []

    for target in targets:
        if target.is_file():
            # Single file
            console.print(f"\n📄 Processing file: {target}")
            result = module.process_file(target)
            all_results.append(result)

            if result.diff and verbose:
                console.print("\n[yellow]Changes:[/yellow]")
                console.print(result.diff)

        else:
            # Directory
            console.print(f"\n📁 Processing directory: {target}")
            results = module.process_directory(target)
            all_results.extend(results)

    # Display summary
    summary = module.get_summary(all_results)

    console.print("\n" + "=" * 60)
    console.print("[bold]Summary:[/bold]")
    console.print(f"Total files: {summary['total_files']}")
    console.print(f"Successful: {summary['successful_files']}")
    console.print(f"Failed: {summary['failed_files']}")
    console.print(f"Issues found: {summary['total_issues']}")
    console.print(f"Issues fixed: {summary['total_fixed']}")

    if summary['errors']:
        console.print("\n[red]Errors:[/red]")
        for error in summary['errors'][:5]:
            console.print(f"  • {error}")

    # Return exit code
    return 0 if summary['failed_files'] == 0 else 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run custom fix modules for Python code maintenance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available modules
  python run_custom_fixes.py --list

  # Run type annotation fixer in dry-run mode
  python run_custom_fixes.py type_annotations --target src/

  # Apply logging fixes interactively
  python run_custom_fixes.py logging_patterns --target src/ --apply --interactive

  # Fix asyncio patterns with verbose output
  python run_custom_fixes.py asyncio_patterns --target . --verbose

  # Run multiple modules
  python run_custom_fixes.py type_annotations logging_patterns --target src/ --apply
        """
    )

    parser.add_argument(
        "modules",
        nargs="*",
        help="Module(s) to run"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available modules"
    )
    parser.add_argument(
        "--target", "-t",
        action="append",
        dest="targets",
        help="Target file or directory (can be specified multiple times)"
    )
    parser.add_argument(
        "--apply", "-a",
        action="store_true",
        help="Apply fixes (default is dry-run)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode - confirm each fix"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Handle --list
    if args.list:
        list_modules()
        return 0

    # Validate arguments
    if not args.modules:
        console.print("[red]Error: No modules specified[/red]")
        console.print("Use --list to see available modules")
        return 1

    if not args.targets:
        # Default to current directory
        args.targets = ["."]

    # Convert targets to Path objects
    targets = []
    for target in args.targets:
        path = Path(target)
        if not path.exists():
            console.print(f"[red]Error: Target not found: {target}[/red]")
            return 1
        targets.append(path)

    # Run each module
    exit_code = 0
    for module_name in args.modules:
        result = run_module(
            module_name,
            targets,
            dry_run=not args.apply,
            interactive=args.interactive,
            verbose=args.verbose
        )
        if result != 0:
            exit_code = result

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
