"""Mock Meltano compatibility layer for FLEXT project testing.

This module provides a minimal mock implementation of Meltano components
to enable FLEXT modules to import successfully without requiring the full
Meltano installation.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


class MockMeltanoProject:
    """Mock Meltano project implementation."""

    def __init__(self, project_dir: str = "/tmp/mock_meltano"):
        self.project_dir = Path(project_dir)
        self.settings = {}

    def activate(self) -> None:
        """Mock project activation."""
        pass

    def deactivate(self) -> None:
        """Mock project deactivation."""
        pass


class MockMeltanoInvoker:
    """Mock Meltano command invoker."""

    def __init__(self, project: MockMeltanoProject):
        self.project = project

    def invoke(self, command: list[str]) -> dict[str, Any]:
        """Mock command invocation."""
        return {
            "success": True,
            "output": f"Mock execution of: {' '.join(command)}",
            "return_code": 0,
        }


class MockMeltanoPlugin:
    """Mock Meltano plugin representation."""

    def __init__(self, name: str, plugin_type: str = "extractor"):
        self.name = name
        self.type = plugin_type
        self.settings = {}

    def configure(self, **kwargs) -> None:
        """Mock plugin configuration."""
        self.settings.update(kwargs)


@dataclass
class MockMeltanoRun:
    """Mock Meltano run result."""

    success: bool = True
    output: str = "Mock run completed"
    return_code: int = 0


class MockMeltanoClient:
    """Mock Meltano client for API operations."""

    def __init__(self):
        self.project = MockMeltanoProject()
        self.invoker = MockMeltanoInvoker(self.project)

    def run(self, *args, **kwargs) -> MockMeltanoRun:
        """Mock run execution."""
        return MockMeltanoRun()

    def install(self, plugin_name: str) -> bool:
        """Mock plugin installation."""
        return True

    def add(self, plugin_type: str, plugin_name: str) -> MockMeltanoPlugin:
        """Mock plugin addition."""
        return MockMeltanoPlugin(plugin_name, plugin_type)


# Mock meltano module structure
class _MockMeltanoModule:
    """Mock meltano module to satisfy import requirements."""

    def __init__(self):
        self.core = self
        self.cli = self
        self.project = MockMeltanoProject
        self.invoker = MockMeltanoInvoker
        self.plugin = MockMeltanoPlugin
        self.client = MockMeltanoClient

        # Mock additional common imports
        self.Project = MockMeltanoProject
        self.ProjectAddService = type("MockProjectAddService", (), {})
        self.PluginType = type(
            "MockPluginType",
            (),
            {
                "EXTRACTORS": "extractors",
                "LOADERS": "loaders",
                "TRANSFORMS": "transforms",
            },
        )
        self.PluginInstallService = type("MockPluginInstallService", (), {})

    def __getattr__(self, name: str) -> Any:
        """Return mock objects for any missing attributes."""
        if name in [
            "Project",
            "PluginType",
            "ProjectAddService",
            "PluginInstallService",
        ]:
            return getattr(self, name, type(f"Mock{name}", (), {}))
        return lambda *args, **kwargs: f"Mock {name} called"


# Install mock meltano in sys.modules if not already present
import sys

if "meltano" not in sys.modules:
    mock_meltano = _MockMeltanoModule()
    sys.modules["meltano"] = mock_meltano
    sys.modules["meltano.core"] = mock_meltano
    sys.modules["meltano.cli"] = mock_meltano
    sys.modules["meltano.core.project"] = mock_meltano
    sys.modules["meltano.core.invoker"] = mock_meltano
    sys.modules["meltano.core.plugin"] = mock_meltano


def install_meltano_mock() -> None:
    """Install the meltano mock in sys.modules."""
    if "meltano" not in sys.modules:
        mock_meltano = _MockMeltanoModule()
        sys.modules["meltano"] = mock_meltano
        sys.modules["meltano.core"] = mock_meltano
        sys.modules["meltano.cli"] = mock_meltano
        sys.modules["meltano.core.project"] = mock_meltano
        sys.modules["meltano.core.invoker"] = mock_meltano
        sys.modules["meltano.core.plugin"] = mock_meltano
        print("✅ Mock Meltano compatibility layer installed")
    else:
        print("⚠️ Meltano already available in sys.modules")


if __name__ == "__main__":
    install_meltano_mock()
    print("Mock Meltano compatibility layer ready for testing")
