"""Settings facade for flext-workspace — workspace-level settings.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextSettings, m


class FlextRootSettings(FlextSettings):
    """Workspace root settings — extends flext-core settings with FLEXT_ROOT_ prefix."""

    model_config: ClassVar[m.SettingsConfigDict] = m.SettingsConfigDict(
        env_prefix="FLEXT_ROOT_",
    )


settings: FlextRootSettings = FlextRootSettings.fetch_global()
"""Pre-instantiated root settings singleton — ``from flext import settings``."""

__all__: tuple[str, ...] = ("FlextRootSettings", "settings")
