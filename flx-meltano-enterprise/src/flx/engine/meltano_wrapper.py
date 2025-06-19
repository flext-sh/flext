"""
Meltano Engine wrapper for asynchronous operations.

This module provides a high-level interface to Meltano operations,
wrapping the Meltano CLI and Python API for use within the FLX platform.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Optional
# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies


import structlog
from meltano.core.plugin import PluginRef, PluginType
from meltano.core.project import Project
from meltano.core.project_add_service import ProjectAddService

# Lazy import to avoid circular dependencies
settings = lazy_import('flx.config', 'settings')
# Lazy imports to avoid circular dependencies
Event = lazy_import('flx.events.event_bus', 'Event')
EventBus = lazy_import('flx.events.event_bus', 'EventBus')

logger = structlog.get_logger()


class MeltanoEngine:
    """Asynchronous wrapper for Meltano operations."""

    def __init__(self, project_root: Path) -> None:
        """Initialize the Meltano engine."""
        self.project_root = project_root
        self.project: Optional[Project] = None
        self.logger = logger.bind(component="meltano_engine")
        self._executor = asyncio.get_event_loop().run_in_executor

    async def initialize(self) -> None:
        """Initialize the Meltano project."""
        self.logger.info("Initializing Meltano project", root=str(self.project_root))

        try:
            # Create project directory if it doesn't exist
            self.project_root.mkdir(parents=True, exist_ok=True)

            # Check if meltano.yml exists
            meltano_yml = self.project_root / "meltano.yml"
            if not meltano_yml.exists():
                await self._init_project()

            # Load project
            self.project = await self._executor(None, Project.find, self.project_root)

            self.logger.info("Meltano project initialized successfully")

        except Exception as e:
            self.logger.error("Failed to initialize Meltano project", error=str(e))
            raise

    async def cleanup(self) -> None:
        """Cleanup Meltano resources."""
        self.logger.info("Cleaning up Meltano engine")
        # Meltano doesn't require explicit cleanup
        pass

    async def _init_project(self) -> None:
        """Initialize a new Meltano project."""
        self.logger.info("Creating new Meltano project")

        cmd = ["meltano", "init", str(self.project_root), "--no-usage-stats"]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        _stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Failed to init Meltano project: {stderr.decode()}")

        self.logger.info("Meltano project created")

    async def run_pipeline(
        self,
        extractor: str,
        loader: str,
        transform: Optional[str] = None,
        state_id: Optional[str] = None,
        full_refresh: bool = False,
        env: Optional[dict[str, str]] = None,
        event_bus: Optional[EventBus] = None,
    ) -> dict[str, Any]:
        """Run an ELT pipeline."""
        self.logger.info(
            "Running pipeline",
            extractor=extractor,
            loader=loader,
            transform=transform,
            state_id=state_id,
            full_refresh=full_refresh,
        )

        # Build command
        cmd = ["meltano", "run"]

        if transform:
            cmd.extend([extractor, transform, loader])
        else:
            cmd.extend([extractor, loader])

        # Add flags
        if state_id:
            cmd.extend(["--state-id", state_id])

        if full_refresh:
            cmd.append("--full-refresh")

        # Prepare environment
        run_env = dict(settings.model_dump())
        if env:
            run_env.update(env)

        # Create process
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=self.project_root,
            env=run_env,
        )

        # Stream output
        output_lines = []
        if process.stdout:
            async for line in process.stdout:
                line_str = line.decode().rstrip()
                output_lines.append(line_str)

                # Log output
                self.logger.debug("Pipeline output", line=line_str)

                # Publish output event if event bus provided
                if event_bus:
                    await event_bus.publish(
                        Event.create(
                            "pipeline.output",
                            {
                                "extractor": extractor,
                                "loader": loader,
                                "line": line_str,
                            },
                        )
                    )

        # Wait for completion
        await process.wait()

        # Prepare result
        result = {
            "exit_code": process.returncode,
            "stdout": "\n".join(output_lines),
            "success": process.returncode == 0,
            "extractor": extractor,
            "loader": loader,
            "transform": transform,
        }

        if process.returncode == 0:
            self.logger.info("Pipeline completed successfully", **result)
        else:
            self.logger.error("Pipeline failed", **result)

        return result

    async def add_plugin(
        self,
        plugin_type: str,
        plugin_name: str,
        variant: Optional[str] = None,
    ) -> bool:
        """Add a plugin to the project."""
        self.logger.info(
            "Adding plugin",
            type=plugin_type,
            name=plugin_name,
            variant=variant,
        )

        if not self.project:
            raise RuntimeError("Project not initialized")

        try:
            add_service = ProjectAddService(self.project)
            plugin_ref = PluginRef(
                plugin_type=PluginType(plugin_type),
                name=plugin_name,
                variant=variant,
            )

            # Add plugin
            await self._executor(None, add_service.add, plugin_ref)

            self.logger.info("Plugin added successfully")
            return True

        except Exception as e:
            self.logger.error("Failed to add plugin", error=str(e))
            return False

    async def remove_plugin(
        self,
        plugin_type: str,
        plugin_name: str,
    ) -> bool:
        """Remove a plugin from the project."""
        self.logger.info(
            "Removing plugin",
            type=plugin_type,
            name=plugin_name,
        )

        cmd = ["meltano", "remove", plugin_type, plugin_name]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_root,
        )

        _stdout, stderr = await process.communicate()

        if process.returncode == 0:
            self.logger.info("Plugin removed successfully")
            return True
        else:
            self.logger.error("Failed to remove plugin", error=stderr.decode())
            return False

    async def get_state(self, state_id: str) -> dict[str, Any]:
        """Get pipeline state."""
        cmd = ["meltano", "state", "get", state_id, "--json"]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_root,
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return json.loads(stdout.decode())
        else:
            self.logger.error("Failed to get state", error=stderr.decode())
            return {}

    async def set_state(self, state_id: str, state_data: dict[str, Any]) -> bool:
        """Set pipeline state."""
        cmd = ["meltano", "state", "set", state_id, "--json"]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_root,
        )

        _stdout, stderr = await process.communicate(
            input=json.dumps(state_data).encode()
        )

        if process.returncode == 0:
            self.logger.info("State set successfully")
            return True
        else:
            self.logger.error("Failed to set state", error=stderr.decode())
            return False

    async def clear_state(self, state_id: str) -> bool:
        """Clear pipeline state."""
        cmd = ["meltano", "state", "clear", state_id]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_root,
        )

        _stdout, stderr = await process.communicate()

        if process.returncode == 0:
            self.logger.info("State cleared successfully")
            return True
        else:
            self.logger.error("Failed to clear state", error=stderr.decode())
            return False

    async def list_plugins(
        self,
        plugin_type: Optional[str] = None,
        installed_only: bool = False,
    ) -> list[dict[str, Any]]:
        """List available or installed plugins."""
        cmd = ["meltano", "list"]

        if plugin_type:
            cmd.append(plugin_type)

        if installed_only:
            cmd.append("--installed")

        cmd.append("--json")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_root,
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return json.loads(stdout.decode())
        else:
            self.logger.error("Failed to list plugins", error=stderr.decode())
            return []

    async def get_config(self, plugin_name: str) -> dict[str, Any]:
        """Get plugin configuration."""
        cmd = ["meltano", "config", plugin_name, "list", "--json"]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_root,
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return json.loads(stdout.decode())
        else:
            self.logger.error("Failed to get config", error=stderr.decode())
            return {}

    async def set_config(
        self,
        plugin_name: str,
        config_key: str,
        config_value: Any,
    ) -> bool:
        """Set plugin configuration."""
        cmd = ["meltano", "config", plugin_name, "set", config_key, str(config_value)]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_root,
        )

        _stdout, stderr = await process.communicate()

        if process.returncode == 0:
            self.logger.info("Config set successfully")
            return True
        else:
            self.logger.error("Failed to set config", error=stderr.decode())
            return False
