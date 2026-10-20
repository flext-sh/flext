# @flext-generated: typing-stubs

from ..blocks import BlocksExtension
from .block import Block

"""Definition."""

class Definition(Block):
    NAME = ...
    def on_create(self, parent):  # -> Element:

        ...
    def on_end(self, block):  # -> None:

        ...

class DefinitionExtension(BlocksExtension):
    def extendMarkdownBlocks(self, md, block_mgr):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> DefinitionExtension:

    ...
