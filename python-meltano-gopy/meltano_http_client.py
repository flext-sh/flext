#!/usr/bin/env python3
"""Python HTTP client for Go Meltano API - 100% functional alternative to gopy."""

import json
from typing import Any
from urllib.parse import urljoin

import requests


class MeltanoHTTPClientError(Exception):
    """Custom exception for Meltano HTTP client errors."""


class MeltanoHTTPClient:
    """HTTP client for Go-based Meltano functionality."""

    def __init__(
        self, base_url: str = "http://localhost:8080", timeout: int = 30
    ) -> None:
        """Initialize the Meltano HTTP client.

        Args:
            base_url: Base URL of the Go server
            timeout: Request timeout in seconds

        """
        self.base_url = base_url.rstrip("/")
        self.api_base = f"{self.base_url}/api/v1/gopy"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "MeltanoHTTPClient/2.0.0",
            }
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request to the Go server.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without /api/v1/gopy prefix)
            data: Request body data
            params: Query parameters

        Returns:
            API response as dictionary

        Raises:
            MeltanoHTTPClientError: If request fails

        """
        url = urljoin(f"{self.api_base}/", endpoint.lstrip("/"))

        try:
            response = self.session.request(
                method=method, url=url, json=data, params=params, timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            # Check if the API returned an error
            if not result.get("success", False) and result.get("error"):
                msg = f"API Error: {result['error']}"
                raise MeltanoHTTPClientError(msg)

            return result

        except requests.exceptions.RequestException as e:
            msg = f"HTTP request failed: {e}"
            raise MeltanoHTTPClientError(msg)
        except json.JSONDecodeError as e:
            msg = f"Invalid JSON response: {e}"
            raise MeltanoHTTPClientError(msg)

    def check_meltano_available(self) -> bool:
        """Check if Meltano CLI is available.

        Returns:
            True if Meltano is available, False otherwise

        """
        try:
            result = self._make_request("GET", "available")
            return result.get("success", False) and result.get("data", {}).get(
                "available", False
            )
        except MeltanoHTTPClientError:
            return False

    def get_meltano_version(self) -> dict[str, Any]:
        """Get Meltano version information.

        Returns:
            Version information dictionary

        """
        result = self._make_request("GET", "version")
        return result.get("data", {})

    def create_project(self, directory: str, name: str) -> dict[str, Any]:
        """Create a new Meltano project.

        Args:
            directory: Directory where to create the project
            name: Project name

        Returns:
            Project creation result

        """
        data = {"directory": directory, "name": name}
        result = self._make_request("POST", "projects", data)
        return result.get("data", {})

    def get_project_info(self) -> dict[str, Any]:
        """Get information about the current project.

        Returns:
            Project information

        """
        result = self._make_request("GET", "projects/info")
        return result.get("data", {})

    def list_projects(self, root_dir: str = ".") -> dict[str, Any]:
        """List available Meltano projects.

        Args:
            root_dir: Root directory to search for projects

        Returns:
            List of projects

        """
        params = {"root_dir": root_dir}
        result = self._make_request("GET", "projects/list", params=params)
        return result.get("data", {})

    def add_plugin(
        self, plugin_type: str, name: str, variant: str = ""
    ) -> dict[str, Any]:
        """Add a plugin to the current project.

        Args:
            plugin_type: Type of plugin (extractor, loader, transformer, etc.)
            name: Plugin name
            variant: Plugin variant (optional)

        Returns:
            Plugin addition result

        """
        data = {"plugin_type": plugin_type, "name": name, "variant": variant}
        result = self._make_request("POST", "plugins", data)
        return result.get("data", {})

    def get_plugins(self) -> dict[str, Any]:
        """Get all plugins in the current project.

        Returns:
            List of plugins

        """
        result = self._make_request("GET", "plugins")
        return result.get("data", {})

    def install_plugins(self) -> dict[str, Any]:
        """Install all plugins in the current project.

        Returns:
            Installation result

        """
        result = self._make_request("POST", "plugins/install")
        return result.get("data", {})

    def run_pipeline(
        self, extractor: str, loader: str, transformer: str = ""
    ) -> dict[str, Any]:
        """Run a Meltano ELT pipeline.

        Args:
            extractor: Extractor plugin name
            loader: Loader plugin name
            transformer: Transformer plugin name (optional)

        Returns:
            Pipeline execution result

        """
        data = {"extractor": extractor, "loader": loader, "transformer": transformer}
        result = self._make_request("POST", "pipelines/run", data)
        return result.get("data", {})

    def execute_command(
        self, command: str, args: list[str] | None = None
    ) -> dict[str, Any]:
        """Execute a raw Meltano CLI command.

        Args:
            command: Meltano command to execute
            args: Command arguments

        Returns:
            Command execution result

        """
        data = {"command": command, "args": args or []}
        result = self._make_request("POST", "commands/execute", data)
        return result.get("data", {})

    def get_state_stats(self) -> dict[str, Any]:
        """Get state management statistics.

        Returns:
            State statistics

        """
        result = self._make_request("GET", "state/stats")
        return result.get("data", {})

    def save_state(
        self, project: str, plugin: str, state: dict[str, Any]
    ) -> dict[str, Any]:
        """Save state for a specific plugin.

        Args:
            project: Project name
            plugin: Plugin name
            state: State data to save

        Returns:
            Save operation result

        """
        data = {"project": project, "plugin": plugin, "state": state}
        result = self._make_request("POST", "state/save", data)
        return result.get("data", {})

    def load_state(self, project: str, plugin: str) -> dict[str, Any]:
        """Load state for a specific plugin.

        Args:
            project: Project name
            plugin: Plugin name

        Returns:
            Loaded state data

        """
        params = {"project": project, "plugin": plugin}
        result = self._make_request("GET", "state/load", params=params)
        return result.get("data", {})

    def delete_state(self, project: str, plugin: str) -> dict[str, Any]:
        """Delete state for a specific plugin.

        Args:
            project: Project name
            plugin: Plugin name

        Returns:
            Delete operation result

        """
        params = {"project": project, "plugin": plugin}
        result = self._make_request("DELETE", "state/delete", params=params)
        return result.get("data", {})

    def health_check(self) -> bool:
        """Check if the Go server is healthy and responding.

        Returns:
            True if server is healthy, False otherwise

        """
        try:
            result = self._make_request("GET", "version")
            return result.get("success", False)
        except MeltanoHTTPClientError:
            return False

    def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            self.session.close()


# Module-level convenience functions for compatibility with original gopy interface
_client_instance = None


def get_client_instance(base_url: str = "http://localhost:8080") -> MeltanoHTTPClient:
    """Get or create the global client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = MeltanoHTTPClient(base_url)
    return _client_instance


