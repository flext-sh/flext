#!/usr/bin/env python3
"""Meltano Bridge for Go Integration.

This module creates a simple Python interface that can be called from Go
using gopy to provide Meltano functionality as a library.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

# Import Meltano components
try:
    # Try basic meltano import first
    import meltano
    from meltano.core.project import Project

    MELTANO_AVAILABLE = True

    # Optional imports that might not be available in all versions
    try:
        from meltano.core.project_add_service import ProjectAddService
    except ImportError:
        ProjectAddService = None

    try:
        from meltano.core.plugin_invoker import PluginInvoker
    except ImportError:
        PluginInvoker = None

    try:
        from meltano.core.plugin import PluginType
    except ImportError:
        PluginType = None

except ImportError as e:
    logging.warning(f"Meltano not available: {e}")
    MELTANO_AVAILABLE = False


class MeltanoResult:
    """Result wrapper for Meltano operations."""

    def __init__(self, success: bool, data: Any = None, error: str = ""):
        self.success = success
        self.data = data
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary for JSON serialization."""
        return {"success": self.success, "data": self.data, "error": self.error}


class MeltanoBridge:
    """Bridge class to expose Meltano functionality to Go via gopy.

    This class provides a simplified interface to common Meltano operations
    that can be easily called from Go code.
    """

    def __init__(self, project_root: str = "."):
        """Initialize the Meltano bridge with a project root."""
        self.project_root = Path(project_root)
        self.project = None

        if MELTANO_AVAILABLE:
            try:
                # Try different ways to find the project
                if hasattr(Project, "find_nearest"):
                    self.project = Project.find_nearest(self.project_root)
                elif hasattr(Project, "find"):
                    self.project = Project.find(self.project_root)
                else:
                    # Create a basic project instance
                    self.project = Project(self.project_root)
            except Exception as e:
                logging.warning(f"Could not load Meltano project: {e}")

    def is_available(self) -> bool:
        """Check if Meltano is available and working."""
        # Meltano is available if we can import it, even without a project
        return MELTANO_AVAILABLE

    def init_project(self, project_name: str, project_dir: str = "") -> str:
        """Initialize a new Meltano project.

        Args:
        ----
            project_name: Name of the project
            project_dir: Directory to create project in (optional)

        Returns:
        -------
            JSON string with result

        """
        try:
            if not project_dir:
                project_dir = project_name

            # Meltano init only accepts the project directory name
            # We need to change to the parent directory and run init there
            Path.cwd()

            cmd = ["meltano", "init", project_dir]

            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True, check=False
            )

            if result.returncode == 0:
                return json.dumps(
                    MeltanoResult(
                        success=True,
                        data=f"Project {project_name} initialized successfully",
                    ).to_dict()
                )
            return json.dumps(
                MeltanoResult(
                    success=False, error=result.stderr or result.stdout
                ).to_dict()
            )

        except Exception as e:
            return json.dumps(MeltanoResult(success=False, error=str(e)).to_dict())

    def add_plugin(
        self, plugin_type: str, plugin_name: str, plugin_variant: str = ""
    ) -> str:
        """Add a plugin to the Meltano project.

        Args:
        ----
            plugin_type: Type of plugin (extractor, loader, transformer, etc.)
            plugin_name: Name of the plugin
            plugin_variant: Variant of the plugin (optional)

        Returns:
        -------
            JSON string with result

        """
        try:
            if not self.project:
                return json.dumps(
                    MeltanoResult(
                        success=False, error="No Meltano project loaded"
                    ).to_dict()
                )

            cmd = ["meltano", "add", plugin_type, plugin_name]
            if plugin_variant:
                cmd.append(plugin_variant)

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project.root, check=False
            )

            if result.returncode == 0:
                return json.dumps(
                    MeltanoResult(
                        success=True, data=f"Plugin {plugin_name} added successfully"
                    ).to_dict()
                )
            return json.dumps(
                MeltanoResult(
                    success=False, error=result.stderr or result.stdout
                ).to_dict()
            )

        except Exception as e:
            return json.dumps(MeltanoResult(success=False, error=str(e)).to_dict())

    def install_plugins(self) -> str:
        """Install all plugins in the project.

        Returns
        -------
            JSON string with result

        """
        try:
            if not self.project:
                return json.dumps(
                    MeltanoResult(
                        success=False, error="No Meltano project loaded"
                    ).to_dict()
                )

            result = subprocess.run(
                ["meltano", "install"],
                capture_output=True,
                text=True,
                cwd=self.project.root,
                check=False,
            )

            if result.returncode == 0:
                return json.dumps(
                    MeltanoResult(
                        success=True, data="All plugins installed successfully"
                    ).to_dict()
                )
            return json.dumps(
                MeltanoResult(
                    success=False, error=result.stderr or result.stdout
                ).to_dict()
            )

        except Exception as e:
            return json.dumps(MeltanoResult(success=False, error=str(e)).to_dict())

    def run_pipeline(self, extractor: str, loader: str, transformer: str = "") -> str:
        """Run a Meltano pipeline.

        Args:
        ----
            extractor: Name of the extractor plugin
            loader: Name of the loader plugin
            transformer: Name of the transformer plugin (optional)

        Returns:
        -------
            JSON string with result

        """
        try:
            if not self.project:
                return json.dumps(
                    MeltanoResult(
                        success=False, error="No Meltano project loaded"
                    ).to_dict()
                )

            cmd = ["meltano", "run", extractor]
            if transformer:
                cmd.append(transformer)
            cmd.append(loader)

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project.root, check=False
            )

            if result.returncode == 0:
                return json.dumps(
                    MeltanoResult(
                        success=True,
                        data=f"Pipeline {extractor} -> {loader} executed successfully",
                    ).to_dict()
                )
            return json.dumps(
                MeltanoResult(
                    success=False, error=result.stderr or result.stdout
                ).to_dict()
            )

        except Exception as e:
            return json.dumps(MeltanoResult(success=False, error=str(e)).to_dict())

    def get_plugins(self) -> str:
        """Get list of all plugins in the project.

        Returns
        -------
            JSON string with plugin list

        """
        try:
            if not self.project:
                return json.dumps(
                    MeltanoResult(
                        success=False, error="No Meltano project loaded"
                    ).to_dict()
                )

            result = subprocess.run(
                ["meltano", "config", "meltano", "list"],
                capture_output=True,
                text=True,
                cwd=self.project.root,
                check=False,
            )

            if result.returncode == 0:
                return json.dumps(
                    MeltanoResult(success=True, data=result.stdout).to_dict()
                )
            return json.dumps(
                MeltanoResult(
                    success=False, error=result.stderr or result.stdout
                ).to_dict()
            )

        except Exception as e:
            return json.dumps(MeltanoResult(success=False, error=str(e)).to_dict())

    def get_project_info(self) -> str:
        """Get information about the current project.

        Returns
        -------
            JSON string with project information

        """
        try:
            if not self.project:
                return json.dumps(
                    MeltanoResult(
                        success=False, error="No Meltano project loaded"
                    ).to_dict()
                )

            project_info = {
                "name": self.project.name,
                "root": str(self.project.root),
                "config_file": str(self.project.meltano_file_path),
                "environment": getattr(self.project, "environment", "dev"),
            }

            return json.dumps(MeltanoResult(success=True, data=project_info).to_dict())

        except Exception as e:
            return json.dumps(MeltanoResult(success=False, error=str(e)).to_dict())

    def execute_command(self, command: str, args: list[str] | None = None) -> str:
        """Execute a raw Meltano command.

        Args:
        ----
            command: Meltano command to execute
            args: List of arguments for the command

        Returns:
        -------
            JSON string with result

        """
        try:
            if not self.project:
                return json.dumps(
                    MeltanoResult(
                        success=False, error="No Meltano project loaded"
                    ).to_dict()
                )

            cmd = ["meltano", command]
            if args:
                cmd.extend(args)

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project.root, check=False
            )

            return json.dumps(
                MeltanoResult(
                    success=result.returncode == 0,
                    data=result.stdout if result.returncode == 0 else None,
                    error=result.stderr if result.returncode != 0 else "",
                ).to_dict()
            )

        except Exception as e:
            return json.dumps(MeltanoResult(success=False, error=str(e)).to_dict())


