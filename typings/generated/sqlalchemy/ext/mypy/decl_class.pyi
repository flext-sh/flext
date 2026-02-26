import util as util
from mypy.nodes import ClassDef
from mypy.plugin import SemanticAnalyzerPluginInterface

def scan_declarative_assignments_and_apply_types(cls: ClassDef, api: SemanticAnalyzerPluginInterface, is_mixin_scan: bool = ...) -> list[util.SQLAlchemyAttribute] | None: ...
