"""Type stubs for bandit.core.meta_ast module."""

import ast
import collections
import logging

LOG: logging.Logger

class BanditMetaAst:
    nodes: collections.OrderedDict[str, dict[str, ast.AST | str | int]]
    def __init__(self) -> None: ...
    def add_node(self, node: ast.AST, parent_id: str, depth: int) -> None:
        """Add a node to the AST node collection.

        :param node: The AST node to add
        :param parent_id: The ID of the node's parent
        :param depth: The depth of the node
        """
