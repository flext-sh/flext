# @flext-generated: typing-stubs

from markdown.blockprocessors import BlockProcessor
from markdown.treeprocessors import Treeprocessor

from .blocks import BlocksExtension
from .blocks.block import Block

"""
Fancy lists in the style of Pandoc.

---
# A Python implementation of John Gruber's Markdown.

# Started by Manfred Stienstra (http://www.dwerg.net/).
# Maintained for a few years by Yuri Takhteyev (http://www.freewisdom.org).
# Currently maintained by Waylan Limberg (https://github.com/waylan),
# Dmitry Shachnev (https://github.com/mitya57) and Isaac Muse (https://github.com/facelessuser).

# Copyright 2007-2023 The Python Markdown Project (v. 1.7 and later)
# Copyright 2004, 2005, 2006 Yuri Takhteyev (v. 0.2-1.6b)
# Copyright 2004 Manfred Stienstra (the original version)

# License: BSD (see LICENSE.md for details).
---

Adapted to support "fancy" behavior by Copyright 2024 Isaac Muse.

Work in progress, not fully tested.
"""
ROMAN_MAP = ...
OL_STYLE = ...

def roman2int(s):  # -> int:

    ...

class FancyOListProcessor(BlockProcessor):
    TAG = ...
    SIBLING_TAGS = ...
    OL_TYPES = ...
    def __init__(self, parser, config) -> None: ...
    def test(self, parent, block):  # -> bool:

        ...
    def run(self, parent, blocks):  # -> None:

        ...
    def get_start(self, fancy_type, m):  # -> str | None:

        ...
    def get_fancy_type(self, m, first, fancy_type): ...
    def get_items(
        self, sibling, block, blocks
    ):  # -> tuple[list[Any], Any | Literal['']]:

        ...

class FancyListBlock(Block):
    NAME = ...
    ARGUMENT = ...
    OL_TYPE = ...
    def on_init(self):  # -> None:

        ...
    def on_validate(self, parent):  # -> bool:

        ...
    def on_create(self, parent):  # -> Element:

        ...
    def on_end(self, block):  # -> None:

        ...

class FancyUListProcessor(FancyOListProcessor):
    SIBLING_TAGS = ...
    TAG = ...
    def __init__(self, parser, config) -> None: ...

class FancyListTreeprocessor(Treeprocessor):
    def run(self, root):  # -> Element:

        ...

class FancyListExtension(BlocksExtension):
    def __init__(self, *args, **kwargs) -> None: ...
    def extendMarkdownBlocks(self, md, blocks):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> FancyListExtension:

    ...
