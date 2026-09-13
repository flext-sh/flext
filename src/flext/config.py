"""Config facade for flext-workspace — workspace-level configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import config


class FlextRootConfig(config.FlextConfig):
    """Workspace root configuration — extends flext-core config."""

    CONFIG_DIR: str = "config"


config: FlextRootConfig = FlextRootConfig.fetch_global()
"""Process-wide root configuration singleton."""

__all__: tuple[str, ...] = ("FlextRootConfig", "config")
