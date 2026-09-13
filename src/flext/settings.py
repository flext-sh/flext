"""Settings facet for flext-workspace — settings singleton."""

from __future__ import annotations

from typing import ClassVar

from pydantic_settings import SettingsConfigDict

from flext_core import FlextSettings


class FlextRootSettings(FlextSettings):
    """Workspace root settings facade — access via settings.*."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="FLEXT_ROOT_", extra="ignore"
    )


settings: FlextRootSettings = FlextRootSettings.fetch_global()
"""Process-wide flext settings singleton resolved from the global container."""

__all__: tuple[str, ...] = ("FlextRootSettings", "settings")
