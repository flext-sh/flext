"""Mock flext_meltano module for testing compatibility."""

import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class MockMeltanoService:
    """Mock Meltano service for testing."""

    def __init__(self):
        self.project_root = "/tmp/mock_project"
        self.is_active = False

    def activate_project(self, project_path: str) -> bool:
        """Mock project activation."""
        self.project_root = project_path
        self.is_active = True
        return True

    def run_pipeline(self, pipeline_name: str) -> dict[str, Any]:
        """Mock pipeline execution."""
        return {
            "success": True,
            "pipeline": pipeline_name,
            "output": f"Mock execution of {pipeline_name}",
            "return_code": 0,
        }

    def install_plugin(self, plugin_type: str, plugin_name: str) -> bool:
        """Mock plugin installation."""
        return True


class MockMeltanoIntegration:
    """Mock Meltano integration for FLEXT."""

    def __init__(self):
        self.service = MockMeltanoService()
        self.config = {}

    def initialize(self, **kwargs) -> None:
        """Mock initialization."""
        self.config.update(kwargs)

    def get_service(self) -> MockMeltanoService:
        """Get mock Meltano service."""
        return self.service


# Mock flext_meltano module structure
class _MockFlextMeltanoModule:
    """Mock flext_meltano module."""

    def __init__(self):
        self.MeltanoService = MockMeltanoService
        self.MeltanoIntegration = MockMeltanoIntegration
        self.service = MockMeltanoService()
        self.integration = MockMeltanoIntegration()

    def __getattr__(self, name: str) -> Any:
        """Return mock objects for missing attributes."""
        return lambda *args, **kwargs: f"Mock flext_meltano.{name} called"


def install_flext_meltano_mock() -> None:
    """Install mock flext_meltano in sys.modules."""
    if "flext_meltano" not in sys.modules:
        mock_module = _MockFlextMeltanoModule()
        sys.modules["flext_meltano"] = mock_module
        print("✅ Mock flext_meltano installed")


# Auto-install if imported
install_flext_meltano_mock()
