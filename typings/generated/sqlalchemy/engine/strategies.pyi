import sqlalchemy.engine.mock
from typing import ClassVar

class MockEngineStrategy:
    MockConnection: ClassVar[type[sqlalchemy.engine.mock.MockConnection]] = ...
