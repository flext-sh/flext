#!/usr/bin/env python3
"""FLEXT Script Runner - Executor centralizado de scripts.

Este script serve como ponto de entrada único para execução de todos os scripts
do workspace FLEXT usando flext_tools para máxima reutilização.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from scripts.core.script_registry import ScriptRegistry

from flext_tools import Colors, print_colored
from flext_tools.core.script_base import FlextScript, ScriptMetadata


class ScriptRunner(FlextScript):
    """Executor centralizado de scripts FLEXT."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="script_runner",
            description="Executor centralizado para todos os scripts FLEXT",
            category="core",
            version="2.0.0",
        )

    def validate_preconditions(self) -> bool:
        """Validate preconditions."""
        scripts_dir = Path(__file__).parent.parent

        if not scripts_dir.exists():
            print_colored("❌ Scripts directory not found", Colors.RED)
            return False

        print_colored("✅ Scripts directory found", Colors.GREEN)
        return True

    def execute_main_logic(self, **kwargs: object) -> bool:
        """Execute script runner logic."""
        try:
            list_scripts = kwargs.get("list", False)
            script_name = kwargs.get("script_name")

            print_colored("🚀 FLEXT SCRIPT RUNNER", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Import script registry (lazy import)
            try:
                registry = ScriptRegistry()

                if list_scripts:
                    self._list_all_scripts(registry)
                    return True

                if script_name:
                    return self._run_script(registry, script_name, kwargs)
                print_colored(
                    "❌ No script specified. Use --list to see available scripts.",
                    Colors.RED,
                )
                return False

            except ImportError as e:
                print_colored(f"❌ Failed to import script registry: {e}", Colors.RED)
                return False

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error in script runner: {e}", Colors.RED)
            return False

    def _list_all_scripts(self, registry: object) -> None:
        """List all available scripts."""
        print_colored("📋 AVAILABLE SCRIPTS", Colors.BLUE)
        print_colored("=" * 40, Colors.BLUE)

        scripts = registry.list_scripts()

        if not scripts:
            print_colored("No scripts found", Colors.YELLOW)
            return

        # Group by category
        by_category: dict[str, list[Any]] = {}
        for script in scripts:
            category = (
                script.category.value
                if hasattr(script.category, "value")
                else str(script.category)
            )
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(script)

        # Print by category
        for category, category_scripts in sorted(by_category.items()):
            print_colored(f"\n📁 {category.title()}:", Colors.CYAN)
            for script in sorted(category_scripts, key=lambda s: s.name):
                priority = (
                    script.priority.value
                    if hasattr(script.priority, "value")
                    else str(script.priority)
                )
                print(f"  • {script.name} ({priority}) - {script.description}")

        print_colored(f"\n📊 Total: {len(scripts)} scripts", Colors.GREEN)

    def _run_script(
        self,
        registry: object,
        script_name: str,
    ) -> bool:
        """Run a specific script."""
        script_metadata = registry.get_script(script_name)

        if not script_metadata:
            print_colored(f"❌ Script '{script_name}' not found", Colors.RED)
            print_colored("Use --list to see available scripts", Colors.YELLOW)
            return False

        print_colored(f"🎯 Running script: {script_name}", Colors.BLUE)
        print_colored(f"📋 Description: {script_metadata.description}", Colors.CYAN)

        try:
            # Import and run the script

            spec = importlib.util.spec_from_file_location(
                f"script_{script_name}",
                script_metadata.file_path,
            )

            if not spec or not spec.loader:
                print_colored(f"❌ Failed to load script: {script_name}", Colors.RED)
                return False

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find and run main function
            if hasattr(module, "main"):
                result = module.main()
                return bool(result == 0)
            print_colored(f"❌ Script {script_name} has no main() function", Colors.RED)
            return False

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error running script {script_name}: {e}", Colors.RED)
            return False

    def create_parser(self) -> object:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--list",
            action="store_true",
            help="List all available scripts",
        )

        parser.add_argument("script_name", nargs="?", help="Name of script to run")

        return parser

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = ScriptRunner()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
