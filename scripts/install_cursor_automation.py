#!/usr/bin/env python3
"""FLEXT Cursor Agent Automation Installer.

Automatically installs and configures FLEXT automation for Cursor Agent.
Provides transparent integration with Claude Code patterns.

Usage:
    python3 scripts/install_cursor_automation.py [--force] [--verbose]

"""

from __future__ import annotations

import argparse
import json
import os
import shutil
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


class CursorAutomationInstaller:
    """Installs FLEXT automation for Cursor Agent."""

    def __init__(self, project_root: Path, *, verbose: bool = False) -> None:
        """Initialize the Cursor automation installer."""
        self.project_root = project_root
        self.verbose = verbose
        self.cursor_dir = project_root / ".cursor"
        self.backup_dir = project_root / ".cursor" / "backups"

    def log(self, message: str) -> None:
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"🔧 {message}")

    def create_backup(self, file_path: Path) -> Result[Path]:
        """Create backup of existing file."""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            if file_path.exists():
                backup_path = self.backup_dir / f"{file_path.name}.backup"
                shutil.copy2(file_path, backup_path)
                self.log(f"Created backup: {backup_path}")
                return Result.ok(backup_path)

            return Result.ok(None)

        except Exception as e:
            return Result.err(f"Failed to create backup for {file_path}: {e}")

    def make_executable(self, file_path: Path) -> Result[bool]:
        """Make file executable."""
        try:
            current = file_path.stat().st_mode
            file_path.chmod(current | stat.S_IEXEC)
            return Result.ok(True)
        except Exception as e:
            return Result.err(f"Failed to make {file_path} executable: {e}")

    def install_automation_script(self) -> Result[bool]:
        """Install the main automation script."""
        try:
            source = self.project_root / "cursor-agent-automation.py"
            if not source.exists():
                return Result.err("cursor-agent-automation.py not found")

            # Make sure it's executable
            result = self.make_executable(source)
            if result.is_failure:
                return result

            self.log("✅ Automation script ready")
            return Result.ok(True)

        except Exception as e:
            return Result.err(f"Failed to install automation script: {e}")

    def install_git_hooks(self) -> Result[bool]:
        """Install Git hooks for automation."""
        try:
            hooks_dir = self.project_root / ".git" / "hooks"
            if not hooks_dir.exists():
                return Result.err("Git hooks directory not found (.git/hooks)")

            cursor_hooks_dir = self.cursor_dir / "hooks"
            if not cursor_hooks_dir.exists():
                return Result.err("Cursor hooks directory not found (.cursor/hooks)")

            installed_count = 0

            # Install all available hooks
            for hook_file in cursor_hooks_dir.glob("*"):
                if hook_file.is_file():
                    git_hook = hooks_dir / hook_file.name

                    # Create backup of existing hook
                    self.create_backup(git_hook)

                    # Copy our hook
                    shutil.copy2(hook_file, git_hook)

                    # Make executable
                    self.make_executable(git_hook)

                    self.log(f"✅ Git hook '{hook_file.name}' installed")
                    installed_count += 1

            if installed_count == 0:
                return Result.err("No hooks found to install")

            self.log(f"✅ Installed {installed_count} Git hooks")
            return Result.ok(True)

        except Exception as e:
            return Result.err(f"Failed to install Git hooks: {e}")

    def install_cursor_extensions(self) -> Result[bool]:
        """Install Cursor extensions."""
        try:
            extensions_dir = self.cursor_dir / "extensions"
            if not extensions_dir.exists():
                self.log("No extensions directory found, skipping")
                return Result.ok(True)

            # Check if we have extensions to install
            flext_extension = extensions_dir / "flext-automation.js"
            if flext_extension.exists():
                self.log("✅ FLEXT Cursor extension ready")
            else:
                self.log(
                    "ℹ️  FLEXT extension not found (this is normal if using external extension)",
                )

            return Result.ok(True)

        except Exception as e:
            return Result.err(f"Failed to install Cursor extensions: {e}")

    def update_cursor_config(self) -> Result[bool]:
        """Update Cursor configuration."""
        try:
            config_file = self.cursor_dir / "config.json"
            if not config_file.exists():
                self.log("No Cursor config found, creating default")
                return Result.ok(True)

            # Load and validate config
            try:
                with Path(config_file).open("r", encoding="utf-8") as f:
                    config = json.load(f)

                if "flext" in config and config["flext"].get("automation", {}).get(
                    "enabled",
                ):
                    self.log("✅ Cursor config validated")
                else:
                    self.log("⚠️  FLEXT automation not enabled in Cursor config")

            except json.JSONDecodeError:
                return Result.err("Invalid JSON in Cursor config")

            return Result.ok(True)

        except Exception as e:
            return Result.err(f"Failed to update Cursor config: {e}")

    def run_initial_setup(self) -> Result[dict[str, Any]]:
        """Run initial setup and validation."""
        try:
            # Update Cursor rules from CLAUDE.md
            update_script = self.project_root / "scripts" / "update_cursor_rules.py"
            if update_script.exists():
                self.log("Running initial Cursor rules update...")
                result = subprocess.run(
                    [sys.executable, str(update_script), "--force"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )

                if result.returncode != 0:
                    self.log(f"⚠️  Rules update warning: {result.stderr.strip()}")

            # Test automation script
            automation_script = self.project_root / "cursor-agent-automation.py"
            if automation_script.exists():
                self.log("Testing automation script...")
                result = subprocess.run(
                    [sys.executable, str(automation_script), "skills"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=10,
                )

                if result.returncode == 0:
                    self.log("✅ Automation script working")
                else:
                    self.log(
                        f"⚠️  Automation script test failed: {result.stderr.strip()}",
                    )

            return Result.ok({
                "automation_script": automation_script.exists(),
                "cursor_config": (self.cursor_dir / "config.json").exists(),
                "manifest": (self.cursor_dir / "manifest.json").exists(),
            })

        except Exception as e:
            return Result.err(f"Initial setup failed: {e}")

    def detect_cursor_environment(self) -> dict[str, Any]:
        """Detect Cursor environment and capabilities."""
        info = {
            "is_cursor": False,
            "version": None,
            "has_extensions": False,
            "has_hooks": False,
            "automation_ready": False,
        }

        # Check environment variables
        if (
            os.environ.get("CURSOR") == "true"
            or os.environ.get("TERM_PROGRAM") == "Cursor"
        ):
            info["is_cursor"] = True

        # Check for Cursor-specific files
        cursor_config = self.cursor_dir / "config.json"
        if cursor_config.exists():
            info["has_config"] = True
            try:
                config = json.loads(cursor_config.read_text(encoding="utf-8"))
                info["automation_ready"] = (
                    config.get("flext", {}).get("automation", {}).get("enabled", False)
                )
            except (OSError, ValueError, json.JSONDecodeError):
                # Config file exists but is unreadable/corrupted - use defaults
                pass

        # Check extensions
        extensions_dir = self.cursor_dir / "extensions"
        info["has_extensions"] = extensions_dir.exists() and any(
            extensions_dir.iterdir(),
        )

        # Check hooks
        hooks_dir = self.cursor_dir / "hooks"
        info["has_hooks"] = hooks_dir.exists() and any(hooks_dir.iterdir())

        return info

    def install(self, *, force: bool = False) -> Result[dict[str, Any]]:
        """Install FLEXT automation for Cursor Agent."""
        try:
            self.log("🚀 Starting FLEXT Cursor Agent Automation Installation")
            self.log(f"Project root: {self.project_root}")

            # Detect environment
            env_info = self.detect_cursor_environment()
            self.log(f"Cursor detected: {env_info['is_cursor']}")

            results = {
                "environment": env_info,
                "steps": {},
            }

            # Step 1: Install automation script
            self.log("Step 1: Installing automation script...")
            result = self.install_automation_script()
            results["steps"]["automation_script"] = result.is_success
            if result.is_failure:
                return Result.err(
                    f"Automation script installation failed: {result.error}",
                )

            # Step 2: Install Git hooks
            self.log("Step 2: Installing Git hooks...")
            result = self.install_git_hooks()
            results["steps"]["git_hooks"] = result.is_success
            if result.is_failure and not force:
                self.log(f"⚠️  Git hooks installation failed: {result.error}")

            # Step 3: Install Cursor extensions
            self.log("Step 3: Installing Cursor extensions...")
            result = self.install_cursor_extensions()
            results["steps"]["cursor_extensions"] = result.is_success

            # Step 4: Update Cursor config
            self.log("Step 4: Updating Cursor configuration...")
            result = self.update_cursor_config()
            results["steps"]["cursor_config"] = result.is_success

            # Step 5: Run initial setup
            self.log("Step 5: Running initial setup...")
            result = self.run_initial_setup()
            if result.is_success:
                results["steps"]["initial_setup"] = True
                results["setup_info"] = result.value
            else:
                results["steps"]["initial_setup"] = False
                if not force:
                    return Result.err(f"Initial setup failed: {result.error}")

            # Summary
            successful_steps = sum(1 for step in results["steps"].values() if step)
            total_steps = len(results["steps"])

            results["summary"] = {
                "successful_steps": successful_steps,
                "total_steps": total_steps,
                "success_rate": successful_steps / total_steps,
            }

            self.log(
                f"✅ Installation completed: {successful_steps}/{total_steps} steps successful",
            )

            if successful_steps == total_steps:
                self.log("🎉 FLEXT Cursor Agent Automation fully installed!")
                self.log("💡 Use '/flext-validate' in Cursor to test the integration")
            else:
                self.log(
                    f"⚠️  Partial installation: {successful_steps}/{total_steps} steps completed",
                )

            return Result.ok(results)

        except Exception as e:
            return Result.err(f"Installation failed: {e}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Install FLEXT Cursor Agent Automation",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force installation even with errors",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory",
    )

    args = parser.parse_args()

    installer = CursorAutomationInstaller(args.project_root, args.verbose)
    result = installer.install(force=args.force)

    if result.is_success:
        data = result.value

        if args.verbose:
            print("\n📊 Installation Details:")
            print(f"  Environment: {data['environment']}")
            print(f"  Steps: {data['steps']}")
            if "setup_info" in data:
                print(f"  Setup: {data['setup_info']}")

        summary = data["summary"]
        print(
            f"\n✅ Installation completed: {summary['successful_steps']}/{summary['total_steps']} steps",
        )
        return 0

    print(f"❌ Installation failed: {result.error}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