# Global instance for gopy
_bridge = None


def get_bridge(project_root: str = ".") -> MeltanoBridge:
    """Get or create the global bridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = MeltanoBridge(project_root)
    return _bridge


# Simple functions for gopy binding
def init_project(project_name: str, project_dir: str = "") -> str:
    """Initialize a new Meltano project."""
    return get_bridge().init_project(project_name, project_dir)


def add_plugin(plugin_type: str, plugin_name: str, plugin_variant: str = "") -> str:
    """Add a plugin to the Meltano project."""
    return get_bridge().add_plugin(plugin_type, plugin_name, plugin_variant)


def install_plugins() -> str:
    """Install all plugins in the project."""
    return get_bridge().install_plugins()


def run_pipeline(extractor: str, loader: str, transformer: str = "") -> str:
    """Run a Meltano pipeline."""
    return get_bridge().run_pipeline(extractor, loader, transformer)


def get_plugins() -> str:
    """Get list of all plugins in the project."""
    return get_bridge().get_plugins()


def get_project_info() -> str:
    """Get information about the current project."""
    return get_bridge().get_project_info()


def execute_command(command: str, args_json: str = "[]") -> str:
    """Execute a raw Meltano command."""
    try:
        args = json.loads(args_json) if args_json else []
        return get_bridge().execute_command(command, args)
    except json.JSONDecodeError:
        return json.dumps(
            MeltanoResult(
                success=False, error="Invalid JSON in args_json parameter"
            ).to_dict()
        )


def is_available() -> bool:
    """Check if Meltano is available."""
    return get_bridge().is_available()


if __name__ == "__main__":
    # Test the bridge
    bridge = MeltanoBridge()

    if bridge.is_available():
        pass
