import sqlalchemy.event as event
import sqlalchemy.exc as exc
import sqlalchemy.sql.events as events

class ConventionDict:
    def __init__(self, const, table, convention) -> None: ...
    def __getitem__(self, key): ...
