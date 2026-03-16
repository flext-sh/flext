"""Type stubs for bandit.core.test_set module."""

import logging

LOG: logging.Logger

class Wrapper:
    name: str
    plugin: object
    def __init__(self, name: str, plugin: object) -> None: ...

class BanditTestSet:
    plugins: list[object]
    tests: dict[str, list[object]]
    def __init__(
        self, config: object, profile: dict[str, object] | None = None
    ) -> None: ...
    def get_tests(self, checktype: str) -> list[object]: ...
