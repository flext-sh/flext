

import ast
import collections
import logging

LOG: logging.Logger

class BanditMetaAst:
    nodes: collections.OrderedDict[str, dict[str, ast.AST | str | int]]
    def __init__(self) -> None: ...
    def add_node(self, node: ast.AST, parent_id: str, depth: int) -> None:
        ...
