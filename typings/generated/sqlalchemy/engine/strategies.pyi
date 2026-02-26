from typing import ClassVar

import sqlalchemy.engine.mock

class MockEngineStrategy:
    MockConnection: ClassVar[type[sqlalchemy.engine.mock.MockConnection]] = ...
