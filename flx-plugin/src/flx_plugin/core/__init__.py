"""FLX Plugin Core - Core plugin system components.

Copyright (c) 2025 FLX Team. All rights reserved.
"""

from flx_plugin.core.base import Plugin, PluginMetadata
from flx_plugin.core.discovery import PluginDiscovery
from flx_plugin.core.loader import PluginLoader
from flx_plugin.core.manager import PluginManager
from flx_plugin.core.types import (
    PluginCapability,
    PluginError,
    PluginExecutionResult,
    PluginLifecycle,
    PluginStatus,
    PluginType,
)
from flx_plugin.core.validators import PluginValidator

__all__ = [
    "Plugin",
    "PluginMetadata",
    "PluginDiscovery",
    "PluginLoader",
    "PluginManager",
    "PluginValidator",
    "PluginType",
    "PluginCapability",
    "PluginLifecycle",
    "PluginStatus",
    "PluginError",
    "PluginExecutionResult",
]
