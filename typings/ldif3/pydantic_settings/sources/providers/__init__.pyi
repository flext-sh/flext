from typing import TYPE_CHECKING

from pydantic_settings.main import BaseSettings

from ..base import ConfigFileSourceMixin, InitSettingsSource
from ..types import PathType

"""YAML file settings source."""
if TYPE_CHECKING: ...

def import_yaml() -> None: ...

class YamlConfigSettingsSource(InitSettingsSource, ConfigFileSourceMixin):
    def __init__(
        self,
        settings_cls: type[BaseSettings],
        yaml_file: PathType | None = ...,
        yaml_file_encoding: str | None = ...,
        yaml_config_section: str | None = ...,
    ) -> None: ...

__all__ = ["YamlConfigSettingsSource"]
