"""Dynamic environment settings facade for the FLEXT workspace.

Loads and validates runtime settings from environment variables and dotenv files
using the ``FLEXT_ROOT_`` namespace prefix. Extends foundational settings from
``flext-core`` to manage workspace execution flags, host environments, and
runtime thresholds.

See Also:
    - ADR-005: Config, Settings, Constants, Templates, Schemas SSOT.
    - ADR-016: Settings & Config Singleton Contract.
    - ADR-024: DI Config Contract Derived Defaults Minimal Overrides.
    - :mod:`flext.config`: Static configuration and immutable parameters facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextSettings, m, t


class FlextRootSettings(FlextSettings):
    """Workspace environment settings contract.

    Parses, validates, and exposes dynamic runtime configuration values supplied
    via process environment variables prefixed with ``FLEXT_ROOT_``.

    Attributes:
        model_config: Pydantic settings configuration dictating environment variable
            prefix resolution and field population semantics.

    See Also:
        - :class:`flext_core.FlextSettings`: Base settings container.

    """

    model_config: ClassVar[t.SettingsConfigDict] = m.SettingsConfigDict(
        env_prefix="FLEXT_ROOT_",
    )


settings: FlextRootSettings = FlextRootSettings.fetch_global()
"""Active process-wide settings singleton.

Pre-instantiated and cached for direct import by workspace consumers:
``from flext import settings``.
"""

__all__: tuple[str, ...] = ("FlextRootSettings", "settings")
