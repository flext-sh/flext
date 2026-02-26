from typing import Any, ClassVar

from sqlalchemy.engine.base import Connection, Engine

TYPE_CHECKING: bool

class ConcreteBase:
    @classmethod
    def __declare_first__(cls): ...

class AbstractConcreteBase(ConcreteBase):
    __no_table__: ClassVar[bool] = ...
    @classmethod
    def __declare_first__(cls): ...

class DeferredReflection:
    _sa_decl_prepare: ClassVar[bool] = ...
    @classmethod
    def prepare(cls, bind: Engine | Connection, **reflect_kw: Any) -> None: ...
