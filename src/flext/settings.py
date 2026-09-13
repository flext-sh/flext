"""Settings facade for flext-workspace — workspace-level settings.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import settings


class FlextRootSettings(settings.FlextSettings):
    """Workspace root settings — extends flext-core settings with FLEXT_ROOT_ prefix."""

    class Config:
        """Pydantic config for root settings."""

        env_prefix = "FLEXT_ROOT_"


settings: FlextRootSettings = FlextRootSettings.fetch_global()
"""Process-wide root settings singleton."""

__all__: tuple[str, ...] = ("FlextRootSettings", "settings")
