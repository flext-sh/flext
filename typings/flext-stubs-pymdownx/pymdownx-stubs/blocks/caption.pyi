# @flext-generated: typing-stubs

from markdown.treeprocessors import Treeprocessor

from ..blocks import BlocksExtension
from .block import Block

"""
Captions.

Captions should be placed after a block, that block will be wrapped in a `figure`
and captions will be inserted either at the end of the figure or at the beginning.
If the preceding block happens to be a `figure`, if no `figcaption` is detected
within, the caption will be injected into that figure instead of wrapping.
Keep in mind that when `md_in_html` is used and raw HTML is used, if `markdown=1`
is not present on the caption, the caption will be invisible to this extension.

Class, IDs, or other attributes will be attached to the figure, not the caption.

`types`:
    A dictionary with figure type names and prefix templates. A template will be
    used depending on whether the current type is assumed or directly specified.
`prepend`:
    Will prepend `figcaption` at the start of a `figure` instead of the end.
`auto`:
    Will generate IDs and prefixes via the provided template for all figures of
    a given type as long as they also define a prefix template.
`auto_level`:
    Auto number will not be shown below the given level depth. A value of 0, the
    default, disables the feature, 1 would show only auto-generate IDs and
    prefixes for the outermost figures with prefixes, etc. This level is only
    considered for each figure type individually.

"""
RE_FIG_NUM = ...
RE_SEP = ...

def update_tag(el, fig_type, fig_num, template, prepend, md):  # -> None:

    ...

class CaptionTreeprocessor(Treeprocessor):
    def __init__(self, md, types, config) -> None: ...
    def run(self, doc):  # -> None:

        ...

class Caption(Block):
    NAME = ...
    PREFIX = ...
    CLASSES = ...
    ARGUMENT = ...
    OPTIONS = ...
    def on_init(self):  # -> None:

        ...
    def on_validate(self, parent):  # -> bool:

        ...
    def on_create(self, parent):  # -> Element:

        ...
    def on_add(self, block):  # -> Element | None:

        ...
    def on_end(self, block):  # -> None:

        ...

class CaptionExtension(BlocksExtension):
    def __init__(self, *args, **kwargs) -> None: ...
    def extendMarkdownBlocks(self, md, block_mgr):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> CaptionExtension:

    ...
