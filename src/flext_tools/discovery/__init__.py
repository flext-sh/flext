"""Módulo de descoberta de dependências."""

from flext_tools.discovery.base import DependencyDiscovery
from flext_tools.discovery.config import ConfigFileDiscovery
from flext_tools.discovery.python import PythonImportDiscovery

__all__: list[str] = [
    "ConfigFileDiscovery",
    "DependencyDiscovery",
    "PythonImportDiscovery",
]
