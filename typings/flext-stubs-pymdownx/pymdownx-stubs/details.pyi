# @flext-generated: typing-stubs

from markdown import Extension
from markdown.blockprocessors import BlockProcessor

"""
Details.

pymdownx.details

MIT license.

Copyright (c) 2017 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
RE_NORMAL_HEADING = ...

class DetailsProcessor(BlockProcessor):
    START = ...
    COMPRESS_SPACES = ...
    def __init__(self, parser) -> None: ...
    def detab_by_length(self, text, length):  # -> tuple[LiteralString, str]:

        ...
    def parse_content(
        self, parent, block
    ):  # -> tuple[Element, LiteralString, str] | tuple[Element | None, Any | LiteralString, str]:

        ...
    def test(self, parent, block):  # -> bool:

        ...
    def run(self, parent, blocks):  # -> None:

        ...

class DetailsExtension(Extension):
    def extendMarkdown(self, md):  # -> None:

        ...
    def reset(self):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> DetailsExtension:

    ...
