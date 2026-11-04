"""Configuration facade for the FLEXT workspace.

Provides unified access to workspace-wide configuration parameters, immutable
contract values, and process-level configuration singletons. Extends the foundational
configuration model from ``flext-core`` to bind root workspace properties.

See Also:
    - ADR-005: Config, Settings, Constants, Templates, Schemas SSOT.
    - ADR-016: Settings & Config Singleton Contract.
    - ADR-024: DI Config Contract Derived Defaults Minimal Overrides.
    - :mod:`flext.settings`: Dynamic environment-driven settings facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import flext_core


class FlextRootConfig(flext_core.FlextConfig):
    """Process-wide workspace configuration container.

    Enforces declarative configuration invariants, provides typed accessors for
    platform parameters, and acts as the root configuration node in dependency
    injection graphs.

    See Also:
        - :class:`flext_core.FlextConfig`: Upstream base configuration contract.

    """

    @classmethod
    def published(cls) -> FlextRootConfig:
        """Retrieve the immutable process-wide configuration singleton.

        Resolves or initializes the global configuration instance cached in the
        application runtime.

        Returns:
            FlextRootConfig: Active process-wide configuration instance.

        """
        return cls.fetch_global()


config = FlextRootConfig
"""Canonical facade alias for ``FlextRootConfig``.

Allows member projects and consumers to access class-level configuration methods
and resolve the published singleton via ``config.published()``.
"""

__all__: tuple[str, ...] = ("FlextRootConfig", "config")
