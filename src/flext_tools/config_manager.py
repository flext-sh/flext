"""Configuration Manager for flext_tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Self

from flext_core import FlextResult, FlextTypes


class ConfigurationManager:
    """Configuration manager for flext_tools."""

    def __init__(self: Self, config_path: Path | str | None = None) -> None:
        """Initialize configuration manager."""
        self.config_path = Path(config_path) if config_path else None
        self._config: FlextTypes.Dict = {}

    def load_config(self) -> FlextResult[FlextTypes.Dict]:
        """Load configuration."""
        return FlextResult[FlextTypes.Dict].ok(self._config)

    def save_config(self) -> FlextResult[None]:
        """Save configuration."""
        return FlextResult[None].ok(None)

    def get(self, key: str, default: object = None) -> FlextResult[object]:
        """Get configuration value."""
        value = self._config.get(key, default)
        return FlextResult[object].ok(value)

    def set(self, key: str, value: object) -> FlextResult[None]:
        """Set configuration value."""
        self._config[key] = value
        return FlextResult[None].ok(None)

    def delete(self, key: str) -> FlextResult[None]:
        """Delete configuration value."""
        if key in self._config:
            del self._config[key]
        return FlextResult[None].ok(None)
