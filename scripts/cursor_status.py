#!/usr/bin/env python3
"""FLEXT Cursor Agent Status Monitor.

Shows the current status of FLEXT automation in Cursor Agent.
Provides transparency into what automation is active and working.

Usage:
    python3 scripts/cursor_status.py [--detailed] [--check-health]
"""

from __future__ import annotations

import argparse
import json
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


# FLEXT result pattern
class Result[T]:
    """A result type that can contain either a value or an error."""

    def __init__(self, value: T | None = None, error: str | None = None) -> None:
        """Initialize a Result with either a value or an error."""
        self.value = value
        self.error = error

    @property
    def is_success(self) -> bool:
        """Return True if the result contains a value (no error)."""
        return self.error is None

    @property
    def is_failure(self) -> bool:
        """Return True if the result contains an error."""
        return self.error is not None

    @classmethod
    def ok(cls, value: T) -> Result[T]:
        """Create a successful result with the given value."""
        return cls(value=value)

    @classmethod
    def err(cls, error: str) -> Result[T]:
        """Create a failed result with the given error message."""
        return cls(error=error)


class CursorStatusMonitor:
    """Monitor FLEXT Cursor Agent automation status."""

    def __init__(self, project_root: Path) -> None:
        """Initialize the Cursor status monitor with project root."""
        self.project_root = project_root
        self.cursor_dir = project_root / ".cursor"

    def get_manifest_info(self) -> dict[str, Any]:
        """Get manifest information."""
        manifest_file = self.cursor_dir / "manifest.json"
        if not manifest_file.exists():
            return {}

        try:
            with Path(manifest_file).open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_config_info(self) -> dict[str, Any]:
        """Get configuration information."""
        config_file = self.cursor_dir / "config.json"
        if not config_file.exists():
            return {}

        try:
            with Path(config_file).open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def check_file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.project_root / path
        return path.exists()

    def check_automation_script(self) -> dict[str, Any]:
        """Check automation script status."""
        script_path = self.project_root / "cursor-agent-automation.py"

        status = {
            "exists": script_path.exists(),
            "executable": False,
            "working": False,
        }

        if status["exists"]:
            # Check if executable
            mode = script_path.stat().st_mode
            status["executable"] = bool(mode & stat.S_IEXEC)

            # Test if it works
            try:
                result = subprocess.run(
                    [sys.executable, str(script_path), "skills"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                status["working"] = result.returncode == 0
                if result.returncode != 0:
                    status["error"] = result.stderr.strip()
            except Exception as e:
                status["error"] = str(e)

        return status

    def check_git_hooks(self) -> dict[str, Any]:
        """Check Git hooks status."""
        hooks_dir = self.project_root / ".git" / "hooks"
        cursor_hooks_dir = self.cursor_dir / "hooks"

        status = {
            "git_hooks_dir": hooks_dir.exists(),
            "cursor_hooks_dir": cursor_hooks_dir.exists(),
            "installed_hooks": [],
        }

        if cursor_hooks_dir.exists():
            for hook_file in cursor_hooks_dir.glob("*"):
                if hook_file.is_file():
                    git_hook = hooks_dir / hook_file.name
                    installed = git_hook.exists()
                    status["installed_hooks"].append({
                        "name": hook_file.name,
                        "installed": installed,
                        "source": str(hook_file),
                        "target": str(git_hook),
                    })

        return status

    def check_extensions(self) -> dict[str, Any]:
        """Check Cursor extensions status."""
        extensions_dir = self.cursor_dir / "extensions"

        status = {
            "extensions_dir": extensions_dir.exists(),
            "extensions": [],
        }

        if extensions_dir.exists():
            for ext_file in extensions_dir.glob("*.js"):
                if ext_file.is_file():
                    status["extensions"].append({
                        "name": ext_file.name,
                        "path": str(ext_file),
                        "size": ext_file.stat().st_size,
                    })

        return status

    def check_rules_sync(self) -> dict[str, Any]:
        """Check if rules are in sync with CLAUDE.md."""
        claude_md = self.project_root / "CLAUDE.md"
        cursorrules = self.project_root / ".cursorrules"

        status = {
            "claude_md_exists": claude_md.exists(),
            "cursorrules_exists": cursorrules.exists(),
            "in_sync": False,
        }

        if status["claude_md_exists"] and status["cursorrules_exists"]:
            try:
                # Check if cursorrules mentions being auto-generated from CLAUDE.md
                content = Path(cursorrules).read_text(encoding="utf-8")
                status["auto_generated"] = "Auto-generated from CLAUDE.md" in content

                # Run update script to check sync
                update_script = self.project_root / "scripts" / "update_cursor_rules.py"
                if update_script.exists():
                    result = subprocess.run(
                        [sys.executable, str(update_script)],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    # If return code is 0 and no changes needed, it's in sync
                    status["in_sync"] = (
                        result.returncode == 0 and "No updates needed" in result.stdout
                    )

            except Exception as e:
                status["error"] = str(e)

        return status

    def run_health_check(self) -> dict[str, Any]:
        """Run comprehensive health check."""
        health = {
            "overall_status": "unknown",
            "components": {},
            "issues": [],
            "recommendations": [],
        }

        # Check automation script
        automation = self.check_automation_script()
        health["components"]["automation_script"] = automation

        if not automation["exists"]:
            health["issues"].append("Automation script not found")
            health["recommendations"].append(
                "Run: python3 scripts/install_cursor_automation.py",
            )
        elif not automation["working"]:
            health["issues"].append("Automation script not working")
            health["recommendations"].append("Check automation script for errors")

        # Check Git hooks
        hooks = self.check_git_hooks()
        health["components"]["git_hooks"] = hooks

        if not hooks["cursor_hooks_dir"]:
            health["issues"].append("Cursor hooks directory not found")
        elif not hooks["installed_hooks"]:
            health["issues"].append("No Git hooks installed")
            health["recommendations"].append(
                "Run: python3 scripts/install_cursor_automation.py",
            )

        # Check extensions
        extensions = self.check_extensions()
        health["components"]["extensions"] = extensions

        # Check rules sync
        rules_sync = self.check_rules_sync()
        health["components"]["rules_sync"] = rules_sync

        if not rules_sync["in_sync"]:
            health["issues"].append("Cursor rules not in sync with CLAUDE.md")
            health["recommendations"].append(
                "Run: python3 scripts/update_cursor_rules.py --force",
            )

        # Determine overall status
        if health["issues"]:
            health["overall_status"] = "issues_found"
        else:
            health["overall_status"] = "healthy"

        return health

    def display_status(
        self,
        *,
        detailed: bool = False,
        health_check: bool = False,
    ) -> None:
        """Display status information."""
        print("🔍 FLEXT Cursor Agent Automation Status")
        print("=" * 50)

        if health_check:
            health = self.run_health_check()
            self.display_health_status(health, detailed)
        else:
            self.display_basic_status(detailed)

    def display_basic_status(self, *, detailed: bool) -> None:
        """Display basic status."""
        # Automation script
        automation = self.check_automation_script()
        status_icon = (
            "✅" if automation["working"] else "❌" if automation["exists"] else "⚠️"
        )
        print(
            f"{status_icon} Automation Script: {'Working' if automation['working'] else 'Issues' if automation['exists'] else 'Not found'}",
        )

        # Git hooks
        hooks = self.check_git_hooks()
        installed_count = sum(1 for h in hooks["installed_hooks"] if h["installed"])
        total_hooks = len(hooks["installed_hooks"])
        status_icon = (
            "✅" if installed_count == total_hooks and total_hooks > 0 else "⚠️"
        )
        print(f"{status_icon} Git Hooks: {installed_count}/{total_hooks} installed")

        # Extensions
        extensions = self.check_extensions()
        status_icon = "✅" if extensions["extensions"] else "ℹ️"
        print(f"{status_icon} Extensions: {len(extensions['extensions'])} available")

        # Rules sync
        rules_sync = self.check_rules_sync()
        status_icon = "✅" if rules_sync["in_sync"] else "⚠️"
        print(
            f"{status_icon} Rules Sync: {'In sync' if rules_sync['in_sync'] else 'Out of sync'}",
        )

        if detailed:
            print("\n📋 Details:")
            if automation["working"]:
                print("  • Automation script is functional")
            if hooks["installed_hooks"]:
                print("  • Installed hooks:")
                for hook in hooks["installed_hooks"]:
                    status = "✅" if hook["installed"] else "❌"
                    print(f"    {status} {hook['name']}")
            if extensions["extensions"]:
                print("  • Available extensions:")
                for ext in extensions["extensions"]:
                    print(f"    • {ext['name']} ({ext['size']} bytes)")

    def display_health_status(self, health: dict[str, Any], *, detailed: bool) -> None:
        """Display health status."""
        overall_status = health["overall_status"]
        status_icon = {"healthy": "✅", "issues_found": "⚠️", "unknown": "❓"}.get(
            overall_status,
            "❓",
        )

        print(
            f"{status_icon} Overall Status: {overall_status.replace('_', ' ').title()}",
        )

        # Issues
        if health["issues"]:
            print(f"\n❌ Issues Found ({len(health['issues'])}):")
            for issue in health["issues"]:
                print(f"  • {issue}")

        # Recommendations
        if health["recommendations"]:
            print(f"\n💡 Recommendations ({len(health['recommendations'])}):")
            for rec in health["recommendations"]:
                print(f"  • {rec}")

        if detailed:
            _display_component_details(health["components"])


def _display_component_details(components: dict[str, Any]) -> None:
    """Display detailed component information."""
    print("\n📊 Component Details:")
    for component_name, component_data in components.items():
        print(f"\n  {component_name.title()}:")
        _display_component_data(component_data)


def _display_component_data(component_data: dict[str, Any]) -> None:
    """Display data for a single component."""
    for key, value in component_data.items():
        if isinstance(value, list):
            _display_list_value(key, value)
        else:
            print(f"    {key}: {value}")


def _display_list_value(key: str, value: list[Any]) -> None:
    """Display a list value with proper formatting."""
    if value:
        print(f"    {key}: {len(value)} items")
        for item in value[:3]:  # Show first 3
            item_desc = (
                item.get("name", str(item)) if isinstance(item, dict) else str(item)
            )
            print(f"      • {item_desc}")
        if len(value) > 3:
            print(f"      ... and {len(value) - 3} more")
    else:
        print(f"    {key}: empty")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="FLEXT Cursor Agent Status Monitor")
    parser.add_argument(
        "--detailed",
        "-d",
        action="store_true",
        help="Show detailed information",
    )
    parser.add_argument(
        "--check-health",
        action="store_true",
        help="Run comprehensive health check",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory",
    )

    args = parser.parse_args()

    monitor = CursorStatusMonitor(args.project_root)
    monitor.display_status(detailed=args.detailed, health_check=args.check_health)


if __name__ == "__main__":
    main()
