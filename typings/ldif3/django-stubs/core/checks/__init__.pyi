from collections.abc import Sequence
from typing import Any

from django.apps.settings import AppConfig
from django.core.checks.messages import CheckMessage

def check_all_models(
    app_configs: Sequence[AppConfig] | None = ..., **kwargs: Any
) -> Sequence[CheckMessage]: ...
def check_lazy_references(
    app_configs: Sequence[AppConfig] | None = ..., **kwargs: Any
) -> Sequence[CheckMessage]: ...
