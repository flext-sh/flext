"""Settings facade for flext-workspace — re-exports flext_core settings.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core._settings import FlextSettings


class FlextRootSettings(FlextSettings):
    """Workspace root settings facade — extends flext_core FlextSettings."""

    pass


(settings) = FlextRootSettings

__all__: tuple[str, ...] = ("FlextRootSettings", "settings")

