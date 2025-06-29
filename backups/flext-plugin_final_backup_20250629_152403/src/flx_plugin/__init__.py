"""FLX Plugin - Enterprise Plugin System with Hot Reload.

Copyright (c) 2025 FLX Team. All rights reserved.
"""

from __future__ import annotations

__version__ = "0.1.0"

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

__all__ = [
    # Types
    "PluginType",
    "PluginCapability",
    "PluginLifecycle",
    "PluginStatus",
    "PluginError",
    "PluginExecutionResult",
    # Core
    "Plugin",
    "PluginMetadata",
    "PluginDiscovery",
    "PluginLoader",
    "PluginManager",
    # Version
    "__version__",
]
