# @flext-generated: typing-stubs

from markdown import Extension
from markdown.inlinepatterns import InlineProcessor

"""
Inline Highlighting.

pymdownx.inlinehilite

An alternative inline code extension that highlights code.  Can
use CodeHilite to source its settings or pymdownx.highlight.

`:::javascript var test = 0;`

- or -

`#!javascript var test = 0;`

Copyright 2014 - 2017 Isaac Muse <isaacmuse@gmail.com>
"""
BACKTICK_CODE_RE = ...
ESCAPED_BSLASH = ...
DOUBLE_BSLASH = ...

class InlineHiliteException(Exception): ...

class InlineHilitePattern(InlineProcessor):
    RE_LANG = ...
    def __init__(self, pattern, config, md) -> None: ...
    def extend_custom_inline(self, name, formatter):  # -> None:

        ...
    def get_settings(self):  # -> None:

        ...
    def highlight_code(
        self, src=..., language=..., classname=..., md=...
    ):  # -> Element:

        ...
    def handle_code(self, lang, src):  # -> str | None:

        ...
    def find_code_spans(self, start: int, text: str) -> tuple[int, int] | None: ...
    def handleMatch(
        self, m, data
    ):  # -> tuple[str | Any, int, int] | tuple[str | Any | None, int, int] | tuple[str, None, None] | tuple[None, None, None]:

        ...

class InlineHiliteExtension(Extension):
    def __init__(self, *args, **kwargs) -> None: ...
    def extendMarkdown(self, md):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> InlineHiliteExtension:

    ...
