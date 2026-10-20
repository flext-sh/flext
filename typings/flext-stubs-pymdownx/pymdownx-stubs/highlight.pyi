# @flext-generated: typing-stubs

from markdown import Extension
from markdown.treeprocessors import Treeprocessor

"""
Highlight.

A library for managing code highlighting.

All Changes Copyright 2014-2017 Isaac Muse.

---

CodeHilite Extension for Python-Markdown
========================================

Adds code/syntax highlighting to standard Python-Markdown code blocks.

See <https://pythonhosted.org/Markdown/extensions/code_hilite.html>
for documentation.

Original code Copyright 2006-2008 [Waylan Limberg](https://github.com/waylan).

All changes Copyright 2008-2014 The Python Markdown Project

License: [BSD](http://www.opensource.org/licenses/bsd-license.php)
"""
p_ver = ...
HtmlFormatter = ...
pygments = ...
RE_PYG_CODE = ...
CODE_WRAP = ...
CODE_WRAP_ON_PRE = ...
CLASS_ATTR = ...
ID_ATTR = ...
DEFAULT_CONFIG = ...
if pygments:
    class InlineHtmlFormatter(HtmlFormatter):
        def wrap(
            self, source
        ):  # -> Generator[tuple[Literal[0], Literal['']] | tuple[Any, Any], Any, None]:

            ...

    class BlockHtmlFormatter(HtmlFormatter):
        RE_SPAN_NUMS = ...
        RE_TABLE_NUMS = ...
        def __init__(self, **options) -> None: ...
        def wrap(self, source):  # -> Any:

            ...

class Highlight:
    def __init__(
        self,
        md,
        guess_lang=...,
        pygments_style=...,
        use_pygments=...,
        noclasses=...,
        extend_pygments_lang=...,
        linenums=...,
        linenums_special=...,
        linenums_style=...,
        linenums_class=...,
        language_prefix=...,
        code_attr_on_pre=...,
        auto_title=...,
        auto_title_map=...,
        line_spans=...,
        anchor_linenums=...,
        line_anchors=...,
        pygments_lang_class=...,
        stripnl=...,
        default_lang=...,
        title_mode=...,
    ) -> None: ...
    def get_extended_language(self, language): ...
    def get_lexer(self, src, language, inline, stripnl):  # -> tuple[Any, Any]:

        ...
    def escape(self, txt): ...
    def highlight(
        self,
        src,
        language,
        css_class=...,
        hl_lines=...,
        linestart=...,
        linestep=...,
        linespecial=...,
        inline=...,
        classes=...,
        id_value=...,
        attrs=...,
        title=...,
        code_block_count=...,
    ): ...

class HighlightTreeprocessor(Treeprocessor):
    def __init__(self, md, ext) -> None: ...
    def code_unescape(self, text): ...
    def run(self, root):  # -> None:

        ...

class HighlightExtension(Extension):
    def __init__(self, *args, **kwargs) -> None: ...
    def get_pymdownx_highlight_settings(self):  # -> dict[str, Any]:

        ...
    def get_pymdownx_highlighter(self):  # -> type[Highlight]:

        ...
    def extendMarkdown(self, md):  # -> None:

        ...
    def reset(self):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> HighlightExtension:

    ...
