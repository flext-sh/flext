"""Configuration Manager for flext_tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Self

from flext_core import FlextCore


class ConfigurationManager:
    """Configuration manager for flext_tools."""

    def __init__(self: Self, config_path: Path | str | None = None) -> None:
        """Initialize configuration manager."""
        self.config_path = Path(config_path) if config_path else None
        self._config: FlextCore.Types.StringDict = {}

    def load_config(self) -> FlextCore.Result[FlextCore.Types.StringDict]:
        """Load configuration."""
        return FlextCore.Result[FlextCore.Types.StringDict].ok(self._config)

    def save_config(self) -> FlextCore.Result[None]:
        """Save configuration."""
        return FlextCore.Result[None].ok(None)

    def get(self, key: str, default: str | None = None) -> FlextCore.Result[str | None]:
        """Get configuration value."""
        value = self._config.get(key, default)
        return FlextCore.Result[str | None].ok(value)

    def set(self, key: str, value: str) -> FlextCore.Result[None]:
        """Set configuration value."""
        self._config[key] = value
        return FlextCore.Result[None].ok(None)

    def delete(self, key: str) -> FlextCore.Result[None]:
        """Delete configuration value."""
        if key in self._config:
            del self._config[key]
        return FlextCore.Result[None].ok(None)
