# @flext-generated: typing-stubs

import xml.etree.ElementTree as ET
from typing import Any

from markdown import Extension, Markdown
from markdown.blockparser import BlockParser
from markdown.blockprocessors import BlockProcessor
from markdown.treeprocessors import Treeprocessor

"""
Extension for "enhanced" blockquotes.

This extension deviates from Python Markdown's original blockquote extension by:

- not grouping consecutive block quotes together.
- Allowing optional callout behavior that mimics GitHub or Obsidian.
"""

class QuotesProcessor(BlockProcessor):
    RE = ...
    RE_CALLOUT = ...
    def __init__(self, parser: BlockParser, config: dict[str, Any]) -> None: ...
    def test(self, parent: ET.Element, block: str) -> bool: ...
    def run(self, parent: ET.Element, blocks: list[str]) -> None: ...
    def clean(self, line: str) -> str: ...

class QuotesTreeprocessor(Treeprocessor):
    def run(self, root: ET.Element) -> ET.Element: ...

class QuotesExtension(Extension):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def extendMarkdown(self, md: Markdown) -> None: ...

def makeExtension(*args: Any, **kwargs: Any) -> Extension: ...
