import sqlalchemy.dialects as dialects
import sqlalchemy.engine as engine
import sqlalchemy.engine.cursor as engine_cursor
import sqlalchemy.engine.default as engine_default
import sqlalchemy.engine.reflection as engine_reflection
import sqlalchemy.engine.result as engine_result
import sqlalchemy.engine.url as engine_url
import sqlalchemy.orm as orm
import sqlalchemy.orm.attributes as orm_attributes
import sqlalchemy.orm.base as orm_base
import sqlalchemy.orm.clsregistry as orm_clsregistry
import sqlalchemy.orm.context as orm_context
import sqlalchemy.orm.decl_api as orm_decl_api
import sqlalchemy.orm.decl_base as orm_decl_base
import sqlalchemy.orm.dependency as orm_dependency
import sqlalchemy.orm.descriptor_props as orm_descriptor_props
import sqlalchemy.orm.mapper as orm_mapper
import sqlalchemy.orm.persistence as orm_persistence
import sqlalchemy.orm.properties as orm_properties
import sqlalchemy.orm.relationships as orm_relationships
import sqlalchemy.orm.session as orm_session
import sqlalchemy.orm.state as orm_state
import sqlalchemy.orm.strategies as orm_strategies
import sqlalchemy.orm.strategy_options as orm_strategy_options
import sqlalchemy.orm.util as orm_util
import sqlalchemy.sql.default_comparator as sql_default_comparator
import sqlalchemy.sql.dml as sql_dml
import sqlalchemy.sql.elements as sql_elements
import sqlalchemy.sql.functions as sql_functions
import sqlalchemy.sql.naming as sql_naming
import sqlalchemy.sql.schema as sql_schema
import sqlalchemy.sql.selectable as sql_selectable
import sqlalchemy.sql.sqltypes as sql_sqltypes
import sqlalchemy.sql.traversals as sql_traversals
import sqlalchemy.sql.util as sql_util
from typing import Callable

TYPE_CHECKING: bool

class _ModuleRegistry:
    def __init__(self, prefix: str = ...) -> None: ...
    def preload_module(self, *deps: str) -> Callable[[_FN], _FN]: ...
    def import_prefix(self, path: str) -> None: ...
preload_module: method
import_prefix: method
