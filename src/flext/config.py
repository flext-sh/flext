"""Config facade for flext-workspace — re-exports flext_core config.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core._config import FlextConfig


class FlextRootConfig(FlextConfig):
    """Workspace root config facade — extends flext_core FlextConfig."""

    CONFIG_DIR: str = "config"


(config) = FlextRootConfig

__all__: tuple[str, ...] = ("FlextRootConfig", "config")

