import sqlalchemy.util as util
from . import extensions as extensions
from sqlalchemy.ext.declarative.extensions import AbstractConcreteBase as AbstractConcreteBase, ConcreteBase as ConcreteBase, DeferredReflection as DeferredReflection
from sqlalchemy.orm.decl_api import DeclarativeMeta as DeclarativeMeta, declared_attr as declared_attr

__all__ = ['declarative_base', 'synonym_for', 'has_inherited_table', 'instrument_declarative', 'declared_attr', 'as_declarative', 'ConcreteBase', 'AbstractConcreteBase', 'DeclarativeMeta', 'DeferredReflection']

def declarative_base(*arg, **kw): ...
def as_declarative(*arg, **kw): ...
def has_inherited_table(*arg, **kw): ...
def synonym_for(*arg, **kw): ...

# Names in __all__ with no definition:
#   AbstractConcreteBase
#   ConcreteBase
#   DeclarativeMeta
#   DeferredReflection
#   declared_attr
#   instrument_declarative
