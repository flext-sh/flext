"""Type stubs for bandit.core.extension_loader module."""

from __future__ import annotations

import logging

LOG: logging.Logger

class Manager:
    builtin: list[str]
    def __init__(
        self,
        formatters_namespace: str = ...,
        plugins_namespace: str = ...,
        blacklists_namespace: str = ...,
    ) -> None: ...
    def load_formatters(self, formatters_namespace: str) -> None: ...
    def load_plugins(self, plugins_namespace: str) -> None: ...
    def get_test_id(self, test_name: str) -> str | None: ...
    def load_blacklists(self, blacklist_namespace: str) -> None: ...
    def validate_profile(self, profile: dict[str, list[str]]) -> None:
        """Validate that everything in the configured profiles looks good."""
    def check_id(self, test: str) -> bool: ...

MANAGER: Manager
