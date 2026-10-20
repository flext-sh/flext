# @flext-generated: typing-stubs

from markdown import Extension
from markdown.inlinepatterns import HtmlInlineProcessor

"""
Smart Symbols.

pymdownx.smartsymbols
Really simple plugin to add support for:
  copyright, trademark, and registered symbols
  plus/minus, not equal, arrows via:

    copyright  = `(c)`
    trademark  = `(tm)`
    registered = `(r)`
    plus/minus = `+/-`
    care/of    = `c/o`
    fractions  = `1/2` etc.
        (only certain available unicode fractions)
    arrows:
        left   = `<--`
        right  = `-->`
        both   = `<-->`
    not equal  = `=/=`
       (maybe this could be =/= in the future as this might be more
        intuitive to non-programmers)

MIT license.

Copyright (c) 2014 - 2017 Isaac Muse <isaacmuse@gmail.com>

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
RE_TRADE = ...
RE_COPY = ...
RE_REG = ...
RE_PLUSMINUS = ...
RE_NOT_EQUAL = ...
RE_CARE_OF = ...
RE_ORDINAL_NUMBERS = ...
RE_ARROWS = ...
RE_FRACTIONS = ...
REPL = ...
FRAC = ...
ARR = ...

class SmartSymbolsPattern(HtmlInlineProcessor):
    def __init__(self, pattern, replace, md) -> None: ...
    def handleMatch(self, m, data):  # -> tuple[str, int, int]:

        ...

class SmartSymbolsExtension(Extension):
    def __init__(self, *args, **kwargs) -> None: ...
    def add_pattern(self, patterns, md):  # -> None:

        ...
    def extendMarkdown(self, md):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> SmartSymbolsExtension:

    ...
