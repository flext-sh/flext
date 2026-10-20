# @flext-generated: typing-stubs

import re
import xml.etree.ElementTree as ET

from markdown import Extension, Markdown
from markdown.inlinepatterns import InlineProcessor

"""BracketSpan."""

class BracketSpanProcessor(InlineProcessor):
    ATTR_RE = ...
    NAME_RE = ...
    def __init__(self, pattern: str, md: Markdown | None = ...) -> None: ...
    def get_next_entry(self) -> tuple[ET.Element, int, int] | None: ...
    def get_cached_result(self, start: int) -> tuple[ET.Element, int, int]: ...
    def build_element(
        self,
        data: str,
        end: int,
        current: tuple[int, list[tuple[ET.Element, int, int]]],
        attributes: str,
    ) -> tuple[ET.Element, int]: ...
    def handleMatch(
        self, m: re.Match[str], data: str
    ) -> tuple[ET.Element | str | None, int | None, int | None]: ...
    def reset(self):  # -> None:

        ...

class BracketSpanExtension(Extension):
    def __init__(self, *args, **kwargs) -> None: ...
    def extendMarkdown(self, md):  # -> None:

        ...
    def reset(self):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> BracketSpanExtension:

    ...
