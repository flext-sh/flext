# @flext-generated: typing-stubs

from markdown.treeprocessors import Treeprocessor

from ..blocks import BlocksExtension
from .block import Block

"""Tabs."""
HEADERS = ...

class TabbedTreeprocessor(Treeprocessor):
    def __init__(self, md, config) -> None: ...
    def get_parent_header_slug(
        self, root, header_map, parent_map, el
    ):  # -> Literal['']:

        ...
    def run(self, doc):  # -> None:

        ...

class Tab(Block):
    NAME = ...
    ARGUMENT = ...
    OPTIONS = ...
    def on_init(self):  # -> None:

        ...
    def last_child(self, parent):  # -> None:

        ...
    def on_add(self, block):  # -> Element | None:

        ...
    def on_create(self, parent):  # -> Element:

        ...

class TabExtension(BlocksExtension):
    def __init__(self, *args, **kwargs) -> None: ...
    def extendMarkdownBlocks(self, md, block_mgr):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> TabExtension:

    ...
