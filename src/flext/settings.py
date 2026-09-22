"""Settings facade for flext-workspace — workspace-level settings.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ConfigDict

from flext_core import FlextSettings

if TYPE_CHECKING:
    from . import t


class FlextRootSettings(FlextSettings):
    """Workspace root settings — extends flext-core settings with FLEXT_ROOT_ prefix."""

    model_config = ConfigDict(env_prefix="FLEXT_ROOT_")


settings = FlextRootSettings

__all__: t.VariadicTuple[str] = ("FlextRootSettings", "settings")