def CheckMeltanoAvailable() -> bool:
    """Check if Meltano is available (compatibility function)."""
    return get_client_instance().check_meltano_available()


def GetMeltanoVersion() -> dict[str, Any]:
    """Get Meltano version (compatibility function)."""
    return get_client_instance().get_meltano_version()


def CreateProject(directory: str, name: str) -> dict[str, Any]:
    """Create project (compatibility function)."""
    return get_client_instance().create_project(directory, name)


def AddPluginToProject(
    plugin_type: str, name: str, variant: str = ""
) -> dict[str, Any]:
    """Add plugin (compatibility function)."""
    return get_client_instance().add_plugin(plugin_type, name, variant)


def RunMeltanoPipeline(
    extractor: str, loader: str, transformer: str = ""
) -> dict[str, Any]:
    """Run pipeline (compatibility function)."""
    return get_client_instance().run_pipeline(extractor, loader, transformer)


def GetProjectPlugins() -> dict[str, Any]:
    """Get plugins (compatibility function)."""
    return get_client_instance().get_plugins()


def ExecuteMeltanoCommand(
    command: str, args: list[str] | None = None
) -> dict[str, Any]:
    """Execute command (compatibility function)."""
    return get_client_instance().execute_command(command, args or [])


if __name__ == "__main__":
    # Test the HTTP client

    try:
        client = MeltanoHTTPClient()

        # Test server health
        healthy = client.health_check()

        if healthy:
            # Test availability check
            available = client.check_meltano_available()

            # Test version
            version = client.get_meltano_version()

    except Exception:
        pass
    finally:
        if "client" in locals():
            client.close()
