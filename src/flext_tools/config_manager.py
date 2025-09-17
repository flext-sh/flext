"""Minimal configuration manager for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from pathlib import Path

from flext_core import FlextResult


class ConfigurationManager:
    """Basic configuration manager for legacy scripts."""

    def __init__(self, config_file: str | Path | None = None) -> None:
        """Initialize configuration manager."""
        self.config_file = Path(config_file) if config_file else None
        self._config: dict[str, str] = {}

    def load_config(self) -> FlextResult[dict[str, str]]:
        """Load configuration from file or environment."""
        try:
            # Load from environment variables
            self._config = {
                key: value
                for key, value in os.environ.items()
                if key.startswith(("FLEXT_", "ORACLE_", "POSTGRES_"))
            }
            return FlextResult[dict[str, str]].ok(self._config)
        except Exception as e:
            return FlextResult[dict[str, str]].fail(f"Config load failed: {e}")

    def get(self, key: str, default: str = "") -> str:
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: str) -> None:
        """Set configuration value."""
        self._config[key] = value

    def validate_config(self) -> FlextResult[None]:
        """Validate configuration."""
        return FlextResult[None].ok(None)
